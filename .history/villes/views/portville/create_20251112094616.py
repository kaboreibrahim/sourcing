from django.views.generic import CreateView, View
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from port.models import Port
from villes.models import VillePort, Localite

# ============================================================
# VUES POUR LA PORTVILLE CREATE
# ============================================================

class VillePortCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle liaison port-ville
    """
    model = VillePort
    template_name = 'portville/ville_port_form.html'
    fields = ['port', 'ville']
    success_message = _("La liaison a été créée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('ville')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Ajouter des attributs pour le chargement dynamique
        form.fields['ville'].widget.attrs.update({
            'id': 'id_ville',
            'onchange': 'loadPortsByPays(this.value)'
        })
        
        form.fields['port'].widget.attrs.update({
            'id': 'id_port'
        })
        
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer une liaison Port-Ville")
        context['button_text'] = _("Créer")
        
        # Si un port est passé en paramètre
        port_id = self.request.GET.get('port')
        if port_id:
            context['port_preselected'] = port_id
        
        # Si une ville est passée en paramètre
        ville_id = self.request.GET.get('ville')
        if ville_id:
            context['ville_preselected'] = ville_id
        
        return context
    
    def form_valid(self, form):
        # Vérifier si la liaison existe déjà
        port = form.cleaned_data['port']
        ville = form.cleaned_data['ville']
        
        # Vérifier si le port est dans le même pays que la ville
        localite = Localite.objects.filter(ville=ville).first()
        if localite and localite.ville.zone.pays != port.pays:
            form.add_error(
                None,
                _("Erreur: Le port %(port)s n'est pas dans le même pays que la ville sélectionnée.") % {
                    'port': port.nom
                }
            )
            return self.form_invalid(form)
        
        existing = VillePort.objects.filter(
            port=port,
            ville=ville,
            deleted__isnull=True
        ).first()
        
        if existing:
            form.add_error(
                None,
                _("Cette liaison existe déjà entre %(port)s et %(ville)s") % {
                    'port': port.nom,
                    'ville': ville.nom
                }
            )
            return self.form_invalid(form)
        
        return super().form_valid(form)

 
class LoadPortsByPaysView(LoginRequiredMixin, View):
    """
    Vue AJAX pour charger les ports en fonction du pays de la ville
    """
    def get(self, request):
        ville_id = request.GET.get('ville_id')
        
        if not ville_id:
            return JsonResponse({'ports': []}, status=400)
        
        try:
            # Récupérer la ville
            from villes.models import Ville
            ville = Ville.objects.filter(id=ville_id).first()
            
            if not ville:
                return JsonResponse({'ports': [], 'error': 'Ville non trouvée'}, status=404)
                
            # Récupérer les ports du même pays que la zone de la ville
            ports = Port.objects.filter(
                pays=ville.zone.pays
            ).values('id', 'nom').order_by('nom')
            
            return JsonResponse({
                'ports': list(ports)
            })
        except Exception as e:
            import traceback
            print(traceback.format_exc())  # Pour le débogage
            return JsonResponse({
                'ports': [],
                'error': str(e)
            }, status=500)