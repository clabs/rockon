from __future__ import annotations

from django.apps import AppConfig


class BaseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rockon.base'
    label = 'rockonbase'

    def ready(self):
        from django_q.signals import post_execute_in_worker

        from rockon.library.task_metrics import report_task_result

        post_execute_in_worker.connect(report_task_result)
