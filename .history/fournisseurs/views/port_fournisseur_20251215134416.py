from django.views.generic import CreateView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from port.models import Port
from fournisseurs.models import Fournisseur, FournisseurPort
from villes.models import Localite

# ============================================================
# VUES POUR LA PORTFOURNISSEUR CREATE
# ============================================================

class PortFournisseurCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """
    Vue pour créer une nouvelle liaison fournisseur-port
    """
    model = FournisseurPort
    template_name = 'port_fournisseur_form.html'
    fields = ['port', 'distance']
    success_message = _("La liaison a été créée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('fournisseur-detail', kwargs={'pk': self.kwargs['fournisseur_id']})
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # Récupérer le fournisseur
        fournisseur = get_object_or_404(Fournisseur, id=self.kwargs['fournisseur_id'])
        
        # Filtrer les ports du même pays que le fournisseur
        if hasattr(fournisseur, 'get_zone') and fournisseur.get_zone():
            pays = fournisseur.get_zone().pays
            form.fields['port'].queryset = Port.objects.filter(pays=pays)
        
        # Ajouter des attributs pour le chargement dynamique
        form.fields['port'].widget.attrs.update({
            'id': 'id_port',
            'class': 'form-control'
        })
        
        form.fields['distance'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Laisser vide pour calculer automatiquement')
        })
        
        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fournisseur = get_object_or_404(Fournisseur, id=self.kwargs['fournisseur_id'])
        
        context.update({
            'title': _("Ajouter un port pour le fournisseur"),
            'button_text': _("Ajouter"),
            'fournisseur': fournisseur,
            'ports_lies': FournisseurPort.objects.filter(fournisseur=fournisseur).select_related('port')
        })
        
        return context
        
    def form_valid(self, form):
        port = form.cleaned_data['port']
        fournisseur = get_object_or_404(Fournisseur, id=self.kwargs['fournisseur_id'])
        
        # Vérifier si le port est dans le même pays que le fournisseur
        if fournisseur.get_zone() and fournisseur.get_zone().pays != port.pays:
            form.add_error(
                None,
                _("Erreur: Le port %(port)s n'est pas dans le même pays que le fournisseur.") % {
                    'port': port.nom
                }
            )
            return self.form_invalid(form)

        # Vérifier si la liaison existe déjà
        existing = FournisseurPort.objects.filter(
            fournisseur=fournisseur,
            port=port,
            deleted__isnull=True
        ).exists()

        if existing:
            form.add_error(
                None,
                _("Ce port est déjà associé à ce fournisseur.")
            )
            return self.form_invalid(form)

        # Créer et sauvegarder
        self.object = form.save(commit=False)
        self.object.fournisseur = fournisseur
        
        # Si la distance n'est pas fournie, essayer de la calculer
        if not self.object.distance:
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
                "Vous pouvez la saisir manuellement en modifiant la liaison.")
            )

        return super().form_valid(form)


 
class LoadPortsByFournisseurView(LoginRequiredMixin, View):
    """
    Vue AJAX pour charger les ports en fonction du pays du fournisseur
    """
    def get(self, request, fournisseur_id):
        try:
            fournisseur = get_object_or_404(Fournisseur, id=fournisseur_id)
            
            if not hasattr(fournisseur, 'get_zone') or not fournisseur.get_zone():
                return JsonResponse({
                    'ports': [],
                    'error': 'Impossible de déterminer le pays du fournisseur.'
                }, status=400)
                
            pays = fournisseur.get_zone().pays
            
            # Exclure les ports déjà associés à ce fournisseur
            ports_associes = FournisseurPort.objects.filter(
                fournisseur=fournisseur,
                deleted__isnull=True
            ).values_list('port_id', flat=True)
            
            ports = Port.objects.filter(
                pays=pays
            ).exclude(
                id__in=ports_associes
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