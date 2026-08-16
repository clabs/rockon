from __future__ import annotations

from django.contrib.auth.models import User
from slugify import slugify

from rockon.base.models import Event
from rockon.library.custom_model import CustomModel, models


class PostStatus(models.TextChoices):
    DRAFT = 'draft', 'Entwurf'
    PUBLISHED = 'published', 'Veröffentlicht'


class NewsAudience(models.TextChoices):
    """Shared audience vocabulary, matching SUPPORTED_ACCOUNT_CONTEXTS."""

    CREW = 'crew', 'Crew'
    BANDS = 'bands', 'Bands'
    EXHIBITORS = 'exhibitors', 'Aussteller'


class NewsPost(CustomModel):
    """A blog-style news post shown in the home feed."""

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    body_markdown = models.TextField()
    body_html = models.TextField(blank=True, editable=False)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_posts',
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='news_posts',
    )
    status = models.CharField(
        max_length=16, choices=PostStatus.choices, default=PostStatus.DRAFT
    )
    publish_at = models.DateTimeField(null=True, blank=True)
    audience_crew = models.BooleanField(default=False)
    audience_bands = models.BooleanField(default=False)
    audience_exhibitors = models.BooleanField(default=False)

    class Meta(CustomModel.Meta):
        ordering = ('-created_at',)
        constraints = (
            models.CheckConstraint(
                condition=models.Q(audience_crew=True)
                | models.Q(audience_bands=True)
                | models.Q(audience_exhibitors=True),
                name='newspost_audience_explicit',
            ),
        )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.slug == '':
            self.slug = str(self.id)
        super().save(*args, **kwargs)

    def targets_audience(self, context: str | None) -> bool:
        """True if this post explicitly targets the given account-context."""
        flags = {
            NewsAudience.CREW: self.audience_crew,
            NewsAudience.BANDS: self.audience_bands,
            NewsAudience.EXHIBITORS: self.audience_exhibitors,
        }
        return flags.get(context, False)
