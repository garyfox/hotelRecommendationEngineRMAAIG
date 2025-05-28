gatherHotelPreferences
A CLI application that uses LLM interaction to determine customer hotel preferences through a guided questionnaire. The system generates search terms (both traditional and vector-based) from customer responses to recommend hotels based on web-scraped reviews and other unstructured data.

🆕 NEW: Claude AI Expert Analysis
The system now includes breakthrough psychological analysis powered by Claude Sonnet 4!

After gathering your preferences and finding real hotels with pricing, Claude provides:

Reading between the lines of your conversation
Brutally honest budget reality checks
Psychological insights about your travel motivations
Practical pros/cons for realistic options
Uncomfortable questions you should ask yourself
Example Analysis:

"You're romanticizing Aspen but have never actually priced out a real trip there. Your $547 budget captures exactly 1 out of 30 available properties. You're essentially asking for a Ferrari experience with a Honda budget."

Features
Python-based CLI application with fixed input handling (no more backspace bugs!)
Integration with local LLM (Ollama) for conversation analysis
6 strategic questions to elicit detailed customer preferences
Real hotel search with live pricing from Booking.com API
Vector storage for customer responses and conversation memory
Comprehensive logging with session-based storage
🧠 Claude Sonnet 4 analysis for expert psychological insights
Coherence and consistency checking via LLM reasoning
Rich CLI interface with visual feedback and status indicators
Installation
Clone the repository:
bash
git clone https://github.com/yourusername/gatherHotelPreferences.git
cd gatherHotelPreferences
Create a virtual environment:
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:
bash
pip install -r requirements.txt
Set up Ollama (for local LLM):
bash
# Install Ollama (see https://ollama.ai/)
ollama serve

# Download the required model
ollama pull gemma3:4b
Set up API keys:
bash
# Required for hotel search
export RAPIDAPI_KEY="your_booking_com_api_key"

# Required for Claude analysis (OPTIONAL but recommended)
export ANTHROPIC_API_KEY="your_anthropic_api_key"

# Optional: Google Maps for enhanced location search
export GOOGLE_MAPS_API_KEY="your_google_maps_key"
API Keys Setup
Required APIs:
RapidAPI (Booking.com): Get your key at rapidapi.com
Anthropic Claude: Get your key at console.anthropic.com
Cost Estimates:
Hotel Search: ~$0.01-0.05 per search (Booking.com API)
Claude Analysis: ~$0.15 per session (Claude Sonnet 4)
Ollama: Free (runs locally)
Usage
Basic Interview (Full Experience)
bash
python main.py interview
Full workflow:

Answer 6 strategic questions about your hotel preferences
Get real-time validation and suggestions for improvement
Search live hotels with current pricing from Booking.com
Receive Claude's expert analysis reading between the lines
All data saved to timestamped session directory
Test Claude Integration
bash
python test_claude_integration.py
Session Data Structure
data/sessions/YYYYMMDD_HHMMSS/
├── conversation_only.txt      # Clean human conversation
├── full_context.txt          # Complete session with LLM reasoning
├── final_responses.txt       # Clean Q&A pairs
├── reasoning_log.txt         # All LLM reasoning steps
├── hotel_results.txt         # Human-readable hotel list
├── hotel_data.json          # Structured hotel data
├── claude_analysis.txt      # 🆕 Claude's expert analysis
├── claude_analysis.json     # 🆕 Structured analysis data
└── metadata.json            # Session metadata
Example Claude Analysis Output
## READING BETWEEN THE LINES
What they're really telling me: You're a skiing enthusiast who's romanticized Aspen but has never actually priced out a real trip there. Your desire for a pool "to rest weary bones" suggests you're either older, out of shape, or anticipating being completely destroyed by Colorado skiing.

The contradiction that reveals everything: You budgeted $547/night for "midrange" in Aspen during peak season, but the actual search results show only ONE option under $550. This massive gap between expectation and reality suggests you're completely inexperienced with luxury destination pricing.

## REALITY CHECK: YOUR BUDGET VS ASPEN
The math: Your $547 budget captures exactly 1 out of 30 available properties. You're essentially asking for a Ferrari experience with a Honda budget.

## HONEST RECOMMENDATIONS
### Option 1: Face Reality - St. Moritz Lodge ($164/night)
**Why this is actually perfect for you:** This is your only option within budget, and it might save you from financial regret while still letting you say you "stayed in Aspen."

**PROS:**
- You can actually afford it without credit card debt
- 8.7 rating means it's genuinely decent, not a dump
- Leaves budget for ski lessons and equipment

**CONS:**
- Zero prestige factor - this isn't Instagram-worthy luxury
- Might not have the pool you specifically mentioned wanting
Project Structure
hotel_recommender/
├── main.py                  # Entry point
├── config.py                # Configuration settings
├── requirements.txt         # Dependencies
├── anthropic/              # 🆕 Claude integration
│   ├── __init__.py
│   └── client.py           # Claude API client and analysis
├── cli/
│   ├── __init__.py
│   ├── interface.py         # CLI interaction logic (FIXED input handling)
│   └── display.py           # Output formatting
├── core/
│   ├── __init__.py
│   └── workflow.py          # Main application flow
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
├── conversation/
│   ├── __init__.py
│   └── logger.py            # Session logging system
├── search/
│   ├── __init__.py
│   ├── hotel_client.py      # Google Maps integration
│   └── integration.py       # LLM-powered search parameter extraction
├── memory/
│   ├── __init__.py
│   ├── llm_conversation_memory.py  # LLM-powered conversation analysis
│   └── simple_memory_workflow.py  # Workflow integration
└── hotel_search.py          # Real hotel search with Booking.com API
Configuration
The system configuration is defined in config.py. Key settings:

Ollama LLM settings (URL, model, timeout)
Vector embedding settings (model, dimensions)
Question validation parameters
API timeouts and retry logic
Claude analysis settings
Recent Major Updates
✅ Fixed Input Handling (Nuclear Option)
Problem: Rich Prompt caused backspace/terminal control issues
Solution: Replaced with pure Python input() while keeping Rich for display
Result: Clean input experience across all terminal emulators
✅ Real Hotel Search Integration
Booking.com API: Live hotel pricing and availability
Pagination: Retrieves up to 60 hotels per search
LLM Extraction: Automatically extracts city/dates from conversation
Error Handling: Graceful fallbacks when APIs are unavailable
✅ Comprehensive Session Logging
Rich Context: Everything needed for frontier LLM analysis
Multiple Formats: Human-readable text + structured JSON
LLM Reasoning: Complete reasoning chain capture
Session Persistence: Timestamped directories for easy retrieval
🆕 Claude Sonnet 4 Integration
Psychological Analysis: Reads between the lines of conversations
Budget Reality Checks: Brutally honest financial analysis
Practical Recommendations: Pros/cons based on real personality insights
API Integration: Clean, structured analysis via Anthropic API
Development
This project is designed with modularity in mind, making it easy to:

Add new questions to the question bank
Swap out LLMs for different providers (Ollama ↔ Anthropic ↔ OpenAI)
Change vector embedding approaches
Add new hotel search providers
Extend Claude analysis with new psychological frameworks
Troubleshooting
Common Issues:
Input/Backspace Problems:

✅ FIXED: Replaced Rich Prompt with pure Python input()
API Key Issues:

bash
# Check if keys are set
echo $RAPIDAPI_KEY
echo $ANTHROPIC_API_KEY

# Set them if missing
export RAPIDAPI_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
Ollama Connection:

bash
# Make sure Ollama is running
ollama serve

# Test connection
ollama list
Claude Analysis Fails:

Check API key is set correctly
Verify internet connection
Try the test script: python test_claude_integration.py
No Hotels Found:

Verify RAPIDAPI_KEY is set
Check destination spelling
Try different date ranges
License
MIT License

What Makes This Special
This isn't just another hotel booking tool. It's a psychological analysis engine that:

Understands human psychology through conversation analysis
Challenges assumptions with real market data
Provides uncomfortable truths about travel motivations
Delivers actionable insights beyond surface preferences
The Claude integration transforms this from a preference gathering tool into a travel psychology consultant that helps people understand what they actually want versus what they think they want.

Perfect for: Travel psychology research, hospitality industry insights, personal travel planning, understanding consumer behavior in luxury markets.
