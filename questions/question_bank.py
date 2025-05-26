"""
Updated question bank for the hotel recommendation system with travel dates.
"""
from typing import Dict, List, Optional


# Define the updated 6 strategic questions (added travel dates)
QUESTIONS = [
    {
        "id": "destination",
        "text": "Where are you planning to travel? Please include the city, country, and any specific neighborhoods or areas you're interested in.",
        "description": "Understanding the destination helps determine available hotel options and location preferences.",
    },
    {
        "id": "travel_dates",
        "text": "What are your exact travel dates? Please provide your check-in and check-out dates (e.g., 'August 1 to August 8, 2025' or 'checking in July 15th, checking out July 22nd').",
        "description": "Specific travel dates are required to check hotel availability and pricing.",
    },
    {
        "id": "trip_purpose",
        "text": "What's the main purpose of your trip? (e.g., business, family vacation, romantic getaway, adventure travel, etc.) Please provide some details about your plans.",
        "description": "The purpose of the trip influences the type of hotel and amenities that would be most suitable.",
    },
    {
        "id": "budget_preference",
        "text": "What's your budget range per night for accommodation? Would you prefer budget-friendly, mid-range, or luxury options?",
        "description": "Budget is a key factor in hotel recommendations and helps filter suitable options.",
    },
    {
        "id": "amenities_features",
        "text": "What hotel amenities or features are most important to you? (e.g., pool, spa, gym, restaurants, room service, family-friendly, pet-friendly, etc.)",
        "description": "Specific amenities and features help narrow down hotel options based on personal preferences.",
    },
    {
        "id": "stay_experience",
        "text": "Describe your ideal hotel experience. What atmosphere, style, or type of property are you looking for? (e.g., boutique hotel, resort, B&B, modern, historic, etc.)",
        "description": "Understanding the desired experience helps match the traveler with hotels that have the right ambiance and style.",
    },
]


def get_questions() -> List[Dict]:
    """
    Get the list of questions for the hotel preference interview.

    Returns:
        List[Dict]: List of question dictionaries
    """
    return QUESTIONS


def get_question_by_id(question_id: str) -> Optional[Dict]:
    """
    Get a question by its ID.

    Args:
        question_id: The ID of the question to retrieve

    Returns:
        Optional[Dict]: The question dictionary if found, None otherwise
    """
    for question in QUESTIONS:
        if question["id"] == question_id:
            return question

    return None
