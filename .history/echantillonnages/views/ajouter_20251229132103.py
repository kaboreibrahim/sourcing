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

    

class ModifierEchantillonView(LoginRequiredMixin, UpdateView):
    model = Echantionnage
    form_class = EchantionnageForm
    template_name = 'echantillons/ajouter_echantillon_modal.html'
    
    def form_valid(self, form):
        self.object = form.save()
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return super().form_valid(form)
        
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Données invalides'}, status=400)
        return super().form_invalid(form)