from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Subscription


class SubscriptionAdmin(admin.ModelAdmin):
	list_display = ('user', 'author')

admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)