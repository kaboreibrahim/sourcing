from django.views.generic import UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from port.models import Port
from port.forms import PortForm


class PortUpdateView(LoginRequiredMixin, UpdateView):
    model = Port
    form_class = PortForm
    template_name = 'port/port_form.html'
    context_object_name = 'port'

    def get_success_url(self):
        return reverse_lazy('port-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Le port a été mis à jour avec succès."))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier le port : {}" ).format(self.object.nom)
        context['submit_text'] = _("Mettre à jour")
        return context
