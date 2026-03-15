from __future__ import annotations

from datetime import date

from rockon.library.custom_admin import CustomAdminModel, admin
from .models import (
    Attendance,
    AttendanceAddition,
    Crew,
    CrewMember,
    EventTeam,
    GuestListEntry,
    Shirt,
    Skill,
    Team,
    TeamCategory,
    TeamMember,
)


def _age_cutoff_date(years: int) -> date:
    today = date.today()
    try:
        return today.replace(year=today.year - years)
    except ValueError:
        # Handle Feb 29 on non-leap years.
        return today.replace(year=today.year - years, day=28)


class Over16Filter(admin.SimpleListFilter):
    title = 'over 16'
    parameter_name = 'over_16'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        cutoff = _age_cutoff_date(16)
        if value == 'yes':
            return queryset.filter(user__profile__birthday__isnull=False).filter(
                user__profile__birthday__lte=cutoff
            )
        if value == 'no':
            return queryset.filter(
                user__profile__birthday__gt=cutoff
            ) | queryset.filter(user__profile__birthday__isnull=True)
        return queryset


class Over18Filter(admin.SimpleListFilter):
    title = 'over 18'
    parameter_name = 'over_18'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Yes'),
            ('no', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        cutoff = _age_cutoff_date(18)
        if value == 'yes':
            return queryset.filter(user__profile__birthday__isnull=False).filter(
                user__profile__birthday__lte=cutoff
            )
        if value == 'no':
            return queryset.filter(
                user__profile__birthday__gt=cutoff
            ) | queryset.filter(user__profile__birthday__isnull=True)
        return queryset


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
        'stays_overnight',
        'over_16',
        'over_18',
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
        Over16Filter,
        Over18Filter,
        'created_at',
        'updated_at',
    )
    actions = [mark_confirmed, mark_rejected, mark_arrived, mark_unknown]
    show_facets = admin.ShowFacets.ALWAYS

    @admin.display(boolean=True, description='Over 16')
    def over_16(self, obj):
        return obj.user.profile.over_16()

    @admin.display(boolean=True, description='Over 18')
    def over_18(self, obj):
        return obj.user.profile.over_18()

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('user', 'user__profile', 'crew', 'shirt')
        )


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


class EventTeamInline(admin.TabularInline):
    model = EventTeam
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('event', 'lead', 'vize_lead', 'created_at', 'updated_at')
    autocomplete_fields = ('event', 'lead', 'vize_lead')

    def get_queryset(self, request):
        return (
            super().get_queryset(request).select_related('event', 'lead', 'vize_lead')
        )


@admin.register(Team)
class TeamAdmin(CustomAdminModel):
    inlines = (EventTeamInline,)
    list_display = (
        'name',
        'category',
        'description',
        'is_public',
        'updated_at',
    )
    search_fields = ('name', 'category__name', 'description')
    ordering = ('name', 'category__name', 'is_public', 'updated_at')
    list_filter = ('category__name', 'events__name', 'is_public', 'updated_at')


@admin.register(EventTeam)
class EventTeamAdmin(CustomAdminModel):
    inlines = (TeamMemberInline,)
    list_display = ('team', 'event', 'lead', 'vize_lead', 'is_public', 'updated_at')
    search_fields = (
        'team__name',
        'event__name',
        'lead__first_name',
        'lead__last_name',
        'vize_lead__first_name',
        'vize_lead__last_name',
    )
    ordering = ('event__start', 'team__name', 'updated_at')
    list_filter = (
        'event__name',
        'team__category__name',
        'team__is_public',
        'updated_at',
    )
    autocomplete_fields = ('event', 'team', 'lead', 'vize_lead')

    @admin.display(boolean=True, description='Public')
    def is_public(self, obj):
        return obj.team.is_public


@admin.register(TeamCategory)
class TeamCategoryAdmin(CustomAdminModel):
    list_display = ('name', 'description', 'image', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name', 'description', 'updated_at')


@admin.register(TeamMember)
class TeamMemberAdmin(CustomAdminModel):
    list_display = ('crewmember', 'team', 'event', 'state', 'created_at', 'updated_at')
    search_fields = (
        'event_team__team__name',
        'event_team__event__name',
        'crewmember__user__first_name',
        'crewmember__user__last_name',
    )
    ordering = ('event_team__team__name', 'state')
    list_filter = (
        'event_team__team__name',
        'event_team__event',
        'state',
    )

    @admin.display(ordering='event_team__team__name')
    def team(self, obj):
        return obj.team

    @admin.display(ordering='event_team__event__name')
    def event(self, obj):
        return obj.event
