# Generated by Django 3.2.3 on 2024-09-19 12:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20240919_1459'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='subscribers',
        ),
    ]
