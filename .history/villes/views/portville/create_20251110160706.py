from django.views.generic import  CreateView ,View
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from port.models import Port
from villes.models import VillePort,Localite


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
        # Rediriger vers le détail de la commodité
        return reverse_lazy('ville-port-list')

    # def get_success_url(self):
    #     # Rediriger vers le détail de la commodité
    #     return reverse_lazy('commodite-detail', kwargs={'pk': self.object.commodite.pk})
       
    
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
    
    def form_valid(self, form):
        # Vérifier si la liaison existe déjà
        port = form.cleaned_data['port']
        ville = form.cleaned_data['ville']
        
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
            return JsonResponse({'ports': []})
        
        try:
            # Récupérer le pays de la ville via la localité
            localite = Localite.objects.filter(ville_id=ville_id).first()
            if not localite or not localite.ville or not localite.ville.pays:
                return JsonResponse({'ports': []})
                
            # Récupérer les ports du même pays
            ports = Port.objects.filter(
                pays=localite.ville.pays
            ).values('id', 'nom').order_by('nom')
            
            return JsonResponse({
                'ports': list(ports)
            })
        except Exception as e:
            return JsonResponse({
                'ports': [],
                'error': str(e)
            }, status=400)