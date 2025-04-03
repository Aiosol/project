# Generated by Django 5.1.7 on 2025-04-03 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='site_config/')),
                ('key', models.CharField(blank=True, max_length=50, null=True)),
                ('value', models.TextField(blank=True, null=True)),
                ('category', models.CharField(default='general', max_length=50)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Site Configuration',
                'verbose_name_plural': 'Site Configurations',
            },
        ),
    ]
