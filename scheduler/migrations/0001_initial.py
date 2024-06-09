# Generated by Django 5.0.6 on 2024-06-08 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('arrival_time', models.IntegerField()),
                ('burst_time', models.IntegerField()),
                ('priority', models.IntegerField(default=0)),
            ],
        ),
    ]