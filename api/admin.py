from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from api.models import (
    Conversation,
    CustomerProfile,
    CustomerSupportRepProfile,
    Message,
    User,
)

admin.site.register(User, UserAdmin)
admin.site.register(Message, ModelAdmin)
admin.site.register(Conversation, ModelAdmin)
admin.site.register(CustomerProfile, ModelAdmin)
admin.site.register(CustomerSupportRepProfile, ModelAdmin)
