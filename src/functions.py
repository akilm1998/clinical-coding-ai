import base64
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime

from scrapping_code import get_icd10_info

MAX_CODING_CANDIDATES = 50


def get_data(patient_data: str):
    with open(patient_data, "r") as file:
        data = json.load(file)
        return data


def normalize_patient_data(data):
    """
    Normalize a Synthea FHIR Bundle into a patient-centric structure
    suitable for downstream clinical-document generation.

    Input:
        data: parsed FHIR Bundle (dict)

    Returns:
        dict containing patient demographics and encounter-linked
        clinical resources.
    """

    resources = [
        entry["resource"] for entry in data.get("entry", []) if "resource" in entry
    ]

    patient = next((r for r in resources if r.get("resourceType") == "Patient"), None)

    if patient is None:
        raise ValueError("FHIR Bundle does not contain a Patient resource.")

    normalized = {
        "patient": _normalize_patient(patient),
        "encounters": [],
    }

    for encounter in (r for r in resources if r.get("resourceType") == "Encounter"):
        normalized["encounters"].append(_normalize_encounter(encounter, resources))

    return normalized


def _normalize_patient(patient):
    """Extract patient-level information relevant to clinical context."""

    name = patient.get("name", [{}])[0]

    full_name = (
        name.get("prefix", [""])[0]
        + " "
        + name.get("given", [""])[0]
        + " "
        + name.get("family", "")
    ).strip()

    birth_date = patient.get("birthDate")
    alive = is_patient_alive(patient)

    return {
        "name": full_name,
        "gender": patient.get("gender"),
        "birth_date": birth_date,
        "alive": alive,
        "marital_status": patient.get("maritalStatus", {}).get("text"),
        "language": _get_language(patient),
        "race": _get_extension_value(patient, "us-core-race"),
        "ethnicity": _get_extension_value(patient, "us-core-ethnicity"),
    }


def is_patient_alive(patient):
    if patient.get("deceasedBoolean") is True:
        return False

    if patient.get("deceasedDateTime") is not None:
        return False

    return True


def _normalize_encounter(encounter, resources):
    """Build the clinical context associated with one encounter."""

    encounter_id = encounter.get("id")

    return {
        "id": encounter_id,
        "status": encounter.get("status"),
        "class": encounter.get("class", {}).get("code"),
        "type": _extract_codeable_concept(encounter.get("type", [])),
        "period": encounter.get("period"),
        "reason": _extract_codeable_concept(encounter.get("reasonCode", [])),
        "conditions": _find_resources_for_encounter(
            "Condition", encounter_id, resources
        ),
        "medications": _find_resources_for_encounter(
            "MedicationRequest", encounter_id, resources
        ),
        "observations": _find_resources_for_encounter(
            "Observation", encounter_id, resources
        ),
        "diagnostic_reports": _find_resources_for_encounter(
            "DiagnosticReport", encounter_id, resources
        ),
        "procedures": _find_resources_for_encounter(
            "Procedure", encounter_id, resources
        ),
        "notes": _find_resources_for_encounter(
            "DocumentReference", encounter_id, resources
        ),
    }


def calculate_age_at_encounter(birth_date, encounter_date):
    if not birth_date or not encounter_date:
        return None

    birth = date.fromisoformat(birth_date)
    encounter = date.fromisoformat(encounter_date)

    return (
        encounter.year
        - birth.year
        - ((encounter.month, encounter.day) < (birth.month, birth.day))
    )


def _find_resources_for_encounter(resource_type, encounter_id, resources):
    """Find resources explicitly linked to an encounter."""

    matches = []

    for resource in resources:
        if resource.get("resourceType") != resource_type:
            continue

        encounter = resource.get("encounter", {})
        reference = encounter.get("reference", "")

        if reference.endswith(encounter_id):
            matches.append(resource)

    return matches


def get_active_conditions(resources, current_date):
    active_conditions = []

    for resource in resources:
        if resource.get("resourceType") != "Condition":
            continue

        condition_status = (
            resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code")
        )

        if condition_status != "active":
            continue

        onset = resource.get("onsetDateTime")

        if onset:
            onset_date = datetime.fromisoformat(onset)

            if onset_date > current_date:
                continue

        active_conditions.append(resource)

    return active_conditions


def get_condition_encounter(condition, encounters):
    encounter_reference = condition.get("encounter", {}).get("reference")

    if not encounter_reference:
        return None

    for encounter in encounters:
        if encounter_reference.endswith(encounter.get("id", "")):
            return encounter

    return None


def get_condition_evidence(condition, resources, encounters):

    encounter = get_condition_encounter(condition, encounters)

    if encounter is None:
        return {"condition": condition, "evidence": []}

    encounter_id = encounter.get("id")

    encounter_evidence = {
        "encounter_id": encounter_id,
        "encounter_date": encounter.get("period", {}).get("start"),
        "resources": {
            "conditions": _find_resources_for_encounter(
                "Condition", encounter_id, resources
            ),
            "procedures": _find_resources_for_encounter(
                "Procedure", encounter_id, resources
            ),
            "observations": _find_resources_for_encounter(
                "Observation", encounter_id, resources
            ),
            "medications": _find_resources_for_encounter(
                "MedicationRequest", encounter_id, resources
            ),
            "diagnostic_reports": _find_resources_for_encounter(
                "DiagnosticReport", encounter_id, resources
            ),
            "document_references": _find_resources_for_encounter(
                "DocumentReference", encounter_id, resources
            ),
        },
    }

    return {"condition": condition, "evidence": [encounter_evidence]}


def _extract_codeable_concept(items):
    """Extract coding information from CodeableConcept-like structures."""

    result = []

    for item in items or []:
        for coding in item.get("coding", []):
            result.append(
                {
                    "system": coding.get("system"),
                    "code": coding.get("code"),
                    "display": coding.get("display"),
                }
            )

        if item.get("text"):
            result.append({"text": item["text"]})

    return result


def _get_language(patient):

    communication = patient.get("communication", [])

    if not communication:
        return None

    return communication[0].get("language", {}).get("text")


def _get_extension_value(patient, extension_name):
    """Extract the text value from a US Core patient extension."""

    for extension in patient.get("extension", []):
        if extension_name not in extension.get("url", ""):
            continue

        for nested in extension.get("extension", []):
            if nested.get("url") == "text":
                return nested.get("valueString")

    return None


def get_encounter_data(data, encounter_id):
    resources = [
        entry["resource"] for entry in data.get("entry", []) if "resource" in entry
    ]

    encounter = next(
        (
            resource
            for resource in resources
            if resource.get("resourceType") == "Encounter"
            and resource.get("id") == encounter_id
        ),
        None,
    )

    if encounter is None:
        raise ValueError(f"Encounter not found: {encounter_id}")

    diagnostic_reports = _find_resources_for_encounter(
        "DiagnosticReport",
        encounter_id,
        resources,
    )

    notes = []

    for report in diagnostic_reports:
        clinical_note = decode_note(report)

        if clinical_note is not None:
            notes.append(
                {
                    "source": "DiagnosticReport",
                    "source_id": report.get("id"),
                    "clinical_note": clinical_note,
                }
            )

    return {
        "encounter": encounter,
        "encounter_reason": _extract_codeable_concept(encounter.get("reasonCode", [])),
        "conditions": _find_resources_for_encounter(
            "Condition",
            encounter_id,
            resources,
        ),
        "procedures": _find_resources_for_encounter(
            "Procedure",
            encounter_id,
            resources,
        ),
        "observations": _find_resources_for_encounter(
            "Observation",
            encounter_id,
            resources,
        ),
        "medications": _find_resources_for_encounter(
            "MedicationRequest",
            encounter_id,
            resources,
        ),
        "diagnostic_reports": diagnostic_reports,
        "notes": notes,
    }


def decode_note(note):
    """Decode the Base64-encoded clinical note from a DiagnosticReport."""

    presented_form = note.get("presentedForm", [])

    if not presented_form:
        return None

    encoded_data = presented_form[0].get("data")

    if not encoded_data:
        return None

    return base64.b64decode(encoded_data).decode("utf-8")


def build_coding_context(data, encounter_id):
    """
    Build the clinical context for the latest/current encounter.

    Includes:
        - patient demographics
        - patient age at encounter
        - current encounter
        - conditions linked to the current encounter
        - active conditions as of the current encounter
        - evidence from encounters explicitly attached to active conditions
        - current clinical notes
    """

    normalized_data = normalize_patient_data(data)

    encounter_data = get_encounter_data(data, encounter_id)

    encounter_date = encounter_data["encounter"]["period"]["start"]

    current_date = datetime.fromisoformat(encounter_date)

    age_at_encounter = calculate_age_at_encounter(
        normalized_data["patient"]["birth_date"],
        encounter_date[:10],
    )

    resources = [
        entry["resource"] for entry in data.get("entry", []) if "resource" in entry
    ]

    active_conditions = get_active_conditions(resources, current_date)

    condition_evidence = []

    for condition in active_conditions:
        evidence = get_condition_evidence(
            condition, resources, normalized_data["encounters"]
        )

        condition_evidence.append(evidence)

    clinical_notes = [
        note["clinical_note"]
        for note in encounter_data["notes"]
        if note.get("clinical_note")
    ]

    return {
        "patient": {
            **normalized_data["patient"],
            "age": age_at_encounter,
        },
        "current_encounter": encounter_data["encounter"],
        "encounter_reason": encounter_data["encounter_reason"],
        "current_issues": encounter_data["conditions"],
        "active_conditions": active_conditions,
        "condition_evidence": condition_evidence,
        "clinical_notes": clinical_notes,
        "procedures": encounter_data["procedures"],
        "observations": encounter_data["observations"],
        "medications": encounter_data["medications"],
        "diagnostic_reports": encounter_data["diagnostic_reports"],
    }


def collect_unique_codes(results: list[dict]) -> list:
    unique_codes = set()

    for result in results:
        for search_result in result["results"]:
            for candidate in search_result["candidates"]:
                unique_codes.add(candidate["code"])

    return list(unique_codes)


def scrape_codes(codes):
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(get_icd10_info, codes))
    return results


def scrape_codes_until_complete(codes, max_retries=3, retry_wait=5):
    remaining_codes = codes
    scraped_results = []

    for attempt in range(max_retries + 1):
        current_results = scrape_codes(remaining_codes)

        failed_codes = [
            code
            for code, result in zip(remaining_codes, current_results)
            if result is None
        ]

        successful_results = [
            result for result in current_results if result is not None
        ]

        scraped_results.extend(successful_results)

        if not failed_codes:
            remaining_codes = []
            break

        remaining_codes = failed_codes

        if attempt < max_retries:
            print(
                f"\n{len(failed_codes)} codes failed."
                f"\nWaiting {retry_wait} seconds before retry..."
                f"\nRetrying: {failed_codes}"
            )

            time.sleep(retry_wait)

    return scraped_results, remaining_codes


def expand_non_billable_codes(
    results: list[dict],
) -> dict[str, dict]:
    """
    Build the canonical unique ICD-10 candidate pool.

    Normal retrieved candidates are added first. If a candidate is
    non-billable, its direct child codes are discovered and each child
    is fetched through get_icd10_info() so that it has the same
    complete ICD-10 information as a normal code.
    """

    unique_codes = {}

    # ---------------------------------------------------------
    # STEP 1: Collect all normally retrieved candidates.
    # ---------------------------------------------------------

    unique_code_list = collect_unique_codes(results)

    unique_codes = {code: {"code": code} for code in unique_code_list}

    # ---------------------------------------------------------
    # STEP 2: Expand non-billable candidates.
    # ---------------------------------------------------------

    original_codes = list(unique_codes.keys())

    for code in original_codes:
        # if len(unique_codes) >= MAX_CODING_CANDIDATES:
        #     break

        icd_info = get_icd10_info(code)

        if not icd_info:
            continue

        # Store complete ICD-10 metadata for every normal candidate.
        unique_codes[code] = icd_info

        # Billable candidates require no hierarchy expansion.
        if icd_info.get("billable") is not False:
            continue

        child_codes = icd_info.get("child_codes", [])

        # -----------------------------------------------------
        # Expand direct child codes.
        # -----------------------------------------------------

        for child in child_codes:
            child_code = child.get("code")

            if not child_code:
                continue

            if child_code in unique_codes:
                continue

            print(f"Expanding {code} -> {child_code}")

            child_info = get_icd10_info(child_code)

            if not child_info:
                continue

            # Store complete ICD-10 metadata for the child code.
            unique_codes[child_code] = child_info

    print(f"UNIQUE CODES: {unique_codes}")

    return unique_codes


def prepare_coding_context(scraped_results):
    """
    Prepare scraped ICD-10-CM information for LLM #2.

    The original scraped results are preserved.
    This function creates a reduced representation containing
    information relevant to final coding reasoning.
    """

    sections_to_keep = {
        "APPROXIMATE SYNONYMS",
        "CLINICAL INFORMATION",
        "APPLICABLE TO",
        "USE ADDITIONAL",
        "TYPE 1 EXCLUDES",
        "TYPE 2 EXCLUDES",
        "CODE FIRST",
        "INCLUDES",
        "CODE ALSO",
    }

    prepared_results = []

    for result in scraped_results:
        prepared_result = {
            "code": result.get("code"),
            "description": result.get("description"),
            "billable": result.get("billable"),
            "sections": {},
        }

        sections = result.get("sections", {})

        for section_name, entries in sections.items():
            if section_name not in sections_to_keep:
                continue

            prepared_result["sections"][section_name] = entries

        prepared_results.append(prepared_result)

    return prepared_results


if __name__ == "__main__":
    req_list = [
        "Z80.43",
        "O99",
        "O36.92",
        "O09.291",
        "O29.01",
        "P92.9",
        "F10.9",
        "Z85.810",
        "O99.21",
        "O36.90",
        "N96",
        "Z62.812",
        "O09.292",
        "Z34.03",
        "O9A.3",
        "E66.9",
        "F10.10",
        "O09.2",
        "O09.02",
        "O32.2",
        "O99.210",
        "F10.95",
        "Z68",
        "O09.00",
        "O32.1",
        "E66.01",
        "O99.310",
        "Z34.00",
        "F10.230",
        "Z34.02",
        "O29.193",
        "F13.120",
        "F13.90",
        "O99.31",
        "O36.91",
        "O99.211",
        "O24.9",
        "E66.2",
        "F10.94",
        "O04.6",
        "O24.3",
        "O09.92",
        "O29",
        "O09.29",
        "O32.4",
        "O09.829",
        "Z83.430",
        "O09.12",
        "O09.01",
        "O09.42",
        "Z34",
        "O09.30",
        "O10.92",
        "O36.93",
        "Z34.01",
        "E66",
        "O09.299",
        "F10.1",
        "O22.02",
        "F13.130",
        "Z62.81",
        "F40.232",
        "F13.230",
        "Z3A. 30",
        "F10.20",
        "O29.191",
        "O00.1",
        "Z68.30",
        "O26.21",
        "O99.84",
        "O10.019",
        "F10.2",
        "O09.A2",
        "O09.03",
        "O26.20",
        "O10.02",
        "O21.8",
        "O00.0",
        "O09.293",
    ]

    # req_list = [
    #     "E11.9",
    #     "O9A.2",
    #     "Z3A.30",
    #     "O09.A2",
    # ]
    results = scrape_codes_until_complete(req_list)
