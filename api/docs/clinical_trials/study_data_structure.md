# ClinicalTrials.gov Study Data Structure

This document shows the available study data fields and their data types for search and retrieval.

## Key Information

- **Piece Name** and **Alt Piece Names** are unique identifiers for fields
- Fields marked with **⤷** start nested documents (use SEARCH operator)
- Fields marked with **✗** are available for search but not for retrieval
- Fields marked with **✓** produce synonyms

## Protocol Section

### Identification Module

| Field | Description | Type | Alt Names |
|-------|-------------|------|-----------|
| NCTId | National Clinical Trial ID | text | NCT-ID |
| BriefTitle | Brief Title | text | BRIEF-TITLE |
| OfficialTitle | Official Title | text | OFFICIAL-TITLE |
| Acronym | Acronym | text | ACRONYM |
| OrgStudyId | Organization's Unique Protocol ID | text | ORGANIZATION-STUDY-ID |
| SecondaryId | Secondary ID | text | SECONDARY-ID |

### Status Module

| Field | Description | Type | Alt Names |
|-------|-------------|------|-----------|
| OverallStatus | Overall Recruitment Status | enum Status | OVERALL-STATUS |
| StartDate | Study Start Date | PartialDate | START-DATE |
| PrimaryCompletionDate | Primary Completion Date | PartialDate | COMPLETION-DATE-PRIMARY |
| CompletionDate | Study Completion Date | PartialDate | COMPLETION-DATE |
| StudyFirstPostDate | Study First Posted Date | NormalizedDate | STUDY-FIRST-POSTED |
| LastUpdatePostDate | Last Update Posted Date | NormalizedDate | LAST-UPDATE-POSTED |

### Conditions Module

| Field | Description | Type | Alt Names |
|-------|-------------|------|-----------|
| Condition | Primary Disease/Condition | text[] | CONDITIONS |
| Keyword | Keywords | text[] | KEYWORDS |

### Design Module

| Field | Description | Type | Alt Names |
|-------|-------------|------|-----------|
| StudyType | Study Type | enum StudyType | STUDY-TYPE, STUDY-TYPES |
| Phase | Study Phase | enum Phase[] | PHASE |
| DesignAllocation | Design Allocation | enum DesignAllocation | DESIGN-ALLOCATION |
| DesignInterventionModel | Interventional Study Model | enum InterventionalAssignment | DESIGN-INTERVENTION-MODEL |
| DesignPrimaryPurpose | Design Primary Purpose | enum PrimaryPurpose | DESIGN-PRIMARY-PURPOSE |
| DesignObservationalModel | Observational Study Model | enum ObservationalModel | DESIGN-OBSERVATIONAL-MODEL |
| DesignTimePerspective | Time Perspective | enum DesignTimePerspective | DESIGN-TIME-PERSPECTIVE |
| DesignMasking | Design Masking | enum DesignMasking | DESIGN-MASKING |
| EnrollmentCount | Enrollment | integer | ENROLLMENT |

### Arms/Interventions Module

| Field | Description | Type | Alt Names |
|-------|-------------|------|-----------|
| ArmGroupLabel | Arm Group Label | text | ARM-GROUP-LABEL |
| ArmGroupType | Arm Group Type | enum ArmGroupType | ARM-GROUP-TYPE |
| ArmGroupDescription | Arm Description | markup | ARM-GROUP-DESCRIPTION |
| InterventionType | Intervention Type | enum InterventionType | INTERVENTION-TYPE |
| InterventionName | Intervention Name | text | INTERVENTION, INTERVENTIONS |
| InterventionDescription | Intervention Description | markup | INTERVENTION-DESCRIPTION |
| InterventionOtherName | Other Intervention Name | text[] | INTERVENTION-OTHER-NAME |

### Outcomes Module

| Field | Description | Type | Alt Names |
|-------|-------------|------|-----------|
| PrimaryOutcomeMeasure | Primary Outcome Title | text | PRIMARY-OUTCOME-MEASURE |
| PrimaryOutcomeDescription | Primary Outcome Description | markup | - |
| PrimaryOutcomeTimeFrame | Primary Outcome Time Frame | text | - |
| SecondaryOutcomeMeasure | Secondary Outcome Title | text | SECONDARY-OUTCOME-MEASURE |
| SecondaryOutcomeDescription | Secondary Outcome Description | markup | - |
| SecondaryOutcomeTimeFrame | Secondary Outcome Time Frame | text | - |
| OtherOutcomeMeasure | Other Outcome Title | text | - |

### Eligibility Module

| Field | Description | Type | Alt Names |
|-------|-------------|------|-----------|
| EligibilityCriteria | Inclusion/Exclusion Criteria | markup | - |
| HealthyVolunteers | Accepts Healthy Volunteers | boolean | HEALTHY-VOLUNTEERS |
| Sex | Sex/Gender | enum Sex | GENDER |
| MinimumAge | Minimum Age | NormalizedTime | MINIMUM-AGE |
| MaximumAge | Maximum Age | NormalizedTime | MAXIMUM-AGE |
| StdAge | Age Group | enum StandardAge[] | AGE-GROUP |
| StudyPopulation | Study Population Description | markup | - |

### Contacts/Locations Module

| Field | Description | Type | Alt Names |
|-------|-------------|------|-----------|
| CentralContactName | Central Contact Name | text | - |
| CentralContactPhone | Central Contact Phone | text | - |
| CentralContactEMail | Central Contact Email | text | - |
| LocationFacility | Facility Name | text | LOCATION-NAME, FACILITY |
| LocationStatus | Individual Site Status | enum RecruitmentStatus | LOCATION-STATUS |
| LocationCity | City | text | LOCATION-CITY, CITY |
| LocationState | State | text | LOCATION-STATE, STATE |
| LocationCountry | Country | text | LOCATION-COUNTRY, COUNTRY |
| LocationContactName | Location Contact Name | text | - |

### Sponsor/Collaborators Module

| Field | Description | Type | Alt Names |
|-------|-------------|------|-----------|
| LeadSponsorName | Lead Sponsor Name | text | SPONSOR, LEAD-SPONSOR |
| LeadSponsorClass | Lead Sponsor Type | enum AgencyClass | LEAD-SPONSOR-CLASS |
| CollaboratorName | Collaborator Name | text | COLLABORATOR |
| CollaboratorClass | Collaborator Type | enum AgencyClass | COLLABORATOR-CLASS |
| ResponsiblePartyInvestigatorFullName | Responsible Party Investigator Name | text | - |
| ResponsiblePartyInvestigatorTitle | Responsible Party Investigator Title | text | - |
| ResponsiblePartyInvestigatorAffiliation | Responsible Party Investigator Affiliation | text | - |

### Description Module

| Field | Description | Type | Alt Names |
|-------|-------------|------|-----------|
| BriefSummary | Brief Summary | markup | - |
| DetailedDescription | Detailed Description | markup | - |

## Enumeration Types

### Status Values
- ACTIVE_NOT_RECRUITING
- COMPLETED
- ENROLLING_BY_INVITATION
- NOT_YET_RECRUITING
- RECRUITING
- SUSPENDED
- TERMINATED
- WITHDRAWN
- UNKNOWN

### StudyType Values
- EXPANDED_ACCESS
- INTERVENTIONAL
- OBSERVATIONAL

### Phase Values
- NA (Not Applicable)
- EARLY_PHASE1
- PHASE1
- PHASE2
- PHASE3
- PHASE4

### Sex Values
- FEMALE
- MALE
- ALL

### StandardAge Values
- CHILD
- ADULT
- OLDER_ADULT

### InterventionType Values
- BEHAVIORAL
- BIOLOGICAL
- COMBINATION_PRODUCT
- DEVICE
- DIAGNOSTIC_TEST
- DIETARY_SUPPLEMENT
- DRUG
- GENETIC
- PROCEDURE
- RADIATION
- OTHER

### ArmGroupType Values
- EXPERIMENTAL
- ACTIVE_COMPARATOR
- PLACEBO_COMPARATOR
- SHAM_COMPARATOR
- NO_INTERVENTION
- OTHER

### RecruitmentStatus Values
- ACTIVE_NOT_RECRUITING
- COMPLETED
- ENROLLING_BY_INVITATION
- NOT_YET_RECRUITING
- RECRUITING
- SUSPENDED
- TERMINATED
- WITHDRAWN

### AgencyClass Values
- NIH
- FED
- OTHER_GOV
- INDIV
- INDUSTRY
- NETWORK
- OTHER
- UNKNOWN

### PrimaryPurpose Values
- TREATMENT
- PREVENTION
- DIAGNOSTIC
- SUPPORTIVE_CARE
- SCREENING
- HEALTH_SERVICES_RESEARCH
- BASIC_SCIENCE
- DEVICE_FEASIBILITY
- OTHER

### DesignAllocation Values
- RANDOMIZED
- NON_RANDOMIZED
- NA

### InterventionalAssignment Values
- SINGLE_GROUP
- PARALLEL
- CROSSOVER
- FACTORIAL
- SEQUENTIAL

### ObservationalModel Values
- COHORT
- CASE_CONTROL
- CASE_ONLY
- CASE_CROSSOVER
- ECOLOGIC_OR_COMMUNITY
- FAMILY_BASED
- DEFINED_POPULATION
- NATURAL_HISTORY
- OTHER

### DesignTimePerspective Values
- RETROSPECTIVE
- PROSPECTIVE
- CROSS_SECTIONAL
- OTHER

### DesignMasking Values
- NONE
- SINGLE
- DOUBLE
- TRIPLE
- QUADRUPLE

## Derived Section

### Condition Browse Module

| Field | Description | Type |
|-------|-------------|------|
| ConditionMeshTerm | Condition MeSH Term | text |
| ConditionAncestorTerm | Condition Ancestor MeSH Term | text |
| ConditionBrowseLeafName | Condition Leaf Topic Name | text |
| ConditionBrowseBranchName | Condition Branch Topic Name | text |

### Intervention Browse Module

| Field | Description | Type |
|-------|-------------|------|
| InterventionMeshTerm | Intervention MeSH Term | text |
| InterventionAncestorTerm | Intervention Ancestor MeSH Term | text |
| InterventionBrowseLeafName | Intervention Leaf Topic Name | text |
| InterventionBrowseBranchName | Intervention Branch Topic Name | text |

## Search Usage Examples

### Basic Field Search
```
AREA[Condition]breast cancer
AREA[InterventionName]chemotherapy
AREA[LocationCity]Boston
```

### Nested Document Search
```
SEARCH[Location](AREA[LocationCity]Portland AND AREA[LocationState]Maine)
```

### Enumeration Search
```
AREA[Phase]PHASE3
AREA[OverallStatus]RECRUITING
AREA[StudyType]INTERVENTIONAL
```

### MeSH Term Search
```
AREA[ConditionMeshTerm]breast neoplasms
AREA[InterventionMeshTerm]antineoplastic agents
```

## Best Practices

1. **Use appropriate field names** from the Alt Piece Names when available
2. **Use SEARCH operator** for nested documents (marked with ⤷)
3. **Use exact enum values** for enumeration fields
4. **Use MeSH terms** for medical concept searches
5. **Combine related fields** for comprehensive searches
6. **Consider field weights** in search areas for relevance ranking