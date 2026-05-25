from __future__ import annotations

import base64
import json
import logging
from datetime import datetime, timezone

import webauthn
import webauthn.helpers.structs
from django.conf import settings
from ninja import Router
from ninja.security import django_auth

from rockon.api.schemas.passkey import (
    PasskeyAuthCompleteIn,
    PasskeyListOut,
    PasskeyRegisterCompleteIn,
    PasskeyRenameIn,
)
from rockon.api.schemas.status import StatusOut
from rockon.base.models import PasskeyCredential

logger = logging.getLogger(__name__)
passkeyRouter = Router()


def _parse_device_info(user_agent: str) -> str:
    ua = user_agent.lower()
    if 'edg/' in ua or 'edge/' in ua:
        browser = 'Edge'
    elif 'firefox/' in ua:
        browser = 'Firefox'
    elif 'chrome/' in ua:
        browser = 'Chrome'
    elif 'safari/' in ua:
        browser = 'Safari'
    else:
        browser = 'Browser'
    if 'iphone' in ua:
        os = 'iPhone'
    elif 'ipad' in ua:
        os = 'iPad'
    elif 'android' in ua:
        os = 'Android'
    elif 'windows' in ua:
        os = 'Windows'
    elif 'macintosh' in ua or 'mac os' in ua:
        os = 'macOS'
    elif 'linux' in ua:
        os = 'Linux'
    else:
        os = 'Gerät'
    return f'{browser} auf {os}'


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip('=')


def _b64url_decode(s: str) -> bytes:
    # Re-add padding stripped by browsers
    padding = 4 - len(s) % 4
    if padding != 4:
        s += '=' * padding
    return base64.urlsafe_b64decode(s)


# ── Registration (requires existing session / magic-link login) ───────────────

@passkeyRouter.post(
    '/register/begin/',
    response=dict,
    url_name='passkey_register_begin',
    auth=django_auth,
)
def register_begin(request):
    user = request.user
    existing = [
        webauthn.helpers.structs.PublicKeyCredentialDescriptor(
            id=_b64url_decode(c.credential_id)
        )
        for c in PasskeyCredential.objects.filter(user=user).only('credential_id')
    ]
    options = webauthn.generate_registration_options(
        rp_id=settings.WEBAUTHN_RP_ID,
        rp_name=settings.WEBAUTHN_RP_NAME,
        user_id=str(user.pk).encode(),
        user_name=user.email,
        user_display_name=user.get_full_name() or user.email,
        exclude_credentials=existing,
    )
    request.session['_webauthn_registration_challenge'] = _b64url_encode(options.challenge)
    return {'options': json.loads(webauthn.options_to_json(options))}


@passkeyRouter.post(
    '/register/complete/',
    response={200: StatusOut, 400: StatusOut},
    url_name='passkey_register_complete',
    auth=django_auth,
)
def register_complete(request, data: PasskeyRegisterCompleteIn):
    challenge_b64 = request.session.pop('_webauthn_registration_challenge', None)
    if not challenge_b64:
        return 400, {'status': 'error', 'message': 'No pending registration challenge.'}

    challenge = _b64url_decode(challenge_b64)
    try:
        verification = webauthn.verify_registration_response(
            credential=data.credential,
            expected_challenge=challenge,
            expected_rp_id=settings.WEBAUTHN_RP_ID,
            expected_origin=settings.WEBAUTHN_ORIGIN,
        )
    except Exception:
        logger.exception('Passkey registration verification failed')
        return 400, {'status': 'error', 'message': 'Registration verification failed.'}

    credential_id = _b64url_encode(verification.credential_id)
    if PasskeyCredential.objects.filter(credential_id=credential_id).exists():
        return 400, {'status': 'error', 'message': 'Credential already registered.'}

    PasskeyCredential.objects.create(
        user=request.user,
        credential_id=credential_id,
        public_key=bytes(verification.credential_public_key),
        sign_count=verification.sign_count,
        aaguid=str(verification.aaguid) if verification.aaguid else '',
        name=data.name.strip()[:255],
        device_info=_parse_device_info(request.META.get('HTTP_USER_AGENT', '')),
    )
    return 200, {'status': 'ok', 'message': 'Passkey registered.'}


# ── Authentication (no session required — this IS the login flow) ─────────────

@passkeyRouter.post(
    '/auth/begin/',
    response=dict,
    url_name='passkey_auth_begin',
)
def auth_begin(request):
    # Empty allow_credentials = discoverable credentials; browser offers matching passkey
    options = webauthn.generate_authentication_options(
        rp_id=settings.WEBAUTHN_RP_ID,
        allow_credentials=[],
    )
    request.session['_webauthn_authentication_challenge'] = _b64url_encode(options.challenge)
    return {'options': json.loads(webauthn.options_to_json(options))}


@passkeyRouter.post(
    '/auth/complete/',
    response={200: StatusOut, 400: StatusOut, 403: StatusOut},
    url_name='passkey_auth_complete',
)
def auth_complete(request, data: PasskeyAuthCompleteIn):
    challenge_b64 = request.session.pop('_webauthn_authentication_challenge', None)
    if not challenge_b64:
        return 400, {'status': 'error', 'message': 'No pending authentication challenge.'}

    challenge = _b64url_decode(challenge_b64)

    raw_id = data.credential.get('rawId') or data.credential.get('id', '')
    credential_id = raw_id.rstrip('=')
    try:
        stored = PasskeyCredential.objects.select_related('user').get(credential_id=credential_id)
    except PasskeyCredential.DoesNotExist:
        return 403, {'status': 'error', 'message': 'Unknown credential.'}

    try:
        verification = webauthn.verify_authentication_response(
            credential=data.credential,
            expected_challenge=challenge,
            expected_rp_id=settings.WEBAUTHN_RP_ID,
            expected_origin=settings.WEBAUTHN_ORIGIN,
            credential_public_key=bytes(stored.public_key),
            credential_current_sign_count=stored.sign_count,
        )
    except Exception:
        logger.exception('Passkey authentication verification failed')
        return 400, {'status': 'error', 'message': 'Authentication verification failed.'}

    stored.sign_count = verification.new_sign_count
    stored.last_used_at = datetime.now(tz=timezone.utc)
    stored.save(update_fields=['sign_count', 'last_used_at'])

    # Store the verified user ID in the session for the login redirect view.
    # login() itself is called there (a regular Django view) so the session
    # cookie is set on the redirect response — not on this JSON response.
    request.session['_passkey_verified_user_id'] = stored.user.pk
    return 200, {'status': 'ok', 'message': 'Authenticated.'}


# ── Credential management ─────────────────────────────────────────────────────

@passkeyRouter.get(
    '/',
    response=PasskeyListOut,
    url_name='passkey_list',
    auth=django_auth,
)
def list_passkeys(request):
    passkeys = PasskeyCredential.objects.filter(user=request.user).order_by('created_at')
    return {
        'passkeys': [
            {
                'id': str(p.id),
                'name': p.name,
                'device_info': p.device_info,
                'created_at': p.created_at.isoformat(),
                'last_used_at': p.last_used_at.isoformat() if p.last_used_at else None,
            }
            for p in passkeys
        ]
    }


@passkeyRouter.delete(
    '/{credential_uuid}/',
    response={200: StatusOut, 404: StatusOut},
    url_name='passkey_delete',
    auth=django_auth,
)
def delete_passkey(request, credential_uuid: str):
    deleted, _ = PasskeyCredential.objects.filter(
        id=credential_uuid, user=request.user
    ).delete()
    if not deleted:
        return 404, {'status': 'error', 'message': 'Passkey not found.'}
    return 200, {'status': 'ok', 'message': 'Passkey deleted.'}


@passkeyRouter.patch(
    '/{credential_uuid}/',
    response={200: StatusOut, 404: StatusOut},
    url_name='passkey_rename',
    auth=django_auth,
)
def rename_passkey(request, credential_uuid: str, data: PasskeyRenameIn):
    updated = PasskeyCredential.objects.filter(
        id=credential_uuid, user=request.user
    ).update(name=data.name.strip()[:255])
    if not updated:
        return 404, {'status': 'error', 'message': 'Passkey not found.'}
    return 200, {'status': 'ok', 'message': 'Passkey renamed.'}
