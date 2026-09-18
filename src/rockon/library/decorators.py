from __future__ import annotations

from functools import wraps

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect

from rockon.base.models import Event


def check_band_application_open(view_func):
    @wraps(view_func)
    def _wrapped_view_func(request, *args, **kwargs):
        slug = kwargs.get('slug', None)
        event = get_object_or_404(Event, slug=slug)
        if not event.band_application_open:
            return redirect('bands:bid_closed', slug=slug)
        return view_func(request, *args, **kwargs)

    return _wrapped_view_func


def require_group(group_name):
    """Require login and membership in `group_name`, redirecting to LOGIN_URL otherwise.

    Equivalent to stacking @login_required and
    @user_passes_test(lambda u: u.groups.filter(name=group_name).exists()) —
    both anonymous users and users missing the group redirect to LOGIN_URL,
    matching user_passes_test's existing behavior.
    """

    def decorator(view_func):
        @login_required
        @user_passes_test(lambda u: u.groups.filter(name=group_name).exists())
        @wraps(view_func)
        def _wrapped_view_func(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)

        return _wrapped_view_func

    return decorator
