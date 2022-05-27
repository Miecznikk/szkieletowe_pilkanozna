# Generated by Django 4.0.4 on 2022-05-27 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Football', '0015_match_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostScore',
            fields=[
                ('message_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='Football.message')),
            ],
            bases=('Football.message',),
        ),
        migrations.AlterField(
            model_name='match',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]