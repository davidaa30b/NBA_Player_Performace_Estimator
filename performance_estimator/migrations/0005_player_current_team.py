# Generated by Django 5.1.4 on 2025-02-05 14:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('performance_estimator', '0004_player_image_team_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='current_team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='current_players', to='performance_estimator.team'),
        ),
    ]
