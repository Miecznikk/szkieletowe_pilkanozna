# Generated by Django 4.0.4 on 2022-05-23 12:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Football', '0007_message_invite'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='sender',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='sender', to='Football.player'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='message',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to='Football.player'),
        ),
    ]
