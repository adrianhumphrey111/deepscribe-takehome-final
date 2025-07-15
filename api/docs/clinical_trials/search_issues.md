# Clinical Trial Search Issues and Solutions

## Common Search Problems

### 1. Overly Restrictive AND Logic
**Problem**: Using AND logic between conditions results in searches for trials that study ALL conditions together, which is rare.

**Example**: `(diabetes) AND (hypothyroidism)` finds only trials studying both conditions simultaneously.

**Solution**: Use OR logic for related conditions or search primary diagnosis only.

### 2. Geographic Filtering vs Ranking
**Problem**: Geographic filtering with `filter.geo` excludes all trials outside the radius, missing potentially relevant studies.

**Solution**: Remove geographic filtering from API query. Instead, use location as a ranking factor in post-processing.

### 3. Condition Extraction Accuracy
**Problem**: LLM may extract secondary conditions or infer conditions not explicitly mentioned.

**Example**: Patient with Huntington's disease might have search generated for unrelated conditions.

**Solution**: Focus on primary diagnosis and validate extracted conditions against transcript.

## Search Strategy Recommendations

### Primary Diagnosis Focus
- Search for primary diagnosis first
- Add related conditions with OR logic only if explicitly mentioned
- Avoid inferring conditions not clearly stated

### Location Handling
- Include all geographic locations in initial search
- Rank results by distance from patient location
- Consider telehealth/remote trial options

### Condition Combination Logic
```
GOOD: EXPANSION[Concept]huntington disease
GOOD: EXPANSION[Concept]breast cancer OR EXPANSION[Concept]ductal carcinoma
BAD:  (diabetes) AND (hypothyroidism)
```

### Debugging Steps
1. Check patient data extraction accuracy
2. Verify primary vs secondary conditions
3. Test search without geographic filters
4. Validate RAG-generated queries against patient profile