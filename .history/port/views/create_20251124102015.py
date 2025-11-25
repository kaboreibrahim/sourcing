from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin

from port.models import Port
from port.forms import PortForm


class PortCreateView(LoginRequiredMixin, CreateView):
    model = Port
    form_class = PortForm
    template_name = 'port/port_form.html'
    success_url = reverse_lazy('port-list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Le port a été créé avec succès."))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Créer un nouveau port")
        context['submit_text'] = _("Créer")
        return context
