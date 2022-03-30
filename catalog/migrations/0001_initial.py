# Generated by Django 3.2.8 on 2021-11-23 06:39

import catalog.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Categories',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('slug', models.SlugField(blank=True, editable=False)),
            ],
            options={
                'verbose_name': 'Categories',
                'verbose_name_plural': 'Categories',
            },
            bases=(models.Model, catalog.models.CapitilizingNames),
        ),
        migrations.CreateModel(
            name='Characteristics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('slug', models.SlugField(blank=True, editable=False)),
            ],
            options={
                'verbose_name': 'Characteristics',
                'verbose_name_plural': 'Characteristics',
            },
            bases=(models.Model, catalog.models.CapitilizingNames),
        ),
        migrations.CreateModel(
            name='Cars',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, unique=True)),
                ('slug', models.SlugField(blank=True, editable=False, max_length=128)),
                ('price', models.PositiveIntegerField(default=0, help_text='USD')),
                ('image', models.ImageField(blank=True, null=True, upload_to='catalog/')),
                ('description', models.TextField(blank=True, max_length=1024)),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('computed_rating', models.PositiveSmallIntegerField(choices=[(1, 'Bad'), (2, 'Normal'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')], default=0)),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='catalog.categories')),
                ('characteristics', models.ManyToManyField(related_name='cars', to='catalog.Characteristics')),
            ],
            options={
                'verbose_name': 'Cars',
                'verbose_name_plural': 'Cars',
            },
        ),
    ]
