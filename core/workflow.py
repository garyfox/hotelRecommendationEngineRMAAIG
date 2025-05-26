"""
Main workflow for the hotel recommendation system.
"""
from typing import Dict, List, Tuple, Any

from questions.question_bank import get_questions
from questions.suggestion import generate_suggestions
from llm.coherence import check_coherence, check_logical_consistency
from vector.embeddings import embed_text
from vector.storage import store_vector


# In core/workflow.py - replace entirely
from memory.simple_memory_workflow import LLMMemoryWorkflow

# For backwards compatibility, create an alias
class InterviewWorkflow(LLMMemoryWorkflow):
    """Legacy wrapper - now uses LLM memory system."""
    pass
