from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'email',
        'username',
        'is_active',
        'is_staff',
        'is_superuser'
    )
    search_fields = (
        'email',
        'username'
    )
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (
            'Персональная информация', {
                'fields': ('first_name', 'last_name')
            }
        ),
        ('Разрешения',
         {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',
                       'is_staff', 'is_active')
        }),
    )
    ordering = ('username',)
