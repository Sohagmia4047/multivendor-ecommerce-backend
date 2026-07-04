from django.contrib import admin
from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'bio')
    search_fields = ('email', 'username')

admin.site.register(User, UserAdmin)
