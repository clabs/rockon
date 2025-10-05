from __future__ import annotations

from rockon.library.custom_admin import CustomAdminModel, admin
from .models import (
    Attendance,
    AttendanceAddition,
    Crew,
    CrewMember,
    GuestListEntry,
    Shirt,
    Skill,
    Team,
    TeamCategory,
    TeamMember,
)


class AttendanceAdmin(CustomAdminModel):
    list_display = ('day', 'event', 'phase', 'updated_at')
    search_fields = ('day', 'event')
    ordering = ('day', 'event', 'created_at', 'updated_at')
    list_filter = ('day', 'event__name', 'phase')


class AttendanceAdditionAdmin(CustomAdminModel):
    list_display = ('attendance', 'comment', 'amount', 'updated_at')
    search_fields = ('attendance', 'comment', 'amount')
    ordering = ('attendance', 'comment', 'amount', 'updated_at')
    list_filter = ('attendance__day', 'comment', 'amount', 'updated_at')


@admin.action(description='Mark selected crew members as confirmed')
def mark_confirmed(modeladmin, request, queryset):
    queryset.update(state='confirmed')


@admin.action(description='Mark selected crew members as rejected')
def mark_rejected(modeladmin, request, queryset):
    queryset.update(state='rejected')


@admin.action(description='Mark selected crew members as arrived')
def mark_arrived(modeladmin, request, queryset):
    queryset.update(state='arrived')


@admin.action(description='Mark selected crew members as unknown')
def mark_unknown(modeladmin, request, queryset):
    queryset.update(state='unknown')


class CrewMemberAdmin(CustomAdminModel):
    list_display = (
        '__str__',
        'crew',
        'state',
        'nutrition',
        'stays_overnight',
        'updated_at',
    )
    search_fields = (
        'user__first_name',
        'user__last_name',
    )
    ordering = ('user', 'shirt', 'nutrition', 'stays_overnight', 'updated_at')
    list_filter = (
        'crew__name',
        'state',
        'shirt__size',
        'shirt__cut',
        'nutrition',
        'stays_overnight',
        'created_at',
        'updated_at',
    )
    actions = [mark_confirmed, mark_rejected, mark_arrived, mark_unknown]


class CrewAdmin(CustomAdminModel):
    list_display = ('name', 'event', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name', 'event', 'created_at', 'updated_at')
    list_filter = ('event__name',)


class GuestListEntryAdmin(CustomAdminModel):
    list_display = ('crew_member', 'voucher', 'day', 'send', 'updated_at')
    search_fields = ('crew_member__user__last_name', 'voucher')
    ordering = ('crew_member', 'voucher', 'day', 'send', 'updated_at')
    list_filter = ('day', 'send', 'updated_at')


class ShirtAdmin(CustomAdminModel):
    list_display = ('size', 'cut', 'updated_at')
    search_fields = ('size', 'cut')
    ordering = ('size', 'cut', 'updated_at')
    list_filter = (
        'size',
        'cut',
    )


class SkillAdmin(CustomAdminModel):
    list_display = ('name', 'explanation', 'icon', 'updated_at')
    search_fields = ('name', 'explanation')
    ordering = ('name', 'updated_at')


class TeamAdmin(CustomAdminModel):
    list_display = (
        'name',
        'lead',
        'vize_lead',
        'description',
        'is_public',
        'updated_at',
    )
    search_fields = ('name', 'lead', 'vize_lead', 'description')
    ordering = ('name', 'lead', 'vize_lead', 'is_public', 'updated_at')
    list_filter = ('name', 'is_public', 'updated_at')


class TeamCategoryAdmin(CustomAdminModel):
    list_display = ('name', 'description', 'image', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name', 'description', 'updated_at')


class TeamMemberAdmin(CustomAdminModel):
    list_display = ('crewmember', 'team', 'state', 'created_at', 'updated_at')
    search_fields = (
        'team__name',
        'crewmember__user__first_name',
        'crewmember__user__last_name',
    )
    ordering = ('team', 'state')
    list_filter = (
        'team__name',
        'crewmember__crew__event',
    )


admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(AttendanceAddition, AttendanceAdditionAdmin)
admin.site.register(Crew, CrewAdmin)
admin.site.register(CrewMember, CrewMemberAdmin)
admin.site.register(GuestListEntry, GuestListEntryAdmin)
admin.site.register(Shirt, ShirtAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamCategory, TeamCategoryAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
