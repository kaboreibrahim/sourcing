from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from cotation.models import DemandeCotation
from cotation.forms import DemandeCotationForm
from cotation.utils.email_helpers import queue_all_emails
import uuid

class DemandeCotationCreateView(CreateView):
    """
    Vue pour créer une nouvelle demande de cotation
    """
    model = DemandeCotation
    form_class = DemandeCotationForm
    template_name = 'cotations/create.html'
    success_url = reverse_lazy('cotation_success')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Ajouter les emails dans la queue
        queue_all_emails(self.object)
        
        messages.success(
            self.request,
            f'Votre demande de cotation a été enregistrée avec succès. '
            f'Référence: {self.object.ref}. Un email de confirmation vous sera envoyé sous peu.'
        )
        
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Une erreur est survenue lors de la soumission du formulaire. '
            'Veuillez corriger les erreurs ci-dessous.'
        )
        return super().form_invalid(form)


def cotation_success_view(request):
    """
    Vue de confirmation après la soumission d'une demande
    """
    return render(request, 'cotations/cotation_success.html')


class DemandeCotationUpdateView(LoginRequiredMixin, UpdateView):
    """
    Vue pour mettre à jour le statut d'une demande de cotation
    """
    model = DemandeCotation
    fields = ['statut']
    template_name = 'cotations/update.html'
    pk_url_kwarg = 'pk'
    
    def get_object(self, queryset=None):
        try:
            # Convertir l'UUID de l'URL en objet UUID
            uuid_str = self.kwargs.get(self.pk_url_kwarg)
            uuid_obj = uuid.UUID(str(uuid_str))
            return get_object_or_404(DemandeCotation, pk=uuid_obj)
        except (ValueError, TypeError):
            raise Http404("Demande de cotation non trouvée")
    
    def get_success_url(self):
        return reverse_lazy('cotation_detail', kwargs={'pk': str(self.object.pk)})
    
    def form_valid(self, form):
        messages.success(
            self.request,
            f'Le statut de la demande {self.object.ref} a été mis à jour.'
        )
        return super().form_valid(form)
