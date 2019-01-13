from django.conf import settings
from django.db import models


class Webhooks(models.Model):
    owner_username = models.CharField(max_length=255)
    webhook_url = models.URLField(unique=True)
    hook_id = models.CharField(max_length=255, blank=True, null=True)
    guild_id = models.CharField(max_length=255, blank=True, null=True)
    channel_id = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.owner_username, self.hook_id)

    class Meta:
        verbose_name = 'Webhooks'
        verbose_name_plural = 'Webhooks'


class Hacks(models.Model):
    smwc_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    smwc_href = models.CharField(max_length=255)
    file_uri = models.CharField(max_length=255, null=True, blank=True)
    download_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    difficulty = models.CharField(max_length=255, null=True, blank=True)
    authors = models.CharField(max_length=255, null=True, blank=True)
    length = models.CharField(max_length=255, null=True, blank=True)
    demo = models.BooleanField(null=True, blank=True)
    featured = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.name, self.smwc_id)

    class Meta:
        verbose_name = 'Hacks'
        verbose_name_plural = 'Hacks'

    def get_hack_url(self):
        if self.smwc_href:
            if self.smwc_href.startswith('https'):
                return self.smwc_href
            else:
                return settings.APP_SMWC_URL + self.smwc_href
        else:
            return None

    def get_archive_url(self):
        if self.file_uri:
            return '{}/{}'.format(settings.APP_ROMS_URL, self.file_uri)
        else:
            return None
