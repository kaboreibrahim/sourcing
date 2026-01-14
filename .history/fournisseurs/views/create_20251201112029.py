from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from fournisseurs.models import Fournisseur
from villes.models import Localite
from django.conf import settings

class FournisseurCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer un nouveau fournisseur
    """
    model = Fournisseur
    template_name = 'fournisseur_form.html'
    fields = [
        'nom', 'nom_responsable', 'contact', 'ville', 'localite',
        'latitude', 'longitude', 'document_fourni_aex'
    ]
    success_message = _("Le fournisseur %(nom)s a été créé avec succès")
    
    def get_success_url(self):
        return reverse_lazy('fournisseur-detail', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer un nouveau fournisseur")
        context['button_text'] = _("Créer")
        
        # Si une ville est passée en paramètre
        ville_id = self.request.GET.get('ville')
        if ville_id:
            context['ville_preselected'] = ville_id
         # Ajouter le token Mapbox pour la carte interactive
        context['mapbox_token'] = getattr(settings, 'MAPBOX_ACCESS_TOKEN', '')
       
        return context
    
    def get_form(self, form_class=None):
        """
        Personnaliser le formulaire pour ajouter des attributs aux champs
        """
        form = super().get_form(form_class)
        
        # Ajouter un attribut data pour identifier le champ ville
        form.fields['ville'].widget.attrs.update({
            'id': 'id_ville',
            'onchange': 'loadLocalites(this.value)'
        })
        
        form.fields['localite'].widget.attrs.update({
            'id': 'id_localite'
        })
        
        return form


class LoadLocalitesView(LoginRequiredMixin, View):
    """
    Vue AJAX pour charger les localités d'une ville
    """
    def get(self, request):
        ville_id = request.GET.get('ville_id')
        
        if not ville_id:
            return JsonResponse({'localites': []})
        
        try:
            # Utiliser distinct() pour éviter les doublons
            localites = Localite.objects.filter(
                ville_id=ville_id
            ).values('id', 'nom').distinct().order_by('nom')
            
            return JsonResponse({
                'localites': list(localites)
            })
        except Exception as e:
            return JsonResponse({
                'localites': [],
                'error': str(e)
            }, status=400)