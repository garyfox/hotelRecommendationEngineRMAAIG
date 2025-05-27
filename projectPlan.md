# Hotel Recommendation System - Project Plan

## TODO
- add logging
- add handling to help if the customer asks about things they've already answered, ie close to restaurants and quiet in a previous questions
- vectorize and store the entirety of the conversation history, not just the final table
- add 'click through' style testing mechanism
- explore using a smaller local ollama model
- still sometimes asks for more detail when not needed
- unsure what to do if the customer is adversarial
- unsure what to do if the customer adds 'ah shucks' style things are they in the search terms?

Hotel Recommendation System - Updated Project Plan
Current Status: ~85% Complete - Core System Functional
The core preference gathering system with conversation logging is fully operational. Next phase: build the booking API bridge.
Completed Components ✅
Phase 1: Setup and Foundation - COMPLETE

 Development environment and dependencies
 Modular project structure
 CLI interface with Rich (backspace issues resolved)
 Ollama LLM connection with visual feedback

Phase 2: Question Engine Development - COMPLETE

 5 strategic questions designed
 Question flow logic with state management
 LLM-powered suggestion system
 Response validation (coherence & consistency)

Phase 3: Vector Processing - COMPLETE

 Text embedding with SentenceTransformers
 FAISS vector storage system
 Search term generation from preferences
 Vector similarity matching capability

Phase 4: Core Integration - COMPLETE

 End-to-end workflow
 Component integration
 Rich CLI with status indicators
 Error handling and graceful degradation

Phase 5: Conversation Logging System - COMPLETE ✅

 Comprehensive plaintext storage schema

Session-based directory structure: data/sessions/YYYYMMDD_HHMMSS/
full_context.txt - Complete conversation + LLM reasoning for frontier analysis
conversation_only.txt - Clean human conversation flow
final_responses.txt - Just Q&A pairs
reasoning_log.txt - All LLM interactions and decisions
metadata.json - Session statistics


 Real-time logging integration

All LLM interactions automatically captured
Conversation flow logged as it happens
System reasoning chain preserved
Session metrics tracked


 Main CLI integration

Logging integrated into python main.py interview
Backspace issue permanently resolved
Session files created for every interview



Next Phase: Booking API Bridge 🚧
Phase 6: City + Date Extraction (NEXT)

 Simple focused parser - Extract ONLY what matters:

City from conversation → Booking.com destination ID
Check-in date → YYYY-MM-DD format
Check-out date → YYYY-MM-DD format


 Strict date validation

Refuse vague dates ("summer", "next month")
Require specific MM DD YYYY format
Validate date logic (checkin < checkout, not past)


 LLM-powered parsing

Use Ollama to extract city/dates from stored plaintext
Map cities to Booking.com destination IDs
Fallback handling for unknown destinations



Phase 7: Booking.com Integration

 API search execution

Connect parsed data to existing test_booking_api.py
Execute real hotel searches
Return pricing and availability


 Hotel results storage

Add hotel_results.txt to session files
Store search parameters and results
Prepare data for frontier LLM analysis



Phase 8: Frontier LLM Analysis Ready

 Complete context package

Conversation + reasoning + real hotel data
Ready for Claude subscription analysis
Rich context for intelligent recommendations



Known Working Components

Full conversation capture - Everything logged for analysis
LLM reasoning chain - All system decisions preserved
Real-time session management - Files created as interviews happen
Stable CLI experience - Input issues resolved
Working Booking.com API - Ready for integration

Immediate Next Steps (Priority Order)

Build city/date parser - Extract essentials from conversation logs
Integrate with Booking API - Connect parser to hotel search
Store hotel results - Add to conversation logging schema
Test complete pipeline - Conversation → parsing → hotel search → results

Architecture Strengths

Modular design enables easy enhancement
Rich conversation context for frontier LLM analysis
Real booking integration provides market data
Comprehensive logging captures complete reasoning chain
Focused approach - only parse what actually matters (city + dates)

Success Metrics Achieved

✅ Smooth interview completion - Backspace issues resolved
✅ Complete conversation capture - All context preserved
✅ LLM reasoning visibility - System decisions logged
✅ Session management - Organized file structure
✅ Working hotel API - Ready for real searches

Files Ready for Frontier LLM Analysis
The conversation logging system now provides everything needed for Claude analysis:

Complete human conversation flow
System reasoning and decision points
Generated search terms and preferences
Session metadata and statistics
Ready to add: Real hotel search results with pricing

Next conversation should focus on the booking bridge implementation.

## Project Overview
A CLI application that uses LLM interaction to determine customer hotel preferences through a guided questionnaire. The system will generate search terms (both traditional and vector-based) from customer responses to recommend hotels based on web-scraped reviews and other unstructured data.

The system aims to create coherent, useful, and structured outputs (a table of questions and answers) while incorporating a reasoning layer that goes beyond simple prompt engineering. This structured approach ensures consistent data collection while allowing for flexible, varied customer responses that the system can intelligently process.

## Requirements
- Python-based CLI application
- Integration with a local LLM (Ollama)
- 5 strategic questions to elicit detailed customer preferences
- Vector storage for customer responses
- Coherence, detail, and usefulness checking via LLM
- Structured data collection (table of questions and answers)
- Reasoning layer beyond simple prompt engineering
- Consistent format with flexibility for varied customer responses
- Modular design for future front-end integration

## Project Components

### 1. System Architecture
- **Core Application**: Main CLI interface and workflow orchestration
- **Question Module**: Question generation and management
- **LLM Interface**: Communication with local Ollama LLM
- **Vector Processing**: Embedding and storing responses
- **Suggestion Engine**: Helper for customer response elaboration
- **Data Storage**: Persistence layer for customer preferences

### 2. Development Phases

#### Phase 1: Setup and Foundation (Days 1-2)
- [ ] Set up development environment and dependencies
- [ ] Create project structure with modular components
- [ ] Implement basic CLI interface
- [ ] Establish connection to local Ollama LLM

#### Phase 2: Question Engine Development (Days 3-4)
- [ ] Design 5 strategic questions for preference elicitation
- [ ] Implement question flow logic
- [ ] Create suggestion prompts to guide detailed responses
- [ ] Build response validation with LLM

#### Phase 3: Vector Processing (Days 5-6)
- [ ] Implement text embedding functionality
- [ ] Create vector storage system
- [ ] Design search term generation from preferences
- [ ] Build coherence checking mechanism

#### Phase 4: Integration and Testing (Days 7-8)
- [ ] Connect all components into cohesive system
- [ ] Implement end-to-end workflow
- [ ] Add logging and error handling
- [ ] Perform system testing with sample scenarios

#### Phase 5: Documentation and Refinement (Days 9-10)
- [ ] Create comprehensive documentation
- [ ] Refine code and optimize performance
- [ ] Add hooks for future front-end integration
- [ ] Final testing and quality assurance

## Technologies and Dependencies
- Python 3.9+
- Ollama (local LLM)
- Vector database (e.g., FAISS, Chroma)
- Sentence transformers for embeddings
- Rich (for enhanced CLI experience)
- Pytest (for testing)

## File Structure
```
hotel_recommender/
├── main.py                  # Entry point
├── config.py                # Configuration settings
├── requirements.txt         # Dependencies
├── README.md                # Project documentation
├── cli/
│   ├── __init__.py
│   ├── interface.py         # CLI interaction logic
│   └── display.py           # Output formatting
├── core/
│   ├── __init__.py
│   ├── workflow.py          # Main application flow
│   └── validation.py        # Input validation
├── llm/
│   ├── __init__.py
│   ├── ollama_client.py     # Ollama integration
│   ├── prompt_templates.py  # LLM prompts
│   └── coherence.py         # Response quality checking
├── questions/
│   ├── __init__.py
│   ├── question_bank.py     # Core questions
│   ├── suggestion.py        # Response enhancement prompts
│   └── flow.py              # Question sequencing
├── vector/
│   ├── __init__.py
│   ├── embeddings.py        # Text vectorization
│   ├── storage.py           # Vector database operations
│   └── search.py            # Search term generation
└── tests/
    ├── __init__.py
    ├── test_cli.py
    ├── test_llm.py
    ├── test_questions.py
    └── test_vector.py
```

## Extensibility Considerations
- Clear separation of concerns for easy component replacement
- Configuration-driven design for minimal code changes
- Standardized interfaces between modules
- Comprehensive logging for debugging and enhancement
- Hooks for future front-end integration

## Documentation Approach
- Inline code documentation using docstrings
- Function and class purpose descriptions
- Module relationship diagrams
- Setup and usage instructions
- Example flows and expected outputs
