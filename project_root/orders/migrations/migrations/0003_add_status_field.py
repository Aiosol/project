# Create a new file: orders/migrations/0003_add_status_field.py

from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_accounting_key_order_accounting_reference_and_more'),
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='crm.orderstatus',
            ),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='inventory_updated',
            field=models.BooleanField(default=False),
        ),
    ]