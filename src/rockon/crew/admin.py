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


@admin.register(Attendance)
class AttendanceAdmin(CustomAdminModel):
    list_display = ('day', 'event', 'phase', 'updated_at')
    search_fields = ('day', 'event')
    ordering = ('day', 'event', 'created_at', 'updated_at')
    list_filter = ('day', 'event__name', 'phase')


@admin.register(AttendanceAddition)
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


@admin.register(CrewMember)
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
    show_facets = admin.ShowFacets.ALWAYS

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'crew', 'shirt')


@admin.register(Crew)
class CrewAdmin(CustomAdminModel):
    list_display = ('name', 'event', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name', 'event', 'created_at', 'updated_at')
    list_filter = ('event__name',)


@admin.register(GuestListEntry)
class GuestListEntryAdmin(CustomAdminModel):
    list_display = ('crew_member', 'voucher', 'day', 'send', 'updated_at')
    search_fields = ('crew_member__user__last_name', 'voucher')
    ordering = ('crew_member', 'voucher', 'day', 'send', 'updated_at')
    list_filter = ('day', 'send', 'updated_at')


@admin.register(Shirt)
class ShirtAdmin(CustomAdminModel):
    list_display = ('size', 'cut', 'updated_at')
    search_fields = ('size', 'cut')
    ordering = ('size', 'cut', 'updated_at')
    list_filter = (
        'size',
        'cut',
    )


@admin.register(Skill)
class SkillAdmin(CustomAdminModel):
    list_display = ('name', 'explanation', 'icon', 'updated_at')
    search_fields = ('name', 'explanation')
    ordering = ('name', 'updated_at')


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('crewmember', 'state', 'created_at', 'updated_at')
    autocomplete_fields = ('crewmember',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('crewmember__user')


@admin.register(Team)
class TeamAdmin(CustomAdminModel):
    inlines = (TeamMemberInline,)
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


@admin.register(TeamCategory)
class TeamCategoryAdmin(CustomAdminModel):
    list_display = ('name', 'description', 'image', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name', 'description', 'updated_at')


@admin.register(TeamMember)
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
