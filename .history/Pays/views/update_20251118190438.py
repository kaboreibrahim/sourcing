from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from ..models import Pays
from ..forms import PaysForm

class PaysUpdateView(UpdateView):
    model = Pays
    form_class = PaysForm
    template_name = 'pays/pays_form.html'
    context_object_name = 'pays'
    
    def get_success_url(self):
        return reverse_lazy('pays-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _("Les informations du pays ont été mises à jour avec succès!")
        )
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier le pays: {}").format(self.object.nom)
        context['submit_text'] = _("Mettre à jour")
        return context
