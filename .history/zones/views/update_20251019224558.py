from django.views.generic import UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from zones.models import Zone

class ZoneUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Vue pour modifier une zone
    """
    model = Zone
    template_name = 'zone_form.html'
    fields = ['description']
    success_message = _("La zone %(numero)s a été modifiée avec succès")
    
    def get_success_url(self):
        return reverse_lazy('zone-detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        # Get the zone number from the saved instance
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return response

    def get_success_message(self, cleaned_data):
        return self.success_message % {'numero': self.object.numero}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier la zone %(numero)s") % {'numero': self.object.numero}
        context['button_text'] = _("Mettre à jour")
        return context