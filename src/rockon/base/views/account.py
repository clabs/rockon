from __future__ import annotations

from django.contrib.auth import authenticate, login
from django.contrib.auth import (
    BACKEND_SESSION_KEY,
    HASH_SESSION_KEY,
    SESSION_KEY,
)
from django.contrib.auth import logout as django_auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.template import loader
from django.urls import reverse

from rockon.base.models import Event, PasskeyCredential
from rockon.base.services import (
    assign_account_context_group,
    get_fallback_event_for_user,
)


@login_required
def account(request):
    """A view that returns the user profile for logged in users."""
    template = loader.get_template('account/account.html')
    extra_context = {'site_title': 'Profil'}
    account_context = request.GET.get('ctx')
    if account_context:
        assign_account_context_group(request.user, account_context)
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
        current_event = Event.objects.order_by('start').first()

    if not current_event:
        template = loader.get_template('errors/403.html')
        extra_context = {
            'site_title': 'Magic Link angefordert',
            'reason': 'Es ist derzeit keine Veranstaltung konfiguriert.',
        }
        return HttpResponseForbidden(template.render(extra_context, request))

    if not user.groups.all().exists():
        next_url = reverse('base:select_context')
    elif user.groups.filter(name='bands').exists():
        target_event = get_fallback_event_for_user(user) or current_event
        next_url = reverse('bands:bid_router', kwargs={'slug': target_event.slug})
    else:
        next_url = reverse('crm_user_home')

    if not PasskeyCredential.objects.filter(user=user).exists():
        return redirect(f'{reverse("base:passkey_prompt")}?next={next_url}')

    return redirect(next_url)


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


def passkey_login_redirect(request):
    """Complete passkey login: read verified user from session, call login(), then route."""
    user_id = request.session.pop('_passkey_verified_user_id', None)
    if not user_id:
        return redirect(reverse('base:login_request'))

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect(reverse('base:login_request'))

    # Avoid login() / cycle_key(): the browser already holds the session cookie
    # from auth/begin. Writing auth keys directly keeps the session ID stable.
    # WebAuthn ceremony prevents fixation so skipping cycle_key() is safe.
    request.session[SESSION_KEY] = str(user.pk)
    request.session[BACKEND_SESSION_KEY] = 'rockon.base.passkey_auth.PasskeyAuth'
    request.session[HASH_SESSION_KEY] = user.get_session_auth_hash()
    request.user = user

    current_event = Event.get_current_event()
    if not current_event:
        current_event = Event.objects.order_by('start').first()

    if not user.groups.all().exists():
        return redirect(reverse('base:select_context'))

    if user.groups.filter(name='bands').exists():
        target_event = get_fallback_event_for_user(user) or current_event
        return redirect(reverse('bands:bid_router', kwargs={'slug': target_event.slug}))

    return redirect(reverse('crm_user_home'))


@login_required
def passkey_prompt(request):
    """Prompt logged-in user to register a passkey on their device."""
    next_url = request.GET.get('next', reverse('base:account'))
    template = loader.get_template('account/passkey_prompt.html')
    extra_context = {
        'site_title': 'Passkey speichern',
        'next_url': next_url,
    }
    return HttpResponse(template.render(extra_context, request))
