# Generated by Django 3.1.7 on 2021-03-22 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_auto_20210319_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='notificationType',
            field=models.CharField(default='MESSAGE', max_length=20),
        ),
        migrations.AddField(
            model_name='notification',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='api.team'),
        ),
    ]