# Create a new migration file: orders/migrations/0006_tracking_fields.py

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_order_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='tracking_code',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='consignment_id',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]