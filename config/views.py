from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime


def home(request):
    """Dashboard home page with stats and recent activity"""
    context = {
        'book_count': 0,
        'document_count': 0,
        'todo_count': 0,
        'collection_count': 0,
        'recent_books': [],
        'recent_todos': [],
    }

    # Get counts if user is authenticated
    if request.user.is_authenticated:
        from apps.books.models import Book, BookRating
        from apps.documents.models import Document
        from apps.todos.models import Todo
        from apps.user_collections.models import Collection

        context['book_count'] = Book.objects.count()
        context['document_count'] = Document.objects.filter(user=request.user).count()
        context['todo_count'] = Todo.objects.filter(user=request.user, status__in=['PLANNED', 'IN_PROGRESS']).count()
        context['collection_count'] = Collection.objects.filter(user=request.user).count()

        # Recent books (last 5 added)
        context['recent_books'] = Book.objects.order_by('-created_at')[:5]

        # Recent todos (last 5 active)
        context['recent_todos'] = Todo.objects.filter(
            user=request.user,
            status__in=['PLANNED', 'IN_PROGRESS']
        ).order_by('-created_at')[:5]

    # Greeting based on time of day
    hour = datetime.now().hour
    if hour < 12:
        context['greeting'] = 'Guten Morgen'
    elif hour < 18:
        context['greeting'] = 'Guten Tag'
    else:
        context['greeting'] = 'Guten Abend'

    return render(request, 'home.html', context)


def logout_view(request):
    """Einfache Logout-View (akzeptiert GET)"""
    logout(request)
    messages.success(request, 'Du wurdest erfolgreich abgemeldet.')
    return redirect('home')
