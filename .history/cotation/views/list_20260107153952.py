from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from cotation.models import DemandeCotation, EmailQueue
from cotation.forms import DemandeCotationForm
import uuid
from django.http import Http404

class DemandeCotationListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste de toutes les demandes de cotation
    """
    model = DemandeCotation
    template_name = 'cotations/list.html'
    context_object_name = 'demandes'
    paginate_by = 20
    ordering = ['-date_demande']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres de recherche
        search = self.request.GET.get('search')
        statut = self.request.GET.get('statut')
        
        if search:
            queryset = queryset.filter(
                Q(nom_client__icontains=search) |
                Q(contact__icontains=search) |
                Q(commodite__nom__icontains=search)
            )
        
        if statut:
            queryset = queryset.filter(statut=statut)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statut_choices'] = DemandeCotation.STATUT_CHOICES
        context['current_statut'] = self.request.GET.get('statut', '')
        context['search_query'] = self.request.GET.get('search', '')
        
        # Ajouter le nombre d'emails en attente
        context['pending_emails_count'] = EmailQueue.objects.filter(sent=False).count()
        
        return context

class DemandeCotationDetailView(LoginRequiredMixin, DetailView):
    """
    Vue pour afficher les détails d'une demande de cotation
    """
    model = DemandeCotation
    template_name = 'cotations/detail.html'
    context_object_name = 'demande'
    pk_url_kwarg = 'pk'
    
    def get_object(self, queryset=None):
        try:
            # Convertir l'UUID de l'URL en objet UUID
            uuid_str = self.kwargs.get(self.pk_url_kwarg)
            uuid_obj = uuid.UUID(str(uuid_str))
            return get_object_or_404(DemandeCotation, pk=uuid_obj)
        except (ValueError, TypeError):
            raise Http404("Demande de cotation non trouvée")


def cotation_success_view(request):
    """
    Vue de confirmation après la soumission d'une demande
    """
    return render(request, 'cotations/cotation_success.html')


 

 