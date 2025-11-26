# ========================================
# FILE: todos/models.py
# ========================================

from django.db import models
from django.utils import timezone

class Todo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['is_resolved', 'due_date', '-created_at']

    def __str__(self):
        return self.title

    def is_overdue(self):
        if self.due_date and not self.is_resolved:
            return self.due_date < timezone.now().date()
        return False
