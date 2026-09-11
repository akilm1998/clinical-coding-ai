# V2 – ICD-10 Data Scraper

V2 focuses on building the ICD-10-CM data acquisition component of the project.

The scraper retrieves structured ICD-10-CM information from [ICD10Data.com](https://www.icd10data.com/) for a user-provided diagnosis code.

The purpose of V2 was to establish a structured ICD-10 knowledge layer that could later be used by downstream coding and retrieval workflows.

---

## V2 Architecture

```text
                 ICD-10-CM Code
                       │
                       ▼
                Search ICD10Data
                       │
                       ▼
                Resolve Code URL
                       │
                       ▼
                  Fetch Web Page
                       │
                       ▼
                   Parse HTML
                       │
                       ▼
             Extract ICD-10 Information
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
        Code       Description   Code Details
                                    │
                                    ▼
                            Dynamic Sections
                                    │
                     ┌──────────────┼──────────────┐
                     ▼              ▼              ▼
                 Code First      Excludes       Includes
                     │              │              │
                     └──────────────┼──────────────┘
                                    │
                                    ▼
                              Other Sections
                                    │
                                    ▼
                             Structured Output
```

---

## V2 Workflow

The scraper follows a multi-step process to convert ICD-10Data web pages into structured coding information.

### 1. Accept an ICD-10-CM Code

The process begins with a user-provided ICD-10-CM code.

```text
Input
  │
  ▼
ICD-10-CM Code
```

---

### 2. Search ICD10Data

The supplied code is used to locate the corresponding ICD-10-CM page on ICD10Data.com.

```text
ICD-10-CM Code
      │
      ▼
ICD10Data Search
      │
      ▼
Matching Code
```

---

### 3. Resolve the Code URL

Once the relevant result is identified, the scraper resolves the URL associated with the ICD-10-CM code.

This provides the page from which the detailed coding information can be retrieved.

---

### 4. Fetch and Parse the Web Page

The resolved page is retrieved and its HTML content is parsed.

The scraper extracts the relevant coding information from the page rather than treating the page as unstructured text.

---

## Extracted ICD-10 Information

V2 extracts multiple types of information associated with an ICD-10-CM code.

### Code

The ICD-10-CM code itself.

### Description

The description associated with the code.

### Code Details

Additional coding information available on the corresponding ICD-10Data page.

This can include dynamic sections such as:

- Code First
- Excludes
- Includes
- Other coding sections

The resulting information is converted into a structured representation for downstream use.

---

# Dynamic Coding Sections

A key part of V2 is handling coding information that appears in different sections of an ICD-10-CM page.

Conceptually:

```text
ICD-10-CM Code
      │
      ▼
Code Details
      │
      ├── Code First
      ├── Excludes
      ├── Includes
      └── Other Sections
```

These sections contain information that can be important when interpreting the available coding options.

V2 therefore preserves these details instead of extracting only the code and description.

---

# Structured Output

The scraper produces structured output containing the extracted ICD-10-CM information.

Conceptually:

```text
ICD-10-CM Code
      │
      ├── Code
      ├── Description
      └── Code Details
             │
             ├── Code First
             ├── Excludes
             ├── Includes
             └── Other Sections
```

This structured representation provides the foundation for using ICD-10 information in later stages of the project.

---

# Why V2?

V1 relied on a supervised prediction approach where the model learned associations between clinical text and ICD-10 codes from the training dataset.

V2 introduced a separate coding knowledge acquisition layer.

Instead of requiring the machine learning model to contain every ICD-10 code and its associated coding information in its learned parameters, V2 explored retrieving coding knowledge from an external structured source.

This creates a separation between:

```text
Clinical / ML Processing
          │
          ▼
     ICD-10 Knowledge
```

The approach provided the foundation for the more structured retrieval and evidence-constrained coding architecture developed in V3.

---

# V2 Status

- [x] ICD-10-CM search implemented
- [x] Code URL resolution implemented
- [x] Web page retrieval implemented
- [x] HTML parsing implemented
- [x] ICD-10 code extraction implemented
- [x] Description extraction implemented
- [x] Code details extraction implemented
- [x] Dynamic coding sections handled
- [x] Structured output generated

---

# Key Implementation

The main implementation for V2 is:

[`scrapping_code.py`](https://github.com/akilm1998/synthetic-clinical-note-generator/blob/v2/scrapping_code.py)

---

# V2 Conclusion

V2 established the ICD-10-CM data acquisition layer for the project.

The key outcome was a structured representation of ICD-10 coding information that could be retrieved independently of the clinical language model.

This became an important foundation for V3, where ICD-10 retrieval was separated from clinical evidence extraction and the final coding decision.
