# Synthetic Clinical Note Generator

A framework for generating high-quality synthetic clinical notes for machine learning research in medical coding.

## Project Goal

Build a reproducible pipeline that generates realistic synthetic clinical notes from structured diagnosis and patient information, with the goal of supporting ICD-10 code prediction from clinical text.

---

## V1 Architecture

```text
              Structured Input
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
   Diagnosis Profile    Patient Profile
          │                   │
          └─────────┬─────────┘
                    ▼
             Synthetic Patient
                    │
                    ▼
            LLM Clinical Note
                Generation
                    │
                    ▼
             Synthetic Clinical
                  Notes
                    │
                    ▼
              Dataset Creation
                    │
                    ▼
             ICD-10 + Clinical Note
                    │
                    ▼
             Baseline ML Model
                    │
                    ▼
                 Evaluation
```

---

## V1 Status

V1 established the initial end-to-end synthetic clinical note generation and machine learning pipeline.

- [x] Repository initialized
- [x] Initial architecture designed
- [x] Diagnosis profile schema implemented
- [x] First diagnosis profile created
- [x] Synthetic patient generation implemented
- [x] Prompt-based clinical note generation implemented
- [x] Initial prompt refinement completed
- [x] Support for additional diagnoses
- [x] Larger synthetic dataset generated
- [x] Automated dataset export implemented
- [x] Synthetic clinical notes exported to Apache Parquet format
- [x] Dataset structure validated
- [x] Clinical notes and ICD-10 codes prepared for machine learning
- [x] Initial baseline machine learning model trained
- [x] Initial model performance evaluated
- [x] Reference clinical notes created and committed

---

## V1 Findings

The initial baseline model achieved very high accuracy.

Further inspection showed that the generated clinical notes frequently contained the diagnosis or condition name associated with the target ICD-10 code.

As a result, the model could learn a direct association between explicitly stated condition names and their corresponding ICD-10 codes, rather than needing to infer the condition from clinical findings, symptoms, laboratory values, medications, and other contextual information.

This highlighted an important limitation in the initial dataset design: high predictive performance did not necessarily demonstrate meaningful clinical reasoning.

The V1 approach also did not adequately distinguish the clinical context, etiology, or subcondition that may determine a more specific ICD-10 code.

For example, identifying a disease from its name is insufficient when the appropriate ICD-10 code depends on additional documented information such as:

- Clinical relationships
- Disease stage
- Etiology
- Complications
- Specific manifestations
- Other coding-relevant context

The supervised ML approach also depends on the conditions and ICD-10 codes represented in its training data.

Introducing previously unseen conditions would require additional representative training data and model retraining, limiting the ability of the approach to generalize to new coding scenarios without expanding the training dataset.

These findings motivated the subsequent evolution of the project toward richer synthetic longitudinal clinical data, external ICD-10 knowledge retrieval, and evidence-based coding decisions.

The V1 dataset, baseline model, and reference clinical notes are retained as the initial proof of concept and as reference material for subsequent iterations.

---

## V1 Conclusion

V1 successfully demonstrated the complete pipeline from structured patient and diagnosis information to synthetic clinical notes, dataset creation, and an initial ICD-10 prediction model.

The primary limitations identified in V1 were:

1. **Direct diagnosis signals in the generated documentation**

   The presence of explicit condition names allowed the baseline model to learn shortcuts between diagnosis terminology and ICD-10 codes, making high accuracy an incomplete measure of clinical reasoning.

2. **Limited clinical context for code selection**

   The approach did not adequately distinguish the clinical context, etiology, relationships, complications, stages, or subconditions that can determine a more specific ICD-10 code.

3. **Dependence on supervised training coverage**

   The model depended on training examples for the conditions and ICD-10 codes it was expected to predict. Supporting previously unseen conditions would require additional training data and model retraining.

These limitations led to the next stage of the project, where the focus shifted from direct diagnosis-to-code prediction toward a more structured and evidence-based coding architecture.
