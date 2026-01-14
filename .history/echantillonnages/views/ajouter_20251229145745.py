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
# Modifier la classe ModifierEchantillonView
class ModifierEchantillonView(LoginRequiredMixin, UpdateView):
    model = Echantionnage
    form_class = EchantionnageForm
    template_name = 'echantillons/ajouter_echantillon_modal.html'
    pk_url_kwarg = 'pk'  # Ajout de cette ligne pour clarifier le nom du paramètre d'URL

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.save()
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Échantillon modifié avec succès',
                'data': {
                    'id': str(self.object.id),
                    'quantite': str(self.object.quantite),
                    'prix': str(self.object.prix),
                    'date': self.object.date_creation.strftime('%Y-%m-%dT%H:%M')  # Format ISO pour les inputs datetime-local
                }
            })
        return super().form_valid(form)
        
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            errors = {field: [str(error) for error in error_list] 
                     for field, error_list in form.errors.items()}
            return JsonResponse({
                'success': False, 
                'errors': errors
            }, status=400)
        return super().form_invalid(form)