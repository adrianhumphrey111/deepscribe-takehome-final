# ClinicalTrials.gov Search Operators

This document explains the search operators, terms, syntax, and expressions for advanced search of study record data on ClinicalTrials.gov.

## Operator Precedence

From highest to lowest precedence:
1. Search terms and source operators
2. NOT operator and context operators
3. AND operator
4. OR operator

## Boolean Operators

Boolean operators connect search terms and define their logical relationship.

| Operator | Example | Description |
|----------|---------|-------------|
| OR | `youth OR teen` | Binary operator - retrieves studies containing either left or right subexpression, or both |
| AND | `heart AND attack` | Binary operator - retrieves studies containing both left and right subexpressions |
| NOT | `bethesda NOT maryland` | Unary operator - retrieves studies that do NOT contain the right subexpression |

## Grouping Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `" "` | `"back pain"` | Forces a sequence of words to be treated as a phrase |
| `()` | `(acetaminophen OR aspirin) AND NOT (heart failure OR heart attack)` | Used to increase operator precedence |

## Context Operators

Context operators control how search terms are evaluated and are followed by parameters in square brackets.

### COVERAGE Operator

Declares the degree to which a search term needs to match the text in an API field.

| Parameter | Description |
|-----------|-------------|
| `FullMatch` | Search term must match all of the text in the field |
| `StartsWith` | Search term must match the beginning of the text |
| `EndsWith` | Search term must match the end of the text |
| `Contains` | Search term must match part of the text (DEFAULT) |

**Example:** `COVERAGE[FullMatch]pain`

### EXPANSION Operator

Declares the degree to which a search term may be expanded.

| Parameter | Description |
|-----------|-------------|
| `None` | Search exactly as is (case and accent marks significant) |
| `Term` | Includes lexical variants (plurals, possessives, alternate spellings, compound words) |
| `Concept` | Includes synonyms based on UMLS (Unified Medical Language System) |
| `Relaxation` | Relaxes adjacency requirements for partial term matches (DEFAULT) |
| `Lossy` | Allows for missing partial terms |

**Example:** `EXPANSION[Concept]breast cancer`

### AREA Operator

Declares which search area should be searched.

**Example:** `AREA[InterventionName]aspirin`

### SEARCH Operator

Restricts search expressions to fields within a data element so multiple pieces can be found together.

**Example:** `SEARCH[Location](AREA[LocationCity]Portland AND AREA[LocationState]Maine)`

## Source Operators

Find studies similar to search terms.

| Operator | Example | Description |
|----------|---------|-------------|
| `MISSING` | `AREA[ResultsFirstPostDate]MISSING` | Finds studies with no values in the specified search area |
| `RANGE` | `AREA[ResultsFirstPostDate]RANGE[01/01/2015, MAX]` | Finds studies with values in the specified range |
| `ALL` | `ALL` | Retrieves all study records in the database |

### RANGE Operator Values

- `MIN` - Smallest value of interest in the current search area
- `MAX` - Largest value of interest in the current search area

## Scoring Operators

Adjust the rank order of search results.

| Operator | Example | Description |
|----------|---------|-------------|
| `TILT` | `TILT[StudyFirstPostDate]"heart attack"` | Biases scoring in favor of the subexpression based on field values |

## Search Expression Structure

All search expressions are OR expressions evaluated in this order:

1. **Source expression**: Search term, range expression, OR expression in parentheses, or MISSING/ALL operator
2. **Operator expression**: Sequence of unary operators followed by source expression
3. **AND expression**: List of operator expressions separated by AND operators
4. **OR expression**: List of AND expressions separated by OR operators

## Examples

### Basic Examples
- `exhaustion`
- `"back pain"`
- `(acetaminophen OR aspirin) AND NOT (heart failure OR heart attack)`

### Medical Condition Examples
- `EXPANSION[Concept]breast cancer`
- `EXPANSION[Concept]invasive ductal carcinoma OR EXPANSION[Concept]breast neoplasm`
- `AREA[Condition]diabetes AND AREA[InterventionName]insulin`

### Location-Based Examples
- `SEARCH[Location](AREA[LocationCity]Boston AND AREA[LocationState]Massachusetts)`
- `SEARCH[Location](AREA[LocationCountry]United States AND AREA[LocationStatus]Recruiting)`

### Complex Examples
- `EXPANSION[Concept]heart disease AND SEARCH[Location](AREA[LocationCountry]United States) AND AREA[Phase]PHASE3`
- `(EXPANSION[Concept]cancer OR EXPANSION[Concept]neoplasm) AND AREA[OverallStatus]RECRUITING`

## Best Practices

1. **Use EXPANSION[Concept]** for medical terms to include synonyms from UMLS
2. **Use SEARCH[Location]** when searching for specific geographic criteria
3. **Use parentheses** to control operator precedence
4. **Use quotes** for exact phrase matching
5. **Combine multiple approaches** for comprehensive results

## Common Patterns for Medical Conditions

### Cancer Searches
```
EXPANSION[Concept]breast cancer OR EXPANSION[Concept]mammary carcinoma OR EXPANSION[Concept]breast neoplasm
```

### Neurological Conditions
```
EXPANSION[Concept]alzheimer OR EXPANSION[Concept]dementia OR EXPANSION[Concept]cognitive impairment
```

### Cardiovascular Conditions
```
EXPANSION[Concept]heart disease OR EXPANSION[Concept]cardiovascular disease OR EXPANSION[Concept]cardiac
```