from django.db import migrations, models
import random


def generate_random_color():
    """Génère une couleur aléatoire au format hexadécimal (#RRGGBB)"""
    return '#{:02x}{:02x}{:02x}'.format(
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )


def set_default_colors(apps, schema_editor):
    Commodite = apps.get_model('commodites', 'Commodite')
    for commodite in Commodite.objects.all():
        if not hasattr(commodite, 'couleur') or not commodite.couleur or commodite.couleur == '#000000':
            commodite.couleur = generate_random_color()
            commodite.save(update_fields=['couleur'])


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
