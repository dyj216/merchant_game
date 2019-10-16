from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import login_required
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic import RedirectView

from .models import Player, City, CityStock


def index(request):
    return render(request, 'merchant_game/index.html')


def city_stock_detail(request, city):
    stock_prices = CityStock.objects.filter(city=city, round=1)[0]
    return render(request, 'merchant_game/city_stock_detail.html', context={'city_stock': stock_prices})


def robbing(request, city):
    return render(request, 'merchant_game/robbing.html', context={'city': city})


def rob(request, city):
    # robber = Player.objects.filter(name=request.POST['robber'])[0]
    robber = get_object_or_404(Player, code=request.POST['robber'].upper())
    robbed = get_object_or_404(Player, code=request.POST['robbed'].upper())
    taken_valuables = request.POST['valuables']
    if taken_valuables == 'money':
        robber.money += robbed.money
        robbed.money = 0
    else:
        robber.item_1_amount += robbed.item_1_amount
        robber.item_2_amount += robbed.item_2_amount
        robber.item_3_amount += robbed.item_3_amount
        robber.item_4_amount += robbed.item_4_amount
        robber.item_5_amount += robbed.item_5_amount
        robber.item_6_amount += robbed.item_6_amount
        robbed.item_1_amount = 0
        robbed.item_2_amount = 0
        robbed.item_3_amount = 0
        robbed.item_4_amount = 0
        robbed.item_5_amount = 0
        robbed.item_6_amount = 0
    robber.save()
    robbed.save()
    return HttpResponseRedirect(reverse('merchant_game:city-stock', args=(city, )))


class CitiesView(LoginRequiredMixin, generic.ListView):
    login_url = '/admin/login/'

    model = City
    context_object_name = "cities"

    def get_queryset(self):
        return City.objects.all()


class PlayersView(generic.ListView):
    model = Player
    context_object_name = "players"
    # template_name = 'merchant_game/player_list.html'

    def get_queryset(self):
        return Player.objects.all()


class PlayerView(generic.DetailView):
    model = Player


class PlayerSearchRedirectView(RedirectView):
    permanent = False
    query_string = False
    pattern_name = 'merchant_game:player'

    def get_redirect_url(self, *args, **kwargs):
        player_code = self.request.GET["pk"].upper()
        get_object_or_404(Player, pk=player_code)
        return super().get_redirect_url(*args, pk=player_code, **kwargs)
