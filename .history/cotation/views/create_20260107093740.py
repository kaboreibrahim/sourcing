from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from cotation.models import DemandeCotation
from cotation.forms import DemandeCotationForm
from cotation.tasks import send_cotation_emails


class DemandeCotationCreateView(CreateView):
    """
    Vue pour créer une nouvelle demande de cotation
    """
    model = DemandeCotation
    form_class = DemandeCotationForm
    template_name = 'cotations/demande_cotation_form.html'
    success_url = reverse_lazy('cotation_success')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Lancer l'envoi des emails en arrière-plan
        send_cotation_emails.delay(self.object.id)
        
        messages.success(
            self.request,
            f'Votre demande de cotation a été enregistrée avec succès. '
            f'Référence: {self.object.ref}. Un email de confirmation vous sera envoyé.'
        )
        
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Une erreur est survenue lors de la soumission du formulaire. '
            'Veuillez corriger les erreurs ci-dessous.'
        )
        return super().form_invalid(form)
 