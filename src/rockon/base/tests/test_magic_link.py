from __future__ import annotations

import asyncio
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from rockon.base.models import MagicLink


class MagicLinkTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='magic-user',
            email='magic@example.com',
            password='secret',
            first_name='Magic',
        )

    @patch('rockon.base.models.magic_link.send_mail_async')
    @patch('rockon.base.models.magic_link.loader.get_template')
    def test_create_and_send_persists_link_and_sends_mail(
        self, get_template, send_mail_async
    ):
        get_template.return_value.render.return_value = '<p>mail</p>'

        MagicLink.create_and_send(self.user)

        magic_link = MagicLink.objects.get(user=self.user)
        self.assertGreater(magic_link.expires_at, now() + timedelta(days=27))
        self.assertLess(magic_link.expires_at, now() + timedelta(days=29))
        send_mail_async.assert_called_once()
        self.assertEqual(
            send_mail_async.call_args.kwargs['recipient_list'],
            ['magic@example.com'],
        )
        self.assertIn(
            reverse('base:login_token', kwargs={'token': magic_link.token}),
            send_mail_async.call_args.kwargs['message'],
        )
        self.assertIn(settings.DOMAIN, send_mail_async.call_args.kwargs['message'])

    @patch('rockon.base.models.magic_link.send_mail_async')
    @patch('rockon.base.models.magic_link.loader.get_template')
    def test_create_and_send_renders_mail_template_with_link_context(
        self, get_template, send_mail_async
    ):
        get_template.return_value.render.return_value = '<p>mail</p>'

        MagicLink.create_and_send(self.user)

        magic_link = MagicLink.objects.get(user=self.user)
        extra_context = get_template.return_value.render.call_args.args[0]
        self.assertEqual(extra_context['name'], 'Magic')
        self.assertEqual(extra_context['recipient'], 'magic@example.com')
        self.assertEqual(extra_context['magic_link_token'], magic_link.token)
        self.assertEqual(
            extra_context['magic_link'],
            f'{settings.DOMAIN}{reverse("base:login_token", kwargs={"token": magic_link.token})}',
        )
        send_mail_async.assert_called_once()

    @patch(
        'rockon.base.models.magic_link.MagicLink.objects.acreate',
        new_callable=AsyncMock,
    )
    @patch('asyncio.to_thread', new_callable=AsyncMock)
    @patch('rockon.base.models.magic_link.loader.get_template')
    def test_acreate_and_send_uses_async_mail_dispatch(
        self, get_template, to_thread, acreate
    ):
        get_template.return_value.render.return_value = '<p>mail</p>'
        fake_link = SimpleNamespace(
            token='00000000-0000-0000-0000-000000000123',
            expires_at=now() + timedelta(days=28),
        )
        acreate.return_value = fake_link

        async def run_test():
            await MagicLink.acreate_and_send(self.user)

        asyncio.run(run_test())

        acreate.assert_awaited_once()
        to_thread.assert_awaited_once()
        self.assertEqual(to_thread.await_args.args[0].__name__, 'send_mail_async')

    def test_magic_link_string_representation_uses_id(self):
        magic_link = MagicLink.objects.create(
            user=self.user,
            expires_at=now() + timedelta(days=1),
        )

        self.assertEqual(str(magic_link), str(magic_link.id))
