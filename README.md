# V3 — Longitudinal Evidence-Based ICD-10 Coding Decision System

V3 extends the ICD-10 data acquisition work from V2 into an end-to-end clinical coding pipeline.

The key design principle is to separate:

- **Clinical understanding** — handled by an LLM
- **ICD-10 knowledge retrieval** — handled through deterministic search and structured retrieval
- **Final coding decision** — handled by a second LLM using the extracted clinical evidence and retrieved ICD-10 information

V3 is designed primarily around the **latest patient encounter**, while retaining the patient's longitudinal history so that historical conditions can be evaluated for relevance to the current encounter.

---

# V3 Architecture

## High-Level Architecture

```text
                 Longitudinal Clinical Documents
                              │
                ┌─────────────┴─────────────┐
                │                           │
        Patient History             Current Encounter
                │                           │
                └─────────────┬─────────────┘
                              ▼
                     ┌────────────────┐
                     │     LLM #1     │
                     │                │
                     │ Clinical       │
                     │ Evidence       │
                     │ Extraction &   │
                     │ Reasoning      │
                     └───────┬────────┘
                             │
                             ▼
                  Structured Clinical Evidence
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
        Conditions      Relationships   Search Terms
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                  ICD-10 Search / Retrieval
                             │
                             ▼
                    Candidate ICD-10 Codes
                             │
                             ▼
                  Billable Code Expansion
                             │
                             ▼
                  Billable ICD-10 Candidates
                             │
                             ▼
                     ┌────────────────┐
                     │     LLM #2     │
                     │                │
                     │ Evidence-      │
                     │ Constrained    │
                     │ Coding         │
                     │ Decision       │
                     └───────┬────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
             Final       Additional    Rejected
             Codes          Codes        Codes
```

---

# V3 Processing Pipeline

## 1. Identify the Current Encounter

The pipeline first identifies the latest available encounter in the patient's longitudinal record.

This encounter represents the primary coding target.

Previous encounters remain available as historical context but are not automatically treated as part of the current encounter.

```text
Longitudinal Patient Record
            │
            ▼
     Latest Encounter
            │
            ▼
      Primary Coding
          Target
```

---

## 2. Extract Clinical Evidence

### LLM #1 — Clinical Interpretation

LLM #1 processes the clinical documentation and converts it into structured clinical evidence.

The extracted information includes:

- Conditions documented in the current encounter
- Active conditions in the patient's history
- Encounter relevance
- Clinical terminology
- Search terms for ICD-10 retrieval
- Relationships between conditions
- Evidence supporting identified relationships

LLM #1 is responsible for clinical interpretation, not for selecting the final ICD-10 codes.

---

# Longitudinal Encounter Relevance

A central feature of V3 is the ability to distinguish between conditions that exist in a patient's history and conditions that are relevant to the current encounter.

An active historical condition is **not automatically included** in the current coding decision.

Instead, the current encounter documentation is examined for evidence connecting a historical condition to a condition being addressed in the current encounter.

The system therefore distinguishes between:

- Current encounter conditions
- Active historical conditions
- Historical conditions related to the current encounter
- Historical conditions not relevant to the current encounter

Conceptually:

```text
                    Patient History
                          │
             ┌────────────┴────────────┐
             │                         │
      Historical Condition       Historical Condition
             │                         │
             ▼                         ▼
   Relationship found          No relationship found
   in current encounter        in current encounter
             │                         │
             ▼                         ▼
      Encounter Relevant          Not Relevant
             │
             ▼
      Included in coding
          reasoning
```

For example:

```text
Historical Record
│
└── CKD
       │
       │ relationship documented
       │ in current encounter
       ▼
Current Encounter
│
└── Diabetes
       │
       ▼
CKD becomes relevant to
the current coding decision
```

This prevents the system from automatically carrying the entire patient history into the current coding decision while still allowing relevant historical conditions to contribute when supported by the current documentation.

---

# Clinical Relationship Extraction

V3 explicitly identifies relationships between conditions from the clinical documentation.

The system does not assume that two conditions are related simply because they commonly coexist.

For example:

```text
Condition A
Condition B
```

does not automatically imply:

```text
Condition A is related to Condition B
```

The relationship must be supported by the supplied clinical documentation.

This distinction is particularly important when determining whether a combination or relationship-specific ICD-10 code is justified.

---

# ICD-10 Search and Candidate Retrieval

LLM #1 generates search terms from the extracted clinical evidence.

These terms are then used to search the ICD-10 data source and retrieve candidate conditions and codes.

The retrieval flow is:

```text
Clinical Evidence
       │
       ▼
LLM #1 Search Terms
       │
       ▼
ICD-10 Search
       │
       ▼
Candidate Results
       │
       ▼
ICD-10 Information
```

The retrieval layer provides coding knowledge to the downstream decision process rather than asking the language model to independently invent ICD-10 codes.

---

# Billable Code Expansion

An initial ICD-10 search may identify a condition or category without directly returning the billable code required for coding.

V3 therefore expands the relevant ICD-10 hierarchy to identify available billable candidates.

Conceptually:

```text
Initial Search Result
        │
        ▼
Condition / Category
        │
        ├── Non-billable parent
        │
        └── Billable descendants
                 │
                 ▼
          Billable Candidate Set
```

This expanded candidate set is passed to LLM #2.

---

# LLM #2 — Coding Decision

LLM #2 receives the coding-relevant information produced by the preceding stages, including:

- Current encounter evidence
- Relevant historical conditions
- Encounter relevance
- Documented clinical relationships
- Retrieved ICD-10 candidates
- Billable ICD-10 candidates
- ICD-10 coding information and rules

LLM #2 evaluates the candidates against the available clinical evidence and determines which codes are supported.

```text
Clinical Evidence
       +
Encounter Relevance
       +
Clinical Relationships
       +
ICD-10 Candidates
       +
Coding Information
       │
       ▼
     LLM #2
       │
       ▼
Coding Decision
```

The decision is constrained by the available evidence and retrieved coding candidates.

---

# Combination Codes

V3 is designed to distinguish between conditions that merely coexist and conditions for which the clinical documentation establishes a coding-relevant relationship.

For example:

```text
CKD + Diabetes
```

If the documentation establishes the appropriate relationship, a combination or relationship-specific coding option may be selected.

If the conditions coexist without the required documented relationship, separate codes may be selected where appropriate.

The presence of two diagnoses alone is not treated as sufficient evidence of a relationship.

---

# Additional Codes

Some coding scenarios require additional codes to fully represent the documented clinical state.

V3 preserves additional coding requirements separately from the main/final coding decision.

The structured output can therefore distinguish between:

- Final codes
- Additional codes
- Other retrieved candidates

---

# Rejected Codes and Evidence

V3 retains retrieved candidates that are not ultimately selected.

Rejected candidates can include:

- The rejected ICD-10 code
- The reason for rejection
- Supporting evidence

Conceptually:

```text
Retrieved Candidates
        │
        ├── Final / Accepted
        │
        ├── Additional
        │
        └── Rejected
              │
              ├── Rejection reason
              └── Supporting evidence
```

This allows the system to provide visibility into both the final coding decision and the alternatives that were considered.

Instead of only asking:

> What code was selected?

the structured output can also answer:

> What candidates were considered, and why were they rejected?

---

# Design Principles

## 1. Documentation Is the Source of Clinical Relationships

The system does not assume a clinical relationship merely because conditions commonly occur together.

A relationship must be supported by the supplied clinical documentation.

```text
Condition A
Condition B

      ≠

Condition A is related to Condition B
```

---

## 2. Encounter Relevance Is Separate From Patient History

An active condition in the patient's longitudinal record is not automatically relevant to the current encounter.

V3 explicitly evaluates historical conditions against the documentation of the current encounter.

A historical condition can become relevant when the current encounter establishes a clinically meaningful relationship to it.

---

## 3. Clinical Evidence and Coding Knowledge Are Separate

Clinical documentation provides evidence about the patient's clinical state.

The ICD-10 knowledge layer provides available coding options and coding information.

```text
Clinical Documentation
        │
        └──► Clinical facts
             Relationships
             Encounter evidence


ICD-10 Knowledge
        │
        └──► Coding options
             Coding information
```

The coding decision evaluates the intersection of these two sources.

---

## 4. Documentation-Constrained Specificity

The system aims to select the most specific code supported by the documentation rather than simply selecting the most specific code available.

Unsupported distinctions should not be introduced without supporting evidence.

Examples include:

- Complications
- Disease relationships
- Stages
- Severity
- Laterality
- Subtypes

---

## 5. Separation of Responsibilities

The architecture intentionally separates:

```text
Clinical Interpretation
        │
        ▼
Structured Clinical Evidence
        │
        ▼
ICD-10 Knowledge Retrieval
        │
        ▼
Evidence-Constrained Coding Decision
```

This makes the individual stages easier to inspect, test, and modify independently.

---

# Structured JSON Output

V3 produces structured JSON rather than only returning a final list of ICD-10 codes.

The output preserves information generated throughout the pipeline, including:

- Current encounter
- Current encounter conditions
- Historical conditions
- Encounter relevance
- Historical conditions related to the current encounter
- Clinical relationships
- Search terms
- Retrieved ICD-10 candidates
- Billable candidates
- Final codes
- Additional codes
- Rejected codes
- Rejection reasoning
- Supporting evidence

The structured output also provides a foundation for downstream visualization and inspection of the patient's longitudinal coding context.

---

# Validation

V3 includes a regression suite covering **30 clinical and coding scenarios**.

The regression suite evaluates the behavior of the complete pipeline rather than only checking whether individual components produce plausible outputs.

The scenarios include:

- Current vs. historical conditions
- Historical conditions related to the current encounter
- Encounter relevance
- Longitudinal patient history
- Multiple concurrent conditions
- Explicit clinical relationships
- Conditions that coexist without a documented relationship
- Combination-code scenarios
- ICD-10 specificity
- Required additional codes
- Billable-code retrieval
- Rejection of unsupported candidate codes
- Evidence supporting coding decisions

The regression suite is used to detect behavioral regressions as the architecture, prompts, retrieval logic, and decision process evolve.

---

# V3 Output Flow

The complete process can be summarized as:

```text
Longitudinal Patient Record
            │
            ▼
     Latest Encounter
            │
            ▼
       LLM #1
            │
            ├── Current conditions
            ├── Historical conditions
            ├── Encounter relevance
            ├── Clinical relationships
            └── ICD-10 search terms
                    │
                    ▼
          ICD-10 Retrieval
                    │
                    ▼
        Candidate Conditions
                    │
                    ▼
        Billable Code Expansion
                    │
                    ▼
              LLM #2
                    │
                    ├── Final codes
                    ├── Additional codes
                    └── Rejected codes
                              │
                              ▼
                    Structured JSON Output
```

---

# Why V3?

A direct approach to medical coding can be represented as:

```text
Clinical Note
     │
     ▼
ICD-10 Code
```

V3 instead decomposes the problem:

```text
Longitudinal Clinical Record
            │
            ▼
     Current Encounter
            │
            ▼
   Clinical Evidence
            │
            ▼
Encounter / Relationship
       Reasoning
            │
            ▼
 ICD-10 Candidate Retrieval
            │
            ▼
   Billable Code Expansion
            │
            ▼
 Evidence-Constrained
     Coding Decision
            │
            ▼
 Structured Coding Output
```

This decomposition makes it possible to separately inspect:

- What the documentation establishes
- Which conditions are relevant to the current encounter
- Which historical conditions are connected to the current encounter
- Which clinical relationships are documented
- Which ICD-10 candidates were retrieved
- Which candidates were selected
- Which candidates were rejected
- Why candidates were rejected

The architecture is intended to provide a more **auditable, testable, inspectable, and evidence-constrained** approach than a direct text-to-code prediction pipeline.

---

# Synthetic Clinical Data

V3 uses synthetic longitudinal clinical documentation for development and testing.

The records can contain multiple encounters across a patient's history, including information such as:

- Clinical notes
- Conditions across encounters
- Tests and observations
- Medications
- Longitudinal clinical events
- Relationships between conditions and encounters

This richer structure allows the pipeline to test scenarios where information from previous encounters may become relevant to the current coding decision.

Synthetic data is used for engineering and research experimentation and should not be treated as real-world clinical ground truth.

---

# Project Status

**Current milestone: V3**

- [x] Longitudinal synthetic clinical records
- [x] Current encounter identification
- [x] Historical condition tracking
- [x] Historical-to-current encounter relevance
- [x] Clinical relationship extraction
- [x] ICD-10 search-term generation
- [x] ICD-10 candidate retrieval
- [x] Billable-code expansion
- [x] Evidence-constrained coding decision
- [x] Additional-code handling
- [x] Rejected-code reasoning
- [x] 30-case regression suite completed

V3 is the current completed coding-pipeline milestone. The structured JSON output provides the foundation for subsequent visualization and human inspection of longitudinal coding decisions.

---

# Scope and Disclaimer

This project is a research and engineering framework for exploring AI-assisted medical coding.

It is **not** intended to:

- Replace professional medical coders
- Replace certified coding workflows
- Replace clinical judgment
- Replace official coding guidelines
- Serve as a production medical coding system
- Provide clinical diagnosis

The use of synthetic clinical documentation also means that regression results should not be interpreted as clinical validation on real-world patient records.

The project is intended to demonstrate system architecture, retrieval design, reasoning workflows, structured outputs, validation practices, and software engineering approaches for AI-assisted clinical coding.
