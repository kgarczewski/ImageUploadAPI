from django.db import migrations

def create_default_plans(apps, schema_editor):
    Plan = apps.get_model('ImageUploader', 'Plan')
    basic = Plan.objects.create(name='Basic', thumbnail_200=True, thumbnail_400=False, original_file=False, expiring_links=False)
    premium = Plan.objects.create(name='Premium', thumbnail_200=True, thumbnail_400=True, original_file=True, expiring_links=False)
    enterprise = Plan.objects.create(name='Enterprise', thumbnail_200=True, thumbnail_400=True, original_file=True, expiring_links=True)

class Migration(migrations.Migration):

    dependencies = [
        ('ImageUploader', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_default_plans),
    ]
