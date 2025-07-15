# System Architecture: Clinical Trials Matcher

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js 13)                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ TranscriptInput │  │ TrialResults    │  │ TrialQASystem   │  │
│  │ Component       │  │ Dashboard       │  │ (Innovation)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ ExtractionReview│  │ TrialComparison │  │ ErrorHandling   │  │
│  │ Component       │  │ View            │  │ Components      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP/REST API
                                │
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (Flask/Python)                     │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Smart LLM       │  │ Patient Data    │  │ Trial Q&A       │  │
│  │ Router          │  │ Extractor       │  │ Engine          │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Clinical Trials │  │ Trial Ranking   │  │ Error Recovery  │  │
│  │ API Client      │  │ Algorithm       │  │ Manager         │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                │ External API Calls
                                │
┌─────────────────────────────────────────────────────────────────┐
│                     External Services                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ OpenAI GPT-4    │  │ Claude 3.5      │  │ ClinicalTrials  │  │
│  │ API             │  │ Sonnet API      │  │ .gov API        │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow Architecture

```
User Input (Transcript)
         │
         ▼
┌─────────────────────┐
│ Smart LLM Router    │ ◄─── Transcript length analysis
│ Decision Engine     │ ◄─── Medical complexity scoring
└─────────────────────┘
         │
         ▼
┌─────────────────────┐      ┌─────────────────────┐
│ Primary LLM         │      │ Fallback LLM        │
│ (Claude/OpenAI)     │ ───► │ (OpenAI/Claude)     │
└─────────────────────┘      └─────────────────────┘
         │                            │
         ▼                            ▼
┌─────────────────────┐      ┌─────────────────────┐
│ Extracted Patient   │      │ Manual Entry Form   │
│ Data + Confidence   │      │ (if both fail)      │
└─────────────────────┘      └─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Clinical Trials     │
│ API Query Builder   │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Trial Ranking       │
│ Algorithm           │
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│ Ranked Results      │
│ + Q&A Interface     │
└─────────────────────┘
```

## API Structure

### Frontend Routes (Next.js)
```
/                    - Main application page
/api/extract         - Patient data extraction endpoint
/api/trials/search   - Trial search endpoint
/api/trials/[id]     - Individual trial details
/api/trials/qa       - Trial Q&A endpoint
/api/health          - Health check endpoint
```

### Backend Endpoints (Flask)

#### 1. Patient Data Extraction
```python
POST /api/extract
Request:
{
    "transcript": "Doctor: How are you feeling today? Patient: I've been having chest pain..."
}

Response:
{
    "success": true,
    "patient_data": {
        "age": 45,
        "gender": "MALE",
        "conditions": ["chest pain", "hypertension"],
        "primary_diagnosis": "unstable angina",
        "medications": ["lisinopril", "aspirin"],
        "location": {
            "city": "San Francisco",
            "state": "CA",
            "zip": "94102"
        }
    },
    "confidence_scores": {
        "age": 0.9,
        "gender": 0.95,
        "primary_diagnosis": 0.85,
        "medications": 0.8
    },
    "provider_used": "claude",
    "extraction_time_ms": 1250
}
```

#### 2. Clinical Trials Search
```python
POST /api/trials/search
Request:
{
    "patient_data": {
        "age": 45,
        "gender": "MALE",
        "conditions": ["chest pain", "hypertension"],
        "primary_diagnosis": "unstable angina",
        "location": {
            "city": "San Francisco",
            "state": "CA"
        }
    },
    "max_results": 10
}

Response:
{
    "success": true,
    "trials": [
        {
            "nct_id": "NCT12345678",
            "title": "Phase III Trial of New Cardiac Medication",
            "status": "RECRUITING",
            "phase": "Phase 3",
            "brief_summary": "This study evaluates...",
            "location": {
                "city": "San Francisco",
                "state": "CA",
                "facility": "UCSF Medical Center"
            },
            "distance_miles": 2.3,
            "match_score": 0.92,
            "eligibility_criteria": {
                "age_min": 18,
                "age_max": 65,
                "gender": "ALL",
                "healthy_volunteers": false
            },
            "contact_info": {
                "name": "Dr. Smith",
                "phone": "(555) 123-4567",
                "email": "smith@ucsf.edu"
            }
        }
    ],
    "total_found": 45,
    "search_metadata": {
        "query_used": "unstable angina",
        "filters_applied": ["age", "location", "status"],
        "search_time_ms": 890
    }
}
```

#### 3. Trial Q&A System
```python
POST /api/trials/qa
Request:
{
    "trial_id": "NCT12345678",
    "question": "What are the potential side effects of this treatment?",
    "patient_context": {
        "age": 45,
        "current_medications": ["lisinopril", "aspirin"],
        "conditions": ["hypertension"]
    }
}

Response:
{
    "success": true,
    "answer": "Based on the trial protocol, the most common side effects include headache (15% of patients), nausea (8%), and fatigue (12%). Given your current medications, there are no significant drug interactions expected.",
    "confidence": 0.88,
    "sources": [
        "Trial Protocol Section 4.2.3",
        "Investigator Brochure p. 45",
        "Previous Phase II results"
    ],
    "response_time_ms": 2100
}
```

#### 4. Individual Trial Details
```python
GET /api/trials/NCT12345678
Response:
{
    "success": true,
    "trial": {
        "nct_id": "NCT12345678",
        "title": "Phase III Trial of New Cardiac Medication",
        "detailed_description": "This is a randomized, double-blind...",
        "study_design": "Interventional",
        "primary_outcome": "Change in ejection fraction at 6 months",
        "secondary_outcomes": ["Quality of life scores", "Hospitalization rates"],
        "enrollment_target": 500,
        "estimated_completion": "2025-12-31",
        "sponsor": "Acme Pharmaceuticals",
        "locations": [...],
        "eligibility": {...},
        "contact_info": {...}
    }
}
```

## Component Architecture

### Frontend Components Structure
```
components/
├── ui/                     # shadcn/ui components
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   └── ...
├── transcript/
│   ├── TranscriptInput.tsx
│   ├── ExtractionReview.tsx
│   └── ProcessingStatus.tsx
├── trials/
│   ├── TrialCard.tsx
│   ├── TrialsList.tsx
│   ├── TrialDetails.tsx
│   ├── TrialComparison.tsx
│   └── TrialQAInterface.tsx
├── common/
│   ├── ErrorBoundary.tsx
│   ├── LoadingSpinner.tsx
│   └── ConfidenceIndicator.tsx
└── layout/
    ├── Header.tsx
    ├── Navigation.tsx
    └── Footer.tsx
```

### Backend Service Architecture
```python
api/
├── __init__.py
├── main.py                 # Flask app setup
├── routes/
│   ├── __init__.py
│   ├── extraction.py      # Patient data extraction
│   ├── trials.py          # Trial search and details
│   └── qa.py             # Q&A system
├── services/
│   ├── __init__.py
│   ├── llm_router.py     # Smart LLM selection
│   ├── patient_extractor.py
│   ├── trials_client.py  # ClinicalTrials.gov API
│   ├── ranking_engine.py # Trial ranking algorithm
│   └── qa_engine.py      # Q&A system
├── models/
│   ├── __init__.py
│   ├── patient_data.py   # Data models
│   ├── trial_data.py
│   └── qa_models.py
└── utils/
    ├── __init__.py
    ├── error_handler.py
    ├── validators.py
    └── security.py
```

## Error Handling Architecture

```python
class ErrorRecoveryManager:
    async def handle_extraction_error(self, error: Exception, transcript: str):
        """Cascading error recovery for LLM extraction"""
        
        # 1. Try alternate LLM provider
        try:
            alternate_provider = self.get_alternate_provider()
            return await alternate_provider.extract_patient_data(transcript)
        except Exception as e2:
            # 2. Return partial extraction for manual completion
            return self.create_manual_entry_template(transcript, [error, e2])
    
    async def handle_api_error(self, error: Exception, request_data: dict):
        """Handle ClinicalTrials.gov API failures"""
        
        # 1. Retry with exponential backoff
        for attempt in range(3):
            try:
                await asyncio.sleep(2 ** attempt)
                return await self.retry_api_call(request_data)
            except Exception:
                continue
        
        # 2. Return cached results if available
        cached_results = await self.get_cached_results(request_data)
        if cached_results:
            return cached_results
        
        # 3. Show degraded experience
        return self.create_error_response(error, "API temporarily unavailable")
```

## Security Architecture

```python
class SecurityManager:
    def __init__(self):
        self.phi_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
            # Additional PHI patterns
        ]
    
    def sanitize_transcript(self, transcript: str) -> str:
        """Remove/mask PHI before LLM processing"""
        sanitized = transcript
        for pattern in self.phi_patterns:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        return sanitized
    
    def ensure_hipaa_compliance(self, api_endpoint: str) -> bool:
        """Verify HIPAA-compliant API endpoints"""
        hipaa_endpoints = {
            'openai': 'https://api.openai.com/v1/chat/completions',
            'claude': 'https://api.anthropic.com/v1/messages'
        }
        return api_endpoint in hipaa_endpoints.values()
```

## Performance Architecture

### Caching Strategy
```python
class CacheManager:
    def __init__(self):
        self.extraction_cache = {}  # LRU cache for extractions
        self.trial_cache = {}       # Time-based cache for trials
        self.qa_cache = {}          # Session-based Q&A cache
    
    async def get_cached_extraction(self, transcript_hash: str):
        """Cache extraction results for similar transcripts"""
        return self.extraction_cache.get(transcript_hash)
    
    async def cache_trial_results(self, query_hash: str, results: list):
        """Cache trial search results for 1 hour"""
        self.trial_cache[query_hash] = {
            'results': results,
            'timestamp': time.time(),
            'ttl': 3600
        }
```

### Concurrent Processing
```python
async def process_transcript_parallel(transcript: str):
    """Process extraction and trial search concurrently"""
    
    # Start extraction
    extraction_task = asyncio.create_task(
        extract_patient_data(transcript)
    )
    
    # Wait for extraction to complete
    patient_data = await extraction_task
    
    # Start trial search while preparing UI
    trial_search_task = asyncio.create_task(
        search_clinical_trials(patient_data)
    )
    
    # Return results as they become available
    return await trial_search_task
```

This architecture provides a robust, scalable foundation for the clinical trials matching system with emphasis on reliability, security, and user experience.