"""
Search package for hotel recommendation system.
"""
from .hotel_client import HotelSearchClient
from .integration import extract_search_parameters, search_hotels_from_preferences

__all__ = ['HotelSearchClient', 'extract_search_parameters', 'search_hotels_from_preferences']
