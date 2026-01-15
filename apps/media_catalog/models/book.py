"""
Book model - specific fields for books.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import Media


class Book(models.Model):
    """Book-specific fields extending the base Media model."""

    media_ptr = models.OneToOneField(
        Media,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name='book'
    )

    authors = models.JSONField(
        _('authors'),
        default=list,
        blank=True,
        help_text=_('List of book authors')
    )
    isbn = models.CharField(
        _('ISBN'),
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )
    publisher = models.CharField(_('publisher'), max_length=200, blank=True)
    page_count = models.PositiveIntegerField(
        _('page count'),
        null=True,
        blank=True
    )
    language = models.CharField(
        _('language'),
        max_length=10,
        blank=True,
        help_text=_('ISO 639-1 language code')
    )

    # External API ID
    openlibrary_id = models.CharField(
        _('Open Library ID'),
        max_length=50,
        unique=True,
        blank=True,
        null=True
    )

    class Meta:
        db_table = 'media_catalog_book'
        verbose_name = _('book')
        verbose_name_plural = _('books')

    def __str__(self):
        return self.media_ptr.title
