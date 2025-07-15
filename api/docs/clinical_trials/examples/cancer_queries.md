# Cancer Clinical Trial Search Examples

This document provides example queries for various cancer types and conditions.

## General Cancer Searches

### Basic Cancer Search
```
EXPANSION[Concept]cancer OR EXPANSION[Concept]neoplasm OR EXPANSION[Concept]tumor
```

### Cancer with Active Recruitment
```
(EXPANSION[Concept]cancer OR EXPANSION[Concept]neoplasm) AND AREA[OverallStatus]RECRUITING
```

### Cancer Interventional Studies
```
EXPANSION[Concept]cancer AND AREA[StudyType]INTERVENTIONAL
```

## Breast Cancer

### Invasive Ductal Carcinoma
```
EXPANSION[Concept]invasive ductal carcinoma OR EXPANSION[Concept]breast cancer OR EXPANSION[Concept]ductal carcinoma OR EXPANSION[Concept]breast neoplasm
```

### Breast Cancer with Chemotherapy
```
(EXPANSION[Concept]breast cancer OR EXPANSION[Concept]mammary carcinoma) AND EXPANSION[Concept]chemotherapy
```

### Metastatic Breast Cancer
```
EXPANSION[Concept]metastatic breast cancer OR EXPANSION[Concept]breast cancer metastases OR (EXPANSION[Concept]breast cancer AND EXPANSION[Concept]metastatic)
```

### Triple Negative Breast Cancer
```
EXPANSION[Concept]triple negative breast cancer OR EXPANSION[Concept]TNBC OR (EXPANSION[Concept]breast cancer AND "triple negative")
```

### HER2 Positive Breast Cancer
```
EXPANSION[Concept]HER2 positive breast cancer OR (EXPANSION[Concept]breast cancer AND EXPANSION[Concept]HER2)
```

## Lung Cancer

### Non-Small Cell Lung Cancer
```
EXPANSION[Concept]non-small cell lung cancer OR EXPANSION[Concept]NSCLC OR EXPANSION[Concept]non small cell lung carcinoma
```

### Small Cell Lung Cancer
```
EXPANSION[Concept]small cell lung cancer OR EXPANSION[Concept]SCLC OR EXPANSION[Concept]small cell lung carcinoma
```

### Lung Adenocarcinoma
```
EXPANSION[Concept]lung adenocarcinoma OR EXPANSION[Concept]pulmonary adenocarcinoma
```

## Colorectal Cancer

### Colorectal Cancer
```
EXPANSION[Concept]colorectal cancer OR EXPANSION[Concept]colon cancer OR EXPANSION[Concept]rectal cancer OR EXPANSION[Concept]colorectal carcinoma
```

### Metastatic Colorectal Cancer
```
EXPANSION[Concept]metastatic colorectal cancer OR (EXPANSION[Concept]colorectal cancer AND EXPANSION[Concept]metastatic)
```

## Prostate Cancer

### Prostate Cancer
```
EXPANSION[Concept]prostate cancer OR EXPANSION[Concept]prostate neoplasm OR EXPANSION[Concept]prostatic carcinoma
```

### Castrate-Resistant Prostate Cancer
```
EXPANSION[Concept]castrate resistant prostate cancer OR EXPANSION[Concept]CRPC OR "castration resistant prostate cancer"
```

## Skin Cancer

### Melanoma
```
EXPANSION[Concept]melanoma OR EXPANSION[Concept]malignant melanoma OR EXPANSION[Concept]cutaneous melanoma
```

### Basal Cell Carcinoma
```
EXPANSION[Concept]basal cell carcinoma OR EXPANSION[Concept]BCC OR EXPANSION[Concept]basal cell skin cancer
```

### Squamous Cell Carcinoma
```
EXPANSION[Concept]squamous cell carcinoma OR EXPANSION[Concept]SCC OR EXPANSION[Concept]squamous cell skin cancer
```

## Hematologic Malignancies

### Leukemia
```
EXPANSION[Concept]leukemia OR EXPANSION[Concept]leukaemia OR EXPANSION[Concept]blood cancer
```

### Acute Myeloid Leukemia
```
EXPANSION[Concept]acute myeloid leukemia OR EXPANSION[Concept]AML OR EXPANSION[Concept]acute myelogenous leukemia
```

### Chronic Lymphocytic Leukemia
```
EXPANSION[Concept]chronic lymphocytic leukemia OR EXPANSION[Concept]CLL
```

### Lymphoma
```
EXPANSION[Concept]lymphoma OR EXPANSION[Concept]lymphatic cancer
```

### Hodgkin Lymphoma
```
EXPANSION[Concept]Hodgkin lymphoma OR EXPANSION[Concept]Hodgkin disease OR EXPANSION[Concept]Hodgkins lymphoma
```

### Non-Hodgkin Lymphoma
```
EXPANSION[Concept]non-Hodgkin lymphoma OR EXPANSION[Concept]NHL OR EXPANSION[Concept]non Hodgkin lymphoma
```

### Multiple Myeloma
```
EXPANSION[Concept]multiple myeloma OR EXPANSION[Concept]plasma cell myeloma OR EXPANSION[Concept]myeloma
```

## Pediatric Cancers

### Childhood Cancer
```
EXPANSION[Concept]childhood cancer OR EXPANSION[Concept]pediatric cancer OR (EXPANSION[Concept]cancer AND AREA[StdAge]CHILD)
```

### Neuroblastoma
```
EXPANSION[Concept]neuroblastoma OR EXPANSION[Concept]neural crest tumor
```

### Wilms Tumor
```
EXPANSION[Concept]Wilms tumor OR EXPANSION[Concept]nephroblastoma OR EXPANSION[Concept]kidney tumor
```

## Brain and CNS Tumors

### Glioblastoma
```
EXPANSION[Concept]glioblastoma OR EXPANSION[Concept]GBM OR EXPANSION[Concept]glioblastoma multiforme
```

### Brain Tumor
```
EXPANSION[Concept]brain tumor OR EXPANSION[Concept]brain neoplasm OR EXPANSION[Concept]intracranial tumor
```

### Meningioma
```
EXPANSION[Concept]meningioma OR EXPANSION[Concept]meningeal tumor
```

## Gynecologic Cancers

### Ovarian Cancer
```
EXPANSION[Concept]ovarian cancer OR EXPANSION[Concept]ovarian neoplasm OR EXPANSION[Concept]ovarian carcinoma
```

### Cervical Cancer
```
EXPANSION[Concept]cervical cancer OR EXPANSION[Concept]cervical neoplasm OR EXPANSION[Concept]cervical carcinoma
```

### Endometrial Cancer
```
EXPANSION[Concept]endometrial cancer OR EXPANSION[Concept]uterine cancer OR EXPANSION[Concept]endometrial carcinoma
```

## Genitourinary Cancers

### Kidney Cancer
```
EXPANSION[Concept]kidney cancer OR EXPANSION[Concept]renal cancer OR EXPANSION[Concept]renal cell carcinoma
```

### Bladder Cancer
```
EXPANSION[Concept]bladder cancer OR EXPANSION[Concept]bladder neoplasm OR EXPANSION[Concept]bladder carcinoma
```

### Testicular Cancer
```
EXPANSION[Concept]testicular cancer OR EXPANSION[Concept]testicular neoplasm OR EXPANSION[Concept]testicular carcinoma
```

## Head and Neck Cancers

### Head and Neck Cancer
```
EXPANSION[Concept]head and neck cancer OR EXPANSION[Concept]head neck cancer OR EXPANSION[Concept]HNSCC
```

### Laryngeal Cancer
```
EXPANSION[Concept]laryngeal cancer OR EXPANSION[Concept]larynx cancer OR EXPANSION[Concept]laryngeal carcinoma
```

### Oral Cancer
```
EXPANSION[Concept]oral cancer OR EXPANSION[Concept]mouth cancer OR EXPANSION[Concept]oral cavity cancer
```

## Gastrointestinal Cancers

### Gastric Cancer
```
EXPANSION[Concept]gastric cancer OR EXPANSION[Concept]stomach cancer OR EXPANSION[Concept]gastric carcinoma
```

### Pancreatic Cancer
```
EXPANSION[Concept]pancreatic cancer OR EXPANSION[Concept]pancreatic neoplasm OR EXPANSION[Concept]pancreatic carcinoma
```

### Hepatocellular Carcinoma
```
EXPANSION[Concept]hepatocellular carcinoma OR EXPANSION[Concept]HCC OR EXPANSION[Concept]liver cancer
```

### Esophageal Cancer
```
EXPANSION[Concept]esophageal cancer OR EXPANSION[Concept]esophagus cancer OR EXPANSION[Concept]esophageal carcinoma
```

## Complex Searches

### Cancer with Immunotherapy
```
(EXPANSION[Concept]cancer OR EXPANSION[Concept]neoplasm) AND (EXPANSION[Concept]immunotherapy OR EXPANSION[Concept]checkpoint inhibitor OR EXPANSION[Concept]PD-1 OR EXPANSION[Concept]PD-L1)
```

### Cancer with Targeted Therapy
```
(EXPANSION[Concept]cancer OR EXPANSION[Concept]neoplasm) AND (EXPANSION[Concept]targeted therapy OR EXPANSION[Concept]molecular targeted therapy OR EXPANSION[Concept]precision medicine)
```

### Cancer Prevention Studies
```
(EXPANSION[Concept]cancer OR EXPANSION[Concept]neoplasm) AND AREA[DesignPrimaryPurpose]PREVENTION
```

### Cancer Screening Studies
```
(EXPANSION[Concept]cancer OR EXPANSION[Concept]neoplasm) AND AREA[DesignPrimaryPurpose]SCREENING
```

### Phase 3 Cancer Trials
```
(EXPANSION[Concept]cancer OR EXPANSION[Concept]neoplasm) AND AREA[Phase]PHASE3
```

### Cancer Trials in the US
```
(EXPANSION[Concept]cancer OR EXPANSION[Concept]neoplasm) AND SEARCH[Location](AREA[LocationCountry]United States)
```

## Tips for Cancer Searches

1. **Use EXPANSION[Concept]** for all medical terms to capture synonyms
2. **Combine general and specific terms** for comprehensive results
3. **Include anatomical site** when relevant (e.g., "lung", "breast")
4. **Use standard abbreviations** (e.g., NSCLC, HCC, AML)
5. **Consider treatment modalities** (chemotherapy, radiation, surgery)
6. **Include stage information** when relevant (metastatic, advanced, early stage)
7. **Use OR operators** to combine related terms
8. **Add filters** for study type, phase, and recruitment status as needed