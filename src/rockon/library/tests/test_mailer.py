from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from rockon.tools.models import LinkShortener
from rockon.library.mailer import get_admin_url, send_mail_async


class MailerTests(TestCase):
    @patch('django_q.tasks.async_task')
    def test_send_mail_async_enqueues_one_task_per_recipient(self, async_task):
        send_mail_async(
            subject='Test subject',
            message='Test message',
            recipient_list=['one@example.com', 'two@example.com'],
            html_message='<p>mail</p>',
            timeout=15,
        )

        self.assertEqual(async_task.call_count, 2)
        first_kwargs = async_task.call_args_list[0].kwargs
        second_kwargs = async_task.call_args_list[1].kwargs
        self.assertEqual(first_kwargs['recipient_list'], ['one@example.com'])
        self.assertEqual(second_kwargs['recipient_list'], ['two@example.com'])
        self.assertEqual(first_kwargs['timeout'], 15)
        self.assertEqual(second_kwargs['timeout'], 15)

    @patch('rockon.library.mailer.logger.exception')
    @patch('django_q.tasks.async_task', side_effect=RuntimeError('broker down'))
    def test_send_mail_async_logs_and_swallows_enqueue_errors(
        self, _async_task, logger_exception
    ):
        send_mail_async(
            subject='Test subject',
            message='Test message',
            recipient_list=['one@example.com'],
        )

        logger_exception.assert_called_once()

    def test_get_admin_url_builds_absolute_admin_change_url(self):
        short_link = LinkShortener.objects.create(
            url='https://example.com/target',
            slug='admin-test',
            comment='admin',
        )

        admin_url = get_admin_url(short_link)

        self.assertTrue(admin_url.startswith('http'))
        self.assertIn('/backstage/rockontools/linkshortener/', admin_url)
        self.assertTrue(admin_url.endswith(f'/{short_link.pk}/change/'))
