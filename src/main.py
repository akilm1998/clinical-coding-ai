import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from functions import (
    build_coding_context,
    collect_unique_codes,
    expand_non_billable_codes,
    get_data,
    prepare_coding_context,
)
from prompt import (
    generate_clinical_conditions,
    generate_coding_decision,
)
from text_to_icd10 import text_to_icd10

# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_01_diabetes_single\generated\fhir\Ardelle563_Kuhic920_00000000-0000-0bb9-30a5-15eed41a1cd8.json"  # 1
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_02_diabetes_ckd_explicit\generated\fhir\Cleo27_Thompson596_00000000-0000-0bba-2bdb-cd1920eec583.json"  # 2
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_03_diabetes_ckd_coexistence\generated\fhir\Joel444_Kuhlman484_00000000-0000-0bbb-d81e-e56007528d4a.json"  # 3
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_04_diabetes_hypertension_explicit\generated\fhir\Ola364_Swaniawski813_00000000-0000-0bbc-356e-5ec38745742e.json"  # 4
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_05_diabetes_hypertension_coexistence\generated\fhir\Ian270_Gerlach374_00000000-0000-0bbd-e1b1-770c6da93bf5.json"  # 5
# patient_data_file = r"regression_cases/case_06_hypertension_single/generated/fhir/Yolonda722_Swift555_00000000-0000-0bbe-dce8-2e35ba7de49f.json"  # 6
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_07_ckd_stage_three\generated\fhir\Luis923_Pedroza523_00000000-0000-0bbf-892b-467ca0e1ac66.json"  # 7
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_08_hypertension_ckd_relationship\generated\fhir\Penelope500_Hoppe518_00000000-0000-0bc0-6edd-c8c8ed4d8c30.json"  # 8
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_09_diabetes_obesity\generated\fhir\Salvatore257_Zemlak964_00000000-0000-0bc1-1b20-e10fd3b153f8.json"  # 9
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_10_diabetes_hyperlipidemia\generated\fhir\Benton624_Howe413_00000000-0000-0bc2-1657-983a2085fca2.json"  # 10
# patient_data_file = r"regression_cases/case_11_diabetes_ckd_hypertension/generated/fhir/Sasha806_Ziemann98_00000000-0000-0bc3-c29a-b08106e9c469.json"  # 11
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_12_copd_single\generated\fhir\Filiberto722_Hodkiewicz467_00000000-0000-0bc4-1fea-29e486dcab4d.json"  # 12
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_13_copd_hypertension\generated\fhir\Laura391_Alcala54_00000000-0000-0bc5-cc2d-422d6d407314.json"  # 13
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_14_asthma_single\generated\fhir\Kia427_Hoeger474_00000000-0000-0bc6-c763-f956ba151bbf.json"  # 14
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_15_asthma_rhinitis\generated\fhir\Lester513_Zboncak558_00000000-0000-0bc7-73a7-119da078e386.json"  # 15
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_16_heart_failure_single\generated\fhir\Maddie576_Hilpert278_00000000-0000-0bc8-d0f6-8b02206bca6a.json"  # 16
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_17_heart_failure_hypertension\generated\fhir\Sheldon401_Ruecker817_00000000-0000-0bc9-7d39-a34a06cf9231.json" # 17
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_18_obesity_hypertension_diabetes\generated\fhir\Freeman822_Hirthe744_00000000-0000-0bca-7870-5a7453a43adb.json"  # 18
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_19_hypothyroidism_single\generated\fhir\Rosalie939_Runolfsdottir785_00000000-0000-0bcb-24b3-72bb3a0802a3.json"  # 19
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_20_gerd_single\generated\fhir\Malcom15_Hilll811_00000000-0000-0bcc-8202-ec1eb9fae987.json"  # 20
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_21_osteoarthritis_single\generated\fhir\Taryn906_Roob72_00000000-0000-0bcd-2e46-0465a05eb14e.json"  # 21
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_22_depression_single\generated\fhir\Grazyna952_Hills818_00000000-0000-0bce-297c-bb90ed3359f8.json"  # 22
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_23_acute_bronchitis\generated\fhir\Steven797_Rosenbaum794_00000000-0000-0bcf-d5bf-d3d7d39721bf.json"  # 23
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_24_viral_respiratory_illness\generated\fhir\Jonas187_Muller251_00000000-0000-0bd0-aaac-445487110fbd.json"  # 24
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_25_dental_caries\generated\fhir\Duane703_Ankunding277_00000000-0000-0bd1-56ef-5c9c6d74d785.json"  # 25
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_26_acute_with_diabetes_history\generated\fhir\Ralph813_Murazik203_00000000-0000-0bd2-5226-13c5ba49802f.json"  # 26
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_27_historical_diabetes_current_uri\generated\fhir\Calandra120_Feil794_00000000-0000-0bd3-fe69-2c0da0ad47f6.json"  # 27
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_28_historical_multiple_current_htn\generated\fhir\Jeanelle736_Mosciski958_00000000-0000-0bd4-5bb8-a57220a02eda.json"  # 28
# patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_29_diabetes_ckd_anemia\generated\fhir\Della552_Altenwerth646_00000000-0000-0bd5-07fb-bdb90703f6a1.json"  # 29
patient_data_file = r"C:\Users\akile\OneDrive\Desktop\medical-coding-project\synthetic-clinical-note-generator\regression_cases\case_30_multiple_relationships\generated\fhir\Mellissa304_Mueller846_00000000-0000-0bd6-0332-74e353d89f4c.json"  # 30


if __name__ == "__main__":
    # -----------------------------------
    # Load environment variables
    # -----------------------------------

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")

    client = OpenAI(api_key=api_key)

    data = get_data(patient_data_file)

    encounters = [
        entry["resource"]
        for entry in data.get("entry", [])
        if entry.get("resource", {}).get("resourceType") == "Encounter"
    ]

    latest_encounter = max(
        encounters, key=lambda encounter: encounter["period"]["start"]
    )
    print("Latest Encounter:")
    print(f"  Date: {latest_encounter['period']['start']}")
    print(f"  Status: {latest_encounter.get('status')}")
    print(f"  Class: {latest_encounter.get('class', {}).get('code')}")

    print("  Type:")
    for t in latest_encounter.get("type", []):
        for coding in t.get("coding", []):
            print(f"    {coding.get('display')} ({coding.get('code')})")

    print("  Reason:")
    for reason in latest_encounter.get("reasonCode", []):
        for coding in reason.get("coding", []):
            print(f"    {coding.get('display')} ({coding.get('code')})")

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

    # Keep the unique retrieved-code artifact for debugging/review.
    unique_candidate_codes = collect_unique_codes(icd10_candidates["results"])
    with open("unique_candidate_codes.txt", "w") as outfile:
        outfile.write(f"{unique_candidate_codes}\n")
    # print(f"Unique ICD-10 candidates: {unique_candidate_codes}")

    # Build the final ICD-10 candidate pool.
    #
    # This includes:
    #   - normally retrieved candidates
    #   - full ICD-10 information for those candidates
    #   - hierarchy expansion for non-billable candidates
    #   - child-code ICD-10 information
    coding_candidates = expand_non_billable_codes(icd10_candidates["results"])

    with open("coding_candidates.json", "w") as outfile:
        json.dump(coding_candidates, outfile, indent=4)

    with open("unique_coding_candidate_codes.txt", "w") as outfile:
        outfile.write(f"{list(coding_candidates.keys())}\n")

    # Preserve the existing scraped ICD-10 artifact name for
    # downstream inspection/debugging. The data now represents
    # the complete candidate pool, including hierarchy expansion.
    scraped_results = list(coding_candidates.values())

    with open("scraped_icd10_codes.json", "w") as outfile:
        json.dump(scraped_results, outfile, indent=4)

    prepared_icd_context = prepare_coding_context(
        scraped_results
    )  # Cleanup Structured Data for Coding Decision Context

    # print("\n=== I12.9 FROM CODING CANDIDATES ===")
    # print(coding_candidates.get("I12.9"))
    # exit(0)

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
