from django.db import models

# Create your models here.

class MenuList(models.Model):
    name = models.CharField(max_length=32, help_text='Menu name')

    url = models.CharField(max_length=32, blank=True, default="")

    is_active = models.BooleanField(default=True)

    order_num = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Menu list"
        verbose_name_plural = "Menu list"
        ordering = ['order_num']

class SocialLinks(models.Model):
    name = models.CharField(max_length=64, unique=True)
    url = models.URLField()
    order_num = models.PositiveSmallIntegerField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Social Links"
        verbose_name_plural = "Social Links"
        ordering = ['order_num']


class Footer(models.Model):
    name = models.CharField(max_length=24, default="Footer")
    address_show = models.BooleanField(default=True)
    address = models.CharField(max_length=512)
    address_google_maps_dir_url = models.URLField(blank=True, default="", help_text="URL for directions from Google Maps, leave empty to disable")
    phone = models.CharField(max_length=24)
    e_mail = models.CharField(max_length=64)
    social_links_show = models.BooleanField(default=True)
    social_links = models.ManyToManyField(SocialLinks, related_name='social_links')
    newsletter_show = models.BooleanField(default=True)
    copyright_show = models.BooleanField(default=True)
    copyright_text = models.CharField(max_length=128)


    def save(self, *args, **kwargs):
        if not self.pk and Footer.objects.exists():
        # if you'll not check for self.pk
        # then error will also raised in update of exists model
            raise ValidationError('There is can be only one Footer instance')
        return super(Footer, self).save(*args, **kwargs)

    def list_social_links(self):
        return [link.name for link in self.social_links.all()]
    list_social_links.short_description = "Social Links"

    def __str__(self):
        return 'Footer'

    class Meta:
        verbose_name = "Footer"
        verbose_name_plural = "Footer"

