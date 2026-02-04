from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Document
from .forms import DocumentForm
from apps.user_collections.models import Collection


class DocumentListView(LoginRequiredMixin, ListView):
    """Display all documents for the current user"""
    model = Document
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'
    paginate_by = 20

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)


class DocumentDetailView(LoginRequiredMixin, DetailView):
    """Display document details"""
    model = Document
    template_name = 'documents/document_detail.html'
    context_object_name = 'document'

    def get_queryset(self):
        # Users can only view their own documents
        return Document.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add user collections
        context['user_collections'] = Collection.objects.filter(
            user=self.request.user
        ).order_by('name')
        context['document_content_type_id'] = ContentType.objects.get_for_model(Document).id

        return context


class DocumentCreateView(LoginRequiredMixin, CreateView):
    """Create a new document"""
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Dokument "{form.instance.title}" erfolgreich erstellt!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('documents:detail', kwargs={'pk': self.object.pk})


class DocumentUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing document"""
    model = Document
    form_class = DocumentForm
    template_name = 'documents/document_form.html'

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f'Dokument "{form.instance.title}" erfolgreich aktualisiert!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('documents:detail', kwargs={'pk': self.object.pk})


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a document"""
    model = Document
    template_name = 'documents/document_confirm_delete.html'
    success_url = reverse_lazy('documents:list')

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        document = self.get_object()
        messages.success(request, f'Dokument "{document.title}" erfolgreich gelöscht!')
        return super().delete(request, *args, **kwargs)
