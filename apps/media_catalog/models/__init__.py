"""
Media catalog models package.
"""

from .base import Media, MediaType
from .movie import Movie
from .tvseries import TVSeries
from .book import Book
from .music import Music
from .concert import Concert
from .document import Document

__all__ = [
    'Media',
    'MediaType',
    'Movie',
    'TVSeries',
    'Book',
    'Music',
    'Concert',
    'Document',
]
