import datetime

import cloudinary.uploader
import requests
from django.shortcuts import render, redirect
import Django_Online_Shop.settings
from . import models
from . import forms
from .admin import get_all_fields
import random
from layout import models as LayoutModels
from django.views.generic.base import ContextMixin
from django.views import generic
from django.db.models import Q
from math import ceil
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

PAGINATE_BY_ITEMS_DEFAULT = 6


def get_previous_and_current_url(request):
    PROHIBITED_PREVIOUS_URLS = ['accounts']

    # get previous url
    previous_url = str(request.META.get('HTTP_REFERER'))

    # constructing like /catalog/jeep
    previous_url = previous_url[7:].strip('/').split("?")[0].rstrip("/").split('/')
    if len(previous_url) > 1:
        previous_url = "/" + "/".join(previous_url[1:])
    else:
        previous_url = "/"

    # constructing like /catalog/jeep
    current_url = str(request.path).split("?")[0].rstrip("/")

    # preparing for catalog views to clean up / keep filtering, page, pagination
    came_outside_catalog = False
    if current_url.strip("/").split("/")[0] == 'catalog':
        if previous_url.strip("/").split("/")[0] != 'catalog':
            came_outside_catalog = True
        else:
            if current_url != previous_url:
                came_outside_catalog = True
            else:
                came_outside_catalog = False

    # constructing full url with all params
    previous_full_url = previous_url
    if previous_full_url != "/":
        previous_page = str(request.session.get('previous_page', 1))
        previous_filters = request.session.get('filters', [])
        searched_list = request.session.get('searched_list', "")
        pag_by = request.session.get('pag_by', PAGINATE_BY_ITEMS_DEFAULT)
        previous_full_url += "/?page=" + previous_page + "&"
        for filter in previous_filters:
            previous_full_url += "characteristics=" + filter + "&"
        previous_full_url += "search=" + str(searched_list) + "&"
        previous_full_url += "Items_per_page=" + str(pag_by)

    # updating previous url is came not from /accounts app
    if previous_url != current_url and not previous_url.strip("/").split("/")[0] in PROHIBITED_PREVIOUS_URLS:
        request.session['previous_full_url'] = previous_full_url
        request.session['previous_url'] = previous_url
    else:
        if previous_url == "/accounts/cart":
            request.session['previous_full_url'] = previous_full_url
            request.session['previous_url'] = previous_url
        else:
            previous_url = request.session.get('previous_url', previous_url)
            previous_full_url = request.session.get('previous_full_url', previous_full_url)

    return {"previous_url": previous_url, "current_url": current_url, 'previous_full_url': previous_full_url,
            'came_outside_catalog': came_outside_catalog}


def get_searched_model(searched_list):
    searched_list = str(searched_list)
    q = Q()
    q |= Q(title__icontains=searched_list)
    q |= Q(category__name__icontains=searched_list)
    q |= Q(characteristics__name__icontains=searched_list)
    model = models.Cars.objects.filter(q).distinct()
    # if did not find any matches by whole search query, search by words
    if not model:
        q = Q()
        searched_list = searched_list.split(" ")
        for word in searched_list:
            q |= Q(title__icontains=word)
            q |= Q(category__name__icontains=word)
            q |= Q(characteristics__name__icontains=word)
        model = models.Cars.objects.filter(q).distinct()
    return model


# class for Navigation menu and footer
# to inherit in all views
class NavView(ContextMixin):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if Django_Online_Shop.settings.DEBUG == False:
            context["menu_list"] = LayoutModels.MenuList.objects.filter(is_active__exact=True).exclude(url__icontains="admin")
        else:
            context["menu_list"] = LayoutModels.MenuList.objects.filter(is_active__exact=True)
        # managing correct url prefix and suffix '/'
        for cont in context["menu_list"]:
            if len(cont.url) > 0:
                cont.url = "/" + cont.url.strip("/") + "/"
            else:
                cont.url = '/'

        # get footer
        context["footer"] = LayoutModels.Footer.objects.first()

        # get social links separate
        # to make east iteration, because stored in separate model
        if LayoutModels.SocialLinks.objects.exists():
            context["social_links"] = context["footer"].social_links.all()

        return context


# class for Pagination of Catalog
# to inherit in different views such as:
#   CarsListView
#   CarsByCategoryListView
# paginate_by shall be disabled within child class
# context["page_obj"] and context["paginator"] show wrong values
# on the next get_context_data()
# therefore are excluded from code, as well as paginate_by
# to avoid double pagination processing
class Pagination(ContextMixin):
    # defining model - inherited by child classes
    model = models.Cars

    def get_model(self):
        # getting model from child class
        class_name = self.__class__.__name__
        model = self.model
        # filtering model depending on view
        if class_name == "CarsSearchView":
            searched_list = self.request.GET.get('search')
            if searched_list:
                # if new search result
                searched_list = str(searched_list).strip(" ")
                self.request.session['searched_list'] = searched_list
                model = get_searched_model(searched_list)
            else:
                searched_list = self.request.session.get('searched_list', "")
                # if no new search result, get from memory
                # if memory empty - show all
                if searched_list:
                    model = get_searched_model(searched_list)
                else:
                    model = model.objects.all()
        elif class_name == "CarsListView":
            model = model.objects.all()
        else:
            model = model.objects.filter(category__slug__exact=self.kwargs['category'])

        model = model.order_by("-computed_rating", "-quantity", "pk")
        return model

    def get_context_data(self, *args, **kwargs):
        # standard - getting context
        context = super().get_context_data(*args, **kwargs)
        # if came not from same category clear all
        # later will be overriden by GET params if from accounts
        came_outside_catalog = get_previous_and_current_url(self.request)['came_outside_catalog']
        if came_outside_catalog == True:
            self.request.session['filters'] = []
            self.request.session['searched_list'] = ""
            self.request.session['previous_page'] = 1

        model = self.get_model()

        # send searched list to template
        context["searched_list"] = self.request.session.get('searched_list', "")

        # update if page is changed
        if 'page' in self.request.GET:
            self.request.session['previous_page'] = self.request.GET.get('page')

        # we keep previous page - because on form update current page is 1
        # so we remember what was the page before form change(items_per_page)
        page = int(self.request.session.get('previous_page', 1))

        # previous or standard value is taken for pagination
        # because we need to find out index of the first item BEFORE
        # the items_per_page was changed
        # if there is no previous value, perhaps user logged out
        # we check if GET sent for these reason
        pag_by = self.request.session.get('pag_by', None)
        if not pag_by:
            pag_by = self.request.GET.get('Items_per_page')
            if not pag_by:
                pag_by = PAGINATE_BY_ITEMS_DEFAULT
        pag_by = int(pag_by)
        # find out current page
        # by page and pagination before items_per_page was changed
        cars_list_index = (page - 1) * pag_by + 1

        # get dropdown menu value
        form = forms.ItemsPerPageForm(self.request.GET or None)
        if form.is_valid():
            self.request.session['pag_by'] = int(form.cleaned_data['Items_per_page'])
            # updating variable to find out new page with new pagination
            pag_by = int(form.cleaned_data['Items_per_page'])
        # On pages update, change page, whenever the dropdown box is not changed
        # put previous value
        else:
            form = forms.ItemsPerPageForm(initial={'Items_per_page': pag_by})

        # sending items_per_page form
        context["form"] = form

        # if clear all (filters) clicked we clear all filters
        # and go to first page if had filters
        if self.request.GET.get('filters-clear-all'):
            if self.request.session['filters']:
                cars_list_index = 1
                self.request.session['previous_page'] = 1
            self.request.session['filters'] = []

        # getting filters values
        main_filter_form = forms.MainFilter(self.request.GET or None)

        # only on submit filters
        if main_filter_form.is_valid():
            # save filter setup
            filters = main_filter_form.cleaned_data['characteristics']
            self.request.session['filters'] = filters
            # generate pagination - for filtered objects
            paginator = Paginator(model.filter(characteristics__name__in=filters), pag_by)
            # update values to send user to first page
            # on filters submission
            # if not from accounts
            if not self.request.GET.get('page'):
                cars_list_index = 1
                self.request.session['previous_page'] = 1
        else:
            if came_outside_catalog == True:
                # generate pagination - for all objects -
                # if by logic above - user shall be redirected to first page
                paginator = Paginator(model, pag_by)
            else:
                # if user change page or
                # clear filters or
                # search
                filters = self.request.session.get('filters', [])
                main_filter_form = forms.MainFilter(initial={'characteristics': filters})
                if filters:
                    # apply filters if have
                    paginator = Paginator(model.filter(characteristics__name__in=filters), pag_by)
                else:
                    # otherwise show all
                    paginator = Paginator(model, pag_by)

        # send filters to page
        context["main_filter_form"] = main_filter_form

        # calculating new page
        if cars_list_index % pag_by:
            cars_list = int(cars_list_index / pag_by) + 1
        else:
            cars_list = int(cars_list_index / pag_by)
        # exceptions
        # preparing objects list to display on page
        try:
            new_page = cars_list
            cars_list = paginator.page(cars_list)
        except PageNotAnInteger:
            # If page is not an integer deliver the first page
            cars_list = paginator.page(1)
            new_page = 1
        except EmptyPage:
            # If page is out of range deliver last page of results
            cars_list = paginator.page(paginator.num_pages)
            new_page = paginator.num_pages

        # put new calculated page as previous page
        # because context["page_obj"].number shows wrong number on
        # next get_context_data()
        self.request.session["previous_page"] = new_page

        # replace current pages
        # object to show
        context["cars_list"] = cars_list
        del cars_list

        # last page
        num_pages = paginator.num_pages

        # arange pages pagination numbers
        pages_list = []
        pages_middle_left = 0
        pages_middle_right = 0
        if num_pages > 5:
            if (num_pages - new_page) >= 2:
                if (new_page - 2) <= 0:
                    for i in range(1, 6):
                        # print 1-5 pages ...
                        pages_list.append(i)
                else:
                    for i in range(new_page - 2, new_page + 3):
                        # print ... x-2 x x+2 ... pages
                        pages_list.append(i)
            else:
                for i in range(num_pages - 4, num_pages + 1):
                    # print ... last 5 pages
                    pages_list.append(i)
            # print ... calculating middles form 1 to x-2 and x+2 to last page
            pages_middle_left = int((pages_list[0] - 1) / 2 + 1)
            pages_middle_right = int(ceil((num_pages - pages_list[4]) / 2) + pages_list[4])
        else:
            for i in range(1, num_pages + 1):
                # print some pages less then 5
                pages_list.append(i)
        # if ... middles == 1 or == 0 or == last page then
        # set None
        # used in template to hide elements ...
        if pages_middle_left in pages_list or pages_middle_left == 0:
            pages_middle_left = None
        if pages_middle_right in pages_list or pages_middle_right == 0:
            pages_middle_right = None
        context["pages_middle_left"] = pages_middle_left
        context["pages_list"] = pages_list
        context["pages_middle_right"] = pages_middle_right

        # sending categories
        # name for template
        # slug for url
        categories_list = models.Categories.objects.all().values('name', 'slug')

        # preparing urls for class - active
        # and page title
        path = self.request.path
        for i in range(len(categories_list)):
            categories_list[i]['url'] = '/catalog/category/' + categories_list[i]['slug'] + "/"
            if path == categories_list[i]['url']:
                context['catalog_title'] = categories_list[i]['name']
        # if current path did not match any of catalog urls
        if not 'catalog_title' in context:
            context['catalog_title'] = "All categories"

        # sending categories list
        context["categories_list"] = categories_list

        # preparing available filters for model
        temp_active_filters = models.Characteristics.objects.values("name").filter(cars__in=model).distinct()
        active_filters = []
        for filter in temp_active_filters:
            active_filters.append(filter['name'])
        context["active_filters"] = active_filters

        context["quantity"] = context["cars_list"].paginator.count
        return context


def rate(request, pk):
    from django.shortcuts import redirect
    if request.method == "POST":
        from django.contrib import messages
        if not request.user.is_authenticated:
            messages.warning(request,"Login to rate a product")
            return redirect(get_previous_and_current_url(request)["previous_full_url"])
        from django.db import transaction
        from accounts.models import Rating
        btn = request.POST.get("btn", None)
        if btn:
            with transaction.atomic():
                rating = Rating.objects.filter(user=request.user, car_id=pk).first()
                if not rating:
                    rating = Rating(user=request.user, rating=btn, car_id=pk)
                    rating.save()
                else:
                    rating.rating = btn
                    rating.save()
    return redirect(get_previous_and_current_url(request)["previous_full_url"])

class IndexView(NavView, generic.TemplateView):
    template_name = "index.html"

    def get_context_data(self, *args, **kwargs):
        # standard - getting context
        context = super().get_context_data(*args, **kwargs)
        model = models.Cars.objects.all()
        if not model:
            return context
        random_model = random.choice(list(model))
        context["random_model"] = random_model
        return context


# Main Catalog
class CarsListView(NavView, Pagination, generic.TemplateView):
    # redefining to pretty name
    template_name = "catalog.html"


class CarsByCategoryListView(NavView, Pagination, generic.TemplateView):
    template_name = "catalog.html"


class CarsSearchView(NavView, Pagination, generic.ListView):
    template_name = "catalog.html"

class CarDetailView(NavView, generic.DetailView):
    template_name = "car.html"
    model = models.Cars
    context_object_name = 'car'

    def get_context_data(self, *args, **kwargs):
        from collections import OrderedDict
        from accounts.models import Rating
        # standard - getting context
        context = super().get_context_data(*args, **kwargs)
        context["car_detail_path"] = self.request.path
        context["characteristics"] = context["car"].characteristics.all()
        context["go_back"] = get_previous_and_current_url(self.request)["previous_full_url"]
        context["quantity"] = kwargs["object"].quantity

        cart = self.request.session.get("cart", OrderedDict())
        if not cart:
            self.request.session["cart"] = OrderedDict()
        context["in_cart"] = True if str(kwargs["object"].pk) in self.request.session.get("cart", {}) else False
        if self.request.user.is_authenticated:
            rating = Rating.objects.filter(user=self.request.user, car_id=kwargs["object"].pk).values("rating").first()
            if rating:
                rating = rating["rating"]
                context["rating"] = rating
        context["category_url"] = \
            models.Categories.objects.filter(name__exact=context["car"].category).values('slug')[0]['slug']
        return context

def image_transfer(request):
    from django.http import HttpResponse
    import os

    def format_public_id(public_id):
        old_public_id = public_id.split('/')
        if "media" in old_public_id:
            old_public_id.remove('media')
        fname = old_public_id[-1].split(".")
        old_public_id[-1] = fname[0]
        old_public_id = "/".join(old_public_id)
        return old_public_id

    def get_default_images():
        cars = models.Cars.objects.all()[:8]
        default = {}
        for car in cars:
            old_public_id = format_public_id(car.image.public_id)
            filename = os.path.join("media", old_public_id + '.jpg')
            car.image = cloudinary.uploader.upload_resource(filename, resource_type="auto", public_id=filename, overwrite=True)
            default[old_public_id] = car.image
            car.save()
        return default

    def populate_all_products(default):
        cars = models.Cars.objects.all()[8:]
        for car in cars:
            if car.image.public_id in default.keys():
                car.image = default[car.image.public_id]
                car.save()

    try:
        default = get_default_images()
        populate_all_products(default)
    except Exception as error:
        return HttpResponse("Error while updating\n", error)
    return HttpResponse("Images updated")
