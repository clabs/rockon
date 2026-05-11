import logging

from django.core.exceptions import PermissionDenied


class StripPermissionDeniedTraceback(logging.Filter):
    def filter(self, record):
        if record.exc_info and issubclass(record.exc_info[0], PermissionDenied):
            record.exc_info = None
            record.exc_text = None
        return True
