from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Sum
from .models import Echantionnage

@receiver([post_save, post_delete], sender=Echantionnage)
def update_quantite_totale(sender, instance, **kwargs):
    """
    Met à jour la quantité totale pour un fournisseur et une commodité donnés
    """
    if not instance.fournisseur or not instance.commodite:
        return
        
    # Calcule la somme des quantités pour ce fournisseur et cette commodité
    total = Echantionnage.objects.filter(
        fournisseur=instance.fournisseur,
        commodite=instance.commodite,
        deleted__isnull=True  # Ne pas compter les échantillons supprimés
    ).aggregate(total=Sum('quantite'))['total'] or 0
    
    # Met à jour tous les enregistrements concernés
    Echantionnage.objects.filter(
        fournisseur=instance.fournisseur,
        commodite=instance.commodite
    ).update(quantite_totale=total)
