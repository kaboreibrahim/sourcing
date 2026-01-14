from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Q, Prefetch, F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth import get_user_model

from fournisseurs.models import Fournisseur, FournisseurPort
from fournisseurs.forms import FournisseurUserCreationForm
from commodites.models import FournisseurCommodite, Commodite
from zones.models import Zone
from villes.models import Ville

Utilisateur = get_user_model()

# ============================================================
# VUES POUR  DETAIL FOURNISSEUR
# ============================================================
 

class FournisseurDetailView(LoginRequiredMixin, DetailView, FormView):
    """
    Vue pour afficher les détails d'un fournisseur avec ses commodités
    et gérer la création de compte utilisateur
    """
    model = Fournisseur
    template_name = 'fournisseur_detail.html'
    context_object_name = 'fournisseur'
    form_class = FournisseurUserCreationForm
    
    def get_queryset(self):
        return Fournisseur.objects.select_related(
            'ville',
            'ville__zone'
        ).prefetch_related(
            'liens_commodites',
            'liens_commodites__commodite'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fournisseur = self.object = self.get_object()
        
        # Récupérer toutes les commodités fournies
        liens = fournisseur.liens_commodites.filter(
            deleted__isnull=True
        ).select_related('commodite').order_by('commodite__nom')
        
        # Vérifier si un compte utilisateur existe déjà pour ce fournisseur
        has_user_account = Utilisateur.objects.filter(
            last_name=fournisseur.nom,
            type_user='FS'
        ).exists()
        
        context.update({
            'liens_commodites': liens,
            'total_commodites': liens.count(),
            'has_coordinates': bool(fournisseur.latitude and fournisseur.longitude),
            'has_user_account': has_user_account,
            'user_form': self.get_form() if not has_user_account else None,
        })
        
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        # Vérifier si un compte existe déjà
        if Utilisateur.objects.filter(last_name=self.object.nom, type_user='FS').exists():
            messages.warning(request, _("Un compte utilisateur existe déjà pour ce fournisseur."))
            return redirect('fournisseur-detail', pk=self.object.pk)
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        fournisseur = self.get_object()
        
        # Créer l'utilisateur
        user = form.save(fournisseur=fournisseur)
        
        # Lier le fournisseur à l'utilisateur (ajoutez un champ user au modèle Fournisseur si nécessaire)
        # fournisseur.user = user
        # fournisseur.save(update_fields=['user'])
        
        messages.success(
            self.request,
            _("Le compte utilisateur a été créé avec succès. Identifiants : {}").format(
                form.cleaned_data['username']
            )
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('fournisseur-detail', kwargs={'pk': self.object.pk})
