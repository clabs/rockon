from __future__ import annotations

import logging

from django.conf import settings
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.template import loader
from ninja import File, Router
from ninja.files import UploadedFile
from ninja.security import django_auth

from rockon.api.schemas.exhibitor_signup import ExhibitorSignupIn, ExhibitorSignupOut
from rockon.base.models import Event, Organisation
from rockon.library.mailer import get_admin_url, send_mail_async
from rockon.exhibitors.models import (
    Asset,
    Attendance,
    Exhibitor,
    ExhibitorAsset,
    ExhibitorAttendance,
)

logger = logging.getLogger(__name__)

exhibitorSignup = Router()


@exhibitorSignup.post(
    '{slug}/',
    response=ExhibitorSignupOut,
    url_name='exhibitor_signup_v2',
    auth=django_auth,
)
def exhibitor_signup(
    request,
    slug: str,
    data: ExhibitorSignupIn,
    logo: UploadedFile = File(None),
):
    """Exhibitor signup endpoint (Django Ninja v2)."""

    # Check group membership
    if not request.user.groups.filter(name='exhibitors').exists():
        return 403, {'status': 'error', 'message': 'Keine Berechtigung.'}

    event = get_object_or_404(Event, slug=slug)

    # Associate user with event
    request.user.profile.events.add(event)
    request.user.save()

    # Get or create organisation
    if data.org_id:
        try:
            organisation = Organisation.objects.get(id=data.org_id)
        except Organisation.DoesNotExist:
            return ExhibitorSignupOut(
                status='error', message='Organisation nicht gefunden.'
            )
    else:
        organisation = Organisation.objects.create(
            org_name=data.organisation_name,
            org_address=data.organisation_address,
            org_house_number=data.organisation_address_housenumber,
            org_address_extension=data.organisation_address_extension,
            org_zip=data.organisation_zip,
            org_place=data.organisation_place,
        )

    organisation.members.add(request.user)
    organisation.save()

    # Check if exhibitor already exists for this org + event
    if Exhibitor.objects.filter(organisation=organisation, event=event).exists():
        return ExhibitorSignupOut(
            status='exists', message='Anmeldung existiert bereits.'
        )

    # Create exhibitor
    exhibitor = Exhibitor.objects.create(
        event=event,
        organisation=organisation,
        general_note=data.general_note,
        offer_note=data.offer_note,
        website=data.website,
    )

    # Save logo if provided
    if logo:
        exhibitor.logo.save(logo.name, logo, save=True)

    # Bulk-fetch referenced objects and create records in bulk
    if data.attendances:
        att_ids = [att.id for att in data.attendances]
        att_map = {a.id: a for a in Attendance.objects.filter(id__in=att_ids)}
        ExhibitorAttendance.objects.bulk_create(
            [
                ExhibitorAttendance(
                    exhibitor=exhibitor,
                    day=att_map[att.id],
                    count=att.count,
                )
                for att in data.attendances
                if att.id in att_map
            ]
        )

    if data.assets:
        asset_ids = [a.id for a in data.assets]
        asset_map = {a.id: a for a in Asset.objects.filter(id__in=asset_ids)}
        ExhibitorAsset.objects.bulk_create(
            [
                ExhibitorAsset(
                    exhibitor=exhibitor,
                    asset=asset_map[item.id],
                    count=item.count,
                )
                for item in data.assets
                if item.id in asset_map
            ]
        )

    # Send admin notification email (non-blocking)
    _send_admin_notification(event, organisation, exhibitor)

    return ExhibitorSignupOut(
        status='created', message='Anmeldung erfolgreich erstellt.'
    )


def _send_admin_notification(event, organisation, exhibitor):
    """Send admin notification email. Failures are logged but don't block the response."""
    try:
        admins = list(
            Group.objects.get(name='exhibitor_admins').user_set.values_list(
                'email', flat=True
            )
        )
        if not admins:
            return

        admin_url = get_admin_url(exhibitor)

        template = loader.get_template('mail/exhibitor_signup.html')
        extra_context = {
            'event_name': event.name,
            'organisation': organisation.org_name,
            'admin_url': admin_url,
        }

        message = (
            f'Hallo Admin-Team,\nes gibt eine neue Anmeldung eines Ausstellers bei '
            f'{event.name}. Bitte überprüft die Angaben und schaut ob alles stimmt.'
            f'\n\nIm Admin ansehen: {admin_url}'
        )

        send_mail_async(
            subject=f'{settings.EMAIL_SUBJECT_PREFIX} Neue Ausstelleranmeldung',
            message=message,
            recipient_list=admins,
            html_message=template.render(extra_context),
            timeout=5,
        )
    except Group.DoesNotExist:
        pass  # No admin group configured
    except Exception:
        logger.exception('Error in exhibitor signup notification')
