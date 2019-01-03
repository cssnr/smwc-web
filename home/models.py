from django.db import models


class Webhooks(models.Model):
    owner_username = models.CharField(max_length=255)
    webhook_url = models.URLField(unique=True)
    hook_id = models.IntegerField()
    guild_id = models.IntegerField()
    channel_id = models.IntegerField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}: {}'.format(self.owner_username, self.hook_id)

    class Meta:
        verbose_name = 'Webhooks'
        verbose_name_plural = 'Webhooks'
