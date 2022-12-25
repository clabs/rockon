from __future__ import annotations

from crm.models import Person, EmailVerification

from django.http import JsonResponse

def verify_email(request, token):
    """Verify email."""
    try:
        verficiation = EmailVerification.objects.get(token=token)
        print(verficiation)
        person = Person.objects.get(id=verficiation.person.id)
        person.email_verified = True
        person.save()
        verficiation.delete()
        # FIXME: redirect to a page that says "Email verified"
        return JsonResponse({"status": "success", "message": "Email verified"})
    except (EmailVerification.DoesNotExist, Person.DoesNotExist):
        # FIXME: redirect to a page that says "Token not found"
        return JsonResponse({"status": "error", "message": "Token not found"}, status=400)
