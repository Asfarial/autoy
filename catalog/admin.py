from django.contrib import admin
from . import models
from .filters import PricesRangeFilter
from layout import models as LayoutModels
from accounts.models import Profile, Order, LineItem
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
from django.db import models as m
from django.forms import CheckboxSelectMultiple
from accounts.models import Rating


# Register your models here.

# Function to get all fields
# obj = models.Cars - for example
# Remove unnecessarry within call function
# by variable.remove('id')
# for list_display = tuple(variable)
# for fields = list(variable)
# on error with list display print(variable) and variable.remove('foreign key or manytomany causing error')
def get_all_fields(obj):
    return [field.name
            for field in obj._meta.get_fields()
            ]


def arrange_titles_cars(titles) -> tuple:
    titles.remove('characteristics')
    titles.remove('lineitem')
    titles.remove('slug')
    titles.remove('rating')
    titles.append(titles.pop(titles.index('image')))
    titles.insert(titles.index('price'), 'list_characteristics')
    titles.remove('image')
    titles.remove('description')
    titles = tuple(titles)
    return titles


class LineItemInline(admin.StackedInline):
    model = LineItem
    readonly_fields = ['model', 'title', 'price', 'quantity', 'in_order_number']
    temp_fields = get_all_fields(LineItem)
    temp_fields.remove("id")
    temp_fields.remove("in_order_number")
    fields = temp_fields
    can_delete = False
    verbose_name = "Item"
    verbose_name_plural = "Order Items"

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    import copy
    model = Order
    inlines = [LineItemInline]
    temp_fields = get_all_fields(Order)
    temp_fields.remove("lineitem")
    temp_fields.remove("id")
    temp_fields.remove("status")
    readonly_fields = temp_fields
    temp_fields_display = copy.deepcopy(temp_fields)
    temp_fields_display.append("status")
    fieldsets = (
        (None, {
            'fields': temp_fields_display}),
    )
    list_display = ('get_orders', 'user', "first_name", "last_name", "email", "phone", "bought_date", "city", "address",
                    "delivery")
    search_fields = ("id", 'user', "first_name", "last_name", "email", "bought_date", "city", "address", "phone", "delivery")

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def get_orders(self, obj):
        return obj.__str__()

    get_orders.short_description = 'Orders'
    get_orders.admin_order_field = 'bought_date'


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    readonly_fields = ["agreement"]
    exclude = ["temp_email"]
    verbose_name_plural = 'Profile'


class RatingInline(admin.TabularInline):
    model = Rating
    readonly_fields = ['car', "date"]
    fields=["car", "rating", "date"]
    verbose_name = "Rating"
    verbose_name_plural = "Ratings"

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, RatingInline)
    readonly_fields = ["date_joined", "last_login"]

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class CarsAdminInlineChar(admin.StackedInline):
    model = models.Cars.characteristics.through
    extra = 0
    readonly_fields = ['cars']
    can_delete = False
    verbose_name = "Cars"
    verbose_name_plural = "Cars"

    def has_add_permission(self, request, obj):
        return False


class CarsAdminInline(admin.StackedInline):
    model = models.Cars
    show_change_link = True
    view_on_site = False
    extra = 0
    titles = get_all_fields(models.Cars)
    titles.remove('category')
    exclude = list(titles)
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


@admin.register(models.Characteristics)
class CharacteristicsAdmin(admin.ModelAdmin):
    list_display = ('name', 'list_quantity')
    inlines = [CarsAdminInlineChar]


@admin.register(models.Categories)
class ChategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'list_quantity')
    inlines = [CarsAdminInline]


from accounts.models import Rating


@admin.register(models.Cars)
class CarsAdmin(admin.ModelAdmin):
    titles = get_all_fields(models.Cars)
    titles = arrange_titles_cars(titles)
    list_filter = ('category', 'characteristics', PricesRangeFilter)
    readonly_fields = ["computed_rating"]
    list_display = titles
    list_display_links = ['title']
    ordering = ["pk"]
    filter_horizontal = ['characteristics']
    search_fields = ['title', 'category__name', 'price', 'description', 'characteristics__name']

    # disabled checkboxes, because, they do not update on add
    # formfield_overrides = {m.ManyToManyField: {'widget': CheckboxSelectMultiple}}


@admin.register(LayoutModels.MenuList)
class MenuListAdmin(admin.ModelAdmin):
    title = get_all_fields(LayoutModels.MenuList)
    title.remove('id')
    list_display = tuple(title)
    fieldsets = (
        (None, {
            'fields': list_display,
            'description': "<br><p style=\"padding: 0px; font-size: 16px; font-weight: bold\">Attention!</p><p>URL: - for home - leave empty.</p><p style=\"padding-bottom: 24px\">If You create new pages - append views.py and urls.py</p>"
        }),
    )


@admin.register(LayoutModels.SocialLinks)
class SocialLinks(admin.ModelAdmin):
    list_display = ('name', 'url', 'order_num')


@admin.register(LayoutModels.Footer)
class FooterAdmin(admin.ModelAdmin):
    list_display = ('name', 'address_show', 'newsletter_show', 'social_links_show', 'copyright_show')
    # disabled checkboxes, because, they do not update on add
    # formfield_overrides = {m.ManyToManyField: {'widget': CheckboxSelectMultiple}}
    fieldsets = (
        ('Address', {
            'fields': ('address', 'address_google_maps_dir_url', 'address_show')
        }),
        ('Contacts', {
            'fields': ('phone', 'e_mail')
        }),
        ('Social Links', {
            'fields': ('social_links', 'social_links_show')
        }),
        ('Copyright', {
            'fields': ('copyright_text', 'copyright_show')
        }),
        ('Newsletter', {
            'fields': ('newsletter_show',),
        }),
    )
