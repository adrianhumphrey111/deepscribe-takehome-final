# ClinicalTrials.gov Search Areas

Search areas describe the parts of a study record that are searched for content. They consist of groups of weighted study fields that can be searched together.

## Available Search Areas

### BasicSearch Area
**Request parameter:** `query.term`  
**Description:** Default search area for queries entered in "Other terms" field  
**Weight range:** 0.1 - 1.0  
**Contains 57 data fields including:**
- NCTId (1.0)
- Acronym (1.0)
- BriefTitle (0.89)
- OfficialTitle (0.85)
- Condition (0.81)
- InterventionName (0.8)
- InterventionOtherName (0.75)
- Phase (0.65)
- Keywords (0.6)
- BriefSummary (0.6)

### ConditionSearch Area
**Request parameter:** `query.cond`  
**Description:** Default search area for "Conditions or disease" field  
**Contains 7 data fields:**
- Condition (0.95)
- BriefTitle (0.6)
- OfficialTitle (0.55)
- ConditionMeshTerm (0.5)
- ConditionAncestorTerm (0.4)
- Keyword (0.3)
- NCTId (0.2)

### InterventionSearch Area
**Request parameter:** `query.intr`  
**Description:** Default search area for "Intervention / treatment" field  
**Contains 12 data fields:**
- InterventionName (0.95)
- InterventionType (0.85)
- ArmGroupType (0.85)
- InterventionOtherName (0.75)
- BriefTitle (0.65)
- OfficialTitle (0.6)
- InterventionMeshTerm (0.5)
- InterventionAncestorTerm (0.4)

### LocationSearch Area
**Request parameter:** `query.locn`  
**Description:** Default search area for "Location terms" field  
**Contains 5 data fields:**
- LocationCity (0.95)
- LocationState (0.95)
- LocationCountry (0.95)
- LocationFacility (0.95)
- LocationZip (0.35)

### OutcomeSearch Area
**Request parameter:** `query.outc`  
**Description:** Default search area for "Outcome measure" field  
**Contains 9 data fields:**
- PrimaryOutcomeMeasure (0.9)
- SecondaryOutcomeMeasure (0.8)
- PrimaryOutcomeDescription (0.6)
- SecondaryOutcomeDescription (0.5)
- OtherOutcomeMeasure (0.4)
- OutcomeMeasureTitle (0.4)

### TitleSearch Area
**Request parameter:** `query.titles`  
**Description:** Default search area for "Title / acronym" field  
**Contains 3 data fields:**
- Acronym (0.99)
- BriefTitle (0.95)
- OfficialTitle (0.8)

### SponsorSearch Area
**Request parameter:** `query.spons`  
**Description:** Default search area for "Sponsor / collaborator" field  
**Contains 3 data fields:**
- LeadSponsorName (0.99)
- CollaboratorName (0.9)
- OrgFullName (0.6)

### EligibilitySearch Area
**Contains 2 data fields:**
- EligibilityCriteria (0.95)
- StudyPopulation (0.8)

### ContactSearch Area
**Contains 4 data fields:**
- OverallOfficialName (0.95)
- CentralContactName (0.9)
- OverallOfficialAffiliation (0.85)
- LocationContactName (0.8)

### IdSearch Area
**Request parameter:** `query.id`  
**Description:** Default search area for "Study IDs" field  
**Contains 5 data fields:**
- NCTId (0.99)
- NCTIdAlias (0.9)
- Acronym (0.85)
- OrgStudyId (0.8)
- SecondaryId (0.75)

### PatientSearch Area
**Request parameter:** `query.patient`  
**Description:** Comprehensive search area for patient-focused searches  
**Contains 47 data fields including:**
- Acronym (1.0)
- Condition (0.95)
- BriefTitle (0.9)
- OfficialTitle (0.85)
- ConditionMeshTerm (0.8)
- ConditionAncestorTerm (0.7)
- BriefSummary (0.65)
- InterventionName (0.6)
- PrimaryOutcomeMeasure (0.6)
- StdAge (0.6)

## Additional Search Areas

### InterventionNameSearch Area
- InterventionName (0.99)
- InterventionOtherName (0.9)

### OutcomeNameSearch Area
- PrimaryOutcomeMeasure (0.98)
- SecondaryOutcomeMeasure (0.8)
- OtherOutcomeMeasure (0.5)
- OutcomeMeasureTitle (0.3)

### ExternalIdsSearch Area
- OrgStudyId (0.9)
- SecondaryId (0.7)

### FunderTypeSearch Area
- LeadSponsorClass (0.99)
- CollaboratorClass (0.9)

### ResponsiblePartySearch Area
- ResponsiblePartyInvestigatorFullName (0.9)
- ResponsiblePartyOldNameTitle (0.8)
- ResponsiblePartyInvestigatorAffiliation (0.8)

### NCTIdSearch Area
- NCTId (0.99)
- NCTIdAlias (0.9)

## Usage Guidelines

### For Medical Conditions
Use **ConditionSearch** area with EXPANSION[Concept]:
```
AREA[Condition]EXPANSION[Concept]breast cancer
```

### For Interventions/Treatments
Use **InterventionSearch** area:
```
AREA[InterventionName]EXPANSION[Concept]chemotherapy
```

### For Geographic Searches
Use **LocationSearch** area with SEARCH operator:
```
SEARCH[Location](AREA[LocationCity]Boston AND AREA[LocationState]Massachusetts)
```

### For Comprehensive Patient Searches
Use **PatientSearch** area for broad patient-focused queries:
```
AREA[PatientSearch]EXPANSION[Concept]diabetes
```

## Field Weights

Higher weights indicate more relevant fields:
- **1.0**: Most relevant (NCTId, Acronym)
- **0.9-0.99**: Highly relevant (primary fields)
- **0.8-0.89**: Very relevant (key descriptive fields)
- **0.6-0.79**: Relevant (secondary descriptive fields)
- **0.3-0.59**: Moderately relevant (supporting fields)
- **0.1-0.29**: Less relevant (peripheral fields)

## Best Practices

1. **Choose appropriate search areas** based on your query type
2. **Use ConditionSearch** for disease/condition queries
3. **Use InterventionSearch** for treatment/drug queries
4. **Use LocationSearch** for geographic constraints
5. **Use PatientSearch** for comprehensive patient-focused searches
6. **Combine multiple areas** for complex queries
7. **Consider field weights** when prioritizing search terms