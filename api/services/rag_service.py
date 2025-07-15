import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import json
from services.llm_router import SmartLLMRouter
from config import Config

logger = logging.getLogger(__name__)

class RAGService:
    """Service for generating optimized ClinicalTrials.gov search queries using RAG"""
    
    def __init__(self, config: Config):
        self.config = config
        self.llm_router = SmartLLMRouter(config)
        self.docs_path = Path(__file__).parent.parent / "docs" / "clinical_trials"
        self.documentation_cache = {}
        
    def _load_documentation(self) -> Dict[str, str]:
        """Load ClinicalTrials.gov documentation files"""
        if self.documentation_cache:
            return self.documentation_cache
            
        docs = {}
        
        # Load main documentation files
        doc_files = [
            "search_operators.md",
            "search_areas.md", 
            "study_data_structure.md"
        ]
        
        for doc_file in doc_files:
            file_path = self.docs_path / doc_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    docs[doc_file] = f.read()
                    
        # Load example files
        examples_path = self.docs_path / "examples"
        if examples_path.exists():
            for example_file in examples_path.glob("*.md"):
                with open(example_file, 'r', encoding='utf-8') as f:
                    docs[f"examples/{example_file.name}"] = f.read()
                    
        self.documentation_cache = docs
        return docs
    
    def _extract_relevant_docs(self, condition: str, docs: Dict[str, str]) -> str:
        """Extract relevant documentation sections based on the medical condition"""
        relevant_content = []
        
        # Always include search operators and areas
        relevant_content.append("# Search Operators Documentation")
        relevant_content.append(docs.get("search_operators.md", ""))
        
        relevant_content.append("\n# Search Areas Documentation")
        relevant_content.append(docs.get("search_areas.md", ""))
        
        # Include cancer examples if condition mentions cancer
        condition_lower = condition.lower()
        cancer_terms = [
            'cancer', 'carcinoma', 'neoplasm', 'tumor', 'tumour', 'malignant',
            'oncology', 'sarcoma', 'lymphoma', 'leukemia', 'melanoma',
            'adenocarcinoma', 'squamous cell', 'basal cell', 'glioblastoma',
            'myeloma', 'metastatic', 'invasive', 'ductal'
        ]
        
        if any(term in condition_lower for term in cancer_terms):
            cancer_examples = docs.get("examples/cancer_queries.md", "")
            if cancer_examples:
                relevant_content.append("\n# Cancer Query Examples")
                relevant_content.append(cancer_examples)
        
        # Include relevant parts of study data structure
        study_structure = docs.get("study_data_structure.md", "")
        if study_structure:
            relevant_content.append("\n# Key Study Data Fields")
            # Extract key sections
            lines = study_structure.split('\n')
            in_relevant_section = False
            for line in lines:
                if any(section in line for section in [
                    "## Protocol Section",
                    "### Conditions Module", 
                    "### Design Module",
                    "### Arms/Interventions Module",
                    "## Enumeration Types",
                    "## Search Usage Examples"
                ]):
                    in_relevant_section = True
                    relevant_content.append(line)
                elif line.startswith("##") and in_relevant_section:
                    in_relevant_section = False
                elif in_relevant_section or line.startswith("### "):
                    relevant_content.append(line)
        
        return '\n'.join(relevant_content)
    
    async def generate_search_query(self, condition: str, additional_context: Dict[str, Any] = None) -> str:
        """Generate an optimized ClinicalTrials.gov search query for a medical condition"""
        try:
            # Load documentation
            docs = self._load_documentation()
            
            # Extract relevant documentation
            relevant_docs = self._extract_relevant_docs(condition, docs)
            
            # Build context for the LLM
            context = {
                "condition": condition,
                "additional_context": additional_context or {}
            }
            
            # Create the question and context for QA interface
            question = f"Generate an optimized ClinicalTrials.gov search query for the medical condition: {condition}"
            if additional_context:
                question += f" with additional context: {json.dumps(additional_context, indent=2)}"
            
            # Select provider and generate query using QA interface
            provider = self.llm_router.select_provider(condition)
            response = await provider.generate_qa_response(question, relevant_docs)
            
            # Extract the query from the response
            query = self._extract_query_from_response(response, condition)
            
            logger.info(f"Generated search query for '{condition}': {query}")
            return query
            
        except Exception as e:
            logger.error(f"Error generating search query for '{condition}': {str(e)}")
            # Fallback to simple expansion query
            return f"EXPANSION[Concept]{condition}"
    
    def _extract_query_from_response(self, response: str, condition: str) -> str:
        """Extract the search query from LLM response"""
        # Clean up the response
        query = response.strip()
        
        # Remove common prefixes if present
        prefixes_to_remove = [
            "Search Query:",
            "Query:",
            "The search query is:",
            "Here is the search query:",
            "```",
            "The optimized query is:"
        ]
        
        for prefix in prefixes_to_remove:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
        
        # Remove trailing punctuation and cleanup
        query = query.rstrip('.')
        
        # Remove code block markers if present
        if query.startswith('```') and query.endswith('```'):
            query = query[3:-3].strip()
        
        # If query is empty or too short, use fallback
        if not query or len(query) < 10:
            return f"EXPANSION[Concept]{condition}"
        
        return query
    
    def _validate_query(self, query: str) -> bool:
        """Basic validation of the generated query"""
        # Check for required elements
        if not query:
            return False
        
        # Check for basic syntax elements
        valid_operators = [
            'EXPANSION[Concept]', 'EXPANSION[Term]', 'EXPANSION[None]',
            'AREA[', 'SEARCH[', 'AND', 'OR', 'NOT'
        ]
        
        # At least one operator should be present
        has_operator = any(op in query for op in valid_operators)
        
        # Check for balanced parentheses
        open_count = query.count('(')
        close_count = query.count(')')
        balanced_parens = open_count == close_count
        
        # Check for balanced brackets
        open_bracket_count = query.count('[')
        close_bracket_count = query.count(']')
        balanced_brackets = open_bracket_count == close_bracket_count
        
        return has_operator and balanced_parens and balanced_brackets
    
    async def generate_query_with_filters(self, condition: str, filters: Dict[str, Any] = None) -> str:
        """Generate a search query with additional filters"""
        base_query = await self.generate_search_query(condition)
        
        if not filters:
            return base_query
        
        filter_parts = []
        
        # Add recruitment status filter
        if filters.get('recruitment_status'):
            statuses = filters['recruitment_status']
            if isinstance(statuses, list):
                status_filter = ','.join(statuses)
            else:
                status_filter = statuses
            filter_parts.append(f"AREA[OverallStatus]{status_filter}")
        
        # Add study type filter
        if filters.get('study_type'):
            filter_parts.append(f"AREA[StudyType]{filters['study_type']}")
        
        # Add phase filter
        if filters.get('phase'):
            phases = filters['phase']
            if isinstance(phases, list):
                phase_filter = ' OR '.join([f"AREA[Phase]{phase}" for phase in phases])
                filter_parts.append(f"({phase_filter})")
            else:
                filter_parts.append(f"AREA[Phase]{phases}")
        
        # Add location filter
        if filters.get('location'):
            location = filters['location']
            if location.get('country'):
                filter_parts.append(f"AREA[LocationCountry]{location['country']}")
            if location.get('state'):
                filter_parts.append(f"AREA[LocationState]{location['state']}")
            if location.get('city'):
                filter_parts.append(f"AREA[LocationCity]{location['city']}")
        
        # Add age filter
        if filters.get('age_group'):
            filter_parts.append(f"AREA[StdAge]{filters['age_group']}")
        
        # Combine base query with filters
        if filter_parts:
            combined_query = f"({base_query}) AND {' AND '.join(filter_parts)}"
        else:
            combined_query = base_query
        
        return combined_query