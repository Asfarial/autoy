from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from catalog.models import Cars
from Django_Online_Shop import settings

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=150, blank=True)
    city = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    delivery = models.CharField(max_length=50, blank=True)
    agreement = models.BooleanField(default=False, blank=True)
    subscription = models.BooleanField(default=False, blank=True)
    temp_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.user.username


class Rating(models.Model):
    CHOICES = (
        (1, "Bad"),
        (2, "Normal"),
        (3, "Good"),
        (4, "Very Good"),
        (5, "Excellent")
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    car = models.ForeignKey(Cars, on_delete=models.CASCADE, null=True)
    rating = models.PositiveSmallIntegerField(choices=CHOICES)
    date = models.DateField(auto_now_add=True, editable=False)

    def __str__(self):
        return "Rating: {} - {}".format(self.user.username, self.car.title)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    bought_date = models.DateTimeField(auto_now_add=True, editable=False)
    first_name = models.CharField(max_length=150, null=True)
    last_name = models.CharField(max_length=150, null=True)
    email = models.EmailField(null=True)
    address = models.CharField(max_length=150, null=True)
    city = models.CharField(max_length=50, null=True)
    country = models.CharField(max_length=50, null=True)
    phone = models.CharField(max_length=50, null=True)
    delivery = models.CharField(max_length=50, null=True)
    agreement = models.BooleanField(default=False, blank=False)
    total_price = models.PositiveIntegerField(help_text='USD', null=True)
    STATES = (
        ('p', 'Processing (p)'),
        ('s', 'Sent (s)'),
        ('c', 'Completed (c)'),
        ('x', 'Cancelled (x)'),
        ('r', 'Returned (r)'),
    )

    status = models.CharField(max_length=1, choices=STATES, default='p', help_text='Order status')

    def __str__(self):
        return "Order: {}".format(self.id)


class LineItem(models.Model):
    in_order_number = models.PositiveSmallIntegerField(null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    model = models.ForeignKey(Cars, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=128, null=True)
    price = models.PositiveIntegerField(help_text='USD', null=True)
    image = models.ImageField(blank=True, null=True)
    quantity = models.PositiveSmallIntegerField(null=True)
    price_total = models.PositiveIntegerField(help_text='USD', null=True)


    def save(self, *args, **kwargs):
        self.price_total = self.price * self.quantity
        super(LineItem, self).save(*args, **kwargs)

    def __str__(self):
        return "{}. Order: {} - {}".format(self.in_order_number, self.order.id, self.title)


@receiver(post_save, sender=User)
def create_save_user_profile(sender, instance, created, **kwargs):
    if not settings.DB_TRANSFER:
        if created:
            Profile.objects.create(user=instance)
        instance.profile.save()
