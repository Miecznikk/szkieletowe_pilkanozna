# Generated by Django 4.0.4 on 2022-05-18 17:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Football', '0002_player_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='image',
            field=models.ImageField(null=True, upload_to='images/players/'),
        ),
        migrations.AlterField(
            model_name='player',
            name='position',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='Football.position'),
        ),
        migrations.AlterField(
            model_name='player',
            name='shirt_number',
            field=models.IntegerField(null=True),
        ),
    ]
