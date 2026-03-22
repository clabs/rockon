from __future__ import annotations

from django.contrib.auth.models import Group, User

VALID_ACCOUNT_CONTEXTS = ('crew', 'bands', 'exhibitors')


def assign_account_context_group(user: User, account_context: str) -> bool:
    """Assign a user to the group for a supported account context."""
    if account_context not in VALID_ACCOUNT_CONTEXTS:
        return False

    try:
        group = Group.objects.get(name=account_context)
    except Group.DoesNotExist:
        return False

    user.groups.add(group)
    return True
