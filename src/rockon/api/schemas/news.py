from __future__ import annotations

from datetime import datetime

from ninja import Schema


class NewsPostOut(Schema):
    id: str
    title: str
    slug: str
    body_markdown: str
    body_html: str
    status: str
    publish_at: datetime | None = None
    event: str | None = None
    event_name: str | None = None
    audience_crew: bool
    audience_bands: bool
    audience_exhibitors: bool
    author_name: str | None = None
    created_at: datetime
    updated_at: datetime


class NewsPostCreateIn(Schema):
    title: str
    body_markdown: str
    status: str = 'draft'
    publish_at: datetime | None = None
    event: str | None = None
    audience_crew: bool = False
    audience_bands: bool = False
    audience_exhibitors: bool = False


class NewsPostPatchIn(Schema):
    title: str | None = None
    body_markdown: str | None = None
    status: str | None = None
    publish_at: datetime | None = None
    event: str | None = None
    audience_crew: bool | None = None
    audience_bands: bool | None = None
    audience_exhibitors: bool | None = None


class NewsPreviewIn(Schema):
    body_markdown: str


class NewsPreviewOut(Schema):
    body_html: str
