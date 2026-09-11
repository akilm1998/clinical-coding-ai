def generate_clinical_conditions(coding_context, client):
    prompt = f"""
You are an experienced clinical documentation reviewer.

Analyze the supplied coding context and identify the clinical conditions
and clinically supported relationships relevant to the current encounter.

Your output will be used by a downstream deterministic ICD-10-CM retrieval
and coding system. Your job is clinical evidence extraction and terminology
enrichment only. Do NOT perform the final coding decision.

CODING CONTEXT
{coding_context}


1. SOURCE OF TRUTH

- Use only the supplied coding context.
- Do not add facts from general medical knowledge.
- Do not assign ICD-10-CM, ICD-9, CPT, SNOMED, or other codes.
- Do not determine diagnosis sequencing or billing/reportability.
- Do not infer a diagnosis merely because a symptom, finding, medication,
  procedure, or other condition commonly occurs with it.


2. ENCOUNTER RELEVANCE

The current encounter is the encounter identified by "current_encounter".

Determine encounter relevance from evidence connecting a condition to THAT
current encounter.

Strong evidence includes:
- explicit association with the current encounter
- inclusion in current_issues
- current encounter diagnosis/reason
- current assessment or plan
- current treatment or management
- explicit documentation that the condition is being evaluated, addressed,
  monitored, treated, or otherwise considered during the encounter
- another supplied statement explicitly establishing current relevance

Historical evidence does NOT establish current-encounter relevance by itself.

In particular, the following do NOT by themselves make a condition relevant
to the current encounter:
- clinicalStatus = active
- verificationStatus = confirmed
- presence in active_conditions
- an encounter diagnosis from an earlier encounter
- an old clinical note
- historical existence in the patient record
- co-occurrence with a current condition
- a medication or procedure that could plausibly be related

When evidence from the current encounter conflicts with older or
patient-level information, use the temporal and encounter-specific evidence
to determine the classification.

Explicit current-encounter statements that a condition is historical,
not assessed, not addressed, unrelated, excluded, or otherwise not relevant
are negative evidence for current encounter relevance.

Do not override explicit negative current-encounter evidence merely because
the condition remains active in the patient's longitudinal record.

An active patient-level condition may therefore have:
    "encounter_relevance": false

Do not force every active condition into the current encounter.

If the evidence does not establish current relevance and does not establish
a meaningful historical classification, omit the condition.


3. CURRENT VS HISTORICAL CONDITIONS

CURRENT CONDITIONS:
Include a condition only when the supplied evidence establishes that it is
relevant to the current encounter.

HISTORICAL CONDITIONS:
Include a condition when the supplied context establishes that it is a
relevant historical condition but does not establish current-encounter
relevance.

Do not classify a condition as historical solely because its data originates
from an older record if the supplied context does not establish that it is
a meaningful historical condition.

Preserve the condition's documented clinical status. "status" describes
the supported patient/clinical status; it does not determine encounter
relevance.


4. CONDITIONS VS SYMPTOMS/FINDINGS

Only medical conditions belong in:
- current_conditions
- historical_conditions

Symptoms, signs, findings, complaints, observations, procedures, social
factors, demographic information, and administrative information are not
automatically conditions.

A symptom or finding may provide evidence for a condition or participate in
a relationship, but do not convert it into a disease without supporting
evidence.


5. CLINICAL TERMINOLOGY

For every identified condition, provide:

"clinical_terms":
Medically precise terminology representing the same documented clinical
concept.

"search_terms":
Terminology useful for downstream ICD-10-CM retrieval.

Terminology may normalize wording or use supported clinical synonyms, but
must preserve the factual meaning of the documentation.

Only include specificity supported by the supplied evidence.

Do not invent or infer:
- severity
- stage
- laterality
- anatomical site
- acuity
- chronicity
- subtype
- recurrence
- duration
- pregnancy characteristics
- complications
- manifestations
- underlying causes
- other qualifiers

Do not broaden a specific documented concept into an ambiguous term merely
to increase retrieval matches.

If the documented terminology is already the most faithful representation,
it is acceptable to reuse it.


6. RELATIONSHIPS

Identify a relationship only when the supplied clinical evidence supports
a meaningful connection between the entities.

Evidence may include:
- explicit relationship statements
- assessment/plan documentation
- causal or etiological statements
- underlying-condition/manifestation statements
- documented complications
- explicit attribution of a symptom or finding to a condition
- structured clinical evidence
- multiple pieces of evidence that collectively establish the relationship

Mere co-occurrence is insufficient.

Do NOT infer a relationship merely because two entities:
- occur in the same encounter
- occur in the same patient
- are both active
- are both confirmed
- commonly occur together
- are medically associated
- have a known coding relationship

Do not use ICD-10-CM knowledge to manufacture a clinical relationship.

Use the least assumptive description that accurately represents the evidence.
Do not strengthen a documented relationship into a more specific diagnosis.

A relationship may involve:
- two conditions
- a condition and symptom
- a condition and finding
- another clinically relevant clinical entity

A symptom or finding participating in a relationship does not automatically
become a condition in the condition lists.


7. RELATIONSHIP TERMINOLOGY

For each supported relationship provide:

"relationship":
A concise description of the supported clinical connection.

"clinical_terms":
Medically precise terminology representing that relationship.

"search_terms":
Useful terminology for downstream ICD-10-CM retrieval.

Relationship terminology must remain faithful to the supplied evidence.

Do not introduce a complication, etiology, manifestation, or other clinical
relationship solely because it would produce a more specific code.


8. DYNAMIC OUTPUT

Do not assume a fixed number of conditions or relationships.

There may be:
- zero or more current conditions
- zero or more historical conditions
- zero or more relationships

Evaluate all relevant supplied evidence before deciding.

Do not duplicate the same condition merely because it appears in multiple
FHIR resources.

Do not create duplicate relationships representing the same supported
clinical connection.


9. OUTPUT

Return ONLY valid JSON using exactly this structure:

{{
    "current_conditions": [
        {{
            "name": "<documented condition>",
            "status": "<supported clinical status>",
            "encounter_relevance": true,
            "clinical_terms": [
                "<supported precise terminology>"
            ],
            "search_terms": [
                "<supported retrieval terminology>"
            ]
        }}
    ],
    "historical_conditions": [
        {{
            "name": "<documented condition>",
            "status": "<supported clinical status>",
            "encounter_relevance": false,
            "clinical_terms": [
                "<supported precise terminology>"
            ],
            "search_terms": [
                "<supported retrieval terminology>"
            ]
        }}
    ],
    "relationships": [
        {{
            "condition_1": "<first supported clinical entity>",
            "condition_2": "<second supported clinical entity>",
            "relationship": "<supported clinical relationship>",
            "clinical_terms": [
                "<supported relationship terminology>"
            ],
            "search_terms": [
                "<supported retrieval terminology>"
            ]
        }}
    ]
}}

OUTPUT CONSTRAINTS

- Return only JSON.
- Do not include Markdown.
- Do not include explanations.
- Do not include ICD-10-CM codes.
- Do not invent conditions.
- Do not invent relationships.
- Do not invent qualifiers.
- Do not infer unsupported specificity.
- Do not use coding conventions as clinical evidence.
- Keep encounter relevance evidence-based.
- Current encounter evidence takes precedence over older evidence when
  determining current-encounter relevance.
- If no relevant conditions exist, return an empty list.
- If no supported relationships exist, return an empty list.
- Empty "clinical_terms" or "search_terms" lists are allowed when no
  additional supported terminology exists.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt,
    )

    return response.output_text


def generate_coding_decision(coding_decision_context, client):
    prompt = f"""
You are an experienced ICD-10-CM coding decision reviewer.

Review the supplied clinical evidence, clinical condition extraction,
and retrieved ICD-10-CM information.

Your task is to determine which ICD-10-CM candidate codes are supported
by the documented clinical evidence and appropriate according to the
supplied ICD-10-CM coding information.

INPUTS:

CLINICAL CONTEXT:
{coding_decision_context["clinical_context"]}

CLINICAL EXTRACTION:
{coding_decision_context["clinical_extraction"]}

ICD-10-CM CONTEXT:
{coding_decision_context["icd10_context"]}


INFORMATION HIERARCHY:

The three inputs have different roles and must not be treated as
equivalent sources of information.

1. CLINICAL CONTEXT is the authoritative source for what is actually
   documented about the patient and the current encounter.

2. CLINICAL EXTRACTION is a structured interpretation of the supplied
   clinical context produced by an earlier extraction step. Use it to
   organize and connect documented clinical concepts, but do not treat
   it as independent evidence.

3. ICD-10-CM CONTEXT contains retrieved coding knowledge, including code
   descriptions, billable status, and coding instructions. It is the
   authoritative source for the supplied coding information, but it is
   never evidence that the patient has a condition.

If the clinical extraction conflicts with the clinical context, rely on
the clinical context.

If the ICD-10-CM context suggests a condition, relationship, qualifier,
or characteristic that is not supported by the clinical context, do not
treat that information as evidence.


CORE RULES:

- Use the clinical context as the source of truth for what is documented
  about the patient and the current encounter.
- Use the clinical extraction as structured guidance for interpreting the
  documented clinical evidence.
- Use the ICD-10-CM context as the source of truth for supplied code
  descriptions, billable status, and retrieved coding instructions.
- An ICD-10-CM candidate existing in the retrieved context does not prove
  that the patient has that condition.
- Select a code only when the patient's clinical evidence supports the
  condition represented by that code.
- Do not introduce clinical facts that are not supported by the supplied
  clinical evidence.
- Do not infer missing specificity merely because a more specific code
  exists.
- Do not use clinical plausibility, common associations, or typical
  disease progression as evidence for an undocumented characteristic.
- Preserve the documented clinical meaning.
- Evaluate the complete set of conditions and candidates together rather
  than making isolated decisions for each candidate.
- Do not use ICD-10-CM coding knowledge to manufacture a clinical
  condition or clinical relationship.
- Do not use approximate synonyms from the ICD-10-CM context as evidence
  that the patient satisfies a code.


BILLABLE STATUS:

- The "billable" field in the supplied ICD-10-CM context represents the
  billable/specific status extracted from the ICD-10Data code page.
- Treat billable status as coding metadata, not as clinical evidence.
- "billable": true means the candidate is identified as a
  billable/specific ICD-10-CM code.
- "billable": false means the candidate is identified as non-billable or
  non-specific and must not be selected as a final ICD-10-CM code.
- "billable": null means the billable status could not be determined.
  Do not assume that the candidate is billable.
- Billable status alone is not sufficient to select a code. The candidate
  must also be supported by the clinical evidence and applicable coding
  instructions.
- Do not select ICD-10-CM category, chapter, or non-billable header codes
  as final codes.


CLINICAL RELATIONSHIP VS CODING RELATIONSHIP:

- A documented relationship between clinical conditions does not
  automatically establish that a particular ICD-10-CM code applies.
- Before selecting a code that represents a relationship, complication,
  supervision category, or other coded association, verify that the
  supplied clinical evidence supports the specific relationship required
  by that code.
- Do not use an ICD-10-CM code description, approximate synonym,
  "applicable to" terminology, or other retrieved wording as evidence
  that the patient meets the clinical criteria represented by that code.
- A relationship may be retained in the clinical extraction for
  candidate retrieval without being sufficient to support a final code.
- The existence of a clinical relationship and the applicability of a
  specific ICD-10-CM relationship code must be evaluated separately.
- Do not create a clinical relationship merely because two conditions
  commonly occur together.
- Do not infer a coding relationship solely from a medically plausible
  association.


CONDITION-LEVEL CODING EVALUATION:

- Every condition identified as current and encounter-relevant must be
  independently evaluated for coding.
- Independently evaluate each condition against the clinical evidence,
  retrieved candidates, coding instructions, and other selected codes.
- Independent evaluation does NOT mean that every condition must receive
  a separate ICD-10-CM code.
- A condition may be represented by a combination code, an etiology/
  manifestation coding structure, or another applicable coding construct.
- Do not omit a documented current, encounter-relevant condition solely
  because it participates in a clinical relationship with another
  condition.
- Do not omit a condition merely because another selected code represents
  part or all of the relationship between the conditions.
- After identifying a supported combination code, determine whether each
  documented condition is fully represented by that code or whether an
  additional code is required or appropriate.
- Do not add a redundant individual code when the applicable combination
  code already represents that condition and no coding instruction
  requires the additional individual code.
- When a selected combination code requires an additional code to fully
  identify a documented condition or qualifier, add that additional code
  when supported by the clinical evidence.
- The final code set should represent the documented encounter without
  unnecessarily duplicating information.
- A condition that is evaluated but not separately coded must have a
  coding-based reason, such as being fully represented by a selected
  combination code or being excluded by an applicable coding instruction.
- Do not use a relationship itself as a reason to discard an otherwise
  independently supported condition.


CLINICAL SPECIFICITY:

Only select a code requiring a qualifier when that qualifier is supported
by the supplied clinical evidence.

This includes, but is not limited to:

- severity
- stage
- laterality
- anatomical site
- acuity
- chronicity
- recurrence
- timing
- pregnancy characteristics
- complications
- manifestations
- underlying conditions

If the evidence does not support a required qualifier, do not select the
more specific code.

Do not infer a qualifier from a candidate's description.


COMBINATION CODES:

Evaluate whether the supplied ICD-10-CM context contains a combination
code that represents multiple documented conditions or a documented
relationship between conditions.

When a supported combination code exists, evaluate it against separate
codes and prefer the appropriate combination-code representation when
supported by the clinical evidence and coding instructions.

When using a combination code:

- Confirm that every clinical component represented by the combination
  code is supported by the clinical evidence.
- Do not additionally select separate codes for conditions already fully
  represented by the combination code unless the supplied coding
  information requires or supports an additional code.
- Evaluate whether any documented condition or qualifier is not fully
  represented by the combination code and therefore requires or supports
  an additional code.
- Do not omit a documented condition merely because it is related to
  another condition.
- Do not create a clinical relationship merely because a combination code
  exists or because two conditions commonly occur together.

For example, if the clinical evidence documents a diabetes complication
and the supplied ICD-10-CM context supports a diabetes combination code,
evaluate the combination code rather than automatically selecting both
the combination code and the corresponding standalone diabetes code.
If the combination code requires an additional code to identify a
manifestation or other characteristic, evaluate and add that code when
supported.


CODING INSTRUCTIONS:

Evaluate applicable coding instructions contained in the supplied
ICD-10-CM context, including:

- CODE FIRST
- USE ADDITIONAL
- CODE ALSO
- TYPE 1 EXCLUDES
- TYPE 2 EXCLUDES
- INCLUDES

Follow these instructions when they apply to the documented clinical
conditions.

Do not treat coding instructions as evidence that a condition exists.

A coding instruction may determine how supported conditions should be
represented, but it must not create an unsupported condition.


PRIMARY AND SECONDARY ROLES:

For selected codes:

- "primary" means the code should be reported as the primary diagnosis
  for the current encounter based on the supplied clinical evidence and
  coding context.
- "secondary" means the code is additionally supported and relevant to
  the current encounter.

Do not assign a primary or secondary role based only on candidate ranking.

- A condition being documented in the patient's record does not by itself
  make its code reportable for the current encounter.
- Assign a secondary role only when the clinical context establishes that
  the condition is relevant to the current encounter and the supplied
  coding information supports reporting it.
- Do not assume that the most clinically significant chronic condition is
  automatically the primary diagnosis.
- Base sequencing on the supplied encounter context and applicable coding
  information.


ADDITIONAL CODES:

Use "additional_codes" when the supplied ICD-10-CM information indicates
that another code should or may be reported in addition to a selected
code, and the clinical evidence supports that additional code.

- Additional codes must represent information that is not already fully
  represented by the selected code set.
- Do not add an additional code merely because it is a plausible related
  condition.
- Do not add a redundant code solely because the condition was independently
  evaluated.
- An additional code must itself be supported by the clinical evidence.


REJECTED CANDIDATES:

Candidates that are not sufficiently supported should be placed in
"rejected_candidates".

Give a concise reason explaining why the candidate was rejected.

Common reasons may include:

- condition not documented
- required specificity not documented
- candidate represents a different condition
- candidate conflicts with an applicable exclusion
- combination code is more appropriate
- coding instruction makes the candidate inappropriate
- candidate is not relevant to the current encounter
- specific coding relationship required by the candidate is not documented
- candidate is a category or non-reportable code
- candidate is non-billable
- condition is already fully represented by an appropriate selected
  combination code and a separate code is not required


REASON FIELD:

For every selected, additional, or rejected code, provide a concise
reason based on the supplied clinical evidence and/or applicable
ICD-10-CM coding information.

Do not invent evidence.

For selected and additional codes, explain why the code is supported.

For rejected candidates, explain the decisive reason the candidate is not
appropriate.


OUTPUT:

Return ONLY valid JSON using exactly this structure:

{{
    "selected_codes": [
        {{
            "code": "<ICD-10-CM code>",
            "role": "<primary or secondary>",
            "reason": "<concise evidence-based reason>"
        }}
    ],
    "additional_codes": [
        {{
            "code": "<ICD-10-CM code>",
            "reason": "<concise evidence-based reason>"
        }}
    ],
    "rejected_candidates": [
        {{
            "code": "<ICD-10-CM code>",
            "reason": "<concise evidence-based reason>"
        }}
    ]
}}


IMPORTANT:

- Populate all values dynamically from the supplied inputs.
- Do not copy placeholder values into the output.
- Do not include ICD-10-CM codes that are not present in the supplied
  ICD-10-CM context.
- Do not include unsupported codes.
- Do not invent clinical conditions.
- Do not invent clinical relationships.
- Do not invent qualifiers.
- Do not use the ICD-10-CM context itself as evidence that a clinical
  condition or relationship exists in the patient.
- Do not use approximate synonyms as evidence that the patient satisfies
  the corresponding code.
- Do not infer that a documented clinical relationship satisfies the
  specific relationship required by an ICD-10-CM code unless the supplied
  clinical evidence supports that requirement.
- Do not select a candidate with "billable": false.
- Do not assume a candidate with "billable": null is billable.
- Do not assign primary or secondary status based only on candidate
  ranking.
- Do not assign a separate code merely because a condition was independently
  evaluated.
- Do not omit a current, encounter-relevant condition solely because it
  participates in a relationship with another condition.
- Do not select both a combination code and a redundant standalone code
  when the combination code fully represents the same documented condition
  and no supplied coding instruction requires the standalone code.
- Add required additional codes when the supplied coding information
  indicates they are needed.
- Do not include Markdown code fences.
- Do not include explanations before or after the JSON.
- If no codes are supported, return empty "selected_codes" and
  "additional_codes" lists.
- Put unsupported candidates in "rejected_candidates" when appropriate.
"""

    response = client.responses.create(
        model="gpt-5.6-luna",
        input=prompt,
    )

    return response.output_text
