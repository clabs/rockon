from __future__ import annotations

from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as django_auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from rockon.base.models import Event


@login_required
def account(request):
    """A view that returns the user profile for logged in users."""
    template = loader.get_template('account/account.html')
    extra_context = {'site_title': 'Profil'}
    account_context = request.GET.get('ctx')
    if account_context in ['crew', 'bands', 'exhibitors']:
        group = Group.objects.get(name=account_context)
        request.user.groups.add(group)
        request.user.save()
    return HttpResponse(template.render(extra_context, request))


def logout(request):
    template = loader.get_template('account/logout.html')
    extra_context = {
        'site_title': 'Logout',
    }
    if request.user.is_authenticated:
        django_auth_logout(request)
    return HttpResponse(template.render(extra_context, request))


def login_request(request):
    if request.user.is_authenticated:
        return redirect(reverse('base:account'))
    account_context = request.GET.get('ctx', 'crew')
    template = loader.get_template('account/login.html')
    extra_context = {
        'site_title': 'Login',
        'account_context': account_context,
    }
    return HttpResponse(template.render(extra_context, request))


def login_token(request, token):
    """Shows information corresponding to the magic link token."""
    user = authenticate(request, token=token)
    if not user:
        template = loader.get_template('errors/403.html')
        extra_context = {
            'site_title': 'Magic Link angefordert',
            'reason': 'Der angefrate Schlüssel wurde nicht gefunden...',
        }
        return HttpResponseForbidden(template.render(extra_context, request))
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    current_event = Event.get_current_event()

    if not current_event:
        current_event = Event.objects.order_by('start_date').first()

    # Store current_event in user session
    request.session['current_event_id'] = str(current_event.id)
    request.session['current_event_slug'] = current_event.slug
    request.session.save()

    if not user.groups.all().exists():
        return redirect(reverse('base:select_context'))

    if user.groups.filter(name='bands').exists():
        return redirect(
            reverse(
                'bands:bid_router',
                kwargs={'slug': request.session['current_event_slug']},
            )
        )

    return redirect(reverse('crm_user_home'))


def account_created(request):
    """A view that returns the account creation form."""
    template = loader.get_template('account/created.html')
    extra_context = {'site_title': 'Account erstellt'}
    return HttpResponse(template.render(extra_context, request))


def verify_email(request, token):
    """Verify email."""
    template = loader.get_template('account/verify_email.html')
    extra_context = {'site_title': 'E-Mail bestätigen', 'token': token}
    return HttpResponse(template.render(extra_context, request))


def select_context(request):
    template = loader.get_template('account/select_context.html')
    extra_context = {'site_title': 'Bereichswahl'}
    return HttpResponse(template.render(extra_context, request))
