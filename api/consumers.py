import json

from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F

from api.models import Conversation, CustomerSupportRepProfile, Message


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"chat_{self.room_name}"
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.user = self.scope["user"]
        try:
            self.conversation = Conversation.objects.get(id=self.room_name)
        except ObjectDoesNotExist:
            self.disconnect()
        # checking if customer is from the same convo or not.
        if hasattr(self.user, "customer_profile"):
            if self.user.customer_profile == self.conversation.customer:
                # check if a customer_rep is assigned to the convo first.
                if not self.conversation.customer_rep:
                    # fetch the freest customer_rep and assign him to the convo.
                    free_customer_rep = CustomerSupportRepProfile.objects.filter(
                        max_capacity__gt=0
                    ).first()
                    # if no free customer_reps are available return busy.
                    if not free_customer_rep:
                        self.accept()
                        text_data = json.dumps({"message": "busy"})
                        self.send(text_data=text_data)
                        self.close()
                        raise StopConsumer()

                    self.conversation.customer_rep = free_customer_rep
                    # drop the max cap by 1 since the customer rep  has to handle a new customer.
                    free_customer_rep.max_capacity = F("max_capacity") - 1
                    free_customer_rep.save()
                    self.conversation.save()
                self.accept()
        # check if the customer_rep is same as the convo rep.
        if hasattr(self.user, "customer_support_profile"):
            if self.user.customer_support_profile == self.conversation.customer_rep:
                print(self.user)
                self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        close_chat = text_data_json.get("close_chat")
        # if a close chat text is received then it means the issue is resolved by th customer rep.
        if hasattr(self.user, "customer_support_profile") and bool(close_chat):
            self.conversation.customer_rep = None
            self.user.customer_support_profile.max_capacity = F("max_capacity") + 1
            self.user.save()
            self.close()
            raise StopConsumer()

        chat_type = {"type": "chat_message"}
        return_dict = {**chat_type, **text_data_json}
        Message.objects.create(
            text=text_data_json["message"],
            user=self.user,
            conversation=self.conversation,
        )
        async_to_sync(self.channel_layer.group_send)(self.group_name, return_dict)

    def chat_message(self, event):
        text_data = event.copy()
        text_data_type = text_data.pop("type")
        text_data_json = json.dumps(text_data)

        self.send(text_data=text_data_json)
