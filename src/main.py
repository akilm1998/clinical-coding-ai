import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from functions import (
    # analyze_scraped_results,
    # analyze_section_sizes,
    build_coding_context,
    collect_unique_codes,
    get_data,
    # get_resource_summary,
    prepare_coding_context,
    scrape_codes_until_complete,
)
from prompt import (
    generate_clinical_conditions,
    generate_coding_decision,
)
from text_to_icd10 import text_to_icd10

# patient_data_file = (
#     r"C:\Users\akile\OneDrive\Desktop\medical-coding-project"
#     r"\synthetic-clinical-note-generator\src\patients"
#     r"\Earle679_Rohan584_b17949c8-25eb-0f29-f85a-11dcbf64eacd.json"
# ) # Dental

# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\src\patients\Dusty207_Camie739_Borer986_cfbfafa9-f136-b5b1-0d08-1f6c2bd08eef.json"  # Pregnancy

# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\src\patients\Hiram237_Kutch271_dd4175fd-83d4-bc95-8ff9-4943947151d5.json" # diseased
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\src\patients\Pasquale620_Ernser583_466a7f1d-d7ad-fae4-ccfd-2519b8e66c80.json" # Well doing child
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\src\patients\Hiram237_Kutch271_dd4175fd-83d4-bc95-8ff9-4943947151d5.json" # diseased
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\src\patients\Monte325_Reinger292_41d5e462-f845-c9a8-4139-5ea92c78f22d.json" #diseased
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\src\patients\Beatriz277_Manuela585_White193_278910fe-4369-d94b-a0ba-9e5751131402.json" # Medicall Review
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\src\patients\Yuki258_Alex454_Kuhic920_9a1eb151-1e0f-2833-e400-f7c1990341b9.json"
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\src\patients\Dylan44_O'Keefe54_b5c8cec1-8415-25cf-b544-c19e84761e14.json" # CKD + diabetes

# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\src\patients\Dylan44_O'Keefe54_b5c8cec1-8415-25cf-b544-c19e84761e14 copy.json"
patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\src\patients\Patient_final.json"  # CKD + diabetes
if __name__ == "__main__":
    # -----------------------------------
    # Load environment variables
    # -----------------------------------

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)

    data = get_data(patient_data_file)

    # resource_summary = get_resource_summary(data)

    encounters = [
        entry["resource"]
        for entry in data.get("entry", [])
        if entry.get("resource", {}).get("resourceType") == "Encounter"
    ]

    latest_encounter = max(
        encounters, key=lambda encounter: encounter["period"]["start"]
    )
    # print(f"Latest Encounter: {latest_encounter['period']['start']}")
    # exit(0)
    latest_encounter_id = latest_encounter["id"]

    coding_context = build_coding_context(data, latest_encounter_id)
    if not coding_context["patient"]["alive"]:
        raise SystemExit("Patient is deceased. Skipping coding pipeline.")

    # print(f"{coding_context}\n\n\n")
    # exit(0)
    with open("coding_context.json", "w") as outfile:
        json.dump(coding_context, outfile, indent=4)
        # exit(0)

    clinical_conditions = generate_clinical_conditions(
        coding_context, client
    )  # LLM #1 JSON output from clinical condition extraction
    with open("LLM1.txt", "w") as outfile:
        outfile.write(clinical_conditions)
    # print(clinical_conditions)

    # Convert string to dictionary (LLM #1 JSON) for processing in text_to_icd10.py

    try:
        clinical_extraction = json.loads(clinical_conditions)

    except json.JSONDecodeError as error:
        raise SystemExit(f"Invalid JSON: {error}")

    # Retrieve ICD-10 candidates from LLM #1 JSON

    icd10_candidates = text_to_icd10(clinical_extraction)
    # print(type(icd10_candidates))
    unique_candidate_codes = collect_unique_codes(icd10_candidates["results"])
    with open("unique_candidate_codes.txt", "w") as outfile:
        outfile.write(f"{unique_candidate_codes}\n")
    # print(f"Unique ICD-10 candidates: {unique_candidate_codes}")

    # Scrape ICD-10 codes from icd10data website

    scraped_results, failed_codes = scrape_codes_until_complete(unique_candidate_codes)

    if failed_codes:
        print("\nCodes that could not be scraped:")
        for code in failed_codes:
            print(code)
        # print(f"Scraped ICD-10 codes: \n\n{scraped_results}")
    with open("scraped_icd10_codes.json", "w") as outfile:
        json.dump(scraped_results, outfile, indent=4)

    prepared_icd_context = prepare_coding_context(
        scraped_results
    )  # Cleanup Structured Data for Coding Decision Context

    coding_decision_context = {
        "clinical_context": coding_context,
        "clinical_extraction": clinical_extraction,
        "icd10_context": prepared_icd_context,
    }

    # Save coding decision context and intermediate results to JSON files for individual review and debugging
    with open("clinical_context.json", "w") as outfile:
        json.dump(coding_decision_context, outfile, indent=4)

    with open("clinical_extraction.json", "w") as outfile:
        json.dump(clinical_extraction, outfile, indent=4)

    with open("prepared_icd_context.json", "w") as outfile:
        json.dump(prepared_icd_context, outfile, indent=4)
    # analysis = analyze_scraped_results(prepared_icd_context)

    # print()
    # print("=" * 60)
    # print("SCRAPED RESULTS ANALYSIS")
    # print("=" * 60)

    # for key, value in analysis.items():
    #     print(f"{key}: {value}")

    # section_sizes = analyze_section_sizes(prepared_icd_context)

    # print()
    # print("=" * 60)
    # print("SECTION SIZE ANALYSIS")
    # print("=" * 60)

    # sorted_sections = sorted(
    #     section_sizes.items(),
    #     key=lambda item: item[1]["characters"],
    #     reverse=True,
    # )

    # for section_name, stats in sorted_sections:
    #     print(
    #         f"{section_name}: "
    #         f"{stats['characters']} characters | "
    #         f"{stats['entries']} entries | "
    #         f"{stats['codes']} codes"
    #     )

    coding_decision = generate_coding_decision(
        coding_decision_context,
        client,
    )

    print("\n")
    print("=" * 60)
    print("FINAL CODING DECISION")
    print("=" * 60)
    print(coding_decision)

    with open("LLM2_decision.txt", "w") as outfile:
        outfile.write(coding_decision)
