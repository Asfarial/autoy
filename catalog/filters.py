from django.contrib.admin import SimpleListFilter
from django.utils.translation import gettext_lazy as _
from .models import Cars


def get_prices_steps():
    prices = []
    i = 0
    for car in Cars.objects.all():
        prices.append(car.price)
        i += 1
    if not prices:
        return
    max_price = max(prices)
    max_price = max_price - max_price % 10 + 10
    min_price = min(prices)
    min_price = min_price - min_price % 10
    dif = max_price - min_price

    steps = int(dif / 100)
    if not steps:
        return
    steps_price = int(dif / steps)
    list_steps = []
    temp = min_price
    sum = 0
    for y in range(steps):
        list_steps.append(temp + steps_price)
        sum += list_steps[y]
    if sum < max_price:
        list_steps[steps - 1] += max_price - sum
    list_steps.insert(0, min_price)
    list_steps.append(max_price)

    return list_steps


def list_lookup(list_steps):
    if not list_steps:
        return
    list_names = []
    l = len(list_steps)
    for i in range(l):
        if i > 0 and i < l - 1:
            list_names.append(list_steps[i] + list_names[i - 1])
        elif i == 0:
            list_names.append(list_steps[i])
    del list_steps

    temp_list = []
    list_lists = []
    l = len(list_names)
    for i in range(l):
        if i < l - 1:
            temp_list.append(list_names[i])
            temp_list.append(list_names[i + 1])
            list_lists.append(temp_list)
            temp_list = []
    del list_names
    return list_lists


def make_tuple(list_lists):
    if not list_lists:
        return
    list_str = []
    l = len(list_lists)
    for i in range(l):
        list_str.append(str(list_lists[i][0]) + "-" + str(list_lists[i][1]))
    temp_list = []
    tuple_list = []
    for i in list_str:
        temp_list.append(i)
        temp_list.append(i)
        tuple_list.append(tuple(temp_list))
        temp_list = []
    del list_str
    tuple_list = tuple(tuple_list)
    return tuple_list


class PricesRangeFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.

    title = _('Prices range')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'price'



    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        self.list_lists = list_lookup(get_prices_steps())
        self.list_tuple = make_tuple(self.list_lists)
        return self.list_tuple

    def queryset(self, request, queryset):
        """
            Returns the filtered queryset based on the value
            provided in the query string and retrievable via
            `self.value()`.
            """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.

        l = len(self.list_lists)
        for i in range(l):
            if self.value() == self.list_tuple[i][0]:
                return queryset.filter(price__range=(self.list_lists[i][0], self.list_lists[i][1]))
