from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase

from rockon.library.task_metrics import report_task_result


class TaskMetricsTests(TestCase):
    @patch('rockon.library.task_metrics.sentry_sdk.metrics.count')
    def test_report_task_result_uses_group_as_label_when_present(self, count):
        report_task_result(
            sender='django_q',
            task={
                'func': 'some.module.func',
                'group': 'encode_audio_file',
                'success': True,
            },
        )

        count.assert_called_once_with(
            'task.result',
            1,
            attributes={'task': 'encode_audio_file', 'success': True},
        )

    @patch('rockon.library.task_metrics.sentry_sdk.metrics.count')
    def test_report_task_result_falls_back_to_func_name_without_group(self, count):
        def some_func():
            pass

        report_task_result(
            sender='django_q', task={'func': some_func, 'success': False}
        )

        count.assert_called_once_with(
            'task.result',
            1,
            attributes={'task': 'some_func', 'success': False},
        )

    @patch('rockon.library.task_metrics.sentry_sdk.metrics.count')
    def test_report_task_result_falls_back_to_string_func_without_group(self, count):
        report_task_result(
            sender='django_q', task={'func': 'some.module.func', 'success': False}
        )

        count.assert_called_once_with(
            'task.result',
            1,
            attributes={'task': 'some.module.func', 'success': False},
        )
