import ImageUploader.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ImageUploader', '0002_auto_20230220_1530'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='account_tier',
            field=models.ForeignKey(blank=True, default=ImageUploader.models.get_default_plan, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='account_tier_users', to='ImageUploader.plan', to_field='name'),
        ),
    ]