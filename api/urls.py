from django.urls import path

from . import views

urlpatterns = [
    path("register_customer/", views.RegisterCustomerView.as_view()),
    path("register_customer_rep/", views.RegisterCustomerSupportRepView.as_view()),
    path("conversations/", views.ConversationListView.as_view()),
    path("conversations/<int:pk>/", views.ConversationDetailView.as_view()),
]
