from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from .models import Collection, CollectionItem
from .forms import CollectionForm, CollectionItemForm
from django.db.models import Count
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseForbidden
from apps.books.models import Book, BookRating, BookReadStatus

User = get_user_model()


class CollectionListView(LoginRequiredMixin, ListView):
    """Display all collections for the current user"""
    model = Collection
    template_name = 'user_collections/collection_list.html'
    context_object_name = 'collections'
    paginate_by = 12

    def get_queryset(self):
        # Get user's collections with item count annotation
        return Collection.objects.filter(
            user=self.request.user
        ).annotate(
            item_count=Count('items')
        ).prefetch_related('items')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get current tab from query parameter (default: 'collections')
        context['current_tab'] = self.request.GET.get('tab', 'collections')

        # Get rated books for the user
        rated_books = BookRating.objects.filter(
            user=self.request.user
        ).select_related('book').order_by('-updated_at')
        context['rated_books'] = rated_books

        # Get read books for the user
        read_books = BookReadStatus.objects.filter(
            user=self.request.user,
            is_read=True
        ).select_related('book').order_by('-read_date', '-updated_at')
        context['read_books'] = read_books

        return context


class CollectionDetailView(LoginRequiredMixin, DetailView):
    """Display collection details"""
    model = Collection
    template_name = 'user_collections/collection_detail.html'
    context_object_name = 'collection'

    def get_queryset(self):
        # Users can only view their own collections
        return Collection.objects.filter(user=self.request.user).prefetch_related(
            'items__content_type'
        )


class CollectionCreateView(LoginRequiredMixin, CreateView):
    """Create a new collection"""
    model = Collection
    form_class = CollectionForm
    template_name = 'user_collections/collection_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Sammlung "{form.instance.name}" erfolgreich erstellt!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('collections:detail', kwargs={'pk': self.object.pk})


class CollectionUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing collection"""
    model = Collection
    form_class = CollectionForm
    template_name = 'user_collections/collection_form.html'

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f'Sammlung "{form.instance.name}" erfolgreich aktualisiert!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('collections:detail', kwargs={'pk': self.object.pk})


class CollectionDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a collection"""
    model = Collection
    template_name = 'user_collections/collection_confirm_delete.html'
    success_url = reverse_lazy('collections:list')

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        collection = self.get_object()
        messages.success(request, f'Sammlung "{collection.name}" erfolgreich gelöscht!')
        return super().delete(request, *args, **kwargs)


class CollectionItemAddView(LoginRequiredMixin, View):
    """Add an item (book or document) to a collection"""

    def post(self, request, collection_pk, content_type_id, object_id):
        collection = get_object_or_404(
            Collection,
            pk=collection_pk,
            user=request.user
        )

        content_type = get_object_or_404(ContentType, pk=content_type_id)

        # Check if item already exists in this collection
        existing_item = CollectionItem.objects.filter(
            collection=collection,
            content_type=content_type,
            object_id=object_id
        ).first()

        if existing_item:
            messages.warning(request, 'Dieses Item ist bereits in der Sammlung!')
        else:
            # Default to WISHLIST status when adding items
            statuses = ['WISHLIST']

            CollectionItem.objects.create(
                collection=collection,
                content_type=content_type,
                object_id=object_id,
                statuses=statuses
            )
            messages.success(request, f'Item zu "{collection.name}" hinzugefügt!')

        # Redirect back to the referring page or collection detail
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
        return redirect(next_url or reverse_lazy('collections:detail', kwargs={'pk': collection_pk}))


class CollectionItemUpdateView(LoginRequiredMixin, UpdateView):
    """Update a collection item (status, notes, etc.)"""
    model = CollectionItem
    form_class = CollectionItemForm
    template_name = 'user_collections/collection_item_form.html'

    def get_queryset(self):
        return CollectionItem.objects.filter(collection__user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Item erfolgreich aktualisiert!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('collections:detail', kwargs={'pk': self.object.collection.pk})


class CollectionItemRemoveView(LoginRequiredMixin, View):
    """Remove an item from a collection"""

    def post(self, request, pk):
        item = get_object_or_404(
            CollectionItem,
            pk=pk,
            collection__user=request.user
        )

        collection_pk = item.collection.pk
        item.delete()
        messages.success(request, 'Item aus der Sammlung entfernt!')

        return redirect('collections:detail', pk=collection_pk)


class CollectionShareSettingsView(LoginRequiredMixin, TemplateView):
    """Manage sharing settings for a collection"""
    template_name = 'user_collections/collection_share_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection = get_object_or_404(
            Collection,
            pk=self.kwargs['pk'],
            user=self.request.user
        )
        context['collection'] = collection
        context['share_url'] = collection.get_share_url(self.request) if collection.is_public else None
        context['all_users'] = User.objects.exclude(pk=self.request.user.pk).order_by('username')
        context['shared_users'] = collection.shared_with.all()
        return context

    def post(self, request, pk):
        collection = get_object_or_404(
            Collection,
            pk=pk,
            user=request.user
        )

        # Handle public sharing toggle
        if 'toggle_public' in request.POST:
            collection.is_public = not collection.is_public
            collection.save()
            if collection.is_public:
                messages.success(request, f'Sammlung "{collection.name}" ist jetzt öffentlich teilbar!')
            else:
                messages.success(request, f'Öffentliche Freigabe für "{collection.name}" deaktiviert.')

        # Handle adding user to shared list
        elif 'add_user' in request.POST:
            user_id = request.POST.get('user_id')
            if user_id:
                user_to_add = get_object_or_404(User, pk=user_id)
                collection.shared_with.add(user_to_add)
                messages.success(request, f'Sammlung mit {user_to_add.username} geteilt!')

        # Handle removing user from shared list
        elif 'remove_user' in request.POST:
            user_id = request.POST.get('user_id')
            if user_id:
                user_to_remove = get_object_or_404(User, pk=user_id)
                collection.shared_with.remove(user_to_remove)
                messages.success(request, f'Freigabe für {user_to_remove.username} entfernt.')

        return redirect('collections:share_settings', pk=pk)


class SharedCollectionView(DetailView):
    """View a shared collection (read-only, no login required if public)"""
    model = Collection
    template_name = 'user_collections/shared_collection_view.html'
    context_object_name = 'collection'

    def get_object(self):
        token = self.kwargs.get('token')
        collection = get_object_or_404(Collection, share_token=token, is_public=True)
        return collection

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_shared_view'] = True
        context['is_owner'] = self.request.user.is_authenticated and self.request.user == self.object.user
        return context


class UserSharedCollectionsView(LoginRequiredMixin, ListView):
    """View collections shared with the current user"""
    model = Collection
    template_name = 'user_collections/user_shared_collections.html'
    context_object_name = 'collections'
    paginate_by = 12

    def get_queryset(self):
        # Get collections shared with the current user (excluding their own)
        return Collection.objects.filter(
            shared_with=self.request.user
        ).exclude(
            user=self.request.user
        ).annotate(
            item_count=Count('items')
        ).prefetch_related('items').order_by('-updated_at')
