from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Todo
from .forms import TodoForm


class TodoListView(LoginRequiredMixin, ListView):
    """List all todos for the current user"""
    model = Todo
    template_name = 'todos/todo_list.html'
    context_object_name = 'todos'
    paginate_by = 20

    def get_queryset(self):
        queryset = Todo.objects.filter(user=self.request.user).prefetch_related(
            'linked_items__content_type',
            'linked_items'
        )

        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['status_choices'] = Todo.STATUS_CHOICES

        # Statistics
        context['stats'] = {
            'total': Todo.objects.filter(user=self.request.user).count(),
            'planned': Todo.objects.filter(user=self.request.user, status='PLANNED').count(),
            'in_progress': Todo.objects.filter(user=self.request.user, status='IN_PROGRESS').count(),
            'completed': Todo.objects.filter(user=self.request.user, status='COMPLETED').count(),
        }

        return context


class TodoDetailView(LoginRequiredMixin, DetailView):
    """Show todo details"""
    model = Todo
    template_name = 'todos/todo_detail.html'
    context_object_name = 'todo'

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)


class TodoCreateView(LoginRequiredMixin, CreateView):
    """Create a new todo"""
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todos:list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Aufgabe erfolgreich erstellt!')
        return super().form_valid(form)


class TodoUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing todo"""
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todos:list')

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, 'Aufgabe erfolgreich aktualisiert!')
        return super().form_valid(form)


class TodoDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a todo"""
    model = Todo
    template_name = 'todos/todo_confirm_delete.html'
    success_url = reverse_lazy('todos:list')

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Aufgabe erfolgreich gelöscht!')
        return super().delete(request, *args, **kwargs)


class TodoToggleView(LoginRequiredMixin, View):
    """Toggle todo completion status"""

    def post(self, request, pk):
        todo = get_object_or_404(Todo, pk=pk, user=request.user)

        if todo.status == 'COMPLETED':
            todo.status = 'IN_PROGRESS'
            todo.completed_at = None
            messages.info(request, f'"{todo.title}" als nicht erledigt markiert.')
        else:
            todo.mark_completed()
            messages.success(request, f'"{todo.title}" als erledigt markiert!')

        todo.save()
        return redirect('todos:list')
