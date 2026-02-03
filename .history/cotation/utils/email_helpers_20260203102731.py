from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import translation
from cotation.models import EmailQueue

# Variable globale pour stocker la langue sélectionnée
CURRENT_EMAIL_LANGUAGE = 'en'

def send_client_confirmation_email(demande, language=CURRENT_EMAIL_LANGUAGE):
    """
    Envoie directement un email de confirmation client
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
    
    # Sélectionner les templates selon la langue
    if language == 'en':
        html_template = 'emails/cotation_confirmation_en.html'
        text_template = 'emails/cotation_confirmation_en.txt'
        subject = f'Quotation Request Confirmation - {demande.ref}'
    else:
        html_template = 'emails/cotation_confirmation.html'
        text_template = 'emails/cotation_confirmation.txt'
        subject = f'Confirmation de votre demande de cotation - {demande.ref}'
    
    # Activer la langue pour le rendu des templates
    current_language = translation.get_language()
    try:
        translation.activate(language)
        
        # Rendu du template HTML et texte
        html_content = render_to_string(html_template, context)
        text_content = render_to_string(text_template, context)
        
        # Créer et envoyer l'email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email_destinataire]
        )
        email.attach_alternative(html_content, "text/html")
        
        try:
            email.send()
            return True
        except Exception as e:
            print(f"Erreur lors de l'envoi de l'email client: {e}")
            return False
    finally:
        # Restaurer la langue originale
        translation.activate(current_language)


def send_admin_notification_email(demande, language='en'):
    """
    Envoie directement un email de notification admin
    """
    # Liste des emails administrateurs
    admin_emails = getattr(settings, 'ADMIN_EMAILS', [settings.DEFAULT_FROM_EMAIL])
    cc_emails = getattr(settings, 'ADMIN_CC_EMAILS', ['kaboremessi@gmail.com','serge.debetou@oils-of-africa.com','liberia.office@oils-of-africa.com'])
    
    context = {
        'demande': demande,
    }
    
    # Sélectionner les templates selon la langue
    if language == 'en':
        html_template = 'emails/cotation_admin_notification_en.html'
        text_template = 'emails/cotation_admin_notification_en.txt'
        subject = f'New Quotation Request - {demande.ref}'
    else:
        html_template = 'emails/cotation_admin_notification.html'
        text_template = 'emails/cotation_admin_notification.txt'
        subject = f'Nouvelle demande de cotation - {demande.ref}'
    
    # Activer la langue pour le rendu des templates
    current_language = translation.get_language()
    try:
        translation.activate(language)
        
        # Rendu du template HTML et texte
        html_content = render_to_string(html_template, context)
        text_content = render_to_string(text_template, context)
        
        # Créer et envoyer l'email pour chaque admin
        results = []
        for admin_email in admin_emails:
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['sourcing@oils-of-africa.com'],
                cc=cc_emails
            )
            email.attach_alternative(html_content, "text/html")
            
            try:
                email.send()
                results.append(True)
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'email admin à {admin_email}: {e}")
                results.append(False)
        
        return results
    finally:
        # Restaurer la langue originale
        translation.activate(current_language)


def send_all_emails(demande, language='en'):
    """
    Envoie directement tous les emails nécessaires pour une demande
    """
    results = {
        'client_email': False,
        'admin_emails': []
    }
    
    # Email client
    try:
        results['client_email'] = send_client_confirmation_email(demande, language)
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email client: {e}")
        results['client_email'] = False
    
    # Emails admin
    try:
        results['admin_emails'] = send_admin_notification_email(demande, language)
    except Exception as e:
        print(f"Erreur lors de l'envoi des emails admin: {e}")
        results['admin_emails'] = []
    
    return results