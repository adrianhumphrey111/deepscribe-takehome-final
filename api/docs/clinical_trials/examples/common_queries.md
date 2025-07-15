# Common Clinical Trial Search Examples

This document provides example queries for common medical conditions and scenarios.

## Cardiovascular Conditions

### Heart Disease
```
EXPANSION[Concept]heart disease OR EXPANSION[Concept]cardiovascular disease OR EXPANSION[Concept]cardiac disease OR EXPANSION[Concept]coronary artery disease
```

### Hypertension
```
EXPANSION[Concept]hypertension OR EXPANSION[Concept]high blood pressure OR EXPANSION[Concept]elevated blood pressure
```

### Heart Failure
```
EXPANSION[Concept]heart failure OR EXPANSION[Concept]congestive heart failure OR EXPANSION[Concept]CHF OR EXPANSION[Concept]cardiac failure
```

### Atrial Fibrillation
```
EXPANSION[Concept]atrial fibrillation OR EXPANSION[Concept]AFib OR EXPANSION[Concept]irregular heartbeat OR EXPANSION[Concept]arrhythmia
```

## Metabolic Conditions

### Diabetes
```
EXPANSION[Concept]diabetes OR EXPANSION[Concept]diabetes mellitus OR EXPANSION[Concept]diabetic OR EXPANSION[Concept]hyperglycemia
```

### Type 2 Diabetes
```
EXPANSION[Concept]type 2 diabetes OR EXPANSION[Concept]diabetes mellitus type 2 OR EXPANSION[Concept]adult onset diabetes OR EXPANSION[Concept]T2DM
```

### Obesity
```
EXPANSION[Concept]obesity OR EXPANSION[Concept]overweight OR EXPANSION[Concept]weight loss OR EXPANSION[Concept]BMI
```

### Metabolic Syndrome
```
EXPANSION[Concept]metabolic syndrome OR EXPANSION[Concept]insulin resistance OR EXPANSION[Concept]syndrome X
```

## Neurological Conditions

### Alzheimer's Disease
```
EXPANSION[Concept]Alzheimer OR EXPANSION[Concept]Alzheimer's disease OR EXPANSION[Concept]dementia OR EXPANSION[Concept]cognitive impairment
```

### Parkinson's Disease
```
EXPANSION[Concept]Parkinson OR EXPANSION[Concept]Parkinson's disease OR EXPANSION[Concept]Parkinsonian OR EXPANSION[Concept]movement disorder
```

### Multiple Sclerosis
```
EXPANSION[Concept]multiple sclerosis OR EXPANSION[Concept]MS OR EXPANSION[Concept]sclerosis OR EXPANSION[Concept]demyelinating disease
```

### Stroke
```
EXPANSION[Concept]stroke OR EXPANSION[Concept]cerebrovascular accident OR EXPANSION[Concept]CVA OR EXPANSION[Concept]brain attack
```

### Epilepsy
```
EXPANSION[Concept]epilepsy OR EXPANSION[Concept]seizure OR EXPANSION[Concept]seizure disorder OR EXPANSION[Concept]convulsion
```

## Respiratory Conditions

### Asthma
```
EXPANSION[Concept]asthma OR EXPANSION[Concept]bronchial asthma OR EXPANSION[Concept]allergic asthma OR EXPANSION[Concept]airways disease
```

### COPD
```
EXPANSION[Concept]COPD OR EXPANSION[Concept]chronic obstructive pulmonary disease OR EXPANSION[Concept]emphysema OR EXPANSION[Concept]chronic bronchitis
```

### Pneumonia
```
EXPANSION[Concept]pneumonia OR EXPANSION[Concept]lung infection OR EXPANSION[Concept]respiratory infection
```

## Infectious Diseases

### COVID-19
```
EXPANSION[Concept]COVID-19 OR EXPANSION[Concept]coronavirus OR EXPANSION[Concept]SARS-CoV-2 OR EXPANSION[Concept]COVID
```

### HIV
```
EXPANSION[Concept]HIV OR EXPANSION[Concept]human immunodeficiency virus OR EXPANSION[Concept]AIDS OR EXPANSION[Concept]acquired immunodeficiency syndrome
```

### Hepatitis
```
EXPANSION[Concept]hepatitis OR EXPANSION[Concept]liver inflammation OR EXPANSION[Concept]viral hepatitis
```

## Gastrointestinal Conditions

### Inflammatory Bowel Disease
```
EXPANSION[Concept]inflammatory bowel disease OR EXPANSION[Concept]IBD OR EXPANSION[Concept]Crohn's disease OR EXPANSION[Concept]ulcerative colitis
```

### Gastroesophageal Reflux Disease
```
EXPANSION[Concept]GERD OR EXPANSION[Concept]gastroesophageal reflux OR EXPANSION[Concept]acid reflux OR EXPANSION[Concept]heartburn
```

### Irritable Bowel Syndrome
```
EXPANSION[Concept]irritable bowel syndrome OR EXPANSION[Concept]IBS OR EXPANSION[Concept]spastic colon
```

## Rheumatologic Conditions

### Rheumatoid Arthritis
```
EXPANSION[Concept]rheumatoid arthritis OR EXPANSION[Concept]RA OR EXPANSION[Concept]inflammatory arthritis OR EXPANSION[Concept]autoimmune arthritis
```

### Osteoarthritis
```
EXPANSION[Concept]osteoarthritis OR EXPANSION[Concept]degenerative arthritis OR EXPANSION[Concept]wear and tear arthritis
```

### Lupus
```
EXPANSION[Concept]lupus OR EXPANSION[Concept]systemic lupus erythematosus OR EXPANSION[Concept]SLE OR EXPANSION[Concept]autoimmune disease
```

## Mental Health Conditions

### Depression
```
EXPANSION[Concept]depression OR EXPANSION[Concept]major depressive disorder OR EXPANSION[Concept]MDD OR EXPANSION[Concept]depressive disorder
```

### Anxiety
```
EXPANSION[Concept]anxiety OR EXPANSION[Concept]anxiety disorder OR EXPANSION[Concept]generalized anxiety disorder OR EXPANSION[Concept]GAD
```

### Bipolar Disorder
```
EXPANSION[Concept]bipolar disorder OR EXPANSION[Concept]manic depression OR EXPANSION[Concept]bipolar affective disorder
```

### Schizophrenia
```
EXPANSION[Concept]schizophrenia OR EXPANSION[Concept]schizophrenic disorder OR EXPANSION[Concept]psychotic disorder
```

## Complex Searches with Filters

### Diabetes with Cardiovascular Disease
```
(EXPANSION[Concept]diabetes OR EXPANSION[Concept]diabetes mellitus) AND (EXPANSION[Concept]cardiovascular disease OR EXPANSION[Concept]heart disease)
```

### Elderly Patients with Dementia
```
(EXPANSION[Concept]dementia OR EXPANSION[Concept]Alzheimer OR EXPANSION[Concept]cognitive impairment) AND AREA[StdAge]OLDER_ADULT
```

### Pediatric Asthma Studies
```
(EXPANSION[Concept]asthma OR EXPANSION[Concept]bronchial asthma) AND AREA[StdAge]CHILD
```

### Recruiting Interventional Studies
```
EXPANSION[Concept]heart failure AND AREA[StudyType]INTERVENTIONAL AND AREA[OverallStatus]RECRUITING
```

### Phase 3 Diabetes Drug Studies
```
(EXPANSION[Concept]diabetes OR EXPANSION[Concept]diabetes mellitus) AND AREA[Phase]PHASE3 AND AREA[InterventionType]DRUG
```

### Cancer Prevention Studies
```
(EXPANSION[Concept]cancer OR EXPANSION[Concept]neoplasm) AND AREA[DesignPrimaryPurpose]PREVENTION
```

## Location-Based Searches

### Studies in California
```
EXPANSION[Concept]breast cancer AND SEARCH[Location](AREA[LocationState]California)
```

### Studies in Major US Cities
```
EXPANSION[Concept]diabetes AND SEARCH[Location](AREA[LocationCountry]United States AND (AREA[LocationCity]New York OR AREA[LocationCity]Los Angeles OR AREA[LocationCity]Chicago))
```

### International Studies
```
EXPANSION[Concept]HIV AND SEARCH[Location](AREA[LocationCountry]United States OR AREA[LocationCountry]Canada OR AREA[LocationCountry]United Kingdom)
```

## Age-Specific Searches

### Adult Studies Only
```
EXPANSION[Concept]hypertension AND AREA[StdAge]ADULT
```

### Pediatric Studies
```
EXPANSION[Concept]asthma AND AREA[StdAge]CHILD
```

### Geriatric Studies
```
EXPANSION[Concept]dementia AND AREA[StdAge]OLDER_ADULT
```

## Intervention-Specific Searches

### Drug Studies
```
EXPANSION[Concept]diabetes AND AREA[InterventionType]DRUG
```

### Behavioral Interventions
```
EXPANSION[Concept]depression AND AREA[InterventionType]BEHAVIORAL
```

### Device Studies
```
EXPANSION[Concept]heart failure AND AREA[InterventionType]DEVICE
```

### Surgical Procedures
```
EXPANSION[Concept]cancer AND AREA[InterventionType]PROCEDURE
```

## Advanced Examples

### Complex Multi-Condition Search
```
(EXPANSION[Concept]diabetes OR EXPANSION[Concept]diabetes mellitus) AND (EXPANSION[Concept]hypertension OR EXPANSION[Concept]high blood pressure) AND AREA[StudyType]INTERVENTIONAL AND AREA[OverallStatus]RECRUITING
```

### Dose-Finding Studies
```
EXPANSION[Concept]cancer AND ("dose escalation" OR "dose finding" OR "maximum tolerated dose" OR "MTD") AND AREA[Phase]PHASE1
```

### Quality of Life Studies
```
EXPANSION[Concept]cancer AND (EXPANSION[Concept]quality of life OR EXPANSION[Concept]QOL OR "patient reported outcomes")
```

## Tips for Common Searches

1. **Always use EXPANSION[Concept]** for medical terms
2. **Include abbreviations** and alternate spellings
3. **Use OR operators** to combine synonyms
4. **Add anatomical sites** when relevant
5. **Consider related conditions** that might co-occur
6. **Use filters** to narrow results appropriately
7. **Test different term combinations** for best results
8. **Use parentheses** to group related concepts