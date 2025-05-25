# gatherHotelPreferences
Our 2nd attempt to make a useful preference gathering tool with the intent to hand off

# gatherHotelPreferences

A CLI application that uses LLM interaction to determine customer hotel preferences through a guided questionnaire. The system generates search terms (both traditional and vector-based) from customer responses to recommend hotels based on web-scraped reviews and other unstructured data.

## Features

- Python-based CLI application
- Integration with a local LLM (Ollama)
- 5 strategic questions to elicit detailed customer preferences
- Vector storage for customer responses
- Coherence, detail, and usefulness checking via LLM
- Structured data collection (table of questions and answers)
- Reasoning layer beyond simple prompt engineering

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/gatherHotelPreferences.git
cd gatherHotelPreferences
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Make sure Ollama is installed and running:
```bash
ollama serve
```

5. Download the required Ollama model:
```bash
ollama pull mistral
```

## Usage

1. Run the application:
```bash
python main.py interview
```

2. Follow the prompts to answer the 5 questions about your hotel preferences.

3. Review the summary of your preferences and the generated search terms.

## Project Structure

```
hotel_recommender/
├── main.py                  # Entry point
├── config.py                # Configuration settings
├── requirements.txt         # Dependencies
├── cli/
│   ├── __init__.py
│   ├── interface.py         # CLI interaction logic
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
└── vector/
    ├── __init__.py
    ├── embeddings.py        # Text vectorization
    ├── storage.py           # Vector database operations
    └── search.py            # Search term generation
```

## Configuration

The system configuration is defined in `config.py`. You can modify:

- Ollama LLM settings (URL, model, timeout)
- Vector embedding settings (model, dimensions)
- Question validation parameters
- CLI display settings

## Development

This project is designed with modularity in mind, making it easy to:

- Add new questions to the question bank
- Swap out the LLM for a different provider
- Change the vector embedding approach
- Add a front-end interface

## License

[MIT License](LICENSE)
