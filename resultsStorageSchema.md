# Plaintext Storage Schema - Rich Context for Frontier LLM Analysis

## Directory Structure
```
data/
├── sessions/
│   ├── 20241226_143022/           # session_id (timestamp)
│   │   ├── full_context.txt       # Everything for frontier LLM
│   │   ├── conversation_only.txt  # Just human conversation
│   │   ├── final_responses.txt    # Clean Q&A pairs
│   │   ├── reasoning_log.txt      # All LLM reasoning/prompts
│   │   ├── hotel_results.txt      # Pricing data when available
│   │   └── metadata.json          # Session metadata
│   └── 20241226_151045/
└── exports/                       # CSV exports
    └── sessions_analysis.csv
```

## File Contents

### 1. `full_context.txt` - Complete Context for Frontier LLM
```
=== HOTEL PREFERENCE SESSION - COMPLETE CONTEXT ===
Session: 20241226_143022
Started: 2024-12-26 14:30:22
System: gatherHotelPreferences v0.1.0

=== CONVERSATION FLOW ===
[14:30:22] QUESTION (destination): Where are you planning to travel? Please include the city, country, and any specific neighborhoods or areas you're interested in.

[14:30:45] USER: I'm thinking about Rome, Italy. Maybe somewhere near the Colosseum or historic center.

[14:30:46] COHERENCE_CHECK:
System Prompt: "You are evaluating hotel preference answers for search utility..."
User Prompt: "Question: Where are you planning... Answer: I'm thinking about Rome..."
LLM Response: "Yes, this provides specific location preferences that can be matched."

[14:31:15] USER: It's for our 5th anniversary. We want to do romantic dinners and see the sights.

[14:31:16] SUGGESTION_GENERATION:
System Prompt: "Generate helpful suggestions to improve an answer that lacks detail..."
LLM Response: "1. What specific romantic experiences... 2. Are there particular sights..."

[14:31:45] USER (REVISED): We want candlelit dinners, maybe a cooking class together, and definitely want to see the Vatican and Trevi Fountain.

[continues with complete reasoning chain...]

=== FINAL PREFERENCES ===
Destination: Rome, Italy. Somewhere near the Colosseum or historic center.
Trip Purpose: We want candlelit dinners, maybe a cooking class together, and definitely want to see the Vatican and Trevi Fountain.
Budget: Mid-range, maybe $200-300 per night. We want nice but not crazy expensive.
Amenities: Good location, maybe a nice restaurant, and definitely reliable WiFi for posting photos.
Experience: Something romantic and authentic. Maybe a boutique hotel with Italian character rather than a big chain.

=== EXTRACTED SEARCH TERMS ===
Location: rome, colosseum, historic center
Experience: romantic, authentic, boutique
Budget: mid-range, $200-300
Amenities: restaurant, wifi
Activities: vatican, trevi fountain, cooking class

=== HOTEL SEARCH RESULTS ===
Search Parameters: Rome, 2025-02-24 to 2025-02-26, 2 adults, 1 room
Currency: EUR

Hotel Artemide | 8.5/10 | €185/night | €370 total | Near Termini Station
Hotel de Russie | 9.2/10 | €450/night | €900 total | Near Spanish Steps
The First Roma Arte | 8.1/10 | €220/night | €440 total | Via del Vantaggio
[continues...]

=== REASONING QUALITY ANALYSIS ===
- Initial answer quality: Destination clear, purpose vague
- Improvement after suggestions: Added specific activities and romantic focus
- Consistency check: All preferences align (romantic anniversary trip)
- Search term extraction: Successfully mapped to location + experience keywords
- Hotel matching: Found 12 hotels in price range, 8 with romantic/boutique characteristics
```

### 2. `conversation_only.txt` - Pure Human Conversation
```
=== HUMAN CONVERSATION ONLY ===
Session: 20241226_143022

Q: Where are you planning to travel?
A: I'm thinking about Rome, Italy. Maybe somewhere near the Colosseum or historic center.

Q: What's the main purpose of your trip?
A: It's for our 5th anniversary. We want to do romantic dinners and see the sights.
SUGGESTION: What specific romantic experiences are you hoping for?
A: (REVISED) We want candlelit dinners, maybe a cooking class together, and definitely want to see the Vatican and Trevi Fountain.

[continues...]
```

### 3. `reasoning_log.txt` - All LLM Reasoning Chain
```
=== LLM REASONING CHAIN ===

[COHERENCE_CHECK - destination]
System: "You are evaluating hotel preference answers for search utility. A GOOD ANSWER should contain specific, actionable preferences..."
Input: "Question: Where are you planning to travel... Answer: I'm thinking about Rome, Italy..."
Output: "Yes, this provides specific location preferences that can be matched against hotel reviews."
Decision: COHERENT = True

[SUGGESTION_GENERATION - trip_purpose]
System: "Generate helpful suggestions to improve an answer that lacks detail..."
Input: "Question: What's the main purpose... Answer: It's for our 5th anniversary..."
Output: "1. What specific romantic experiences are you hoping for? 2. Are there particular sights..."
Suggestions Shown: 2

[DESTINATION_PARSING - final]
System: "Extract the main destination city from travel text. Return just the city name..."
Input: "Rome, Italy. Maybe somewhere near the Colosseum or historic center."
Output: "Rome"
Mapped To: dest_id=-126693

[continues...]
```

### 4. `hotel_results.txt` - Pricing & Availability Data
```
=== HOTEL SEARCH RESULTS ===
Search Date: 2024-12-26 14:35:10
Parameters: Rome (-126693), 2025-02-24 to 2025-02-26, 2 adults, 1 room

Hotel Artemide
- Rating: 8.5/10 (2,847 reviews)
- Price: €185/night (€370 total, 2 nights)
- Location: Via Nazionale 22, Near Termini Station
- Amenities: Restaurant, WiFi, Business Center
- Match Score: High (location + amenities)

Hotel de Russie
- Rating: 9.2/10 (1,234 reviews)
- Price: €450/night (€900 total, 2 nights)
- Location: Via del Babuino 9, Near Spanish Steps
- Amenities: Spa, Restaurant, Garden, WiFi
- Match Score: Very High (luxury + romantic + location)

[continues with all results...]

=== PREFERENCE MATCHING ANALYSIS ===
Budget Target: €200-300/night
In Range: 8 of 15 hotels
Romance Keywords: 12 hotels mention "romantic", "honeymoon", "couples"
Location Match: 10 hotels within 1km of Colosseum/historic center
Amenity Match: All have WiFi, 9 have restaurants
```

## Questions:

1. **Is this the right level of detail** for your frontier LLM analysis?
2. **Should we combine everything in one file** or keep them separate?
3. **What specific reasoning patterns** do you want to capture?
4. **Hotel matching quality** - should we score how well each hotel matches the conversation?

This approach gives the frontier LLM the complete picture: the human's journey, our reasoning process, and the real pricing data to make intelligent recommendations.
