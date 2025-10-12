from ninja import Router
from ninja.security import django_auth
from rockon.api.schemas.mark_voucher import MarkVoucherIn

from django.shortcuts import get_object_or_404
from rockon.crew.models import GuestListEntry

markVoucher = Router()


@markVoucher.post('', response={204: None}, url_name='mark_voucher', auth=django_auth)
def mark_voucher(request, data: MarkVoucherIn):
    voucher = get_object_or_404(
        GuestListEntry, id=data.id, crew_member__user=request.user
    )
    voucher.send = not voucher.send
    voucher.save()
    return 204, None
