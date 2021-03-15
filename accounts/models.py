from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.html import escape, mark_safe


# Create your models here.


class Department(models.Model):
    name = models.CharField(max_length=120)
    color = models.CharField(max_length=30, default='#007bff')

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)


class Level(models.Model):
    name = models.CharField(max_length=30)
    color = models.CharField(max_length=7, default='#007bff')

    def __str__(self):
        return self.name

    def get_html_badge(self):
        name = escape(self.name)
        color = escape(self.color)
        html = '<span class="badge badge-primary" style="background-color: %s">%s</span>' % (color, name)
        return mark_safe(html)

class title(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='profile', null=True)
    level = models.ForeignKey(title, on_delete=models.CASCADE, related_name='titles', null=True, blank=True)
