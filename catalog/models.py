from django.db import models
from django.urls import reverse
import uuid
from django.template.defaultfilters import slugify
import datetime

from django.core.exceptions import ValidationError


# Create your models here.

# parent class - to capitilize name in Categories and Characteristics
# for the DRY purpose
class CapitilizingNames():
    def capitilize(self, name):
        words = name.split()
        i = 0
        for word in words:
            words[i] = word.capitalize()
            i += 1
        name = " ".join(words)
        return name

    @classmethod
    def get_classname(cls):
        return eval(cls.__name__)


class Categories(models.Model, CapitilizingNames):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(blank=True, editable=False)

    def list_quantity(self):
        return Cars.objects.filter(category__name__exact=self.name).count()
    list_quantity.short_description = "Quantity in Category"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = CapitilizingNames.capitilize(self, self.name)
        if not self.slug:
            self.slug=slugify(self.name)
        super(Categories, self).save(*args, **kwargs)
        return super(self.get_classname(), self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Categories"
        verbose_name_plural = "Categories"


class Characteristics(models.Model, CapitilizingNames):
    name = models.CharField(max_length=256, unique=True)
    slug = models.SlugField(blank=True, editable=False)

    def __str__(self):
        return self.name

    def list_quantity(self):
        return Cars.objects.filter(characteristics__name__exact=self.name).count()
    list_quantity.short_description = "Quantity with Characteristic"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Characteristics, self).save(*args, **kwargs)
        self.name = CapitilizingNames.capitilize(self, self.name)
        return super(self.get_classname(), self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Characteristics"
        verbose_name_plural = "Characteristics"


class Cars(models.Model):
    title = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, blank=True, editable=False)
    characteristics = models.ManyToManyField(Characteristics, related_name='cars')
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True)
    price = models.PositiveIntegerField(default=0, help_text='USD')
    image = models.ImageField(upload_to='catalog/', blank=True, null=True)
    description = models.TextField(max_length=1024, blank=True)
    quantity = models.PositiveIntegerField(default=0)
    CHOICES = (
        (1, "Bad"),
        (2, "Normal"),
        (3, "Good"),
        (4, "Very Good"),
        (5, "Excellent")
    )
    computed_rating = models.PositiveSmallIntegerField(choices=CHOICES, default=0)

    def __str__(self):
        return self.title

    def get_rating(self):
        from accounts.models import Rating
        from django.db.models import Sum
        ratings = Rating.objects.filter(car_id=self.id)
        rating = ratings.aggregate(Sum('rating'))
        if not rating['rating__sum']:
            rating = 0
        else:
            rating = rating['rating__sum']/ratings.count()
        return int(rating)
    get_rating.short_description = "Rating"

    def get_absolute_url(self):
        return reverse('catalog:car', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug=slugify(self.title)
        super(Cars, self).save(*args, **kwargs)

    def list_characteristics(self):
        return [char.name for char in self.characteristics.all()[:6]]
    list_characteristics.short_description = "Characteristics"

    class Meta:
        verbose_name = "Cars"
        verbose_name_plural = "Cars"

from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import Rating
@receiver(post_save, sender=Rating)
def update_computed_rating(sender, instance, **kwargs):
    instance.car.computed_rating = instance.car.get_rating()
    instance.car.save()