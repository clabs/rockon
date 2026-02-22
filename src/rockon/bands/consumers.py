from __future__ import annotations

import json
import logging

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models.band_reaction import ALLOWED_EMOJIS

logger = logging.getLogger(__name__)


class BandReactionConsumer(AsyncJsonWebsocketConsumer):
    """WebSocket consumer for live emoji reactions on a band."""

    async def connect(self):
        self.band_id = self.scope['url_route']['kwargs']['band_id']
        self.group_name = f'band_reactions_{self.band_id}'
        user = self.scope.get('user')

        if not user or user.is_anonymous:
            await self.close()
            return

        is_crew = await self._is_crew_member(user)
        if not is_crew:
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        emoji = content.get('emoji')
        if emoji not in ALLOWED_EMOJIS:
            await self.send_json({'error': 'Invalid emoji'})
            return

        user = self.scope['user']
        reaction = await self._save_reaction(user, emoji)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'reaction.message',
                'emoji': emoji,
                'user_name': await self._get_display_name(user),
                'user_id': user.id,
                'timestamp': reaction.created_at.isoformat(),
            },
        )

    async def reaction_message(self, event):
        """Send reaction broadcast to individual WebSocket client."""
        await self.send_json(
            {
                'emoji': event['emoji'],
                'user_name': event['user_name'],
                'user_id': event['user_id'],
                'timestamp': event['timestamp'],
            }
        )

    @database_sync_to_async
    def _is_crew_member(self, user):
        return user.groups.filter(name='crew').exists()

    @database_sync_to_async
    def _save_reaction(self, user, emoji):
        from .models import BandReaction

        return BandReaction.objects.create(
            band_id=self.band_id,
            user=user,
            emoji=emoji,
        )

    @database_sync_to_async
    def _get_display_name(self, user):
        name = f'{user.first_name} {user.last_name}'.strip()
        return name or user.username
