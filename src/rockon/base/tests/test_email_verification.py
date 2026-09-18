from __future__ import annotations

from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from rockon.base.models import EmailVerification


class EmailVerificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='verify-user',
            email='old@example.com',
            password='secret',
            first_name='Verify',
        )

    @patch('rockon.base.models.email_verification.send_mail_async')
    @patch('rockon.base.models.email_verification.loader.get_template')
    def test_create_and_send_with_new_email_sends_to_new_address(
        self, get_template, send_mail_async
    ):
        get_template.return_value.render.return_value = '<p>mail</p>'

        EmailVerification.create_and_send(self.user, new_email='new@example.com')

        send_mail_async.assert_called_once()
        self.assertEqual(
            send_mail_async.call_args.kwargs['recipient_list'],
            ['new@example.com'],
        )

    @patch('rockon.base.models.email_verification.send_mail_async')
    @patch('rockon.base.models.email_verification.loader.get_template')
    def test_create_and_send_without_new_email_sends_to_user_email(
        self, get_template, send_mail_async
    ):
        get_template.return_value.render.return_value = '<p>mail</p>'

        EmailVerification.create_and_send(self.user)

        send_mail_async.assert_called_once()
        self.assertEqual(
            send_mail_async.call_args.kwargs['recipient_list'],
            ['old@example.com'],
        )
