from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from ..models import Pays
from ..forms import PaysForm

class PaysCreateView(CreateView):
    model = Pays
    form_class = PaysForm
    template_name = 'pays/pays_form.html'
    success_url = reverse_lazy('pays-list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _("Le pays a été créé avec succès!")
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer un nouveau pays")
        context['submit_text'] = _("Créer")
        return context
