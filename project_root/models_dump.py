# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AccountsAddress(models.Model):
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    address_type = models.CharField(max_length=10)
    is_default = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'accounts_address'


class AccountsProfile(models.Model):
    phone_number = models.CharField(max_length=15)
    user = models.OneToOneField('AuthUser', models.DO_NOTHING)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'accounts_profile'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)
    name = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    first_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CartCart(models.Model):
    session_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'cart_cart'


class CartCartitem(models.Model):
    quantity = models.PositiveIntegerField()
    cart = models.ForeignKey(CartCart, models.DO_NOTHING)
    product_variant = models.ForeignKey('ProductsProductvariant', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'cart_cartitem'
        unique_together = (('cart', 'product_variant'),)


class DjangoAdminLog(models.Model):
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    action_time = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class OrdersOrder(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.CharField(max_length=254)
    phone = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    payment_method = models.CharField(max_length=20)
    payment_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    accounting_key = models.CharField(max_length=100, blank=True, null=True)
    accounting_reference = models.CharField(max_length=100, blank=True, null=True)
    courier_consignment_id = models.CharField(max_length=20, blank=True, null=True)
    courier_status = models.CharField(max_length=30, blank=True, null=True)
    courier_tracking_code = models.CharField(max_length=20, blank=True, null=True)
    is_paid = models.BooleanField()
    order_number = models.CharField(unique=True, max_length=20)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders_order'


class OrdersOrderitem(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    quantity = models.PositiveIntegerField()
    order = models.ForeignKey(OrdersOrder, models.DO_NOTHING)
    product_name = models.CharField(max_length=255)
    product_variant = models.ForeignKey('ProductsProductvariant', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'orders_orderitem'


class ProductsCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(unique=True, max_length=50)
    description = models.TextField()
    image = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'products_category'


class ProductsProduct(models.Model):
    name = models.CharField(max_length=200)
    slug = models.CharField(unique=True, max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=5)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    discount_price = models.DecimalField(max_digits=10, decimal_places=5, blank=True, null=True)  # max_digits and decimal_places have been guessed, as this database handles decimal fields as float
    is_featured = models.BooleanField()
    in_stock = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    category = models.ForeignKey(ProductsCategory, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'products_product'


class ProductsProductimage(models.Model):
    image = models.CharField(max_length=100)
    is_primary = models.BooleanField()
    product = models.ForeignKey(ProductsProduct, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'products_productimage'


class ProductsProductvariant(models.Model):
    size = models.CharField(max_length=5)
    color = models.CharField(max_length=50)
    stock_quantity = models.IntegerField()
    sku = models.CharField(unique=True, max_length=100)
    product = models.ForeignKey(ProductsProduct, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'products_productvariant'
