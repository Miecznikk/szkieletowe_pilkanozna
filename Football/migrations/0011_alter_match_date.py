# Generated by Django 4.0.4 on 2022-05-26 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Football', '0010_matchreport_challenge_challenging_team_goal_team_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='date',
            field=models.DateField(),
        ),
    ]
