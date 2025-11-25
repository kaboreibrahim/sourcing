from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin

from port.models import Port


class PortDeleteView(LoginRequiredMixin, DeleteView):
    model = Port
    template_name = 'port/port_confirm_delete.html'
    context_object_name = 'port'

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse_lazy('port-list')

    def get_object(self, queryset=None):
        return get_object_or_404(Port, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, _("Le port a été supprimé avec succès."))
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Confirmer la suppression du port")
        return context
