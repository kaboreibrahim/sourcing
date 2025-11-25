from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from ..models import Pays

class PaysDeleteView(DeleteView):
    model = Pays
    template_name = 'pays/pays_confirm_delete.html'
    context_object_name = 'pays'
    
    def get_success_url(self):
        # Rediriger vers la liste des pays ou vers la page précédente
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('pays:list')
    
    def get_object(self, queryset=None):
        # Récupérer l'objet avec gestion d'erreur 404
        return get_object_or_404(Pays, pk=self.kwargs['pk'])
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(
            self.request,
            _("Le pays a été supprimé avec succès.")
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ajouter le titre de la page
        context['title'] = _("Confirmer la suppression")
        return context