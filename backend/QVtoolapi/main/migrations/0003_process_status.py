# Generated by Django 3.1.2 on 2020-12-28 23:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20201223_1449'),
    ]

    operations = [
        migrations.AddField(
            model_name='process',
            name='status',
            field=models.CharField(choices=[('Init', 'Initialization'), ('Dlg', 'Delegation'), ('Dlb', 'Deliberation'), ('Cur', 'Curation'), ('Elec', 'Election'), ('Res', 'Result')], default='Init', max_length=4),
        ),
    ]