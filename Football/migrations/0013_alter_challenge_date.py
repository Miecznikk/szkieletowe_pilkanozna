# Generated by Django 4.0.4 on 2022-05-27 14:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Football', '0012_alter_challenge_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
