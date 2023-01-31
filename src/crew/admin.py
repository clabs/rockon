from __future__ import annotations

from django.contrib import admin

from .models import Attendance, Crew, CrewMember, Shirt, Skill, Team


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("day", "event", "phase", "updated_at")
    search_fields = ("day", "event")
    ordering = ("day", "event", "created_at", "updated_at")
    list_filter = ("day", "event", "phase")
    readonly_fields = ("created_at", "updated_at")


class CrewMemberAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "crew",
        "shirt",
        "nutrition",
        "stays_overnight",
        "is_underaged",
        "updated_at",
    )
    search_fields = (
        "user__first_name",
        "user__last_name",
    )
    ordering = ("user", "shirt", "nutrition", "stays_overnight", "updated_at")
    list_filter = (
        "user",
        "shirt",
        "nutrition",
        "stays_overnight",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("is_underaged", "created_at", "updated_at")


class CrewAdmin(admin.ModelAdmin):
    list_display = ("name", "event", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name", "event", "created_at", "updated_at")
    list_filter = ("name", "event", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


class ShirtAdmin(admin.ModelAdmin):
    list_display = ("size", "cut", "updated_at")
    search_fields = ("size", "cut")
    ordering = ("size", "cut", "updated_at")
    list_filter = ("size", "cut", "updated_at")
    readonly_fields = ("created_at", "updated_at")


class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "explanation", "icon", "updated_at")
    search_fields = ("name", "explanation")
    ordering = ("name", "updated_at")
    readonly_fields = ("created_at", "updated_at")


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
    readonly_fields = ("created_at", "updated_at")


admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Crew, CrewAdmin)
admin.site.register(CrewMember, CrewMemberAdmin)
admin.site.register(Shirt, ShirtAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Team, TeamAdmin)
