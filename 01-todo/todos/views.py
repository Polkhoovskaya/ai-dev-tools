# ========================================
# FILE: todos/views.py
# ========================================

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Todo
from .forms import TodoForm

class TodoListView(ListView):
    model = Todo
    template_name = 'todos/todo_list.html'
    context_object_name = 'todos'

class TodoCreateView(CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todo_list')

class TodoUpdateView(UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todos/todo_form.html'
    success_url = reverse_lazy('todo_list')

class TodoDeleteView(DeleteView):
    model = Todo
    template_name = 'todos/todo_confirm_delete.html'
    success_url = reverse_lazy('todo_list')

def toggle_resolve(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.is_resolved = not todo.is_resolved
    todo.save()
    return redirect('todo_list')
