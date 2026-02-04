"""
Document model - user-created document entries.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import Media


class Document(Media):
    """Document-specific fields for user-created document entries."""

    document_type = models.CharField(
        _('document type'),
        max_length=100,
        blank=True,
        help_text=_('e.g., article, paper, manual, guide')
    )
    author = models.CharField(_('author'), max_length=200, blank=True)
    file_url = models.URLField(
        _('file URL'),
        max_length=500,
        blank=True,
        help_text=_('Link to the document file')
    )

    class Meta:
        db_table = 'media_catalog_document'
        verbose_name = _('document')
        verbose_name_plural = _('documents')

    def __str__(self):
        return self.title
