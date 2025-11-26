from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Todo
from .forms import TodoForm


# ========================================
# MODEL TESTS
# ========================================

class TodoModelTest(TestCase):
    """Test cases for the Todo model"""

    def setUp(self):
        """Create test fixtures"""
        self.todo = Todo.objects.create(
            title="Test Todo",
            description="Test Description",
            due_date=timezone.now().date() + timedelta(days=1)
        )

    def test_todo_creation(self):
        """Test that a todo can be created with required fields"""
        self.assertEqual(self.todo.title, "Test Todo")
        self.assertEqual(self.todo.description, "Test Description")
        self.assertFalse(self.todo.is_resolved)

    def test_todo_str_method(self):
        """Test the string representation of a todo"""
        self.assertEqual(str(self.todo), "Test Todo")

    def test_todo_defaults(self):
        """Test that default values are set correctly"""
        todo = Todo.objects.create(title="Another Todo")
        self.assertFalse(todo.is_resolved)
        self.assertEqual(todo.description, "")
        self.assertIsNone(todo.due_date)

    def test_is_overdue_with_past_date_unresolved(self):
        """Test is_overdue returns True for unresolved todos with past due date"""
        past_date = timezone.now().date() - timedelta(days=1)
        todo = Todo.objects.create(
            title="Overdue Todo",
            due_date=past_date,
            is_resolved=False
        )
        self.assertTrue(todo.is_overdue())

    def test_is_overdue_with_future_date(self):
        """Test is_overdue returns False for todos with future due date"""
        future_date = timezone.now().date() + timedelta(days=1)
        todo = Todo.objects.create(
            title="Future Todo",
            due_date=future_date,
            is_resolved=False
        )
        self.assertFalse(todo.is_overdue())

    def test_is_overdue_with_resolved_todo(self):
        """Test is_overdue returns False for resolved todos even with past date"""
        past_date = timezone.now().date() - timedelta(days=1)
        todo = Todo.objects.create(
            title="Resolved Overdue Todo",
            due_date=past_date,
            is_resolved=True
        )
        self.assertFalse(todo.is_overdue())

    def test_is_overdue_without_due_date(self):
        """Test is_overdue returns False for todos without a due date"""
        todo = Todo.objects.create(
            title="Todo Without Due Date",
            is_resolved=False
        )
        self.assertFalse(todo.is_overdue())

    def test_todo_ordering(self):
        """Test that todos are ordered correctly"""
        # Clear existing todos
        Todo.objects.all().delete()
        
        unresolved = Todo.objects.create(title="Unresolved", is_resolved=False)
        resolved = Todo.objects.create(title="Resolved", is_resolved=True)
        
        todos = list(Todo.objects.all())
        # Unresolved should come before resolved
        self.assertEqual(todos[0].title, "Unresolved")
        self.assertEqual(todos[1].title, "Resolved")

    def test_auto_timestamps(self):
        """Test that created_at and updated_at are set automatically"""
        todo = Todo.objects.create(title="Timestamp Test")
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)


# ========================================
# FORM TESTS
# ========================================

class TodoFormTest(TestCase):
    """Test cases for the TodoForm"""

    def test_form_valid_with_all_fields(self):
        """Test form is valid with all fields"""
        data = {
            'title': 'Test Todo',
            'description': 'Test Description',
            'due_date': '2025-12-31',
            'is_resolved': False
        }
        form = TodoForm(data)
        self.assertTrue(form.is_valid())

    def test_form_valid_with_required_fields_only(self):
        """Test form is valid with only required fields"""
        data = {
            'title': 'Test Todo',
            'description': '',
            'due_date': '',
            'is_resolved': False
        }
        form = TodoForm(data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_without_title(self):
        """Test form is invalid without title"""
        data = {
            'title': '',
            'description': 'Test Description',
            'due_date': '2025-12-31',
            'is_resolved': False
        }
        form = TodoForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_title_max_length(self):
        """Test form title field has max length validation"""
        data = {
            'title': 'x' * 201,  # Exceeds max_length of 200
            'description': '',
            'due_date': '',
            'is_resolved': False
        }
        form = TodoForm(data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_form_fields_included(self):
        """Test that the form includes all required fields"""
        form = TodoForm()
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('due_date', form.fields)
        self.assertIn('is_resolved', form.fields)

    def test_form_widgets(self):
        """Test that form widgets are configured correctly"""
        form = TodoForm()
        self.assertEqual(form.fields['title'].widget.__class__.__name__, 'TextInput')
        self.assertEqual(form.fields['description'].widget.__class__.__name__, 'Textarea')
        self.assertEqual(form.fields['due_date'].widget.__class__.__name__, 'DateInput')


# ========================================
# VIEW TESTS
# ========================================

class TodoListViewTest(TestCase):
    """Test cases for the TodoListView"""

    def setUp(self):
        """Create test fixtures"""
        self.client = Client()
        self.url = reverse('todo_list')
        self.todo1 = Todo.objects.create(title="Todo 1")
        self.todo2 = Todo.objects.create(title="Todo 2")

    def test_list_view_status_code(self):
        """Test that list view returns 200 status code"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_list_view_template_used(self):
        """Test that list view uses correct template"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'todos/todo_list.html')

    def test_list_view_context(self):
        """Test that list view includes todos in context"""
        response = self.client.get(self.url)
        self.assertIn('todos', response.context)

    def test_list_view_displays_all_todos(self):
        """Test that list view displays all todos"""
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['todos']), 2)
        self.assertIn(self.todo1, response.context['todos'])
        self.assertIn(self.todo2, response.context['todos'])

    def test_list_view_empty(self):
        """Test that list view works when no todos exist"""
        Todo.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['todos']), 0)


class TodoCreateViewTest(TestCase):
    """Test cases for the TodoCreateView"""

    def setUp(self):
        """Create test fixtures"""
        self.client = Client()
        self.url = reverse('todo_create')

    def test_create_view_get_status_code(self):
        """Test that create view GET returns 200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_create_view_template_used(self):
        """Test that create view uses correct template"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'todos/todo_form.html')

    def test_create_view_form_in_context(self):
        """Test that create view includes form in context"""
        response = self.client.get(self.url)
        self.assertIn('form', response.context)

    def test_create_todo_post(self):
        """Test that POST creates a new todo"""
        data = {
            'title': 'New Todo',
            'description': 'Test Description',
            'due_date': '2025-12-31',
            'is_resolved': False
        }
        response = self.client.post(self.url, data)
        self.assertEqual(Todo.objects.count(), 1)
        self.assertEqual(Todo.objects.first().title, 'New Todo')

    def test_create_todo_redirect(self):
        """Test that POST redirects to todo list"""
        data = {
            'title': 'New Todo',
            'description': '',
            'due_date': '',
            'is_resolved': False
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('todo_list'))

    def test_create_todo_invalid_data(self):
        """Test that POST with invalid data doesn't create todo"""
        data = {
            'title': '',  # Empty title - invalid
            'description': 'Test',
            'due_date': '',
            'is_resolved': False
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Todo.objects.count(), 0)


class TodoUpdateViewTest(TestCase):
    """Test cases for the TodoUpdateView"""

    def setUp(self):
        """Create test fixtures"""
        self.client = Client()
        self.todo = Todo.objects.create(title="Original Title", description="Original")
        self.url = reverse('todo_update', args=[self.todo.pk])

    def test_update_view_get_status_code(self):
        """Test that update view GET returns 200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_update_view_template_used(self):
        """Test that update view uses correct template"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'todos/todo_form.html')

    def test_update_view_initial_data(self):
        """Test that update view shows existing data"""
        response = self.client.get(self.url)
        self.assertEqual(response.context['form'].instance, self.todo)

    def test_update_todo_post(self):
        """Test that POST updates the todo"""
        data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'due_date': '',
            'is_resolved': False
        }
        response = self.client.post(self.url, data)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Title')
        self.assertEqual(self.todo.description, 'Updated Description')

    def test_update_todo_redirect(self):
        """Test that POST redirects to todo list"""
        data = {
            'title': 'Updated',
            'description': '',
            'due_date': '',
            'is_resolved': False
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(response, reverse('todo_list'))

    def test_update_nonexistent_todo(self):
        """Test that updating nonexistent todo returns 404"""
        url = reverse('todo_update', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TodoDeleteViewTest(TestCase):
    """Test cases for the TodoDeleteView"""

    def setUp(self):
        """Create test fixtures"""
        self.client = Client()
        self.todo = Todo.objects.create(title="Todo to Delete")
        self.url = reverse('todo_delete', args=[self.todo.pk])

    def test_delete_view_get_status_code(self):
        """Test that delete view GET returns 200"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_delete_view_template_used(self):
        """Test that delete view uses correct template"""
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'todos/todo_confirm_delete.html')

    def test_delete_view_context(self):
        """Test that delete view includes todo in context"""
        response = self.client.get(self.url)
        self.assertEqual(response.context['object'], self.todo)

    def test_delete_todo_post(self):
        """Test that POST deletes the todo"""
        response = self.client.post(self.url)
        self.assertEqual(Todo.objects.count(), 0)

    def test_delete_todo_redirect(self):
        """Test that POST redirects to todo list"""
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse('todo_list'))

    def test_delete_nonexistent_todo(self):
        """Test that deleting nonexistent todo returns 404"""
        url = reverse('todo_delete', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TodoToggleViewTest(TestCase):
    """Test cases for the toggle_resolve view"""

    def setUp(self):
        """Create test fixtures"""
        self.client = Client()
        self.todo = Todo.objects.create(title="Todo", is_resolved=False)
        self.url = reverse('todo_toggle', args=[self.todo.pk])

    def test_toggle_resolve_unresolved_to_resolved(self):
        """Test toggling unresolved todo to resolved"""
        self.assertFalse(self.todo.is_resolved)
        response = self.client.get(self.url)
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.is_resolved)

    def test_toggle_resolve_resolved_to_unresolved(self):
        """Test toggling resolved todo to unresolved"""
        self.todo.is_resolved = True
        self.todo.save()
        response = self.client.get(self.url)
        self.todo.refresh_from_db()
        self.assertFalse(self.todo.is_resolved)

    def test_toggle_resolve_redirect(self):
        """Test that toggle redirects to todo list"""
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('todo_list'))

    def test_toggle_nonexistent_todo(self):
        """Test that toggling nonexistent todo returns 404"""
        url = reverse('todo_toggle', args=[9999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
