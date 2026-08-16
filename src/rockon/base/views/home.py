from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader

from rockon.base.services import (
    get_current_event_for_request,
    get_request_account_context,
)
from rockon.news.services.feed import visible_posts_for_user


@login_required
def home(request):
    """A view that returns the user homeview for logged in users."""
    event = get_current_event_for_request(request)
    account_context = get_request_account_context(request)
    news_posts = visible_posts_for_user(request.user, event, account_context)

    template = loader.get_template('home.html')
    extra_context = {'site_title': 'Home', 'news_posts': news_posts}
    return HttpResponse(template.render(extra_context, request))
