

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from cotation.models import DemandeCotation, EmailQueue
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Envoie les emails en attente dans la queue'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-emails',
            type=int,
            default=50,
            help='Nombre maximum d\'emails à envoyer par exécution'
        )
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='Réessayer d\'envoyer les emails échoués'
        )

    def handle(self, *args, **options):
        max_emails = options['max_emails']
        retry_failed = options['retry_failed']
        
        self.stdout.write(self.style.SUCCESS(
            f'Démarrage de l\'envoi des emails (max: {max_emails})...'
        ))
        
        # Récupérer les emails en attente
        queryset = EmailQueue.objects.filter(
            sent=False,
            attempts__lt=3
        ).order_by('created_at')[:max_emails]
        
        if retry_failed:
            queryset = EmailQueue.objects.filter(
                sent=False
            ).order_by('created_at')[:max_emails]
        
        total_sent = 0
        total_failed = 0
        
        for email_item in queryset:
            try:
                self.stdout.write(f'Envoi de l\'email {email_item.id}...')
                
                # Créer l'email
                cc_emails = [email.strip() for email in email_item.cc_emails.split(',')] if email_item.cc_emails else []
                
                email = EmailMessage(
                    subject=email_item.subject,
                    body=email_item.html_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email_item.to_email],
                    cc=cc_emails,
                )
                email.content_subtype = 'html'
                
                # Envoyer
                email.send(fail_silently=False)
                
                # Marquer comme envoyé
                email_item.sent = True
                email_item.sent_at = timezone.now()
                email_item.attempts += 1
                email_item.save()
                
                total_sent += 1
                self.stdout.write(self.style.SUCCESS(
                    f'✓ Email {email_item.id} envoyé avec succès'
                ))
                
            except Exception as e:
                email_item.attempts += 1
                email_item.error_message = str(e)
                email_item.save()
                
                total_failed += 1
                self.stdout.write(self.style.ERROR(
                    f'✗ Erreur lors de l\'envoi de l\'email {email_item.id}: {str(e)}'
                ))
                logger.error(f'Erreur envoi email {email_item.id}: {str(e)}')
        
        # Résumé
        self.stdout.write(self.style.SUCCESS(
            f'\n--- Résumé ---'
        ))
        self.stdout.write(f'Emails envoyés: {total_sent}')
        self.stdout.write(f'Emails échoués: {total_failed}')
        
        # Nettoyer les anciens emails envoyés (plus de 30 jours)
        deleted_count = EmailQueue.objects.filter(
            sent=True,
            sent_at__lt=timezone.now() - timezone.timedelta(days=30)
        ).delete()[0]
        
        if deleted_count > 0:
            self.stdout.write(self.style.WARNING(
                f'Nettoyage: {deleted_count} anciens emails supprimés'
            ))