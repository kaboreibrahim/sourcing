from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.db import transaction

from cotation.models import EmailQueue

class Command(BaseCommand):
    help = 'Envoie les emails en attente dans la file d\'attente des emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-emails',
            type=int,
            default=50,
            help='Nombre maximum d\'emails à envoyer (défaut: 50)'
        )
        parser.add_argument(
            '--retry-failed',
            action='store_true',
            help='Réessayer les emails en échec (plus de 3 tentatives)'
        )

    def handle(self, *args, **options):
        max_emails = options['max_emails']
        retry_failed = options['retry_failed']
        
        # Récupérer les emails en attente
        queryset = EmailQueue.objects.filter(sent=False)
        
        if not retry_failed:
            queryset = queryset.filter(attempts__lt=3)
        
        emails = queryset.select_related('demande').order_by('created_at')[:max_emails]
        
        if not emails:
            self.stdout.write(self.style.SUCCESS('Aucun email à envoyer.'))
            return
        
        self.stdout.write(f'Envoi de {len(emails)} emails...')
        
        success_count = 0
        for email in emails:
            try:
                with transaction.atomic():
                    # Marquer l'email comme en cours d'envoi
                    email.attempts += 1
                    email.save(update_fields=['attempts', 'updated_at'])
                    
                    # Envoyer l'email
                    send_mail(
                        subject=email.subject,
                        message=email.text_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[email.to_email],
                        html_message=email.html_content,
                        fail_silently=False,
                    )
                    
                    # Marquer comme envoyé
                    email.sent = True
                    email.sent_at = timezone.now()
                    email.save(update_fields=['sent', 'sent_at', 'updated_at'])
                    
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f'Email envoyé: {email.to_email}'))
                    
            except Exception as e:
                error_msg = str(e)
                email.error_message = error_msg[:500]  # Limiter la taille du message d'erreur
                email.save(update_fields=['error_message', 'updated_at'])
                self.stdout.write(
                    self.style.ERROR(f'Erreur d\'envoi à {email.to_email}: {error_msg}')
                )
        
        self.stdout.write(self.style.SUCCESS(f'Terminé. {success_count}/{len(emails)} emails envoyés avec succès.'))
