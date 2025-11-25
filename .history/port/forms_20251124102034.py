from django import forms
from django.utils.translation import gettext_lazy as _

from port.models import Port


class PortForm(forms.ModelForm):
    """Formulaire pour la création et la mise à jour d'un port."""

    class Meta:
        model = Port
        fields = ["nom", "latitude", "longitude", "pays"]
        labels = {
            "nom": _("Nom du port"),
            "latitude": _("Latitude"),
            "longitude": _("Longitude"),
            "pays": _("Pays"),
        }
        widgets = {
            "nom": forms.TextInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                    "placeholder": _("Ex: Port d'Abidjan, Port de San-Pedro..."),
                }
            ),
            "latitude": forms.NumberInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                    "step": "any",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "class": "form-input mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                    "step": "any",
                }
            ),
            "pays": forms.Select(
                attrs={
                    "class": "form-select mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50",
                }
            ),
        }
