from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from cotation.models import EmailQueue
from cotation.forms import DemandeCotationForm
 


class EmailQueueListView(LoginRequiredMixin, ListView):
    """
    Vue pour afficher la liste des emails en attente
    """
    model = EmailQueue
    template_name = 'cotations/email_queue_list.html'
    context_object_name = 'emails'
    paginate_by = 50
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtres
        status = self.request.GET.get('status')
        email_type = self.request.GET.get('type')
        
        if status == 'sent':
            queryset = queryset.filter(sent=True)
        elif status == 'pending':
            queryset = queryset.filter(sent=False)
        
        if email_type:
            queryset = queryset.filter(email_type=email_type)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_count'] = EmailQueue.objects.filter(sent=False).count()
        context['sent_count'] = EmailQueue.objects.filter(sent=True).count()
        context['failed_count'] = EmailQueue.objects.filter(
            sent=False, attempts__gte=3
        ).count()
        return context
