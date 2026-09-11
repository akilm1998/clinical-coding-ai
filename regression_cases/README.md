# Regression cases for clinical relationship extraction

This directory contains deterministic Synthea custom-module fixtures intended for downstream clinical-documentation and coding evaluation.

The cases intentionally keep all relationship evidence in valid Synthea-native FHIR outputs, without embedding ICD-10 answers into the generated bundles. The downstream coding pipeline is expected to read the generated conditions, encounters, and documentation and decide the coding logic itself.

## Included cases

- case_01_diabetes_ckd_no_relationship
- case_02_diabetes_ckd_explicit_relationship
- case_03_diabetes_hypertension_no_relationship
- case_04_diabetes_hypertension_explicit_relationship
- case_05_diabetes_ckd_exam_sequencing
- case_06_ckd_stage_specificity
- case_07_multiple_conditions_one_relationship
- case_08_historical_vs_current_condition
- case_09_encounter_sequencing
- case_10_negative_relationship

## Relationship principle

The positive relationship cases rely on explicit clinical documentation in the generated encounter data; they do not create a combined Condition resource for relationship-bearing diagnoses. Negative cases avoid explicit causal or associative language and rely on separate conditions and neutral note text.

## Generation pattern

The cases use the Generic Module Framework with:

- `Initial`
- `Delay`
- `ConditionOnset`
- `Encounter`
- `EncounterEnd`
- `Procedure` for clinical note/documentation evidence when needed
- `target_encounter` to tie conditions to the intended encounter
- `reason` to provide encounter context

The modules remain minimal and deterministic; they do not modify Synthea core Java or existing built-in disease modules.

The explicit diabetes/CKD fixture uses the native `Procedure` state's optional `note` field so
Synthea's FHIR note exporter emits the relationship evidence in the target encounter's
`DiagnosticReport` and `DocumentReference`. Generate it on Windows with:

```
gradlew.bat run -Params="['-p','1','-s','1002','-ps','1002','-cs','2002','-r','20100101','-e','20030731','-d','custom_modules/coding_tests','-m','*case_02*','--exporter.baseDirectory=output/coding_regression/case_02_diabetes_ckd_explicit_relationship/']"
```
