import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("connected", flush=True)
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def receive(self, text_data):
        pass

    async def weather(self, event):
        try:
            message = event['message']
            await self.send(text_data=json.dumps({
                'type': 'weather',
                'message': message,
            }))
        except Exception as e:
            print("error", e, flush=True)