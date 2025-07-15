import os
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class SimpleRAGService:
    """Simplified RAG service for Vercel deployment without heavy dependencies"""
    
    def __init__(self, config):
        self.config = config
        # Pre-defined query templates based on common medical conditions
        self.query_templates = {
            "cancer": "EXPANSION[Concept]{condition} AND (advanced OR metastatic OR refractory OR recurrent)",
            "diabetes": "EXPANSION[Concept]{condition} AND (type 1 OR type 2 OR insulin OR glucose)",
            "heart": "EXPANSION[Concept]{condition} AND (cardiovascular OR cardiac OR coronary)",
            "default": "EXPANSION[Concept]{condition}"
        }
    
    async def generate_search_query(self, condition: str, additional_context: Dict[str, Any] = None) -> str:
        """Generate an optimized ClinicalTrials.gov search query using template matching"""
        try:
            # Clean and normalize the condition
            condition_lower = condition.lower()
            
            # Determine query template based on condition keywords
            template_key = "default"
            for key in self.query_templates:
                if key in condition_lower:
                    template_key = key
                    break
            
            # Generate base query
            base_query = self.query_templates[template_key].format(condition=condition)
            
            # Add context-based modifiers
            if additional_context:
                modifiers = []
                
                # Add age group modifiers
                age_group = additional_context.get('age_group')
                if age_group == 'pediatric':
                    modifiers.append("pediatric OR child OR adolescent")
                elif age_group == 'elderly':
                    modifiers.append("elderly OR geriatric OR older adult")
                
                # Add cancer stage modifiers
                cancer_stage = additional_context.get('cancer_stage')
                if cancer_stage:
                    modifiers.append(f"stage {cancer_stage} OR {cancer_stage}")
                
                # Add treatment modifiers
                previous_treatments = additional_context.get('previous_treatments')
                if previous_treatments:
                    treatment_terms = []
                    for treatment in previous_treatments[:2]:  # Limit to 2 treatments
                        if treatment:
                            treatment_terms.append(f"EXPANSION[Concept]{treatment}")
                    if treatment_terms:
                        modifiers.append(f"({' OR '.join(treatment_terms)})")
                
                # Combine modifiers with base query
                if modifiers:
                    modifier_query = " AND (" + " OR ".join(modifiers) + ")"
                    base_query += modifier_query
            
            logger.info(f"Generated simple RAG query for '{condition}': {base_query}")
            return base_query
            
        except Exception as e:
            logger.error(f"Error generating search query for '{condition}': {str(e)}")
            # Fallback to simple expansion query
            return f"EXPANSION[Concept]{condition}"
    
    def get_relevant_documents(self, condition: str, k: int = 5) -> List[str]:
        """Return relevant documentation snippets (simplified version)"""
        # Return pre-defined relevant snippets based on condition
        common_snippets = [
            "Use EXPANSION[Concept] for medical terms to include synonyms",
            "Combine related terms with OR, different concepts with AND",
            "Add specific modifiers like 'advanced', 'refractory', 'recurrent' for targeted results",
            "Use parentheses for grouping complex query logic",
            "Focus on medical conditions, interventions, and treatment types"
        ]
        return common_snippets[:k]