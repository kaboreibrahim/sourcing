from django.views.generic import  DetailView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone
from  villes.models import  Localite    
# ============================================================
# VUES POUR LES DETAILS DES LOCALITES
# ============================================================
class LocaliteDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une localité
    """
    model = Localite
    template_name = 'localite/localite_detail.html'
    context_object_name = 'localite'
    
    def get_queryset(self):
        """
        Optimise les requêtes en chargeant la ville et la zone en une seule requête
        """
        return Localite.objects.select_related('ville', 'ville__zone')