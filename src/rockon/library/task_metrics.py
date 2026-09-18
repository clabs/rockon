from __future__ import annotations

import sentry_sdk


def report_task_result(sender, task, **kwargs):
    """Emit a Sentry metric for every completed django-q task (success or failure)."""
    func = task.get('func')
    label = task.get('group') or (
        func if isinstance(func, str) else getattr(func, '__name__', 'unknown')
    )
    sentry_sdk.metrics.count(
        'task.result',
        1,
        attributes={'task': label, 'success': bool(task.get('success'))},
    )
