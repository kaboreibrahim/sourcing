

from django.template.loader import render_to_string
from django.conf import settings
from cotation.models import EmailQueue


def queue_client_confirmation_email(demande):
    """
    Ajoute un email de confirmation client dans la queue
    """
    # Déterminer l'email du destinataire
    email_destinataire = demande.mail if '@' in demande.mail else None
    
    if not email_destinataire:
        return None
    
    # Contexte pour le template
    context = {
        'demande': demande,
        'nom_client': demande.nom_client,
        'commodite': demande.commodite.nom,
        'quantite': demande.quantite,
        'reference': demande.ref,
    }
    
    # Rendu du template HTML et texte
    html_content = render_to_string('emails/cotation_confirmation.html', context)
    text_content = render_to_string('emails/cotation_confirmation.txt', context)
    
    # Créer l'entrée dans la queue
    email_queue = EmailQueue.objects.create(
        demande=demande,
        email_type='CLIENT_CONFIRMATION',
        to_email=email_destinataire,
        subject=f'Confirmation de votre demande de cotation - {demande.ref}',
        html_content=html_content,
        text_content=text_content
    )
    
    return email_queue


def queue_admin_notification_email(demande):
    """
    Ajoute un email de notification admin dans la queue
    """
    # Liste des emails administrateurs
    admin_emails = getattr(settings, 'ADMIN_EMAILS', [settings.DEFAULT_FROM_EMAIL])
    
    context = {
        'demande': demande,
    }
    
    # Rendu du template HTML et texte
    html_content = render_to_string('emails/cotation_admin_notification.html', context)
    text_content = render_to_string('emails/cotation_admin_notification.txt', context)
    
    # Créer une entrée dans la queue pour chaque admin
    email_queues = []
    for admin_email in admin_emails:
        email_queue = EmailQueue.objects.create(
            demande=demande,
            email_type='ADMIN_NOTIFICATION',
            to_email=admin_email,
            subject=f'Nouvelle demande de cotation - {demande.ref}',
            html_content=html_content,
            text_content=text_content
        )
        email_queues.append(email_queue)
    
    return email_queues


def queue_all_emails(demande):
    """
    Ajoute tous les emails nécessaires dans la queue pour une demande
    """
    results = {
        'client_email': None,
        'admin_emails': []
    }
    
    # Email client
    try:
        results['client_email'] = queue_client_confirmation_email(demande)
    except Exception as e:
        print(f"Erreur lors de la création de l'email client: {e}")
    
    # Emails admin
    try:
        results['admin_emails'] = queue_admin_notification_email(demande)
    except Exception as e:
        print(f"Erreur lors de la création des emails admin: {e}")
    
    return results