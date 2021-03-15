from django.contrib import admin
from accounts.models import User, title, Department, Level
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.forms import UserAdminCreationForm, UserAdminChangeForm
# Register your models here.
class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'level', 'first_name', 'last_name', 'email', 'department', 'date_joined')
    list_filter = ('is_instructor','is_student')
    fieldsets = (
        (None, {'fields': ()}),
        ('Personal info', {'fields': ('username', 'level', 'first_name', 'last_name', 'email', 'department', 'date_joined', )}),
        ('Permissions', {'fields': ('is_instructor','is_active','is_student', 'is_superuser', 'is_staff',)}),
    )
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()


    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','level', 'first_name', 'last_name', 'email', 'department', 'date_joined', 'password1', 'password2', 'is_student','is_instructor','is_superuser','is_staff', 'is_active')}
        ),
    )



admin.site.register(User, UserAdmin)
admin.site.register(title)
admin.site.register(Department)
admin.site.register(Level)
