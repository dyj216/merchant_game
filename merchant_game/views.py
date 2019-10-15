from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.views.generic import RedirectView

from .models import Player, City


def index(request):
    return render(request, 'merchant_game/index.html')


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
