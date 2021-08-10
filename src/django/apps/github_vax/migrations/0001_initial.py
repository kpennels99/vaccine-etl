# Generated by Django 3.1.1 on 2021-08-10 06:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GithubVaxData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.TextField(blank=True, max_length=500, null=True)),
                ('iso_code', models.TextField(blank=True, max_length=10, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('total_vaccinations', models.FloatField(blank=True, null=True)),
                ('people_vaccinated', models.FloatField(blank=True, null=True)),
                ('people_fully_vaccinated', models.FloatField(blank=True, null=True)),
                ('daily_vaccinations_raw', models.FloatField(blank=True, null=True)),
                ('daily_vaccinations', models.FloatField(blank=True, null=True)),
                ('total_vaccinations_per_hundred', models.FloatField(blank=True, null=True)),
                ('people_vaccinated_per_hundred', models.FloatField(blank=True, null=True)),
                ('people_fully_vaccinated_per_hundred', models.FloatField(blank=True, null=True)),
                ('daily_vaccinations_per_million', models.FloatField(blank=True, null=True)),
            ],
            options={
                'db_table': 'github_vax_data',
            },
        ),
    ]
