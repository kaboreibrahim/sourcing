from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from port.models import Port
from villes.models import Localite, PortLocalite

# ============================================================
# VUES POUR LA PORTLOCALITE CREATE
# ============================================================

class PortLocaliteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle liaison port-ville
    """
    model = PortLocalite
    template_name = 'portlocalite/port_localite_form.html'
    fields = ['port', 'localite']
    success_message = _("La liaison a été créée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('port-localite-list')
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Ajouter des attributs pour le chargement dynamique
        form.fields['localite'].widget.attrs.update({
            'id': 'id_localite',
            'onchange': 'loadPortsByPays(this.value)'
        })
        
        form.fields['port'].widget.attrs.update({
            'id': 'id_port'
        })
        
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer une liaison Port-Localite")
        context['button_text'] = _("Créer")
        
        # Si un port est passé en paramètre
        port_id = self.request.GET.get('port')
        if port_id:
            context['port_preselected'] = port_id
        
        # Si une localite est passée en paramètre
        localite_id = self.request.GET.get('localite')
        if localite_id:
            context['localite_preselected'] = localite_id
        
        return context
        
    def form_valid(self, form):
        port = form.cleaned_data['port']
        localite = form.cleaned_data['localite']  # Instance déjà correcte

        # Vérifier si le port est dans le même pays que la localite
        if localite.ville.zone.pays != port.pays:
            form.add_error(
                None,
                _("Erreur: Le port %(port)s n'est pas dans le même pays que la localite sélectionnée.") % {
                    'port': port.nom
                }
            )
            return self.form_invalid(form)

        # Vérifier si la liaison existe déjà
        existing = PortLocalite.objects.filter(
            port=port,
            localite=localite,
            deleted__isnull=True
        ).first()

        if existing:
            form.add_error(
                None,
                _("Cette liaison existe déjà entre %(port)s et %(localite)s") % {
                    'port': port.nom,
                    'localite': localite.nom
                }
            )
            return self.form_invalid(form)

        # Créer et sauvegarder
        self.object = form.save(commit=False)
        self.object.calculate_distance()
        self.object.save()

        # Message de succès
        if self.object.distance is not None:
            messages.success(
                self.request,
                _("La liaison a été créée avec succès. Distance calculée : %(distance).2f km") % {
                    'distance': self.object.distance
                }
            )
        else:
            messages.warning(
                self.request,
                _("La liaison a été créée mais n'a pas pu calculer la distance. "
                "Vérifiez que les coordonnées du port et de la ville sont correctes.")
            )

        return super().form_valid(form)


 
class LoadPortsByPaysLocaliteView(LoginRequiredMixin, View):
    """
    Vue AJAX pour charger les ports en fonction du pays de la localite
    """
    def get(self, request):
        localite_id = request.GET.get('localite_id')
        
        if not localite_id:
            return JsonResponse({'ports': []}, status=400)
        
        try:
            localite = Localite.objects.filter(id=localite_id).first()
            
            if not localite:
                return JsonResponse({'ports': [], 'error': 'Localite non trouvée'}, status=404)
                
            # Get the country through ville.zone.pays
            pays = localite.ville.zone.pays
            ports = Port.objects.filter(
                pays=pays
            ).values('id', 'nom').order_by('nom')
            
            return JsonResponse({
                'ports': list(ports)
            })
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return JsonResponse({
                'ports': [],
                'error': str(e)
            }, status=500)