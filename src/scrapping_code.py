import re
import time
from collections import OrderedDict
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://www.icd10data.com"

MAX_RETRIES = 3
RETRY_DELAY = 2

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}


# ============================================================
# TEXT CLEANING
# ============================================================


def normalize_icd_code(code: str) -> str:
    return re.sub(r"\s+", "", code).upper()


def clean_text(value) -> str:
    """
    Normalize whitespace from a BeautifulSoup element or string.
    """

    if isinstance(value, Tag):
        text = " ".join(value.stripped_strings)
    else:
        text = str(value)

    text = text.replace("\xa0", " ")
    text = " ".join(text.split())

    return text.strip()


# ============================================================
# HTTP SESSION
# ============================================================


def create_session() -> requests.Session:
    """
    Create a reusable HTTP session.
    """

    session = requests.Session()
    session.headers.update(HEADERS)

    return session


# ============================================================
# REQUEST WITH RETRIES
# ============================================================


def request_with_retries(
    session: requests.Session,
    method: str,
    url: str,
    **kwargs,
) -> requests.Response:
    """
    Perform an HTTP request with up to 3 retries.

    Retryable:
        - Connection errors
        - Timeout errors
        - HTTP 429
        - HTTP 5xx

    Backoff:
        2 seconds
        4 seconds
        8 seconds
    """

    last_exception = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = session.request(
                method,
                url,
                **kwargs,
            )

            # ------------------------------------------------
            # Retry rate limiting and server errors.
            # ------------------------------------------------

            if response.status_code == 429 or response.status_code >= 500:
                if attempt < MAX_RETRIES:
                    delay = RETRY_DELAY * (2**attempt)

                    print(
                        f"Request returned HTTP "
                        f"{response.status_code}. "
                        f"Retrying in {delay} seconds "
                        f"({attempt + 1}/{MAX_RETRIES})..."
                    )

                    time.sleep(delay)

                    continue

            response.raise_for_status()

            return response

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        ) as exc:
            last_exception = exc

            if attempt < MAX_RETRIES:
                delay = RETRY_DELAY * (2**attempt)

                print(
                    f"Request failed: {exc}. "
                    f"Retrying in {delay} seconds "
                    f"({attempt + 1}/{MAX_RETRIES})..."
                )

                time.sleep(delay)

            else:
                print(f"Request failed after {MAX_RETRIES} retries.")
                print(f"URL: {url}")
                print(f"Reason: {exc}")

    if last_exception:
        raise last_exception

    raise requests.exceptions.RequestException("Request failed.")


# ============================================================
# REMOVE UNWANTED CONTENT
# ============================================================


def remove_unwanted_content(
    soup: BeautifulSoup,
) -> None:
    """
    Remove hidden popovers, scripts, ads, Convert links,
    and other elements that can pollute text extraction.
    """

    selectors = [
        ".z32",
        ".inPopover",
        ".tip",
        ".tipHelp",
        ".images-note",
        "script",
        "style",
        "noscript",
        "iframe",
    ]

    # --------------------------------------------------------
    # Remove selector-based unwanted elements.
    #
    # Take a snapshot before decompose().
    # --------------------------------------------------------

    for selector in selectors:
        elements = list(soup.select(selector))

        for element in elements:
            if (
                getattr(
                    element,
                    "parent",
                    None,
                )
                is not None
            ):
                element.decompose()

    # --------------------------------------------------------
    # Remove advertisement containers.
    #
    # "ad-leaderboard" is a SUBSTRING of the class name.
    #
    # Examples:
    #
    #   ad-leaderboard
    #   foo ad-leaderboard bar
    #   ad-leaderboard-container
    #   footer-ad-leaderboard
    #
    # All of these match.
    # --------------------------------------------------------

    divs = list(soup.find_all("div"))

    for div in divs:
        attrs = getattr(
            div,
            "attrs",
            None,
        )

        if not attrs:
            continue

        classes = attrs.get(
            "class",
            [],
        )

        if not isinstance(
            classes,
            list,
        ):
            continue

        class_string = " ".join(classes)

        if "ad-leaderboard" in class_string:
            if (
                getattr(
                    div,
                    "parent",
                    None,
                )
                is not None
            ):
                div.decompose()

    # --------------------------------------------------------
    # Remove Convert entries.
    #
    # Remove the entire containing <p> or <li> when the href
    # contains "Convert" anywhere.
    # --------------------------------------------------------

    links = list(
        soup.find_all(
            "a",
            href=True,
        )
    )

    for link in links:
        attrs = getattr(
            link,
            "attrs",
            None,
        )

        if not attrs:
            continue

        href = attrs.get(
            "href",
            "",
        )

        if not isinstance(
            href,
            str,
        ):
            continue

        if "Convert" in href:
            parent = link.find_parent(["p", "li"])

            if parent is not None:
                if (
                    getattr(
                        parent,
                        "parent",
                        None,
                    )
                    is not None
                ):
                    parent.decompose()

            else:
                link.decompose()


# ============================================================
# FIND EXACT ICD-10 URL
# ============================================================


def get_icd10data_url(
    session: requests.Session,
    code: str,
) -> Optional[str]:
    """
    Find the exact ICD-10Data URL using the site's search page.

    IMPORTANT:
        We use the site's search endpoint instead of constructing
        the ICD URL ourselves.

        Example:

            I10

        resolves to:

            /ICD10CM/Codes/I00-I99/I10-I1A/I10-/I10
    """

    code = normalize_icd_code(code)

    response = request_with_retries(
        session,
        "GET",
        f"{BASE_URL}/search",
        params={
            "s": code,
        },
        timeout=20,
    )

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # --------------------------------------------------------
    # Find exact search result.
    # --------------------------------------------------------

    for search_line in soup.select(".searchLine"):
        identifier = search_line.select_one("span.identifier")

        if not identifier:
            continue

        found_code = normalize_icd_code(identifier.get_text(" ", strip=True))

        # Exact code match only.
        if found_code != code:
            continue

        # Prefer the main result link.
        link = search_line.select_one("strong a[href]")

        # Fallback.
        if not link:
            link = search_line.select_one("a[href]")

        if not link:
            continue

        href = link.get("href")

        if not isinstance(
            href,
            str,
        ):
            continue

        return urljoin(
            BASE_URL,
            href,
        )

    return None


# ============================================================
# FIND MAIN ICD CODE CONTAINER
# ============================================================


def get_main_heading_container(
    soup: BeautifulSoup,
    code: str,
) -> Optional[Tag]:
    """
    Find the headingContainer belonging to the requested
    ICD-10 code.
    """

    code = normalize_icd_code(code)

    for container in soup.select("div.headingContainer"):
        identifier = container.select_one("span.identifierDetail")

        if not identifier:
            continue

        found_code = normalize_icd_code(identifier.get_text(" ", strip=True))

        if found_code == code:
            return container

    return None


# ============================================================
# GET DESCRIPTION
# ============================================================


def get_description(
    heading_container: Tag,
) -> Optional[str]:
    """
    Extract the main ICD description.
    """

    description_tag = heading_container.find_next_sibling(
        "h2",
        class_="codeDescription",
    )

    if description_tag:
        return clean_text(description_tag)

    return None


# ============================================================
# DETECT NEXT ICD CODE
# ============================================================


def is_next_code_heading(
    tag: Tag,
    main_heading: Tag,
) -> bool:
    """
    Detect another ICD headingContainer.
    """

    if tag is main_heading:
        return False

    if tag.name != "div":
        return False

    classes = tag.get("classes") or []

    if not isinstance(
        classes,
        list,
    ):
        return False

    return "headingContainer" in classes


# ============================================================
# SECTION NORMALIZATION
# ============================================================


def normalize_section_text(
    text: str,
) -> str:
    """
    Normalize heading text for comparison.
    """

    text = clean_text(text)

    text = text.replace(
        ":",
        "",
    )

    return text.lower().strip()


# ============================================================
# SECTION DETECTION
# ============================================================


def get_section_name(
    tag: Tag,
) -> Optional[str]:
    """
    Determine whether a tag represents an ICD section heading.
    """

    if tag.name not in {
        "span",
        "div",
        "h2",
        "h3",
        "h4",
        "h5",
        "strong",
    }:
        return None

    text = clean_text(tag)

    if not text:
        return None

    if len(text) > 180:
        return None

    normalized = normalize_section_text(text)

    classes = tag.get("classes") or []

    if isinstance(
        classes,
        list,
    ):
        class_string = " ".join(classes).lower()

        if "headingcontainer" in class_string:
            return None

        if "codedescription" in class_string:
            return None

    # --------------------------------------------------------
    # Exact section headings.
    # --------------------------------------------------------

    exact_headings = {
        "includes": "INCLUDES",
        "type 1 excludes": "TYPE 1 EXCLUDES",
        "excludes1": "TYPE 1 EXCLUDES",
        "excludes 1": "TYPE 1 EXCLUDES",
        "type 2 excludes": "TYPE 2 EXCLUDES",
        "excludes2": "TYPE 2 EXCLUDES",
        "excludes 2": "TYPE 2 EXCLUDES",
        "approximate synonyms": "APPROXIMATE SYNONYMS",
        "present on admission": "PRESENT ON ADMISSION",
        "clinical information": "CLINICAL INFORMATION",
        "coding rules": "ICD-10-CM CODING RULES",
        "code history": "CODE HISTORY",
        "code also": "CODE ALSO",
        "code first": "CODE FIRST",
        "applicable to": "APPLICABLE TO",
        "parent code notes": "PARENT CODE NOTES",
        "use additional": "USE ADDITIONAL",
        "use external cause": "USE EXTERNAL CAUSE",
    }

    if normalized in exact_headings:
        return exact_headings[normalized]

    # --------------------------------------------------------
    # Annotation back-references.
    # --------------------------------------------------------

    if normalized.startswith("the following code(s) above"):
        if "contain annotation back-references" in normalized:
            return "ANNOTATION BACK-REFERENCES"

        if "may be applicable to" in normalized:
            return "ANNOTATION BACK-REFERENCES"

    # --------------------------------------------------------
    # Diagnosis Index.
    # --------------------------------------------------------

    if normalized.startswith("diagnosis index entries containing back-references to"):
        return "DIAGNOSIS INDEX ENTRIES CONTAINING BACK-REFERENCES"

    # --------------------------------------------------------
    # Diagnostic Related Groups.
    # --------------------------------------------------------

    if (
        normalized.startswith("icd-10-cm ")
        and "is grouped within diagnostic related group" in normalized
    ):
        return "DIAGNOSTIC RELATED GROUPS"

    # --------------------------------------------------------
    # NO Convert section.
    #
    # Convert links are removed before extraction.
    # --------------------------------------------------------

    return None


# ============================================================
# LIST EXTRACTION
# ============================================================


def extract_list_items(
    ul: Tag,
) -> list[str]:
    """
    Extract direct <li> children only.
    """

    results = []

    for li in ul.find_all(
        "li",
        recursive=False,
    ):
        li_copy = BeautifulSoup(
            str(li),
            "html.parser",
        ).find("li")

        if li_copy is None:
            continue

        # Remove helper content from copied LI.
        for unwanted in li_copy.select(
            ".z32, .inPopover, .tip, .tipHelp, .images-note"
        ):
            unwanted.decompose()

        text = clean_text(li_copy)

        if text and text not in results:
            results.append(text)

    return results


# ============================================================
# ANNOTATION LIST EXTRACTION
# ============================================================


def extract_annotation_list(
    heading_tag: Tag,
) -> list[str]:
    """
    Extract the list associated with:

        Type 1 Excludes
        Type 2 Excludes
        Includes
    """

    results = []

    parent = heading_tag.parent

    if not isinstance(
        parent,
        Tag,
    ):
        return results

    # --------------------------------------------------------
    # Preferred: direct UL.
    # --------------------------------------------------------

    direct_uls = parent.find_all(
        "ul",
        recursive=False,
    )

    for ul in direct_uls:
        for item in extract_list_items(ul):
            if item not in results:
                results.append(item)

    if results:
        return results

    # --------------------------------------------------------
    # Fallback: nearby siblings.
    # --------------------------------------------------------

    current = heading_tag

    for _ in range(10):
        current = current.find_next_sibling()

        if current is None:
            break

        if not isinstance(
            current,
            Tag,
        ):
            continue

        if get_section_name(current):
            break

        if current.name == "ul":
            for item in extract_list_items(current):
                if item not in results:
                    results.append(item)

            break

    return results


# ============================================================
# FOOTER DETECTION
# ============================================================


def is_footer_text(
    text: str,
) -> bool:
    """
    Detect known ICD10Data footer content.
    """

    text_lower = clean_text(text).lower()

    footer_markers = [
        "reimbursement claims with a date of service",
        "advertise with us",
        "license icd10 data",
        "copyright",
        "all about icd-10",
        "coders' specialty guide",
    ]

    return any(marker in text_lower for marker in footer_markers)


# ============================================================
# DIAGNOSIS INDEX EXTRACTION
# ============================================================


def extract_diagnosis_index(
    heading_tag: Tag,
) -> list[str]:
    """
    Extract Diagnosis Index entries.
    """

    results = []

    parent = heading_tag.parent

    if not isinstance(
        parent,
        Tag,
    ):
        return results

    # --------------------------------------------------------
    # Direct UL.
    # --------------------------------------------------------

    for ul in parent.find_all(
        "ul",
        recursive=False,
    ):
        for item in extract_list_items(ul):
            if is_footer_text(item):
                continue

            if item not in results:
                results.append(item)

    if results:
        return results

    # --------------------------------------------------------
    # Fallback.
    # --------------------------------------------------------

    current = heading_tag

    for _ in range(10):
        current = current.find_next_sibling()

        if current is None:
            break

        if not isinstance(
            current,
            Tag,
        ):
            continue

        if get_section_name(current):
            break

        if current.name == "ul":
            for item in extract_list_items(current):
                if not is_footer_text(item):
                    if item not in results:
                        results.append(item)

            break

    return results


# ============================================================
# EXTRACT ALL SECTIONS DYNAMICALLY
# ============================================================


def extract_dynamic_sections(
    heading_container: Tag,
) -> dict[str, list[str]]:
    """
    Dynamically extract ICD sections.

    Extraction stops when:
        - another ICD code begins
        - another recognized section begins
        - footer content begins
    """

    sections = OrderedDict()

    current_section = None

    for tag in heading_container.find_all_next():
        if not isinstance(
            tag,
            Tag,
        ):
            continue

        # ----------------------------------------------------
        # Stop at next ICD code.
        # ----------------------------------------------------

        if is_next_code_heading(
            tag,
            heading_container,
        ):
            break

        # ----------------------------------------------------
        # Ignore unwanted content.
        # ----------------------------------------------------

        attrs = getattr(
            tag,
            "attrs",
            None,
        )

        if attrs:
            classes = attrs.get(
                "class",
                [],
            )

            if isinstance(
                classes,
                list,
            ):
                class_string = " ".join(classes)

                if "ad-leaderboard" in class_string:
                    continue

                if "z32" in classes:
                    continue

        # ----------------------------------------------------
        # Detect section heading.
        # ----------------------------------------------------

        section_name = get_section_name(tag)

        if section_name:
            current_section = section_name

            if current_section not in sections:
                sections[current_section] = []

            # ------------------------------------------------
            # Type 1 / Type 2 / Includes.
            # ------------------------------------------------

            if current_section in {
                "TYPE 1 EXCLUDES",
                "TYPE 2 EXCLUDES",
                "INCLUDES",
            }:
                items = extract_annotation_list(tag)

                for item in items:
                    if item not in sections[current_section]:
                        sections[current_section].append(item)

            # ------------------------------------------------
            # Diagnosis Index.
            # ------------------------------------------------

            elif current_section == (
                "DIAGNOSIS INDEX ENTRIES CONTAINING BACK-REFERENCES"
            ):
                items = extract_diagnosis_index(tag)

                for item in items:
                    if item not in sections[current_section]:
                        sections[current_section].append(item)

            continue

        # ----------------------------------------------------
        # No active section.
        # ----------------------------------------------------

        if current_section is None:
            continue

        # ----------------------------------------------------
        # Sections already extracted directly.
        # ----------------------------------------------------

        if current_section in {
            "TYPE 1 EXCLUDES",
            "TYPE 2 EXCLUDES",
            "INCLUDES",
            "DIAGNOSIS INDEX ENTRIES CONTAINING BACK-REFERENCES",
        }:
            continue

        # ----------------------------------------------------
        # Footer.
        # ----------------------------------------------------

        text = clean_text(tag)

        if is_footer_text(text):
            current_section = None

            continue

        # ----------------------------------------------------
        # Lists.
        # ----------------------------------------------------

        if tag.name in {
            "ul",
            "ol",
        }:
            items = extract_list_items(tag)

            for item in items:
                if item not in sections[current_section]:
                    sections[current_section].append(item)

            continue

        # ----------------------------------------------------
        # Avoid processing list descendants twice.
        # ----------------------------------------------------

        parent = tag.parent

        if isinstance(
            parent,
            Tag,
        ):
            if parent.name in {
                "li",
                "ul",
                "ol",
            }:
                continue

        # ----------------------------------------------------
        # Paragraphs.
        # ----------------------------------------------------

        if tag.name == "p":
            if text:
                if text not in sections[current_section]:
                    sections[current_section].append(text)

    # --------------------------------------------------------
    # Remove empty sections.
    # --------------------------------------------------------

    sections = OrderedDict(
        (
            name,
            values,
        )
        for name, values in sections.items()
        if values
    )

    return dict(sections)


# ============================================================
# GET CODE METADATA
# ============================================================


def get_code_metadata(
    heading_container: Tag,
) -> dict:
    """
    Extract whether the ICD-10-CM code is billable/specific.

    Returns:
        {
            "billable": True | False | None
        }

    None means the billable status could not be determined
    from the page.
    """

    metadata: dict[str, Optional[bool]] = {
        "billable": None,
    }

    for ul in heading_container.find_all_next("ul"):
        previous_code = ul.find_previous(
            "div",
            class_="headingContainer",
        )

        if previous_code is not heading_container:
            break

        items = [
            clean_text(li)
            for li in ul.find_all(
                "li",
                recursive=False,
            )
        ]

        for item in items:
            item_lower = item.lower()

            if "should not be used for reimbursement purposes" in item_lower:
                metadata["billable"] = False

            elif (
                "is a billable/specific icd-10-cm code" in item_lower
                and "reimbursement purposes" in item_lower
            ):
                metadata["billable"] = True

    return metadata


# ============================================================
# MAIN ICD EXTRACTION FUNCTION
# ============================================================


def get_icd10_info(
    code: str,
) -> Optional[dict]:
    """
    Retrieve and extract ICD-10-CM information.
    """

    code = normalize_icd_code(code)

    print(f"Searching for ICD code: {code}")

    session = create_session()

    try:
        # ----------------------------------------------------
        # STEP 1: Find exact ICD URL.
        # ----------------------------------------------------

        url = get_icd10data_url(
            session,
            code,
        )

        if not url:
            print(f"Could not find ICD code: {code}")

            return None

        print(f"Found URL: {url}")

        # ----------------------------------------------------
        # STEP 2: Download ICD page.
        # ----------------------------------------------------

        response = request_with_retries(
            session,
            "GET",
            url,
            timeout=20,
        )

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # ----------------------------------------------------
        # STEP 3: Remove unwanted content.
        # ----------------------------------------------------

        remove_unwanted_content(soup)

        # ----------------------------------------------------
        # STEP 4: Find exact code container.
        # ----------------------------------------------------

        heading_container = get_main_heading_container(
            soup,
            code,
        )

        if not heading_container:
            print("Could not find the main ICD heading.")

            return None

        # ----------------------------------------------------
        # STEP 5: Extract code metadata.
        # ----------------------------------------------------

        metadata = get_code_metadata(heading_container)

        # ----------------------------------------------------
        # STEP 6: Extract sections.
        # ----------------------------------------------------

        sections = extract_dynamic_sections(heading_container)

        # ----------------------------------------------------
        # STEP 7: Return structured data.
        # ----------------------------------------------------

        return {
            "code": code,
            "description": get_description(heading_container),
            "url": url,
            "billable": metadata["billable"],
            "sections": sections,
        }

    except requests.exceptions.RequestException as exc:
        print(f"Unable to retrieve ICD data: {exc}")

        return None

    finally:
        session.close()


# ============================================================
# PRINT RESULTS
# ============================================================


def print_icd10_info(
    data: dict,
) -> None:
    """
    Print extracted ICD information.
    """

    print()

    print("=" * 70)

    print(f"CODE: {data['code']}")

    print(f"DESCRIPTION: {data['description']}")

    print(f"URL: {data['url']}")

    print(f"BILLABLE: {data['billable']}")

    for (
        section_name,
        items,
    ) in data["sections"].items():
        print()

        print(f"{section_name.upper()}:")

        if not items:
            print("  None")

            continue

        for item in items:
            print(f"  - {item}")

    print()

    print("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    code = input("Enter ICD-10 code: ").strip().upper()

    if not code:
        print("No ICD-10 code entered.")

    else:
        data = get_icd10_info(code)

        if data:
            print_icd10_info(data)
