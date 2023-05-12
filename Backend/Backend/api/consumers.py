from channels.generic.websocket import AsyncJsonWebsocketConsumer

class NotificationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        group_name = self.scope["url_route"]["kwargs"]["group_name"]
        print("connected")
        await self.channel_layer.group_add(
            group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        group_name = self.scope["url_route"]["kwargs"]["group_name"]
        await self.channel_layer.group_discard(
            group_name,
            self.channel_name
        )

    async def receive_json(self, content, **kwargs):
        print("received json")
        await self.send_json(content)

    async def send_notification(self, event):
        print("sending notification")
        await self.send(text_data=event["notification"])
