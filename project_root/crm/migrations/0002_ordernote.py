# Generated by Django 5.1.7 on 2025-03-23 10:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
        ('orders', '0002_order_accounting_key_order_accounting_reference_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderNote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_customer_visible', models.BooleanField(default=False)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crm_notes', to='orders.order')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notes', to='crm.crmuser')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
