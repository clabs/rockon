from __future__ import annotations

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from rockon.library.custom_admin import CustomAdminModel, admin
from .models import (
    EmailVerification,
    Event,
    MagicLink,
    Organisation,
    Sponsoring,
    Task,
    Timeline,
    UserProfile,
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    readonly_fields = ('id', 'created_at', 'updated_at')


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(CustomAdminModel):
    list_display = (
        'full_name',
        'nick_name',
        'email_is_verified',
        'created_at',
        'updated_at',
    )
    readonly_fields = ('user',)
    search_fields = ('user__first_name', 'user__last_name', 'user__email')


@admin.register(EmailVerification)
class EmailVerificationAdmin(CustomAdminModel):
    list_display = ('user', 'id', 'created_at')


@admin.register(MagicLink)
class MagicLinkAdmin(CustomAdminModel):
    list_display = ('user', 'id', 'created_at', 'expires_at')


@admin.register(Event)
class EventAdmin(CustomAdminModel):
    list_display = ('name', 'slug', 'start', 'end', 'created_at', 'updated_at')
    readonly_fields = ('slug',)


@admin.register(Organisation)
class OrganisationAdmin(CustomAdminModel):
    list_display = ('org_name', 'org_address', 'org_zip', 'org_place', 'get_contact')
    search_fields = ('org_name', 'org_address', 'org_zip', 'org_place')

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('members')

    def get_contact(self, obj):
        return next(iter(obj.members.all()), None)


admin.site.register(Sponsoring)
admin.site.register(Task)
admin.site.register(Timeline)
