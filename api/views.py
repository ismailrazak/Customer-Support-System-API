from rest_framework.generics import ListCreateAPIView,CreateAPIView,RetrieveAPIView
from .models import CustomerSupportRepProfile,CustomerProfile,Message,Conversation
from .serializers import ConversationListSerializer,ConversationDetailSerializer,CustomerProfileSerializer,CustomerSupportRepProfileSerializer

class RegisterCustomerView(CreateAPIView):
    queryset = CustomerProfile.objects.all()
    serializer_class = CustomerProfileSerializer

class RegisterCustomerSupportRepView(CreateAPIView):
    queryset = CustomerSupportRepProfile.objects.all()
    serializer_class = CustomerSupportRepProfileSerializer

class ConversationListView(ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if hasattr(user,'customer_support_profile'):
            return Conversation.objects.filter(customer_rep=user.customer_support_profile)
        return []

    serializer_class = ConversationListSerializer

class ConversationDetailView(RetrieveAPIView):
    queryset = Conversation.objects.all()
    serializer_class = ConversationDetailSerializer




