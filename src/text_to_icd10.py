import json
import re
from typing import Optional

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.icd10data.com"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

MAX_CANDIDATES = 5

STOP_WORDS = {
    "and",
    "or",
    "of",
    "the",
    "with",
    "without",
    "in",
    "on",
    "for",
    "a",
    "an",
}


def clean_text(text: str) -> str:
    """
    Normalize whitespace.
    """

    return " ".join(text.split())


def text_to_words(text: str) -> list[str]:
    """
    Convert text into normalized words.
    """

    text = text.lower()

    words = re.findall(
        r"[a-z0-9]+",
        text,
    )

    return [word for word in words if word not in STOP_WORDS]


def calculate_match_score(
    input_words: list[str],
    candidate_text: str,
) -> int:
    """
    Calculate keyword overlap between the search term
    and the ICD-10 description.
    """

    candidate_words = text_to_words(candidate_text)

    input_set = set(input_words)
    candidate_set = set(candidate_words)

    return len(input_set & candidate_set)


def extract_code(search_line) -> Optional[str]:
    """
    Extract the ICD-10 code from one search result.
    """

    identifier = search_line.select_one("span.identifier")

    if not identifier:
        return None

    code = clean_text(
        identifier.get_text(
            " ",
            strip=True,
        )
    ).upper()

    if not code:
        return None

    return code


def extract_description(
    search_line,
) -> Optional[str]:
    """
    Extract the description shown for an ICD-10
    search result.
    """

    search_padded = search_line.select_one("div.searchPadded")

    if not search_padded:
        return None

    description = search_padded.find(
        "div",
        recursive=False,
    )

    if not description:
        return None

    text = clean_text(
        description.get_text(
            " ",
            strip=True,
        )
    )
    return text or None


def get_icd10_candidates(
    search_term: str,
) -> list[dict]:
    """
    Search ICD10Data for one search term.

    Returns multiple candidate codes ranked by
    keyword-match score.

    This function does NOT make the final coding decision.
    """

    search_term = clean_text(search_term)

    if not search_term:
        return []

    print(f"Searching for: {search_term}")

    input_words = text_to_words(search_term)

    response = requests.get(
        f"{BASE_URL}/search",
        params={"s": search_term},
        headers=HEADERS,
        timeout=15,
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    candidates = []

    # ---------------------------------------------
    # GET SEARCH RESULTS
    # ---------------------------------------------

    for search_line in soup.select(".searchLine"):
        code = extract_code(search_line)

        if not code:
            continue

        description = extract_description(search_line)

        if not description:
            continue

        score = calculate_match_score(
            input_words,
            description,
        )

        candidates.append(
            {
                "code": code,
                "description": description,
                "score": score,
            }
        )

    if not candidates:
        print("No ICD-10 results found.")

        return []

    # ---------------------------------------------
    # DEDUPLICATE CODES
    # ---------------------------------------------

    unique_candidates = {}

    for candidate in candidates:
        code = candidate["code"]

        existing = unique_candidates.get(code)

        if existing is None:
            unique_candidates[code] = candidate

        elif candidate["score"] > existing["score"]:
            unique_candidates[code] = candidate

    candidates = list(unique_candidates.values())

    # ---------------------------------------------
    # RANK CANDIDATES
    # ---------------------------------------------

    candidates.sort(
        key=lambda item: (
            -item["score"],
            item["code"],
        )
    )

    # for candidate in candidates:
    #     print(
    #         candidate["code"],
    #         "|",
    #         candidate["description"],
    #         "| score:",
    #         candidate["score"],
    #     )
    return candidates[:MAX_CANDIDATES]


def process_condition(
    condition: dict,
) -> dict:
    """
    Retrieve ICD-10 candidates for one condition.
    """

    results = []

    for search_term in condition.get(
        "search_terms",
        [],
    ):
        candidates = get_icd10_candidates(search_term)

        results.append(
            {
                "search_term": search_term,
                "candidates": candidates,
            }
        )

    return {
        "source_type": "condition",
        "condition": condition.get("name"),
        "status": condition.get("status"),
        "encounter_relevance": condition.get("encounter_relevance"),
        "results": results,
    }


def process_relationship(
    relationship: dict,
) -> dict:
    """
    Retrieve ICD-10 candidates for one
    condition relationship.

    Conditions are NOT combined into one search
    query. The relationship's own search terms
    are used.
    """

    results = []

    for search_term in relationship.get(
        "search_terms",
        [],
    ):
        candidates = get_icd10_candidates(search_term)

        results.append(
            {
                "search_term": search_term,
                "candidates": candidates,
            }
        )

    return {
        "source_type": "relationship",
        "condition_1": relationship.get("condition_1"),
        "condition_2": relationship.get("condition_2"),
        "relationship": relationship.get("relationship"),
        "results": results,
    }


def text_to_icd10(
    llm_output: dict,
) -> dict:
    """
    Process the complete LLM #1 output.

    Handles:
        - current conditions
        - historical conditions
        - relationships

    Returns candidate ICD-10 codes.

    No final coding decision is made here.
    """

    results = []

    # ---------------------------------------------
    # CURRENT CONDITIONS
    # ---------------------------------------------

    for condition in llm_output.get(
        "current_conditions",
        [],
    ):
        results.append(process_condition(condition))

    # ---------------------------------------------
    # HISTORICAL CONDITIONS
    # ---------------------------------------------

    for condition in llm_output.get(
        "historical_conditions",
        [],
    ):
        results.append(process_condition(condition))

    # ---------------------------------------------
    # RELATIONSHIPS
    # ---------------------------------------------

    for relationship in llm_output.get(
        "relationships",
        [],
    ):
        results.append(process_relationship(relationship))

    return {"results": results}


def main():
    """
    Read LLM #1 JSON from the terminal and
    retrieve ICD-10 candidates.
    """

    print("Paste the LLM #1 JSON below.")

    llm_output = input()

    try:
        data = json.loads(llm_output)

    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid JSON: {error}")

    output = text_to_icd10(data)

    print()
    print("=" * 60)
    print("ICD-10 CANDIDATE RESULTS")
    print("=" * 60)

    print(
        json.dumps(
            output,
            indent=2,
        )
    )
    with open("icd10_candidates.json", "w") as outfile:
        json.dump(output, outfile, indent=2)


if __name__ == "__main__":
    main()
    # get_icd10_candidates("Dental caries")
