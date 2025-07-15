# 🧠 DeepScribe LLM Flow Documentation

## 📊 System Overview

DeepScribe uses a sophisticated multi-stage LLM pipeline to match patients with clinical trials. The system combines **patient data extraction**, **RAG-powered query generation**, **intelligent trial search**, and **LLM-based eligibility analysis** to provide accurate trial matching.

---

## 🔄 Complete Flow Architecture

```mermaid
graph TD
    A[📝 Medical Transcript] --> B[🧹 Sanitization & PHI Removal]
    B --> C[🎯 Smart LLM Router]
    C --> D[🤖 Patient Data Extraction]
    D --> E[📋 Structured Patient Data]
    
    E --> F[🔍 RAG Query Generation]
    F --> G[🗄️ Vector Database Search]
    G --> H[📑 ClinicalTrials.gov API]
    
    H --> I[📊 Trial Results]
    I --> J[🎭 LLM Eligibility Filter]
    J --> K[📈 Ranking & Scoring]
    K --> L[✅ Matched Trials]
    
    style A fill:#e1f5fe
    style E fill:#f3e5f5
    style L fill:#e8f5e8
    style G fill:#fff3e0
```

---

## 🎯 Stage 1: Patient Data Extraction

### **Service**: `patient_extractor.py`
**🎯 Purpose**: Transform unstructured medical transcripts into structured patient data

```mermaid
flowchart LR
    A[📝 Raw Transcript] --> B[🧹 PHI Sanitization]
    B --> C[🎯 Smart Router Selection]
    C --> D{🤖 Primary LLM}
    D -->|Success| E[✅ Extraction Result]
    D -->|Failure| F[🔄 Fallback LLM]
    F --> E
    E --> G[🔧 Post-Processing]
    G --> H[📋 Structured Data]
    
    style A fill:#ffebee
    style H fill:#e8f5e8
```

### **Key Features**:
- **🛡️ PHI Protection**: Removes SSN, phone numbers, emails, ZIP codes
- **🎯 Smart Routing**: Selects optimal LLM based on transcript complexity
- **🔄 Automatic Fallback**: OpenAI ↔ Claude failover system
- **🧠 Intelligent Enhancement**: Age inference, location normalization

### **LLM Router Logic**:
```python
# Complexity scoring factors:
- Medical terminology density
- Condition complexity 
- Medication count
- Specialist mentions
- Transcript length

# Selection criteria:
- Short + Simple → OpenAI (fast, cost-effective)
- Long + Complex → Claude (better reasoning)
```

---

## 🔍 Stage 2: RAG-Powered Query Generation

### **Service**: `langchain_rag_service.py`
**🎯 Purpose**: Generate optimized ClinicalTrials.gov search queries using domain knowledge

```mermaid
flowchart TD
    A[📋 Patient Diagnosis] --> B[🔍 Vector Search]
    B --> C[📚 Knowledge Base]
    C --> D[📑 Relevant Documents]
    D --> E[🤖 LLM Query Generation]
    E --> F[⚡ Optimized API Query]
    
    G[📖 CT.gov Documentation] --> H[✂️ Text Splitting]
    H --> I[🧮 Embeddings]
    I --> J[🗄️ FAISS Vector Store]
    J --> B
    
    style C fill:#fff3e0
    style J fill:#e3f2fd
    style F fill:#e8f5e8
```

### **Vector Database Implementation**:
- **📊 Embeddings**: OpenAI `text-embedding-3-small`
- **🗄️ Storage**: FAISS in-memory vector store
- **📚 Knowledge Base**: ClinicalTrials.gov API documentation
- **✂️ Chunking**: Recursive character text splitter

### **Query Enhancement Example**:
```
Input: "acute lymphoblastic leukemia"
Output: "EXPANSION[Concept]acute lymphoblastic leukemia OR EXPANSION[Concept]ALL OR EXPANSION[Concept]acute lymphocytic leukemia"
```

---

## 🔍 Stage 3: Clinical Trials Search

### **Service**: `trials_client.py`
**🎯 Purpose**: Execute intelligent trial searches with geographic and demographic filtering

```mermaid
flowchart LR
    A[⚡ RAG Query] --> B[🌍 Geocoding]
    B --> C[🔧 Filter Building]
    C --> D[🌐 CT.gov API Call]
    D --> E[📊 Raw Results]
    E --> F[🔄 Data Transformation]
    F --> G[📋 Trial Objects]
    
    H[👤 Patient Data] --> C
    I[📍 Location Preferences] --> B
    
    style D fill:#e3f2fd
    style G fill:#e8f5e8
```

### **Search Parameters**:
- **📊 Conditions**: RAG-enhanced query with medical concept expansion
- **👤 Demographics**: Age ranges with buffer zones, gender matching
- **📍 Geography**: Geocoded locations with distance calculations
- **📈 Status**: Active trials (RECRUITING, NOT_YET_RECRUITING, ACTIVE_NOT_RECRUITING)

---

## 🎭 Stage 4: LLM Eligibility Analysis

### **Service**: `llm_eligibility_filter.py`
**🎯 Purpose**: Use AI to analyze complex eligibility criteria and rank trial fit

```mermaid
flowchart TD
    A[📋 Trial List] --> B[📦 Batch Processing]
    B --> C[🤖 LLM Analysis]
    C --> D[📊 Eligibility Scores]
    D --> E[📍 Location Scores]
    E --> F[🧮 Combined Scoring]
    F --> G[✅ Eligible Trials]
    F --> H[❌ Filtered Out]
    
    I[👤 Patient Profile] --> C
    J[📍 Trial Locations] --> E
    
    style C fill:#f3e5f5
    style G fill:#e8f5e8
    style H fill:#ffebee
```

### **Scoring Algorithm**:
```python
combined_score = (eligibility_score × 0.7) + (location_score × 0.3)

# Eligibility factors analyzed:
- Age requirements vs patient age
- Medical condition match
- Required lab values
- Exclusion criteria
- Treatment history
- Comorbidities

# Location factors:
- Geographic distance
- Travel accessibility
- Multi-site availability
```

### **LLM Analysis Process**:
1. **📋 Batch Processing**: Groups trials for efficient analysis (5 trials per batch)
2. **🎯 Structured Prompts**: JSON-formatted eligibility questions
3. **🧠 Reasoning Generation**: Human-readable explanations for decisions
4. **🚫 Smart Filtering**: Automatically excludes poor matches

---

## 📈 Stage 5: Final Ranking & Results

### **Output Structure**:
```mermaid
flowchart LR
    A[✅ Eligible Trials] --> B[🥇 Top Matches]
    A --> C[📋 Additional Matches]
    
    B --> D[🏆 #1 Match]
    B --> E[🥈 #2 Match]
    B --> F[🥉 #3 Match]
    
    C --> G[📊 Lower Matches]
    
    style D fill:#ffd700
    style E fill:#c0c0c0
    style F fill:#cd7f32
```

### **Match Factors Displayed**:
- **🎯 Condition Match**: How well the condition aligns
- **✅ Eligibility Fit**: Meeting inclusion/exclusion criteria  
- **📍 Enrollment Status**: Current recruitment phase
- **🌍 Geographic Proximity**: Distance and accessibility

---

## 🛠️ Technical Implementation Details

### **LLM Provider Management**:
```python
# Smart routing based on:
class SmartLLMRouter:
    def select_provider(transcript):
        complexity = calculate_complexity(transcript)
        length = len(transcript.split())
        
        if length > 1000 or complexity > 0.4:
            return Claude  # Better for complex reasoning
        else:
            return OpenAI  # Faster for simple extractions
```

### **Vector Database Configuration**:
```python
# FAISS setup for clinical trials documentation
vector_store = FAISS.from_documents(
    documents=clinical_docs,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small")
)

# Retrieval chain for query generation
retrieval_chain = create_retrieval_chain(
    retriever=vector_store.as_retriever(search_kwargs={"k": 5}),
    combine_docs_chain=stuff_documents_chain
)
```

### **Error Handling & Fallbacks**:
- **🔄 Provider Fallback**: OpenAI ↔ Claude automatic switching
- **📊 Partial Extraction**: Graceful degradation when some data missing
- **🛡️ PHI Protection**: Multiple sanitization layers
- **⚡ Timeout Handling**: Async operations with proper error boundaries

---

## 📊 Performance Metrics

### **From Sample Log Analysis**:
- **⚡ Extraction Time**: ~25 seconds total pipeline
- **🔍 API Efficiency**: Single ClinicalTrials.gov call with optimized query
- **🎯 Filtering Accuracy**: 7/10 trials filtered out for specific eligibility issues
- **📍 Geographic Matching**: Automatic geocoding (Portland, Oregon → coordinates)

### **LLM Usage Optimization**:
- **📦 Batch Processing**: 5 trials per LLM call for eligibility analysis
- **🎯 Smart Routing**: Complexity-based provider selection
- **🔄 Fallback Strategy**: Minimize failed extractions
- **📊 Token Efficiency**: Structured prompts with JSON responses

---

## 🏁 Real-World Example Flow

Based on the provided logs for an 18-year-old female with B-ALL:

```
1. 📝 Transcript Processing → Extracted: Age 18, B-ALL, Female, Portland OR
2. 🔍 RAG Query Generation → "EXPANSION[Concept]acute lymphoblastic leukemia OR..."  
3. 🌐 API Search → Found 10 initial trials
4. 🎭 LLM Filtering → Filtered out 7 trials:
   - NCT06855810: Age requirement (<18 years)
   - NCT06289673: Age requirement (<18.99 years) 
   - NCT05745181: T-ALL specific (patient has B-ALL)
   - NCT06934382: T-ALL specific (patient has B-ALL)
   - etc.
5. ✅ Final Results → 3 eligible trials with detailed reasoning
```

This demonstrates the system's ability to make nuanced medical decisions, understanding that:
- **Age boundaries** are strictly enforced
- **Disease subtypes** (B-ALL vs T-ALL) are critical distinctions
- **Geographic preferences** are factored into scoring

---

## 🚀 System Advantages

- **🎯 High Precision**: LLM-based eligibility analysis catches nuanced requirements
- **⚡ Efficient Processing**: RAG reduces API calls while improving query quality  
- **🛡️ Privacy First**: Multiple PHI protection layers
- **🔄 Reliable**: Multi-provider fallback ensures high availability
- **📊 Transparent**: Detailed reasoning for all matching decisions
- **🧠 Adaptive**: Smart routing optimizes for speed vs complexity trade-offs

The system successfully combines the power of large language models with traditional search and filtering techniques to provide accurate, explainable clinical trial matching.