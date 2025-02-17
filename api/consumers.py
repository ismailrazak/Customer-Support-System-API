import json
from email.policy import default

import redis
from asgiref.sync import async_to_sync
from channels.exceptions import StopConsumer
from channels.generic.websocket import WebsocketConsumer
from decouple import config
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from api.models import Conversation, CustomerSupportRepProfile, Message

r = redis.Redis(
    host=config("REDIS_HOST", default="redis"),
    port=config("REDIS_PORT", default=6379),
    db=0,
    decode_responses=True,
)


class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"chat_{self.room_name}"
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.user = self.scope["user"]
        self.assign_customer_to_customer_rep()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name, self.channel_name
        )

    def assign_customer_to_customer_rep(self):
        """

        Validates the customer is the same one in the convo first.
        Then checks if a customer_rep is assigned to it or not.if not ,assign a customer_rep.
        if all customer_reps are busy, return message busy and add it to the waiting queue.
        if customer_rep is trying to connect, validate him too.

        """
        try:
            self.conversation = Conversation.objects.get(id=self.room_name)
        except ObjectDoesNotExist:
            self.close()
            raise StopConsumer()
        if hasattr(self.user, "customer_profile"):
            if self.user.customer_profile == self.conversation.customer:
                if not self.conversation.customer_rep:
                    free_customer_rep = CustomerSupportRepProfile.objects.filter(
                        max_capacity__gt=0
                    ).first()
                    if not free_customer_rep:
                        self.accept()
                        self.send(
                            text_data=json.dumps(
                                {
                                    "message": "Customer Representatives are busy for now. Please wait for some time."
                                }
                            )
                        )
                        if r.sismember("conversation_id:set:id", self.room_name) != 1:
                            print(r.llen("conversation_id:id"))
                            r.lpush("conversation_id:id", self.room_name)
                            r.sadd("conversation_id:set:id", self.room_name)

                        self.close()
                        raise StopConsumer()
                    self.conversation.customer_rep = free_customer_rep
                    free_customer_rep.max_capacity = F("max_capacity") - 1
                    free_customer_rep.save()
                    self.conversation.save()
                self.accept()
        if hasattr(self.user, "customer_support_profile"):
            if self.user.customer_support_profile == self.conversation.customer_rep:
                self.accept()

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        self.chat_close_and_redirect(text_data_json)
        chat_type = {"type": "chat_message"}
        return_dict = {**chat_type, **text_data_json}
        Message.objects.create(
            text=text_data_json["message"],
            user=self.user,
            conversation=self.conversation,
        )
        async_to_sync(self.channel_layer.group_send)(self.group_name, return_dict)

    def chat_close_and_redirect(self, text_data_json):
        """

        closes the chat connection when a json message with key close_chat is received.
        Used by customer_rep to close chat and initiate the assignment of next customer from the waiting queue.

        :param text_data_json:
        :return:
        """
        close_chat = text_data_json.get("close_chat")
        if hasattr(self.user, "customer_support_profile") and bool(close_chat):
            self.conversation.customer_rep = None
            self.conversation.save()
            conversation_id = r.rpop("conversation_id:id")

            print(conversation_id)
            if conversation_id:
                r.srem("conversation_id:set:id", conversation_id)
                self.send(text_data=json.dumps({"redirect_id": conversation_id}))
                conversation = Conversation.objects.get(id=conversation_id)
                conversation.customer_rep = self.user.customer_support_profile
                conversation.save()
            else:
                self.user.customer_support_profile.max_capacity = F("max_capacity") + 1
                self.user.customer_support_profile.save()
            self.close()
            raise StopConsumer()

    def chat_message(self, event):
        text_data = event.copy()
        text_data_type = text_data.pop("type")
        text_data_json = json.dumps(text_data)

        self.send(text_data=text_data_json)
