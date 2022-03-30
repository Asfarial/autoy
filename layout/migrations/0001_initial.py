# Generated by Django 4.0.3 on 2022-03-11 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MenuList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Menu name', max_length=32)),
                ('url', models.CharField(blank=True, default='', max_length=32)),
                ('is_active', models.BooleanField(default=True)),
                ('order_num', models.PositiveSmallIntegerField(unique=True)),
            ],
            options={
                'verbose_name': 'Menu list',
                'verbose_name_plural': 'Menu list',
                'ordering': ['order_num'],
            },
        ),
        migrations.CreateModel(
            name='SocialLinks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('url', models.URLField()),
                ('order_num', models.PositiveSmallIntegerField(unique=True)),
            ],
            options={
                'verbose_name': 'Social Links',
                'verbose_name_plural': 'Social Links',
                'ordering': ['order_num'],
            },
        ),
        migrations.CreateModel(
            name='Footer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Footer', max_length=24)),
                ('address_show', models.BooleanField(default=True)),
                ('address', models.CharField(max_length=512)),
                ('address_google_maps_dir_url', models.URLField(blank=True, default='', help_text='URL for directions from Google Maps, leave empty to disable')),
                ('phone', models.CharField(max_length=24)),
                ('e_mail', models.CharField(max_length=64)),
                ('social_links_show', models.BooleanField(default=True)),
                ('newsletter_show', models.BooleanField(default=True)),
                ('copyright_show', models.BooleanField(default=True)),
                ('copyright_text', models.CharField(max_length=128)),
                ('social_links', models.ManyToManyField(related_name='social_links', to='layout.sociallinks')),
            ],
            options={
                'verbose_name': 'Footer',
                'verbose_name_plural': 'Footer',
            },
        ),
    ]
