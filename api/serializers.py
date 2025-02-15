from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomerSupportRepProfile,CustomerProfile,Conversation,Message

class UserSerializer(serializers.ModelSerializer):
    # todo add reverse cusotmerprofile ?
    class Meta:
        model = get_user_model()
        fields = ['id','username','first_name','last_name','email']

class CustomerSupportRepProfileSerializer(serializers.Serializer):
    user = UserSerializer()

    password = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomerSupportRepProfile
        fields = ['id', "password", "password1",'user']

    def validate(self, data):
        password = data.get("password")
        password1 = data.get("password1")
        if password != password1:
            raise serializers.ValidationError({"error": "passwords do not match."})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        password1 = validated_data.pop("password1")
        phone_number = validated_data.pop('phone_number')
        user = validated_data.pop('user')
        user = get_user_model().objects.create(**user)
        user.set_password(password1)
        user.save()
        customer_support_rep_profile = CustomerSupportRepProfile.objects.create(user=user)

        return customer_support_rep_profile


class CustomerProfileSerializer(serializers.Serializer):
    user = UserSerializer()
    phone_number = serializers.IntegerField()
    password  = serializers.CharField(write_only=True)
    password1 = serializers.CharField(write_only=True)

    class Meta:
        fields = ['id', "password", "password1",'user','phone_number']

    def validate(self, data):
        password = data.get("password")
        password1 = data.get("password1")
        if password != password1:
            raise serializers.ValidationError({"error": "passwords do not match."})
        return data

    def create(self, validated_data):
        password = validated_data.pop("password")
        password1 = validated_data.pop("password1")
        phone_number = validated_data.pop('phone_number')
        user = validated_data.pop('user')
        user = get_user_model().objects.create(**user)
        user.set_password(password1)
        user.save()
        customer_profile =CustomerProfile.objects.create(phone_number=phone_number,user=user)

        return customer_profile




class MessageSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    class Meta:
        model = Message
        fields = ['id','text','user','conversation','timestamp']

class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True)

    class Meta:
        models = Conversation
        fields= ['id','customer','customer_rep','messages','created_at']


class ConversationListSerializer(serializers.ModelSerializer):
    latest_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'customer', 'customer_rep', 'latest_message', 'created_at']

    def get_latest_message(self,instance):
        latest_message = instance.messages.first()
        return MessageSerializer(latest_message).data



