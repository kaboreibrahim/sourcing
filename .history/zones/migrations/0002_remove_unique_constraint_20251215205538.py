from django.db import migrations, models


def remove_unique_constraint(apps, schema_editor):
    # Supprimer la contrainte d'unicité existante sur le champ numero
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            "SELECT conname FROM pg_constraint WHERE conname = 'zone_numero_key'"
        )
        if cursor.fetchone():
            cursor.execute(
                "ALTER TABLE zone DROP CONSTRAINT IF EXISTS zone_numero_key"
            )


class Migration(migrations.Migration):

    dependencies = [
        ('zones', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(remove_unique_constraint, migrations.RunPython.noop),
        # La contrainte composite (pays, numero) est déjà définie dans le modèle
    ]
