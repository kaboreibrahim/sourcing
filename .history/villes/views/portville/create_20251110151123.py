from django.views.generic import  CreateView 
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from port.models import Port
from villes.models import VillePort

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

 
# villes/views/portville/ports.py
from django.http import JsonResponse
from port.models import Port
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _

@require_http_methods(["GET"])
def get_ports_by_ville_pays(request, ville_id=None):
    try:
        if ville_id and ville_id != '0':
            from villes.models import Ville
            try:
                ville = Ville.objects.get(pk=ville_id)
                ports = Port.objects.filter(pays=ville.pays, deleted__isnull=True)
            except Ville.DoesNotExist:
                ports = Port.objects.filter(deleted__isnull=True)
        else:
            ports = Port.objects.filter(deleted__isnull=True)
            
        ports_data = [{'id': port.id, 'nom': port.nom} for port in ports]
        return JsonResponse({'ports': ports_data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)