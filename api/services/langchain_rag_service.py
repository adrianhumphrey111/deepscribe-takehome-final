import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

from config import Config

logger = logging.getLogger(__name__)

class LangChainRAGService:
    """LangChain-based RAG service for generating optimized ClinicalTrials.gov search queries"""
    
    def __init__(self, config: Config):
        self.config = config
        self.docs_path = Path(__file__).parent.parent / "docs" / "clinical_trials"
        self.vector_store = None
        self.retrieval_chain = None
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize LangChain components"""
        try:
            # Initialize embeddings (use OpenAI for embeddings as they're more standard)
            if self.config.OPENAI_API_KEY:
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=self.config.OPENAI_API_KEY,
                    model="text-embedding-3-small"
                )
                self.llm = ChatOpenAI(
                    openai_api_key=self.config.OPENAI_API_KEY,
                    model="gpt-4o-mini",
                    temperature=0.1
                )
            elif self.config.ANTHROPIC_API_KEY:
                # Use OpenAI embeddings if available for better compatibility
                # otherwise fall back to sentence transformers
                try:
                    self.embeddings = OpenAIEmbeddings(
                        model="text-embedding-3-small"
                    )
                except:
                    # Fallback to sentence transformers
                    from langchain_community.embeddings import HuggingFaceEmbeddings
                    self.embeddings = HuggingFaceEmbeddings(
                        model_name="all-MiniLM-L6-v2"
                    )
                
                self.llm = ChatAnthropic(
                    anthropic_api_key=self.config.ANTHROPIC_API_KEY,
                    model="claude-3-5-sonnet-20241022",
                    temperature=0.1
                )
            else:
                raise ValueError("No API key available for embeddings and LLM")
            
            # Load and process documents
            self._load_documents_to_vector_store()
            
            # Create retrieval chain
            self._create_retrieval_chain()
            
        except Exception as e:
            logger.error(f"Failed to initialize LangChain components: {e}")
            raise
    
    def _load_documents_to_vector_store(self):
        """Load documentation into vector store"""
        documents = []
        
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
                    content = f.read()
                    documents.append(Document(
                        page_content=content,
                        metadata={"source": doc_file, "type": "documentation"}
                    ))
        
        # Load example files
        examples_path = self.docs_path / "examples"
        if examples_path.exists():
            for example_file in examples_path.glob("*.md"):
                with open(example_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    documents.append(Document(
                        page_content=content,
                        metadata={"source": f"examples/{example_file.name}", "type": "examples"}
                    ))
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(documents)
        
        # Create FAISS vector store (in-memory)
        self.vector_store = FAISS.from_documents(
            documents=split_docs,
            embedding=self.embeddings
        )
        
        logger.info(f"Loaded {len(split_docs)} document chunks into vector store")
    
    def _create_retrieval_chain(self):
        """Create the retrieval chain for RAG"""
        # Create retriever
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Create prompt template
        system_prompt = """You are an expert medical AI assistant specializing in ClinicalTrials.gov search query generation.

Your task is to generate precise, targeted search queries that will return high-quality, relevant clinical trials (typically 20-40 results rather than hundreds).

Use the following context from ClinicalTrials.gov documentation to understand the proper syntax and operators:

{context}

VALID ClinicalTrials.gov SYNTAX:
- EXPANSION[Concept] for medical terms and synonyms
- OR for combining related terms
- AND for combining different concepts
- Parentheses for grouping terms
- DO NOT use AREA[Age], AREA[Stage], or other AREA[] filters (these are handled separately)

Key requirements for your response:
1. Generate ONLY the search query string, no explanations
2. Use ONLY valid ClinicalTrials.gov syntax: EXPANSION[Concept], OR, AND, parentheses
3. Create TARGETED queries using medical terminology and specific subtypes
4. Include the most relevant medical terms and specific modifiers
5. Use AND logic strategically to narrow results when dealing with common conditions
6. Focus on medical conditions, interventions, and treatment types

TARGETING STRATEGIES:
- For cancer: Include specific cancer type, molecular markers, treatment lines
- For common conditions: Add qualifying terms like "advanced", "refractory", "recurrent"
- Use EXPANSION[Concept] for the main term AND specific medical modifiers
- Combine related medical concepts with OR, different concepts with AND
- Do NOT include age, stage, or demographic filters - these are handled separately

Medical condition: {input}

Generate a targeted search query using ONLY EXPANSION[Concept], OR, AND, and parentheses:"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
        ])
        
        # Create document combination chain
        question_answer_chain = create_stuff_documents_chain(self.llm, prompt)
        
        # Create retrieval chain
        self.retrieval_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    async def generate_search_query(self, condition: str, additional_context: Dict[str, Any] = None) -> str:
        """Generate an optimized ClinicalTrials.gov search query"""
        try:
            # Prepare input
            query_input = condition
            if additional_context:
                context_str = ", ".join([f"{k}: {v}" for k, v in additional_context.items()])
                query_input = f"{condition} (Additional context: {context_str})"
            
            # Generate query using retrieval chain
            result = await self._async_invoke(query_input)
            
            # Extract and clean the query
            query = self._extract_query_from_response(result.get("answer", ""), condition)
            
            logger.info(f"Generated LangChain search query for '{condition}': {query}")
            return query
            
        except Exception as e:
            logger.error(f"Error generating search query for '{condition}': {str(e)}")
            # Fallback to simple expansion query
            return f"EXPANSION[Concept]{condition}"
    
    async def _async_invoke(self, input_text: str) -> Dict[str, Any]:
        """Async wrapper for retrieval chain invoke"""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.retrieval_chain.invoke({"input": input_text})
        )
    
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
            "The optimized query is:",
            "Based on the documentation, here's the optimized query:",
            "Optimized search query:"
        ]
        
        for prefix in prefixes_to_remove:
            if query.startswith(prefix):
                query = query[len(prefix):].strip()
        
        # Remove trailing punctuation and cleanup
        query = query.rstrip('.')
        
        # Remove code block markers if present
        if query.startswith('```') and query.endswith('```'):
            query = query[3:-3].strip()
        
        # Remove any remaining markdown formatting
        query = query.replace('`', '').strip()
        
        # If query is empty or too short, use fallback
        if not query or len(query) < 10:
            return f"EXPANSION[Concept]{condition}"
        
        # Validate basic syntax
        if not self._validate_query(query):
            logger.warning(f"Generated query failed validation: {query}")
            return f"EXPANSION[Concept]{condition}"
        
        return query
    
    def _validate_query(self, query: str) -> bool:
        """Basic validation of the generated query"""
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
    
    def get_relevant_documents(self, condition: str, k: int = 5) -> List[Document]:
        """Get relevant documents for a condition (for debugging)"""
        try:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k}
            )
            return retriever.get_relevant_documents(condition)
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []