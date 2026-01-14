# echantillonnages/views/ajouter.py
from django.shortcuts import get_object_or_404, redirect
from django.views.generic.edit import CreateView,UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from commodites.models import Commodite
from ..forms import EchantionnageForm
from echantillonnages.models import Echantionnage

class AjouterEchantillonView(LoginRequiredMixin, CreateView):
    model = Echantionnage
    form_class = EchantionnageForm
    template_name = 'echantillonnages/ajouter_echantillon_modal.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        if 'commodite_id' in self.kwargs:
            kwargs['commodite'] = get_object_or_404(Commodite, id=self.kwargs['commodite_id'])
        return kwargs
        
    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Échantillon ajouté avec succès!'
            })
        return super().form_valid(form)
        
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
        return super().form_invalid(form)

    

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.http import JsonResponse
from django.urls import reverse

class ModifierEchantillonView(LoginRequiredMixin, UpdateView):
    model = Echantionnage
    form_class = EchantionnageForm
    template_name = 'echantillons/ajouter_echantillon_modal.html'
    
    # def get_success_url(self):
    #     # Redirection vers la page de détail de la commodité
    #     return reverse('detail_commodite', kwargs={'pk': self.object.commodite.id})
    
    def form_valid(self, form):
        # Sauvegarder l'objet
        self.object = form.save(commit=False)
        
        # Si vous devez garder l'utilisateur d'origine ou faire d'autres modifications
        # self.object.utilisateur = self.request.user  # Si nécessaire
        
        self.object.save()
        
        # Réponse AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Échantillon modifié avec succès',
                'data': {
                    'id': self.object.id,
                    'quantite': str(self.object.quantite),
                    'prix': str(self.object.prix),
                    'date': self.object.date_creation.strftime('%d/%m/%Y %H:%M')
                }
            })
        
        # Redirection normale
        return super().form_valid(form)
        
    def form_invalid(self, form):
        # Réponse AJAX avec les erreurs
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(error) for error in error_list]
            
            return JsonResponse({
                'success': False, 
                'error': 'Données invalides',
                'errors': errors
            }, status=400)
        
        # Rendu normal avec les erreurs
        return super().form_invalid(form)