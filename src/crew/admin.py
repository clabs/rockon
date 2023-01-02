from __future__ import annotations

from django.contrib import admin

from .models import Attendance, Crew, CrewMember, Shirt, Skill, Team


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("day", "event", "updated_at")
    search_fields = ("day", "event")
    ordering = ("day", "event", "created_at", "updated_at")
    list_filter = ("day", "event")


class CrewMemberAdmin(admin.ModelAdmin):
    list_display = (
        "person",
        "crew",
        "shirt",
        "nutrition",
        "overnight",
        "is_underaged",
        "updated_at",
    )
    search_fields = (
        "person__first_name",
        "person__last_name",
    )
    ordering = ("person", "shirt", "nutrition", "overnight", "updated_at")
    list_filter = (
        "person",
        "shirt",
        "nutrition",
        "overnight",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("is_underaged",)


class CrewAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name", "event", "created_at", "updated_at")
    list_filter = ("name", "event", "created_at", "updated_at")


class ShirtAdmin(admin.ModelAdmin):
    list_display = ("size", "cut", "updated_at")
    search_fields = ("size", "cut")
    ordering = ("size", "cut", "updated_at")
    list_filter = ("size", "cut", "updated_at")


class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "comment", "explanation", "updated_at")
    search_fields = ("name", "comment", "explanation")
    ordering = ("name", "updated_at")
    list_filter = ("name", "explanation", "updated_at")


class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "lead",
        "vize_lead",
        "description",
        "is_public",
        "updated_at",
    )
    search_fields = ("name", "lead", "vize_lead", "description")
    ordering = ("name", "lead", "vize_lead", "is_public", "updated_at")
    list_filter = ("name", "lead", "vize_lead", "is_public", "updated_at")


admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Crew, CrewAdmin)
admin.site.register(CrewMember, CrewMemberAdmin)
admin.site.register(Shirt, ShirtAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Team, TeamAdmin)
