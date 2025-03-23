# In the new migration file in orders/migrations/
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
        ('orders', '0002_order_accounting_key_order_accounting_reference_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='inventory_updated',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='order',
            name='tracking_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
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
    ]