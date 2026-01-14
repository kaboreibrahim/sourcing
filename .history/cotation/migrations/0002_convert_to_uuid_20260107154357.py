from django.db import migrations, models
import uuid

def generate_uuid(apps, schema_editor):
    DemandeCotation = apps.get_model('cotation', 'DemandeCotation')
    for obj in DemandeCotation.objects.all():
        obj.uuid = uuid.uuid4()
        obj.save(update_fields=['uuid'])

class Migration(migrations.Migration):

    dependencies = [
        ('cotation', '0001_initial'),
    ]

    operations = [
        # 1. Ajouter un nouveau champ UUID
        migrations.AddField(
            model_name='demandecotation',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        
        # 2. Remplir le nouveau champ avec des UUID
        migrations.RunPython(generate_uuid, reverse_code=migrations.RunPython.noop),
        
        # 3. Supprimer l'ancien champ id
        migrations.RemoveField(
            model_name='demandecotation',
            name='id',
        ),
        
        # 4. Renommer le champ uuid en id
        migrations.RenameField(
            model_name='demandecotation',
            old_name='uuid',
            new_name='id',
        ),
        
        # 5. Définir le nouveau champ comme clé primaire
        migrations.AlterField(
            model_name='demandecotation',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
