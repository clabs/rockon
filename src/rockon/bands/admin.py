from __future__ import annotations

from rockon.library.custom_admin import CustomAdminModel, admin
from .models import (
    Band,
    BandMedia,
    BandMember,
    BandVote,
    Comment,
    Stage,
    TimeSlot,
    Track,
)


@admin.register(TimeSlot)
class TimeslotAdmin(CustomAdminModel):
    list_display = ('__str__', 'start', 'end', 'band', 'stage__event')
    list_filter = ('stage__name', 'stage__event__name')
    search_fields = ('stage__name',)
    ordering = ('day', 'start', 'end', 'stage')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('stage__event', 'band')


class BandMediaInline(admin.TabularInline):
    model = BandMedia
    extra = 0
    readonly_fields = ('id', 'created_at', 'updated_at', 'thumbnail')
    fields = (
        'media_type',
        'url',
        'file',
        'thumbnail',
        'file_name_original',
        'created_at',
        'updated_at',
    )


@admin.register(Band)
class BandAdmin(CustomAdminModel):
    inlines = (BandMediaInline,)
    list_display = (
        '__str__',
        'contact',
        'bid_status',
        'bid_complete',
        '_has_techrider',
        'track',
        'slot',
        'event',
    )
    list_filter = (
        'event__name',
        'bid_status',
        'bid_complete',
    )
    search_fields = ('name', 'contact__username', 'event__name')
    readonly_fields = (
        '_band_members',
        'slot',
        'guid',
    )
    show_facets = admin.ShowFacets.ALWAYS

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('track', 'contact', 'event')
            .prefetch_related('band_members__user')
        )

    def _band_members(self, obj):
        return ', '.join(
            [
                f'{member.user.first_name} {member.user.last_name}'
                for member in obj.band_members.all()
            ]
        )

    @admin.display(boolean=True)
    def _has_techrider(self, obj):
        return obj.techrider != {}

    @admin.display(boolean=True)
    def bid_complete(self, obj):
        return obj.bid_complete


@admin.register(BandMember)
class BandMemberAdmin(CustomAdminModel):
    list_display = ('_user', 'band', 'position', 'updated_at')
    list_filter = ('band__event__name',)
    search_fields = ('user__username', 'band__name')
    readonly_fields = (
        'user',
        'band',
    )

    def _user(self, obj):
        return f'{obj.user.first_name} {obj.user.last_name}'


@admin.register(BandMedia)
class BandMediaAdmin(CustomAdminModel):
    list_display = (
        'band',
        'media_type',
        'url',
        'file_name_original',
        'file',
        'thumbnail',
    )
    list_filter = ('band__name', 'media_type')
    search_fields = ('band__name', 'media_type', 'url', 'file', 'thumbnail')
    readonly_fields = (
        'band',
        'media_type',
        'thumbnail',
    )
    show_facets = admin.ShowFacets.ALWAYS


@admin.register(Stage)
class StageAdmin(CustomAdminModel):
    list_display = ('name', 'event', 'id')
    list_filter = ('event__name',)
    search_fields = ('name', 'event__name')


@admin.register(Track)
class TrackAdmin(CustomAdminModel):
    list_display = ('name', 'id')
    list_filter = ('events__name',)
    search_fields = ('name', 'events__name')


@admin.register(BandVote)
class BandVoteAdmin(CustomAdminModel):
    list_display = ('band', 'user', 'created_at', 'event')
    list_filter = ('event',)
    search_fields = ('band__name', 'user__username')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_fields(self, request, obj=None):
        # Exclude 'vote' from the fields displayed in the detail view
        fields = super().get_fields(request, obj)
        return [field for field in fields if field != 'vote']


@admin.register(Comment)
class CommentAdmin(CustomAdminModel):
    list_display = ('band', 'user', 'created_at', 'mood')
    list_filter = ('band__name', 'mood')
    search_fields = ('band__name', 'user__username', 'mood')
