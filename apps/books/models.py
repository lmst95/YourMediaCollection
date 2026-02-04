from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Book(models.Model):
    """
    Book metadata from DNB API + local extensions
    Shared across all users (general directory)
    """
    # DNB identifiers
    dnb_id = models.CharField(max_length=255, unique=True, db_index=True)
    isbn = models.CharField(max_length=13, blank=True, null=True, db_index=True)

    # Basic metadata (from DNB)
    title = models.CharField(max_length=500)
    subtitle = models.CharField(max_length=500, blank=True)
    authors = models.JSONField(default=list)  # List of author names
    publishers = models.JSONField(default=list)
    publication_year = models.IntegerField(null=True, blank=True)
    language = models.CharField(max_length=10, blank=True)

    # Additional metadata
    categories = models.JSONField(default=list)  # Subject classifications
    description = models.TextField(blank=True)
    page_count = models.IntegerField(null=True, blank=True)

    # DNB raw data (for future reference)
    dnb_raw_data = models.JSONField(default=dict, blank=True)

    # Local tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Denormalized for performance
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    rating_count = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['publication_year']),
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.publication_year or 'N/A'})"

    def update_average_rating(self):
        """Recalculate average rating from all user ratings"""
        ratings = self.ratings.all()
        if ratings.exists():
            self.rating_count = ratings.count()
            self.average_rating = ratings.aggregate(
                avg=models.Avg('rating')
            )['avg']
        else:
            self.rating_count = 0
            self.average_rating = 0.0
        self.save(update_fields=['average_rating', 'rating_count'])


class BookRating(models.Model):
    """User ratings for books (1-5 stars)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_ratings')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    review_text = models.TextField(blank=True)  # Optional review
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'book']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}: {self.rating}/5"

    def save(self, *args, **kwargs):
        """Update book's average rating when a rating is saved"""
        super().save(*args, **kwargs)
        self.book.update_average_rating()

    def delete(self, *args, **kwargs):
        """Update book's average rating when a rating is deleted"""
        book = self.book
        super().delete(*args, **kwargs)
        book.update_average_rating()


class BookReadStatus(models.Model):
    """User's read status for books"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='book_read_statuses')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='read_statuses')
    is_read = models.BooleanField(default=False)
    read_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'book']
        ordering = ['-created_at']
        verbose_name = 'Buch-Gelesen-Status'
        verbose_name_plural = 'Buch-Gelesen-Status'

    def __str__(self):
        status = "gelesen" if self.is_read else "ungelesen"
        return f"{self.user.username} - {self.book.title}: {status}"
