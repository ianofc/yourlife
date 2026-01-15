import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TalkioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Entrar no grupo da conversa
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Sair do grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receber mensagem do WebSocket (Front-end)
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = self.scope["user"].username if self.scope["user"].is_authenticated else "Anónimo"

        # Enviar para o grupo
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username
            }
        )

    # Receber mensagem do grupo
    async def chat_message(self, event):
        message = event['message']
        username = event['username']

        # Enviar para o WebSocket (Front-end)
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username
        }))
