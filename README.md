# RMAIIG Denver AI Hotel Command Line Hotel Suggestion Agent Proof of Concept

**An intelligent hotel preference gathering system with LLM validation and AI analysis.**

Conducts natural language interviews, validates responses using local LLM reasoning, searches for real hotels with current pricing, and provides expert psychological analysis via Claude AI.

Why did I make this? From a build workshop hosted by https://www.meetup.com/denverai/ the idea was proposed! While I think this idea is a bit too big to properly launch, I wanted to explore the idea of a thoroughly considered AI agent where the customer doesn't have to know anything about AI, LLM's or how to prompt. Rather, meet them where they are and apply deeply considered reasoning to guide them through the process.

Why the command line? It's what I know and was the fastest and easiest way for me to build this proof of concept. I'm not a web developer, so I wanted to focus on the AI and validation aspects of the project, which is really around where, how and why to build reasoning mechanisms, what level of reasoning is needed and when, and considering (despite the command line interface) a customer who is unfamiliar with best practices of frontier-LLM prompting and might not know how to ask questions the right way.

Why the snark in the final recommendation? To show how to drive a LLM to produce something insightful and useful. Up to you if you want something like this or a little nicer!

The corresponding presentation material is also included as a PDF. I can best be reached out to on linkedin at https://linkedin.com/in/garynfox — let's talk!

Huge thanks to Efosa, David, Elena, Daniel C, Daniel R, and Geena!

## ✨ What This Does

- **Smart Interview**: 6 strategic questions with LLM-powered validation
- **Real Hotel Search**: Live Booking.com API (via RapidAPI) with current pricing (up to 60 hotels)
- **AI Analysis**: Claude provides psychological insights and honest recommendations
- **Rich Logging**: Complete conversation capture with LLM reasoning chains, including system and customer prompts
- **Flexible Models**: qwen3:8b (recommended) or gemma3:4b (faster alternative)

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Ollama with qwen3:8b model
- Booking.com API key (via RapidAPI, ~500 free calls per month, 1 call per page of results)
- Anthropic API key (via Anthropic Console) and ~$5 of Anthropic credits (~pennies per call, just once per use of the app)
- Machine that can run Ollama up to 8b parameter models (my specs: macBook pro M3 w/ 36 GB RAM)

### Installation

1. **Setup project**:
```bash
git clone <https://github.com/garyfox/hotelRecommendationEngineRMAAIG>
cd gatherHotelPreferences
pip install -r requirements.txt
```

2. **Install Ollama and models**:
```bash
# Install from https://ollama.ai
ollama serve

# Download models
ollama pull qwen3:8b    # Recommended: good reasoning capabilities
ollama pull gemma3:4b   # Alternative: faster but may struggle with complex tasks
```

3. **Configure API keys**:

**Get your API keys:**
- **Booking.com**: [RapidAPI Booking.com](https://rapidapi.com/tipsters/api/booking-com)
- **Claude AI**: [Anthropic Console](https://console.anthropic.com/)

```bash
export RAPIDAPI_KEY="your_booking_com_api_key"
export ANTHROPIC_API_KEY="your_anthropic_api_key"
```

### Run Your First Interview

```bash
python main.py interview
```

The system will guide you through 6 questions, validate your responses, search for actual hotels, and offer Claude's expert analysis.

## 📊 What You Get

Each interview creates a timestamped session in `data/sessions/` with:

```
20250528_152119/
├── conversation_only.txt    # Clean Q&A dialog
├── hotel_results.txt        # 36 hotels with pricing
├── claude_analysis.txt      # Expert AI insights
├── full_context.txt         # Complete conversation + LLM reasoning
├── hotel_data.json          # Structured data
└── metadata.json           # Session stats
```

### Sample Output

**Hotel Results:**
```
HOTEL SEARCH RESULTS
Location: Santa Barbara
Found: 36 hotels with pagination

1. Casa Jardin - Boutique Suites
   💰 $296/night × 6 nights = $1775 total
   ⭐ Rating: 9.3/10

2. Harbor View Inn
   💰 $399/night × 6 nights = $2394 total
   ⭐ Rating: 8.8/10
```

**Claude Analysis:**
```
## READING BETWEEN THE LINES
You're trying to balance family obligations with personal freedom,
suggesting this trip represents a chance to reclaim some independence...

## HONEST RECOMMENDATIONS
### Face Reality - Casa Jardin ($296/night)
Why this works: Gives you Spanish Revival aesthetic at a reasonable price...
```

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Switch between models
OLLAMA_CONFIG = {
    "model": "qwen3:8b",    # Better reasoning (default)
    # "model": "gemma3:4b", # Faster responses (may not 'pass' all logic tests, but better for your rapid testing)
}

# Adjust timeouts
BOOKING_CONFIG = {"timeout": 30}
```

## 🖥️ Terminal Recommendation

**Best experience**: [Warp](https://warp.dev) - modern terminal with great performance and natural language reasoning

**Also works with**: macOS Terminal, iTerm2, Windows Terminal, PowerShell, Linux terminals.

## 🔧 Troubleshooting

**Ollama connection issues:**
```bash
ollama serve              # Start server
ollama list              # Check installed models
ollama run qwen3:8b "Hi" # Test model
```

**API problems:**
```bash
echo $RAPIDAPI_KEY
echo $ANTHROPIC_API_KEY# Verify key is set
```

**Hotel search fails:**
- Use full location names: "Santa Barbara, California" not just "Santa Barbara" — LLM should reason and parse to a usable JSON
- Ensure dates are in the future
- Check API key has sufficient credits (~500 / month are free!)

**Need help?** See `TROUBLESHOOTING.md` for detailed solutions.

## 🏗️ How It Works

1. **Interview Engine**: 6 strategic questions designed to extract useful preferences
2. **LLM Validation**: Local Ollama model checks response quality and consistency
3. **Hotel Search**: Booking.com API with pagination for comprehensive results
4. **Claude Analysis**: Expert AI reads between the lines and provides honest insights
5. **Rich Logging**: Every decision and reasoning step is captured for analysis

## 🎯 Use Cases

- **Travel Research**: Understand customer psychology before making recommendations, customers don't have know what questions to ask!
- **AI Research**: Rich conversation datasets with complete reasoning chains
- **Customer Insights**: What people say vs. what they actually want

## 📋 System Requirements

- **LLM**: Ollama with qwen3:8b (~5GB) or gemma3:4b (~2.5GB)
- **APIs**: Booking.com (free tier available), Anthropic Claude (optional)
- **Performance**: 3-8 minute interviews, hotel search in 10-20 seconds

## 🛠️ Can't run Ollama? Suggestions!

- **Reasoning and Coherence LLM**: use Anthropic's API on a non-frontier model, such as Sonnet 3.5, should cost very little
- **APIs**: Booking.com (free tier available), Anthropic Claude (optional)
- **Storage**: ~2-5MB per session with complete logs
- **Performance**: 3-8 minute interviews, hotel search in 10-20 seconds

## 🔮 Advanced Usage

**Custom models:**
```bash
# Switch to faster model in config.py
OLLAMA_CONFIG["model"] = "gemma3:4b"
```

**Debug mode:**
```python
# Enable verbose LLM logging in config.py
OLLAMA_CONFIG["verbose"] = True
```

## Future Ideas / ToDo / Up to You!
- Real UI!
- Comparison to other travel options!
- Refactoring (practicing with Claude Code!)
- Dynamic preference-gathering and better questions!
- Alternate preference-gathering mechanisms, perhaps from other information about you, or either-or options!
- Model Context Protocol integration!
- Custom GPT or other wrappers!


## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

Built with Python, Ollama, Claude AI, and a RapidAPI.com that paginates through Booking.com. Creates intelligent insights into what travelers really want.
