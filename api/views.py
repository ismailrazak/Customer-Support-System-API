from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveAPIView

from .models import Conversation, CustomerProfile, CustomerSupportRepProfile, Message
from .serializers import (
    ConversationDetailSerializer,
    ConversationListSerializer,
    CustomerProfileSerializer,
    CustomerSupportRepProfileSerializer,
)


class RegisterCustomerView(CreateAPIView):
    permission_classes = []
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer


class RegisterCustomerSupportRepView(CreateAPIView):
    permission_classes = []
    queryset = CustomerSupportRepProfile.objects.all()
    serializer_class = CustomerSupportRepProfileSerializer


class ConversationListView(ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if hasattr(user, "customer_support_profile"):
            return Conversation.objects.filter(
                customer_rep=user.customer_support_profile
            )
        return []

    serializer_class = ConversationListSerializer


class ConversationDetailView(RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationDetailSerializer
