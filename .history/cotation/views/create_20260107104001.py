from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from cotation.models import DemandeCotation
from cotation.forms import DemandeCotationForm
from cotation.utils.email_helpers import queue_all_emails


class DemandeCotationCreateView(CreateView):
    """
    Vue pour créer une nouvelle demande de cotation
    """
    model = DemandeCotation
    form_class = DemandeCotationForm
    template_name = 'cotations/create.html'
    success_url = reverse_lazy('cotation_list')
    
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
