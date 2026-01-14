from django.db import migrations, models
import random

def set_default_colors(apps, schema_editor):
    Commodite = apps.get_model('commodites', 'Commodite')
    for commodite in Commodite.objects.all():
        if not commodite.couleur or commodite.couleur == '#000000':
            # Générer une couleur aléatoire
            commodite.couleur = '#{:02x}{:02x}{:02x}'.format(
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255)
            )
            commodite.save()

class Migration(migrations.Migration):

    dependencies = [
        ('commodites', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='commodite',
            name='couleur',
            field=models.CharField(
                default='#000000',
                help_text="Couleur pour l'affichage sur la carte (format hexadécimal)",
                max_length=7,
                verbose_name='Couleur'
            ),
        ),
        migrations.RunPython(set_default_colors, migrations.RunPython.noop),
    ]
