import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass


class CustomerProfile(models.Model):
    phone_number = models.PositiveIntegerField(blank=True,null=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='customer_profile')

    def __str__(self):
        return f"{self.user.username}_customer_profile"

class CustomerSupportRepProfile(models.Model):
    max_capacity = models.IntegerField(default=5)
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='customer_support_profile')

    def __str__(self):
        return f"{self.user.username}_customer_rep_profile"

class Conversation(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    customer = models.ForeignKey(CustomerProfile,on_delete=models.SET_NULL,related_name="customer_conversation",null=True,blank=True)
    customer_rep = models.ForeignKey(CustomerSupportRepProfile,on_delete=models.SET_NULL,related_name="customer_rep_conversation",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id

class Message(models.Model):
    text = models.CharField(max_length=200)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,related_name="messages",null=True,blank=True)
    conversation = models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name='messages')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.text
