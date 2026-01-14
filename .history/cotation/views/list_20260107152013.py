from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from cotation.models import DemandeCotation, EmailQueue
from cotation.forms import DemandeCotationForm

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


# class DemandeCotationUpdateView(LoginRequiredMixin, UpdateView):
#     """
#     Vue pour mettre à jour le statut d'une demande de cotation
#     """
#     model = DemandeCotation
#     fields = ['statut']
#     template_name = 'cotations/demande_cotation_update.html'
    
#     def get_success_url(self):
#         return reverse_lazy('cotation_detail', kwargs={'pk': self.object.pk})
    
#     def form_valid(self, form):
#         messages.success(
#             self.request,
#             f'Le statut de la demande {self.object.ref} a été mis à jour.'
#         )
#         return super().form_valid(form)


def cotation_success_view(request):
    """
    Vue de confirmation après la soumission d'une demande
    """
    return render(request, 'cotations/cotation_success.html')


# # Vues basées sur des fonctions (alternative)

# def create_demande_cotation(request):
#     """
#     Vue fonction pour créer une demande de cotation
#     """
#     if request.method == 'POST':
#         form = DemandeCotationForm(request.POST)
#         if form.is_valid():
#             demande = form.save()
            
#             # Lancer l'envoi des emails en arrière-plan
#             send_cotation_emails.delay(demande.id)
            
#             messages.success(
#                 request,
#                 f'Votre demande de cotation a été enregistrée avec succès. '
#                 f'Référence: {demande.ref}. Un email de confirmation vous sera envoyé.'
#             )
            
#             return redirect('cotation_success')
#     else:
#         form = DemandeCotationForm()
    
#     return render(request, 'cotations/demande_cotation_form.html', {
#         'form': form
#     })


# def list_demandes_cotation(request):
#     """
#     Vue fonction pour lister les demandes de cotation
#     """
#     demandes = DemandeCotation.objects.all().order_by('-date_demande')
    
#     # Filtres
#     search = request.GET.get('search')
#     statut = request.GET.get('statut')
    
#     if search:
#         demandes = demandes.filter(
#             Q(nom_client__icontains=search) |
#             Q(contact__icontains=search) |
#             Q(commodite__nom__icontains=search)
#         )
    
#     if statut:
#         demandes = demandes.filter(statut=statut)
    
#     return render(request, 'cotations/demande_cotation_list.html', {
#         'demandes': demandes,
#         'statut_choices': DemandeCotation.STATUT_CHOICES,
#         'current_statut': statut or '',
#         'search_query': search or '',
#     })


# def detail_demande_cotation(request, pk):
#     """
#     Vue fonction pour afficher les détails d'une demande
#     """
#     demande = get_object_or_404(DemandeCotation, pk=pk)
#     return render(request, 'cotations/demande_cotation_detail.html', {
#         'demande': demande
#     })