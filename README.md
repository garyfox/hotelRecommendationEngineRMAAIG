# gatherHotelPreferences

**An intelligent hotel preference gathering system powered by local LLM reasoning and real-time hotel search APIs.**

This system conducts natural language interviews to understand customer hotel preferences, validates responses using LLM-powered coherence checking, and searches for actual hotels with current pricing. Every conversation is logged with complete context for advanced analysis.

## 🎯 What This Does

- **Intelligent Interview**: 6 strategic questions with LLM-powered suggestion system
- **Real Hotel Search**: Live Booking.com API integration with current pricing
- **Rich Conversation Logging**: Complete session capture for LLM analysis
- **Validation & Coherence**: Ensures useful, consistent responses
- **Vector Embeddings**: For semantic search and preference matching

## ✨ Key Features

### 🤖 LLM-Powered Validation
- Uses local Ollama LLM (qwen3:8b) for response quality checking and coherence
- Generates contextual suggestions to improve vague answers
- Checks logical consistency across all responses

### 🏨 Real Hotel Data Integration
- Live Booking.com API searches with current pricing
- Pagination support (up to 60 hotels per search)
- Multi-currency and locale support

### 📋 Comprehensive Session Logging
Creates detailed session files for each conversation:
- `full_context.txt` - Complete conversation + LLM reasoning
- `conversation_only.txt` - Clean human dialog
- `hotel_results.txt` - Search results with pricing
- `reasoning_log.txt` - All LLM decision chains

## 🚀 Quick Start

### Prerequisites

1. **Ollama** - Local LLM server
2. **Booking.com API** - Hotel search (via RapidAPI)
3. **Python 3.8+**

### Installation

1. **Clone and setup environment**:
```bash
git clone https://github.com/yourusername/gatherHotelPreferences.git
cd gatherHotelPreferences
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Install and configure Ollama**:
```bash
# Install Ollama (https://ollama.ai)
ollama serve

# In another terminal, download the model
ollama pull gemma3:4b
```

3. **Get API keys and set environment variables**:
```bash
# Required: Booking.com API via RapidAPI
export RAPIDAPI_KEY="your_booking_com_rapidapi_key"



```

Get your Booking.com API key from [RapidAPI Booking.com endpoint](https://rapidapi.com/tipsters/api/booking-com).

4. **Verify setup**:
```bash
python main.py setup
```

### Run Your First Interview

```bash
python main.py interview
```

This starts an interactive interview that will:
1. Ask 6 strategic questions about hotel preferences
2. Validate responses and suggest improvements
3. Search for actual hotels with current pricing
4. Save everything to a timestamped session directory

## 📊 Example Output

After completing an interview, you'll get a session directory like:

```
data/sessions/20241226_143022/
├── full_context.txt        # Complete conversation + AI reasoning
├── conversation_only.txt   # Clean human dialog
├── final_responses.txt     # Q&A summary
├── hotel_results.txt       # 60 hotels with current pricing
├── reasoning_log.txt       # All LLM decisions
└── metadata.json          # Session metadata
```

### Sample Hotel Results
```
HOTEL SEARCH RESULTS
Location: Rome
Dates: 2025-02-24 to 2025-02-26
Found: 45 hotels (with pagination)

 1. Hotel Artemide
    💰 $185/night × 2 nights = $370 total
    ⭐ Rating: 8.5/10

 2. Hotel de Russie
    💰 $450/night × 2 nights = $900 total
    ⭐ Rating: 9.2/10
```

## 🏗️ Architecture

```
gatherHotelPreferences/
├── main.py                  # CLI entry point
├── config.py               # System configuration
├── cli/                    # Command line interface
│   ├── interface.py        # Main CLI logic (backspace-bug fixed!)
│   └── display.py          # Rich formatting
├── core/                   # Core workflow
│   └── workflow.py         # Interview orchestration
├── llm/                    # LLM integration
│   ├── ollama_client.py    # Local LLM client
│   ├── coherence.py        # Response validation
│   └── prompt_templates.py # LLM prompts
├── questions/              # Question system
│   ├── question_bank.py    # 6 strategic questions
│   ├── suggestion.py       # Improvement suggestions
│   └── flow.py            # Question sequencing
├── vector/                 # Embeddings & search
│   ├── embeddings.py       # SentenceTransformers
│   ├── storage.py          # FAISS vector store
│   └── search.py          # Search term generation
├── search/                 # Hotel search APIs
│   ├── hotel_client.py     # Google Maps integration
│   └── integration.py      # LLM-powered extraction
├── conversation/           # Session logging
│   └── logger.py          # Rich context capture
├── memory/                 # Conversation memory
│   └── llm_conversation_memory.py  # LLM-powered memory
└── hotel_search.py        # Main hotel search logic
```

## 🔧 Configuration

Key settings in `config.py`:

```python
# Ollama LLM
OLLAMA_CONFIG = {
    "base_url": "http://localhost:11434",
    "model": "gemma3:4b",
    "timeout": 60,
}

# Vector embeddings
VECTOR_CONFIG = {
    "embedding_model": "all-MiniLM-L6-v2",
    "vector_dimension": 384,
}
```

## 🔍 API Integration Details

### Booking.com API (Required)
- **Purpose**: Real hotel search with current pricing
- **Cost**: Free tier available on RapidAPI
- **Features**: 60 hotels per search, multiple currencies, pagination

### Google Maps API (Optional)
- **Purpose**: Enhanced location validation
- **Fallback**: System works without it using Booking.com location search

### Ollama (Required)
- **Purpose**: Local LLM for validation and suggestions
- **Model**: Gemma 3 4B (recommended, ~2.5GB download)
- **Alternatives**: Any Ollama-compatible model

## 🐛 Troubleshooting

### Common Issues

**1. "Ollama server is not running"**
```bash
# Start Ollama in background
ollama serve

# Check if model is available
ollama list
```

**2. "No RAPIDAPI_KEY found"**
```bash
# Set your Booking.com API key
export RAPIDAPI_KEY="your_key_here"

# Test API connection
python -c "import os; print(os.getenv('RAPIDAPI_KEY'))"
```

**3. "Could not find destination ID"**
- Some cities need full names: "Vail, Colorado" instead of "Vail"
- Try variations: "Paris, France" vs "Paris"
- Check the hotel_results.txt for debugging info

**4. CLI Input Issues**
- Fixed in v0.1.0 with "nuclear option" - pure Python input
- If still having issues, try different terminal emulator

### Debug Mode

Run with verbose LLM output:
```python
# In config.py, set:
OLLAMA_CONFIG = {
    "verbose": True  # Shows all LLM interactions
}
```

## 🚀 Advanced Usage

### Custom Questions
Edit `questions/question_bank.py` to modify the 6 strategic questions.

### Different LLM Models
```bash
# Try other models
ollama pull mistral:7b
ollama pull llama3:8b

# Update config.py
OLLAMA_CONFIG["model"] = "mistral:7b"
```

### Batch Processing
```python
from core.workflow import InterviewWorkflow
from pathlib import Path

# Process saved conversations
session_dir = Path("data/sessions/20241226_143022")
# Your analysis code here
```

## 🔮 Coming Soon

- **Anthropic Claude Integration**: Final AI-powered hotel recommendations
- **Web Interface**: Browser-based interviews
- **Advanced Analytics**: Preference pattern analysis
- **Multi-language Support**: Interviews in multiple languages

## 📝 Session Data Schema

Each interview creates rich, structured data perfect for advanced LLM analysis:

- **Human conversation flow** with timestamps
- **Complete LLM reasoning chain** for every decision
- **Real hotel pricing data** with search metadata
- **Vector embeddings** for semantic similarity
- **Structured JSON** + human-readable text files

This data is designed to be consumed by frontier LLMs (like Claude) for sophisticated hotel recommendations.

## 🤝 Contributing

This is currently a research/proof-of-concept project. The core system is production-ready, but we're actively developing:

1. Anthropic Claude integration for final recommendations
2. Enhanced error handling and edge cases
3. Performance optimizations for larger datasets

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Built with**: Python, Ollama, SentenceTransformers, FAISS, Rich CLI, Booking.com API

*An intelligent approach to understanding what travelers really want.*
