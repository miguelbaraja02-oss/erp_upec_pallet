from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0005_invitation'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrole',
            name='company',
            field=models.ForeignKey(null=True, to='companies.company', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='userrole',
            unique_together={('user', 'company')},
        ),
    ]
