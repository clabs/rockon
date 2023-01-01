from __future__ import annotations

from django.http import JsonResponse

from crm.models import EmailVerification, Person


def verify_email(request, token):
    """Verify email."""
    try:
        verification = EmailVerification.objects.get(token=token)
        person = Person.objects.get(id=verification.person.id)
        person.email_verified = True
        person.save()
        verification.delete()
        # FIXME: redirect to a page that says "Email verified"
        return JsonResponse({"status": "success", "message": "Email verified"})
    except (EmailVerification.DoesNotExist, Person.DoesNotExist):
        # FIXME: redirect to a page that says "Token not found"
        return JsonResponse(
            {"status": "error", "message": "Token not found"}, status=400
        )
