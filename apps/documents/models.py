from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
import os

User = get_user_model()


def user_document_path(instance, filename):
    """
    Upload documents to: media/documents/{user_id}/{filename}
    """
    return f'documents/{instance.user.id}/{filename}'


class Document(models.Model):
    """User-uploaded documents"""

    DOCUMENT_TYPES = [
        # eBooks
        ('PDF', 'PDF'),
        ('EPUB', 'EPUB'),
        ('MOBI', 'MOBI'),

        # Plain Text
        ('TXT', 'Text'),
        ('MD', 'Markdown'),
        ('MARKDOWN', 'Markdown'),

        # Microsoft Office
        ('DOC', 'Word Document'),
        ('DOCX', 'Word Document (DOCX)'),
        ('XLS', 'Excel Spreadsheet'),
        ('XLSX', 'Excel Spreadsheet (XLSX)'),
        ('PPT', 'PowerPoint Presentation'),
        ('PPTX', 'PowerPoint Presentation (PPTX)'),

        # LibreOffice/OpenOffice
        ('ODT', 'OpenDocument Text'),
        ('ODS', 'OpenDocument Spreadsheet'),
        ('ODP', 'OpenDocument Presentation'),

        # Other
        ('OTHER', 'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    # File information
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    file = models.FileField(
        upload_to=user_document_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    'pdf', 'epub', 'mobi',
                    'txt', 'md', 'markdown',
                    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                    'odt', 'ods', 'odp'
                ]
            )
        ]
    )
    file_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    file_size = models.BigIntegerField()  # in bytes

    # Metadata
    authors = models.JSONField(default=list, blank=True)
    categories = models.JSONField(default=list, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def save(self, *args, **kwargs):
        if self.file:
            # Auto-detect file type from extension
            ext = os.path.splitext(self.file.name)[1].upper().replace('.', '')
            if ext in dict(self.DOCUMENT_TYPES):
                self.file_type = ext
            else:
                self.file_type = 'OTHER'

            # Store file size
            self.file_size = self.file.size

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the file when the model is deleted
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def get_file_size_display(self):
        """Return human-readable file size"""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
