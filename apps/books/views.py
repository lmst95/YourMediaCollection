from django.views.generic import DetailView, ListView, FormView, View
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Value, CharField
from django.db.models.functions import Replace
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Book, BookRating, BookReadStatus
from .forms import BookSearchForm, BookRatingForm, BookReadStatusForm
from .dnb_api import DNBClient
from apps.user_collections.models import Collection
import re


class BookListView(ListView):
    """Display all books with search and filters"""
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 24

    def get_queryset(self):
        queryset = Book.objects.all()

        # Search by title, authors, ISBN
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            # Check if search looks like an ISBN (mostly digits with optional hyphens/spaces)
            cleaned_search = search_query.replace('-', '').replace(' ', '')
            is_isbn_search = re.match(r'^\d{10,13}$', cleaned_search)

            if is_isbn_search:
                # For ISBN search, normalize both the query and stored ISBN
                # Search for books where ISBN (without hyphens/spaces) contains the cleaned query
                queryset = queryset.annotate(
                    isbn_normalized=Replace(
                        Replace('isbn', Value('-'), Value('')),
                        Value(' '), Value('')
                    )
                ).filter(isbn_normalized__icontains=cleaned_search)
            else:
                # Regular search across title, subtitle, authors, and ISBN
                queryset = queryset.filter(
                    Q(title__icontains=search_query) |
                    Q(subtitle__icontains=search_query) |
                    Q(isbn__icontains=search_query) |
                    Q(authors__icontains=search_query)
                )

        # Filter by year
        year = self.request.GET.get('year', '').strip()
        if year:
            queryset = queryset.filter(publication_year=year)

        # Filter by category
        category = self.request.GET.get('category', '').strip()
        if category:
            queryset = queryset.filter(categories__icontains=category)

        # Sort options
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['title', '-title', 'publication_year', '-publication_year', '-average_rating', '-created_at']:
            queryset = queryset.order_by(sort)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add search/filter values for form persistence
        context['search_query'] = self.request.GET.get('search', '')
        context['year_filter'] = self.request.GET.get('year', '')
        context['category_filter'] = self.request.GET.get('category', '')
        context['sort_value'] = self.request.GET.get('sort', '-created_at')

        # Get unique years and categories for filter dropdowns
        context['available_years'] = Book.objects.exclude(
            publication_year__isnull=True
        ).values_list('publication_year', flat=True).distinct().order_by('-publication_year')

        # Get user collections if authenticated
        if self.request.user.is_authenticated:
            context['user_collections'] = Collection.objects.filter(
                user=self.request.user
            ).order_by('name')
            context['book_content_type_id'] = ContentType.objects.get_for_model(Book).id

        return context


class BookDetailView(DetailView):
    """Display book details"""
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add user collections if authenticated
        if self.request.user.is_authenticated:
            context['user_collections'] = Collection.objects.filter(
                user=self.request.user
            ).order_by('name')
            context['book_content_type_id'] = ContentType.objects.get_for_model(Book).id

            # User's rating for this book
            context['user_rating'] = BookRating.objects.filter(
                user=self.request.user,
                book=self.object
            ).first()

            # User's read status
            context['read_status'] = BookReadStatus.objects.filter(
                user=self.request.user,
                book=self.object
            ).first()

            # Forms
            context['rating_form'] = BookRatingForm(instance=context['user_rating'])

            if context['read_status']:
                initial_read = {
                    'is_read': context['read_status'].is_read,
                    'read_date': context['read_status'].read_date or timezone.now().date()
                }
            else:
                initial_read = {'is_read': False, 'read_date': timezone.now().date()}
            context['read_status_form'] = BookReadStatusForm(initial=initial_read)

        return context


class BookSearchImportView(LoginRequiredMixin, FormView):
    """Search for books in DNB and import them"""
    template_name = 'books/book_search_import.html'
    form_class = BookSearchForm

    def form_valid(self, form):
        search_type = form.cleaned_data['search_type']
        query_text = form.cleaned_data['query']
        max_results = form.cleaned_data['max_results']
        sort_by = form.cleaned_data.get('sort_by', '')

        # Search DNB
        client = DNBClient()

        # Build query and get results based on search type
        if search_type == 'isbn':
            # Use dedicated ISBN lookup method for consistent results
            book_data = client.get_by_isbn(query_text)
            results = [book_data] if book_data else []
            query = f'isbn={query_text.replace("-", "").replace(" ", "")}'
        else:
            # Build CQL query for other search types
            if search_type == 'title':
                query = f'tit={query_text}'
            elif search_type == 'author':
                query = f'atr={query_text}'
            else:  # keyword
                query = query_text

            results = client.search_books(query, max_records=max_results)

        # Check which books already exist in database
        for book_data in results:
            existing = Book.objects.filter(dnb_id=book_data['dnb_id']).first()
            book_data['already_exists'] = existing is not None
            book_data['existing_id'] = existing.id if existing else None

        # Sort results if requested
        if sort_by:
            reverse = sort_by.startswith('-')
            field = sort_by.lstrip('-')

            def get_sort_key(book):
                value = book.get(field)
                # Handle authors list - join for sorting
                if field == 'authors' and isinstance(value, list):
                    value = ', '.join(value) if value else ''
                # Handle None values
                if value is None:
                    return '' if field in ['title', 'authors'] else 0
                return value

            results = sorted(results, key=get_sort_key, reverse=reverse)

        # Store results in session for import
        self.request.session['dnb_search_results'] = results
        self.request.session['search_query'] = query

        context = self.get_context_data(form=form)
        context['results'] = results
        context['query'] = query
        context['search_performed'] = True

        return render(self.request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_performed'] = False
        return context


class BookImportFromDNBView(LoginRequiredMixin, View):
    """Import selected books from DNB search results"""

    def post(self, request):
        # Get selected book indices from form
        selected_indices = request.POST.getlist('selected_books')

        if not selected_indices:
            messages.warning(request, 'Keine Bücher ausgewählt.')
            return redirect('books:search_import')

        # Get results from session
        results = request.session.get('dnb_search_results', [])

        if not results:
            messages.error(request, 'Suchergebnisse nicht gefunden. Bitte suchen Sie erneut.')
            return redirect('books:search_import')

        # Import selected books
        created_count = 0
        skipped_count = 0
        failed_count = 0

        for index_str in selected_indices:
            try:
                index = int(index_str)
                if index < 0 or index >= len(results):
                    continue

                book_data = results[index]

                # Skip if book has no ISBN or page count
                if not book_data.get('isbn') or not book_data.get('page_count'):
                    skipped_count += 1
                    continue

                # Check if already exists
                existing = Book.objects.filter(dnb_id=book_data['dnb_id']).first()
                if existing:
                    skipped_count += 1
                    continue

                # Remove display-only fields before creating book
                clean_book_data = {k: v for k, v in book_data.items()
                                  if k not in ['already_exists', 'existing_id']}

                # Create book
                Book.objects.create(**clean_book_data)
                created_count += 1

            except Exception as e:
                failed_count += 1
                messages.error(request, f'Fehler beim Importieren: {e}')

        # Show success message
        if created_count > 0:
            messages.success(
                request,
                f'{created_count} Buch/Bücher erfolgreich importiert!'
            )
        if skipped_count > 0:
            messages.info(
                request,
                f'{skipped_count} Buch/Bücher übersprungen (bereits vorhanden).'
            )
        if failed_count > 0:
            messages.error(
                request,
                f'{failed_count} Buch/Bücher konnten nicht importiert werden.'
            )

        # Clear session
        if 'dnb_search_results' in request.session:
            del request.session['dnb_search_results']

        return redirect('books:list')


class BookRateView(LoginRequiredMixin, View):
    """Rate a book (1-5 stars) with optional review"""

    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        form = BookRatingForm(request.POST)

        if form.is_valid():
            rating_obj, created = BookRating.objects.update_or_create(
                user=request.user,
                book=book,
                defaults={
                    'rating': form.cleaned_data['rating'],
                    'review_text': form.cleaned_data['review_text'],
                }
            )

            action = 'erstellt' if created else 'aktualisiert'
            messages.success(request, f'Deine Bewertung wurde {action}!')
        else:
            messages.error(request, 'Fehler beim Speichern der Bewertung.')

        return redirect('books:detail', pk=pk)


class BookReadStatusToggleView(LoginRequiredMixin, View):
    """Toggle read status for a book"""

    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        form = BookReadStatusForm(request.POST)

        if form.is_valid():
            is_read = form.cleaned_data['is_read']
            read_date = form.cleaned_data.get('read_date')

            # Default to today if marked as read but no date provided
            if is_read and not read_date:
                read_date = timezone.now().date()
            elif not is_read:
                read_date = None

            status_obj, created = BookReadStatus.objects.update_or_create(
                user=request.user,
                book=book,
                defaults={
                    'is_read': is_read,
                    'read_date': read_date
                }
            )

            if is_read:
                messages.success(request, 'Buch als gelesen markiert!')
            else:
                messages.info(request, 'Gelesen-Status entfernt.')

        return redirect('books:detail', pk=pk)


class BookTimelineView(LoginRequiredMixin, ListView):
    """Display read books on a horizontal timeline"""
    template_name = 'books/book_timeline.html'
    context_object_name = 'read_statuses'

    def get_queryset(self):
        return BookReadStatus.objects.filter(
            user=self.request.user,
            is_read=True,
            read_date__isnull=False
        ).select_related('book').order_by('read_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Load user's ratings as dict {book_id: rating}
        ratings = dict(BookRating.objects.filter(
            user=self.request.user
        ).values_list('book_id', 'rating'))
        # Attach rating to each status
        for status in context['read_statuses']:
            status.user_rating = ratings.get(status.book_id)
        return context
