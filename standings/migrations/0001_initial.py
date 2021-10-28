# Generated by Django 3.2.8 on 2021-10-28 17:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Division',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('espn_id', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('espn_id', models.CharField(max_length=200)),
                ('current_week', models.IntegerField()),
                ('nfl_week', models.IntegerField()),
                ('updated_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('espn_id', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('wins', models.IntegerField()),
                ('losses', models.IntegerField()),
                ('victory_points', models.IntegerField()),
                ('points_for', models.FloatField()),
                ('division', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='standings.division')),
            ],
        ),
        migrations.AddField(
            model_name='division',
            name='league',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='standings.league'),
        ),
    ]