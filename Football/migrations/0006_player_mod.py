# Generated by Django 4.0.4 on 2022-05-21 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Football', '0005_player_captain_alter_player_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='mod',
            field=models.BooleanField(default=False),
        ),
    ]
