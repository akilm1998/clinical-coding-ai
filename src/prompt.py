def generate_clinical_conditions(coding_context, client):
    prompt = f"""
You are an experienced clinical documentation reviewer.

Review the supplied coding context and identify the clinically relevant
conditions for the current encounter.

Your task is to:

1. Identify conditions relevant to the current encounter.
2. Distinguish current conditions from historical conditions.
3. Identify clinically meaningful relationships between conditions when
   supported by the overall supplied clinical evidence.
4. Enrich conditions and relationships with medically precise terminology
   that can improve downstream ICD-10-CM candidate retrieval.

Coding context:
{coding_context}


CORE RULES:

- Use the supplied coding context as the source of truth.
- Return only conditions supported by the supplied clinical context.
- Consider the current encounter issues first.
- Include historical conditions when the supplied encounter information,
  clinical note, assessment/plan, procedures, observations, or other
  supplied evidence establishes that they are relevant to the current
  encounter.
- Do not include historical conditions merely because they exist somewhere
  in the patient's record.
- Preserve the condition status supported by the supplied context.
- Distinguish medical conditions from social, demographic, administrative,
  or other non-medical findings.
- Do not assign ICD-10, ICD-9, CPT, SNOMED, or other billing codes.
- Do not make the final coding decision.
- Do not determine primary or secondary diagnosis sequencing.
- Do not determine billing reportability.


CLINICAL TERMINOLOGY:

For each condition, provide:

- "clinical_terms": medically precise terminology that represents the same
  documented clinical concept.
- "search_terms": terminology useful for retrieving ICD-10-CM candidates
  for that same documented clinical concept.

Do not combine a condition with another condition merely because both are
present in the same encounter.

For example, if the context documents obesity and pregnancy separately,
do not create terminology such as "maternal obesity complicating pregnancy"
unless the supplied clinical evidence supports that relationship.

Search terms must represent the documented clinical concept or a clinically
supported relationship involving that concept.

For each relationship, provide:

- "relationship": a concise description of the supported clinical
  relationship.
- "clinical_terms": medically precise terminology describing the
  relationship.
- "search_terms": terminology useful for retrieving ICD-10-CM candidates
  for that relationship.

Use the most clinically specific terminology that is supported by the
supplied evidence.

Do not introduce new clinical facts while enriching terminology.

A qualifier or characteristic may be included only when it is explicitly
documented or directly and unambiguously derivable from the supplied
clinical context.

This applies to characteristics such as:

- severity
- stage
- laterality
- anatomical site
- acuity
- chronicity
- recurrence
- timing
- duration
- pregnancy characteristics
- gestational information
- pregnancy order
- number of occurrences
- complications
- manifestations
- underlying conditions
- other clinically relevant qualifiers

Do not infer missing specificity simply because it is clinically plausible,
commonly associated with the condition, or useful for finding a more
specific ICD-10-CM code.

If the evidence does not support greater specificity, use the more general
medically accurate terminology supported by the source.

Clinical terminology may improve the wording of a documented concept, but
must not change its factual meaning.

Keep qualifiers attached to the condition or clinical event they actually
describe. Do not transfer characteristics from one condition or event to
another.


RELATIONSHIPS:

Relationship extraction is a clinical reasoning task.

Evaluate the conditions together using the complete supplied clinical
context. Do not evaluate each condition independently when determining
whether a clinically meaningful relationship exists.

Identify a relationship when the overall clinical evidence supports a
meaningful connection between two or more documented conditions.

A relationship can be supported by:

- an explicit statement in a clinical note
- an assessment or plan statement
- an encounter diagnosis
- structured clinical terminology
- the combination of multiple documented clinical conditions
- observations or procedures that provide supporting clinical context
- other clinical evidence that, when considered together, supports the
  relationship

The relationship may represent:

- causal relationship
- etiological relationship
- underlying condition and manifestation
- complication
- associated condition
- current condition and relevant historical condition
- other clinically meaningful relationship

Do not require the relationship to appear as one literal sentence.

The supplied clinical context may contain separate pieces of evidence that
must be correlated to identify a clinically meaningful relationship.

For example, if the supplied context contains:

- Type 2 diabetes mellitus
- Chronic kidney disease
- both conditions are active and confirmed
- both conditions are relevant to the same clinical case

evaluate whether the overall clinical evidence supports a relationship
between Type 2 diabetes mellitus and chronic kidney disease.

If the clinical evidence supports that the CKD is related to the diabetes,
identify that relationship.

However, do not automatically create the relationship merely because
diabetes and CKD coexist.

Distinguish between:

    Type 2 diabetes + CKD
    -> relationship may be unsupported

and:

    Type 2 diabetes + CKD
    + additional clinical evidence supporting a diabetes-related kidney
      condition
    -> clinically supported relationship

Do not infer a relationship solely because two conditions:

- share the same encounter
- occur at the same time
- appear in the same patient
- are medically plausible associations
- commonly occur together
- have a known epidemiological association

However, these facts may be considered together with other clinical
evidence when determining whether the overall case supports a meaningful
relationship.

The goal is to identify relationships supported by the clinical case, not
to require a literal relationship statement.

IMPORTANT:

Do not use ICD-10-CM coding knowledge to manufacture a clinical
relationship.

For example, do not reason:

"ICD-10-CM has a diabetes-with-CKD combination code, therefore diabetes must
be causing this patient's CKD."

The clinical relationship must be supported by the supplied clinical
evidence.

Likewise, do not reject a clinically supported relationship merely because
the relationship is not explicitly written as a single sentence.

When a relationship is identified, describe the actual relationship
supported by the evidence.

Do not strengthen the relationship beyond the evidence.

For example, if the supplied evidence supports that CKD is related to Type 2
diabetes mellitus, do not additionally claim:

- diabetic nephropathy
- proteinuria
- renal failure
- a specific diabetic renal manifestation

unless those facts are separately supported.

Relationship extraction is separate from final coding.

You are identifying the clinical relationship that exists in the supplied
case so that downstream ICD-10-CM retrieval and coding reasoning can evaluate
it.

Do not assign an ICD-10-CM code to the relationship.


RELATIONSHIP TERMINOLOGY:

For each identified relationship:

- "relationship": describe the clinically supported connection between the
  conditions.
- "clinical_terms": provide medically precise terminology representing that
  relationship.
- "search_terms": provide terminology useful for retrieving ICD-10-CM
  candidates representing that relationship.

Relationship terminology may be more specific than the individual condition
names when the relationship itself provides that specificity.

For example, if the clinical evidence supports a relationship between
Type 2 diabetes mellitus and chronic kidney disease, useful terminology
could include:

- diabetes mellitus with chronic kidney disease
- diabetic chronic kidney disease
- chronic kidney disease due to Type 2 diabetes mellitus

Only use terminology that is supported by the supplied clinical evidence.

Do not use relationship terminology merely because it would lead to a
more specific ICD-10-CM code.


SEARCH TERMS:

Search terms are for retrieval only.

They should help a downstream ICD-10-CM search find plausible candidate
codes representing the documented clinical concept.

Search terms may include:

- the original condition terminology
- standard medical terminology
- supported clinical synonyms
- supported qualifiers
- supported relationship terminology

When a clinically supported relationship is identified, relationship
search terms may represent the combined clinical concept.

For example:

- Type 2 diabetes mellitus with chronic kidney disease
- diabetic chronic kidney disease
- chronic kidney disease due to Type 2 diabetes mellitus

Do not include ICD-10-CM codes in the output.

Do not choose a code based on the search terms.


DYNAMIC CARDINALITY:

- Do not assume a fixed number of conditions.
- Include every condition supported by the supplied context that meets the
  relevance criteria.
- There may be zero, one, or multiple current conditions.
- There may be zero, one, or multiple historical conditions.
- There may be zero, one, or multiple relationships.
- Multiple relationships may involve the same condition.
- A condition does not require a relationship with another condition.
- If no supported relationships exist, return an empty relationships list.


FIELD DEFINITIONS:

- "name": the condition identified from the supplied clinical context.
- "status": the status supported by the supplied context.
- "encounter_relevance": whether the condition is relevant to the current
  encounter.
- "clinical_terms": medically precise terminology representing the same
  documented clinical concept.
- "search_terms": retrieval terminology for finding plausible ICD-10-CM
  candidates.
- "condition_1": first condition participating in the relationship.
- "condition_2": second condition participating in the relationship.
- "relationship": clinically meaningful description of the supported
  relationship between the conditions.

None of these fields represent a final ICD-10-CM coding decision.


OUTPUT:

Return ONLY valid JSON using this structure:

{{
    "current_conditions": [
        {{
            "name": "<condition name from the supplied context>",
            "status": "<status supported by the supplied context>",
            "encounter_relevance": true,
            "clinical_terms": [
                "<medically precise supported term>"
            ],
            "search_terms": [
                "<useful supported ICD-10-CM retrieval term>"
            ]
        }}
    ],
    "historical_conditions": [
        {{
            "name": "<condition name from the supplied context>",
            "status": "<status supported by the supplied context>",
            "encounter_relevance": true,
            "clinical_terms": [
                "<medically precise supported term>"
            ],
            "search_terms": [
                "<useful supported ICD-10-CM retrieval term>"
            ]
        }}
    ],
    "relationships": [
        {{
            "condition_1": "<condition name>",
            "condition_2": "<condition name>",
            "relationship": "<supported clinical relationship>",
            "clinical_terms": [
                "<medically precise supported relationship term>"
            ],
            "search_terms": [
                "<useful supported ICD-10-CM retrieval term>"
            ]
        }}
    ]
}}

IMPORTANT:

- Populate all values dynamically from the supplied coding context.
- Do not copy the placeholder values into the output.
- Do not invent conditions or relationships.
- Do not invent clinical qualifiers.
- Do not include unsupported specificity.
- Evaluate multiple pieces of clinical evidence together when determining
  relationships.
- Do not require an explicit relationship sentence when the overall
  clinical evidence supports the relationship.
- Do not infer relationships solely from simple co-occurrence.
- If no additional clinical terminology is supported, return an empty
  "clinical_terms" list.
- If no useful supported retrieval terminology exists, return an empty
  "search_terms" list.
- If there are no relevant current conditions, return an empty list.
- If there are no relevant historical conditions, return an empty list.
- If there are no supported relationships, return an empty list.
- Do not include ICD-10-CM codes anywhere in the output.
- Do not include Markdown code fences.
- Do not include explanations before or after the JSON.
- Do not use terminology that implies a clinical relationship, complication,
  encounter subtype, temporal state, or other qualifier unless that
  implication is supported by the supplied evidence.
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


CORE RULES:

- Use the supplied clinical context as the source of truth for what is
  documented about the patient.
- Use the supplied ICD-10-CM context as the source of truth for code
  descriptions and retrieved coding instructions.
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
- A candidate with "billable": false must not be selected as a final
  ICD-10-CM code.
- A candidate with "billable": true may be selected if it is otherwise
  supported by the clinical evidence and applicable coding instructions.
- A candidate with "billable": null has an unknown billable status.
  Do not assume that it is billable.
- Do not select ICD-10-CM category, chapter, or non-billable header codes as
  final codes.
- If a more specific candidate is not supported by the clinical evidence,
  do not fall back to a broader category code merely because it exists in
  the candidate set. Reject the unsupported specific candidates and select
  a supported reportable code only if one is available.


BILLABLE STATUS:

- The "billable" field in the supplied ICD-10-CM context represents the
  billable/specific status extracted from the ICD-10Data code page.
- Treat this field as coding metadata, not as clinical evidence.
- "billable": true means the candidate is identified as a billable/specific
  ICD-10-CM code.
- "billable": false means the candidate is identified as non-billable or
  non-specific and must not be selected as a final code.
- "billable": null means the billable status could not be determined from
  the retrieved page. Do not assume the candidate is billable.
- Billable status alone is not sufficient to select a code. The candidate
  must also be supported by the clinical evidence and applicable coding
  instructions.


CLINICAL RELATIONSHIP VS CODING RELATIONSHIP:

- A documented relationship between clinical conditions does not
  automatically establish that a particular ICD-10-CM code applies.

- Before selecting a code that represents a relationship, complication,
  supervision category, or other coded association, verify that the
  supplied clinical evidence supports the specific relationship required
  by that code.

- Do not use an ICD-10-CM code's description, approximate synonyms,
  "applicable to" terminology, or other retrieved wording as evidence
  that the patient meets the clinical criteria represented by that code.

- For example, documentation of a current pregnancy and a history of
  prior miscarriage does not by itself establish supervision of pregnancy
  with poor reproductive or obstetric history.

- A relationship may be retained in the clinical extraction for candidate
  retrieval without being sufficient to support a final ICD-10-CM code.

- The existence of a clinical relationship and the applicability of a
  specific ICD-10-CM relationship code must be evaluated separately.


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


COMBINATION CODES:

Evaluate whether the supplied ICD-10-CM context contains a combination
code that represents multiple documented conditions or a documented
relationship between conditions.

When a supported combination code exists, evaluate it against separate
codes and prefer the appropriate combination-code representation when
supported by the supplied evidence and coding instructions.

Do not create a clinical relationship merely because two conditions
commonly occur together.


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


ADDITIONAL CODES:

Use "additional_codes" when the supplied ICD-10-CM information indicates
that another code should or may be reported in addition to a selected
code, and the clinical evidence supports that additional code.

Do not add an additional code merely because it is a plausible related
condition.


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


REASON FIELD:

For every selected, additional, or rejected code, provide a concise
reason based on the supplied clinical evidence and/or applicable
ICD-10-CM coding information.

Do not invent evidence.


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
