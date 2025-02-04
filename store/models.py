from django.db import models
from django.contrib.auth.models import User
from django.conf.urls.static import static


# Create your models here.
class Web(models.Model):
    name = models.CharField(max_length=255)
    tagline = models.CharField(max_length=255, null=True, default='Sample Tagline')
    about_us = models.TextField()
    email = models.CharField(max_length=255)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    pin_code = models.CharField(max_length=255, null=True)
    mobile = models.CharField(max_length=16, null=True, blank=True)
    instagram_link = models.CharField(max_length=255, null=True, blank=True)
    youtube_link = models.CharField(max_length=255, null=True, blank=True)
    facebook_link = models.CharField(max_length=255, null=True, blank=True)
    twitter_link = models.CharField(max_length=255, null=True, blank=True)
    terms_and_conditions = models.TextField(null=True, blank=True)
    privacy_policy = models.TextField(null=True, blank=True)
    refund_and_cancellation_policy = models.TextField(null=True, blank=True)
    shipping_policy = models.TextField(null=True, blank=True)

    def __str__(self):
        return "Web - " + str(self.name)


class Address(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)
    pin_code = models.CharField(max_length=255, null=True)
    mobile = models.CharField(max_length=16, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Address - " + self.customer.first_name + " - " + str(self.id)


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.FloatField()
    stock = models.IntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def in_stock(self):
        if self.stock:
            return True
        else:
            return False

    def get_images(self):
        return self.productimage_set.all()

    def get_an_image(self):
        return self.productimage_set.first()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.product.name + " - image - " + str(self.id)

    def image_url(self):
        if self.image.url is not None:
            return self.image.url
        else:
            return static('store/img/unnamed.jpg')


ORDER_STATUS = (
    ('DRAFT', 'DRAFT'),
    ('PENDING', 'PENDING'),
    ('ACCEPTED', 'ACCEPTED'),
    ('SHIPPED', 'SHIPPED'),
    ('DELIVERED', 'DELIVERED'),
    ('COMPLETED', 'COMPLETED'),
    ('CANCELLED', 'CANCELLED')
)


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=64, choices=ORDER_STATUS, default=1)
    order_remarks = models.CharField(max_length=255, blank=True, null=True)
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_id = models.CharField(max_length=191, null=True, blank=True)
    signature = models.CharField(max_length=255, null=True, blank=True)
    pg_order_id = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return "Order - " + str(self.id)

    @property
    def get_cart_total(self):
        items = self.orderitem_set.all()
        return sum(item.get_total for item in items)

    @property
    def get_cart_items_count(self):
        items = self.orderitem_set.all()
        return sum(item.quantity for item in items)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Order - " + str(self.order.id) + " - " + self.product.name

    @property
    def get_total(self):
        return self.product.price * self.quantity


class Message(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    message = models.CharField(max_length=2048)

    def __str__(self):
        return "Message - " + str(self.id)
