from __future__ import annotations

from datetime import date, timedelta

from asgiref.sync import async_to_sync
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import AnonymousUser, Group, User
from django.test import TransactionTestCase, override_settings

from rockon.bands.models import Band, BandReaction
from rockon.bands.routing import websocket_urlpatterns
from rockon.base.models import Event

# TransactionTestCase (not TestCase) is required here: the consumer's DB calls
# run through database_sync_to_async on a separate thread, which can't see
# rows created inside TestCase's per-test atomic transaction.


@override_settings(
    CHANNEL_LAYERS={'default': {'BACKEND': 'channels.layers.InMemoryChannelLayer'}}
)
class BandReactionConsumerTests(TransactionTestCase):
    def setUp(self):
        self.application = URLRouter(websocket_urlpatterns)
        self.crew_group = Group.objects.create(name='crew')
        self.crew_user = User.objects.create_user(
            username='crew-user', email='crew@example.com', password='secret'
        )
        self.crew_user.groups.add(self.crew_group)
        self.other_user = User.objects.create_user(
            username='other-user', email='other@example.com', password='secret'
        )
        start = date(2026, 7, 1)
        event = Event.objects.create(
            name='Rocktreff 2026',
            slug='rocktreff-2026',
            description='desc',
            start=start,
            end=start + timedelta(days=2),
            setup_start=start - timedelta(days=2),
            setup_end=start - timedelta(days=1),
            opening=start,
            closing=start + timedelta(days=1),
            teardown_start=start + timedelta(days=2),
            teardown_end=start + timedelta(days=3),
            location='Berlin',
        )
        self.band = Band.objects.create(event=event, name='Testband')

    def _communicator(self, user=None):
        communicator = WebsocketCommunicator(
            self.application, f'/ws/bands/{self.band.id}/reactions/'
        )
        communicator.scope['user'] = user if user is not None else AnonymousUser()
        return communicator

    def test_anonymous_connection_rejected(self):
        async def run():
            communicator = self._communicator()
            connected, _ = await communicator.connect()
            self.assertFalse(connected)
            await communicator.disconnect()

        async_to_sync(run)()

    def test_non_crew_member_rejected(self):
        async def run():
            communicator = self._communicator(self.other_user)
            connected, _ = await communicator.connect()
            self.assertFalse(connected)
            await communicator.disconnect()

        async_to_sync(run)()

    def test_crew_member_connects(self):
        async def run():
            communicator = self._communicator(self.crew_user)
            connected, _ = await communicator.connect()
            self.assertTrue(connected)
            await communicator.disconnect()

        async_to_sync(run)()

    def test_invalid_emoji_rejected(self):
        async def run():
            communicator = self._communicator(self.crew_user)
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            await communicator.send_json_to({'emoji': 'not-an-emoji'})
            response = await communicator.receive_json_from()
            self.assertIn('error', response)

            await communicator.disconnect()

        async_to_sync(run)()
        self.assertEqual(BandReaction.objects.count(), 0)

    def test_valid_emoji_persists_and_broadcasts(self):
        async def run():
            communicator = self._communicator(self.crew_user)
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

            await communicator.send_json_to({'emoji': '🔥'})
            response = await communicator.receive_json_from()
            self.assertEqual(response['emoji'], '🔥')
            self.assertEqual(response['user_id'], self.crew_user.id)

            await communicator.disconnect()

        async_to_sync(run)()
        self.assertEqual(BandReaction.objects.count(), 1)
        reaction = BandReaction.objects.get()
        self.assertEqual(reaction.emoji, '🔥')
        self.assertEqual(reaction.user, self.crew_user)
        self.assertEqual(reaction.band, self.band)

    def test_broadcast_reaches_other_connected_client(self):
        async def run():
            sender = self._communicator(self.crew_user)
            listener = self._communicator(self.crew_user)

            self.assertTrue((await sender.connect())[0])
            self.assertTrue((await listener.connect())[0])

            await sender.send_json_to({'emoji': '🤘'})
            # both the sender and the other connected client receive the broadcast
            await sender.receive_json_from()
            listener_message = await listener.receive_json_from()
            self.assertEqual(listener_message['emoji'], '🤘')

            await sender.disconnect()
            await listener.disconnect()

        async_to_sync(run)()
