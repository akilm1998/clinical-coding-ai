# 30-case coding regression validation

| Case | Conditions | Relationships | Latest encounter | Complaint | Valid |
| --- | --- | --- | --- | --- | --- |
| case_01 | Diabetes mellitus type 2 (disorder) | none | 2003-05-20T12:50:47+05:30 / 00000000-0000-0bb9-2fdc-cb8ccf99d2ef | Follow-up for type 2 diabetes mellitus | True |
| case_02 | Diabetes mellitus type 2 (disorder); Chronic kidney disease stage 1 (disorder) | diabetes -> CKD | 2003-07-31T14:35:07+05:30 / 00000000-0000-0bba-1c04-a113d5a98d8a | Follow-up for type 2 diabetes mellitus and chronic kidney disease | True |
| case_03 | Diabetes mellitus type 2 (disorder); Chronic kidney disease stage 1 (disorder) | none | 2003-03-07T14:00:20+05:30 / 00000000-0000-0bbb-7101-5a4cd6767e89 | Follow-up for diabetes and kidney disease | True |
| case_04 | Diabetes mellitus type 2 (disorder); Essential hypertension (disorder) | diabetes -> hypertension | 2003-03-09T11:06:26+05:30 / 00000000-0000-0bbc-d700-61217075d3e0 | Evaluation of diabetes and blood pressure | True |
| case_05 | Diabetes mellitus type 2 (disorder); Essential hypertension (disorder) | none | 2003-10-15T10:31:39+05:30 / 00000000-0000-0bbd-2dce-c3cbad3d1f40 | Chronic disease follow-up for diabetes | True |
| case_06 | Essential hypertension (disorder) | none | 2003-12-26T12:16:00+05:30 / 00000000-0000-0bbe-46c9-420c05cc16e7 | Evaluation of hypertension | True |
| case_07 | Chronic kidney disease stage 3 (disorder) | none | 2003-08-02T11:41:12+05:30 / 00000000-0000-0bbf-4f07-bc4e10e384e1 | Follow-up for chronic kidney disease stage 3 | True |
| case_08 | Essential hypertension (disorder); Chronic kidney disease stage 3 (disorder) | hypertension -> CKD | 2003-10-28T14:14:18+05:30 / 00000000-0000-0bc0-a770-030fef37c321 | Follow-up for hypertension and chronic kidney disease | True |
| case_09 | Diabetes mellitus type 2 (disorder); Obesity (disorder) | obesity -> diabetes management | 2003-06-04T13:39:31+05:30 / 00000000-0000-0bc1-0b86-826f8daf47b4 | Follow-up for diabetes and obesity | True |
| case_10 | Diabetes mellitus type 2 (disorder); Hyperlipidemia (disorder) | none | 2003-08-15T15:23:51+05:30 / 00000000-0000-0bc2-9ee2-dca6f5631a7d | Follow-up for diabetes and lipid management | True |
| case_11 | Diabetes mellitus type 2 (disorder); Chronic kidney disease stage 1 (disorder); Essential hypertension (disorder) | diabetes -> CKD | 2003-03-22T14:49:04+05:30 / 00000000-0000-0bc3-c175-fbe7b2d161c3 | Complex follow-up for diabetes, kidney disease, and hypertension | True |
| case_12 | Chronic obstructive lung disease (disorder) | none | 2003-03-24T11:55:10+05:30 / 00000000-0000-0bc4-8d10-08c5568f640f | Follow-up for chronic obstructive pulmonary disease | True |
| case_13 | Chronic obstructive lung disease (disorder); Essential hypertension (disorder) | none | 2003-10-30T11:20:23+05:30 / 00000000-0000-0bc5-fe8e-d347a9c38356 | Follow-up for COPD and hypertension | True |
| case_14 | Asthma (disorder) | none | 2003-01-09T13:04:44+05:30 / 00000000-0000-0bc6-1ac0-60424ddc487b | Evaluation of asthma control | True |
| case_15 | Asthma (disorder); Allergic rhinitis (disorder) | rhinitis -> asthma symptoms | 2003-08-17T12:29:57+05:30 / 00000000-0000-0bc7-e495-db6ac541f677 | Follow-up for asthma and allergic rhinitis | True |
| case_16 | Heart failure (disorder) | none | 2003-08-19T09:36:02+05:30 / 00000000-0000-0bc8-de45-06e514cd8647 | Follow-up for heart failure | True |
| case_17 | Heart failure (disorder); Essential hypertension (disorder) | hypertension -> heart failure | 2003-03-26T09:01:15+05:30 / 00000000-0000-0bc9-f6af-80134437422c | Follow-up for heart failure and hypertension | True |
| case_18 | Obesity (disorder); Essential hypertension (disorder); Diabetes mellitus type 2 (disorder) | obesity -> diabetes; obesity -> hypertension; diabetes -> hypertension | 2003-06-06T10:45:36+05:30 / 00000000-0000-0bca-734c-0e801c29e1f0 | Comprehensive follow-up for metabolic conditions | True |
| case_19 | Hypothyroidism (disorder) | none | 2003-01-11T10:10:50+05:30 / 00000000-0000-0bcb-a52b-dfe960b1f0ef | Follow-up for hypothyroidism | True |
| case_20 | Gastroesophageal reflux disease (disorder) | none | 2003-01-13T07:16:55+05:30 / 00000000-0000-0bcc-1d6b-5699baad0218 | Evaluation of gastroesophageal reflux symptoms | True |
| case_21 | Osteoarthritis of knee (disorder) | none | 2003-08-21T06:42:08+05:30 / 00000000-0000-0bcd-aecb-1e7e6018aa03 | Evaluation of knee pain from osteoarthritis | True |
| case_22 | Depressive disorder (disorder) | none | 2003-11-01T08:26:29+05:30 / 00000000-0000-0bce-a49a-a1089787b346 | Follow-up for depressive disorder | True |
| case_23 | Acute bronchitis (disorder) | none | 2003-06-08T07:51:42+05:30 / 00000000-0000-0bcf-5b07-008dd3839312 | Evaluation of cough due to acute bronchitis | True |
| case_24 | Upper respiratory infection (disorder) | none | 2003-03-16T23:30:48+05:30 / 00000000-0000-0bd0-7a49-da7fbcdb5ac9 | Evaluation of acute viral respiratory illness | True |
| case_25 | Dental caries (disorder) | none | 2003-10-22T22:56:01+05:30 / 00000000-0000-0bd1-fe3a-1715bf069931 | Evaluation of dental pain from dental caries | True |
| case_26 | Acute bronchitis (disorder) | none | 2005-01-02T00:40:22+05:30 / 00000000-0000-0bd2-5553-52751afec2b3 | Evaluation of acute bronchitis | True |
| case_27 | Upper respiratory infection (disorder) | none | 2004-08-09T00:05:35+05:30 / 00000000-0000-0bd3-d026-42e863c9911b | Evaluation of upper respiratory infection | True |
| case_28 | Essential hypertension (disorder) | none | 2005-08-10T21:11:40+05:30 / 00000000-0000-0bd4-f737-b7a1525575b1 | Evaluation of hypertension | True |
| case_29 | Diabetes mellitus type 2 (disorder); Chronic kidney disease stage 1 (disorder); Anemia (disorder) | diabetes -> CKD | 2003-03-18T20:36:54+05:30 / 00000000-0000-0bd5-e256-33b339858c5d | Follow-up for diabetes, kidney disease, and anemia | True |
| case_30 | Diabetes mellitus type 2 (disorder); Chronic kidney disease stage 1 (disorder); Essential hypertension (disorder) | diabetes -> CKD; diabetes -> hypertension | 2003-05-29T22:21:14+05:30 / 00000000-0000-0bd6-8bb4-92b6cee3185a | Complex follow-up for diabetes, renal disease, and hypertension | True |
