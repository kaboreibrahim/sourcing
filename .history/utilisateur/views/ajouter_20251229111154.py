from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView
from commodites.models import Commodite
from django.urls import reverse_lazy
from commodites.forms import CommoditeForm