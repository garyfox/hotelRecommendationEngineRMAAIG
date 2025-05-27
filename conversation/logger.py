"""
Conversation logger for the hotel preference system.
Stores conversation flow according to the plaintext storage schema.
"""
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from config import DATA_DIR


class ConversationLogger:
    """
    Logs conversation flow to plaintext files following the storage schema.
    """

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize the conversation logger.

        Args:
            session_id: Optional session ID, will generate one if not provided
        """
        self.session_id = session_id or self._generate_session_id()
        self.session_dir = Path(DATA_DIR) / "sessions" / self.session_id
        self.session_dir.mkdir(exist_ok=True, parents=True)

        # File paths
        self.full_context_file = self.session_dir / "full_context.txt"
        self.conversation_only_file = self.session_dir / "conversation_only.txt"
        self.final_responses_file = self.session_dir / "final_responses.txt"
        self.reasoning_log_file = self.session_dir / "reasoning_log.txt"
        self.metadata_file = self.session_dir / "metadata.json"

        # In-memory storage for building the files
        self.conversation_entries = []
        self.reasoning_entries = []
        self.final_responses = {}
        self.metadata = {
            "session_id": self.session_id,
            "started_at": datetime.now().isoformat(),
            "status": "in_progress",
            "total_questions": 0,
            "total_revisions": 0,
            "llm_interactions": 0
        }

        # Initialize files
        self._init_files()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID based on timestamp."""
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _init_files(self) -> None:
        """Initialize all the log files with headers."""
        # Full context file
        with open(self.full_context_file, 'w', encoding='utf-8') as f:
            f.write(f"=== HOTEL PREFERENCE SESSION - COMPLETE CONTEXT ===\n")
            f.write(f"Session: {self.session_id}\n")
            f.write(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"System: gatherHotelPreferences v0.1.0\n\n")
            f.write(f"=== CONVERSATION FLOW ===\n")

        # Conversation only file
        with open(self.conversation_only_file, 'w', encoding='utf-8') as f:
            f.write(f"=== HUMAN CONVERSATION ONLY ===\n")
            f.write(f"Session: {self.session_id}\n\n")

        # Reasoning log file
        with open(self.reasoning_log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== LLM REASONING CHAIN ===\n")
            f.write(f"Session: {self.session_id}\n\n")

    def log_question(self, question_id: str, question_text: str) -> None:
        """
        Log a question being asked.

        Args:
            question_id: The ID of the question
            question_text: The full question text
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Store for in-memory processing
        entry = {
            'timestamp': timestamp,
            'type': 'question',
            'question_id': question_id,
            'content': question_text
        }
        self.conversation_entries.append(entry)

        # Update metadata
        self.metadata['total_questions'] += 1

        # Write to full context file
        with open(self.full_context_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] QUESTION ({question_id}): {question_text}\n\n")

        # Write to conversation only file
        with open(self.conversation_only_file, 'a', encoding='utf-8') as f:
            f.write(f"Q: {question_text}\n")

    def log_user_response(self, question_id: str, response: str, is_revision: bool = False) -> None:
        """
        Log a user response.

        Args:
            question_id: The ID of the question being answered
            response: The user's response
            is_revision: Whether this is a revised answer
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        response_type = "USER (REVISED)" if is_revision else "USER"

        # Store for in-memory processing
        entry = {
            'timestamp': timestamp,
            'type': 'user_response',
            'question_id': question_id,
            'content': response,
            'is_revision': is_revision
        }
        self.conversation_entries.append(entry)

        # Update final responses (always use latest)
        self.final_responses[question_id] = response

        # Update metadata
        if is_revision:
            self.metadata['total_revisions'] += 1

        # Write to full context file
        with open(self.full_context_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {response_type}: {response}\n\n")

        # Write to conversation only file
        with open(self.conversation_only_file, 'a', encoding='utf-8') as f:
            if is_revision:
                f.write(f"A: (REVISED) {response}\n")
            else:
                f.write(f"A: {response}\n")

    def log_suggestions(self, question_id: str, suggestions: List[Dict]) -> None:
        """
        Log suggestions provided to the user.

        Args:
            question_id: The ID of the question
            suggestions: List of suggestion dictionaries
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Store for in-memory processing
        entry = {
            'timestamp': timestamp,
            'type': 'suggestions',
            'question_id': question_id,
            'content': suggestions
        }
        self.conversation_entries.append(entry)

        # Write to full context file
        with open(self.full_context_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] SUGGESTIONS:\n")
            for i, suggestion in enumerate(suggestions, 1):
                if isinstance(suggestion, dict):
                    suggestion_text = suggestion.get('text', suggestion)
                    suggestion_type = suggestion.get('type', 'general')
                    f.write(f"  {i}. [{suggestion_type}] {suggestion_text}\n")
                else:
                    f.write(f"  {i}. {suggestion}\n")
            f.write("\n")

        # Write to conversation only file
        with open(self.conversation_only_file, 'a', encoding='utf-8') as f:
            f.write("SUGGESTIONS: ")
            suggestion_texts = []
            for suggestion in suggestions:
                if isinstance(suggestion, dict):
                    suggestion_texts.append(suggestion.get('text', str(suggestion)))
                else:
                    suggestion_texts.append(str(suggestion))
            f.write("; ".join(suggestion_texts) + "\n")

    def log_llm_reasoning(self, interaction_type: str, system_prompt: str,
                         user_prompt: str, llm_response: str,
                         context: Optional[str] = None, decision: Optional[str] = None) -> None:
        """
        Log LLM reasoning step.

        Args:
            interaction_type: Type of interaction (coherence_check, suggestion_generation, etc.)
            system_prompt: The system prompt used
            user_prompt: The user prompt used
            llm_response: The LLM's response
            context: Optional context about the interaction
            decision: Optional decision made based on the response
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Store for in-memory processing
        entry = {
            'timestamp': timestamp,
            'type': interaction_type,
            'system_prompt': system_prompt,
            'user_prompt': user_prompt,
            'llm_response': llm_response,
            'context': context,
            'decision': decision
        }
        self.reasoning_entries.append(entry)

        # Update metadata
        self.metadata['llm_interactions'] += 1

        # Write to full context file
        with open(self.full_context_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {interaction_type.upper()}:\n")
            if context:
                f.write(f"Context: {context}\n")
            f.write(f"System Prompt: \"{system_prompt[:100]}...\"\n")
            f.write(f"User Prompt: \"{user_prompt[:100]}...\"\n")
            f.write(f"LLM Response: \"{llm_response}\"\n")
            if decision:
                f.write(f"Decision: {decision}\n")
            f.write("\n")

        # Write to reasoning log file
        with open(self.reasoning_log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{interaction_type.upper()} - {timestamp}]\n")
            if context:
                f.write(f"Context: {context}\n")
            f.write(f"System: \"{system_prompt}\"\n")
            f.write(f"Input: \"{user_prompt}\"\n")
            f.write(f"Output: \"{llm_response}\"\n")
            if decision:
                f.write(f"Decision: {decision}\n")
            f.write("\n")

    def finalize_session(self, search_terms: Optional[Dict] = None) -> None:
        """
        Finalize the session and write final files.

        Args:
            search_terms: Optional generated search terms
        """
        # Update metadata
        self.metadata['completed_at'] = datetime.now().isoformat()
        self.metadata['status'] = 'completed'

        # Write final responses file
        with open(self.final_responses_file, 'w', encoding='utf-8') as f:
            f.write(f"=== FINAL RESPONSES ===\n")
            f.write(f"Session: {self.session_id}\n\n")

            for question_id, response in self.final_responses.items():
                readable_q = question_id.replace("_", " ").upper()
                f.write(f"{readable_q}: {response}\n\n")

        # Add final sections to full context file
        with open(self.full_context_file, 'a', encoding='utf-8') as f:
            f.write(f"=== FINAL PREFERENCES ===\n")
            for question_id, response in self.final_responses.items():
                readable_q = question_id.replace("_", " ").title()
                f.write(f"{readable_q}: {response}\n")

            if search_terms:
                f.write(f"\n=== EXTRACTED SEARCH TERMS ===\n")
                for category, terms in search_terms.items():
                    f.write(f"{category}: {', '.join(terms)}\n")

            f.write(f"\n=== SESSION SUMMARY ===\n")
            f.write(f"Questions: {self.metadata['total_questions']}\n")
            f.write(f"Revisions: {self.metadata['total_revisions']}\n")
            f.write(f"LLM Interactions: {self.metadata['llm_interactions']}\n")
            f.write(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Write metadata file
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)

    def get_session_info(self) -> Dict[str, Any]:
        """
        Get session information and file paths.

        Returns:
            Dict[str, Any]: Session information
        """
        return {
            'session_id': self.session_id,
            'session_dir': str(self.session_dir),
            'files': {
                'full_context': str(self.full_context_file),
                'conversation_only': str(self.conversation_only_file),
                'final_responses': str(self.final_responses_file),
                'reasoning_log': str(self.reasoning_log_file),
                'metadata': str(self.metadata_file)
            },
            'metadata': self.metadata
        }


# Singleton instance for current session
_current_logger = None


def get_conversation_logger(session_id: Optional[str] = None) -> ConversationLogger:
    """
    Get the current conversation logger instance.

    Args:
        session_id: Optional session ID for new logger

    Returns:
        ConversationLogger: The conversation logger instance
    """
    global _current_logger

    if _current_logger is None or session_id:
        _current_logger = ConversationLogger(session_id)

    return _current_logger
