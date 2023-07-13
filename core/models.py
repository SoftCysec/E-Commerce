from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.db.models.signals import post_save
from django.db.models import Sum



# Create your models here.
CATEGORY_CHOICES =(
    ('D','Dress'),
    ('S','Shirts'),
    ('J','Jeans'),
    ('SW','Swimwear'),
    ('SLW','Sleepwear'),
    ('SPW','Sportwear'),
    ('B','Blazers'),
    ('JA','Jackets'),
    ('SH','Shoes'),
)
LABEL_CHOICES =(
    ('P','primary'),
    ('S','secondary'),
    ('D','danger'),
)

ADDRESS_CHOICES=(
    ('B','Billing'),
    ('S','Shipping'),
    
)
# storing user card info in userprofile
# one to one field (every user has his own profile page)
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete = models.CASCADE
    )
    stripe_customer_id =  models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

# the items will be displayed in a list of items that can be purchased 
# as soon as the item is added to the cart it becomes an order item
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null=True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=4, blank=True, null=True)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1, blank=True, null=True)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
   
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("core:productdetails", kwargs={"slug": self.slug})
    
    def get_add_to_cart_url(self):
        return reverse("core:add_to_cart", kwargs={"slug": self.slug})
    
    def get_remove_from_cart_url(self):
        return reverse("core:remove_from_cart", kwargs={"slug": self.slug})
    
    def get_delete_from_cart_url(self):
        return reverse("core:delete_from_cart", kwargs={"slug": self.slug})
    
    
    
    
    
    
    
# OrderItem is alinking between the Order and the Item
class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True )
    ordered = models.BooleanField(default=False)
    
    # linking order item with item model
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    
    def get_total_item_price(self):
        return self.quantity * self.item.price
    
    def get_total_discount_item_price(self):
         return self.quantity * self.item.discount_price
     
    def get_amount_saved(self):
         return self.get_total_item_price() - self.get_total_discount_item_price()
     
    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
    
   

# link all of of orderitems to the order (shopping cart)
# we store all the itmes that the user has added to the cart inside the order
# and every time they login we fetch the order they have and display the order on the shopping cart
# we will define a boolean field to show the items have been order or not 
# if it is ordered then the next order will be created 
class Order(models.Model):
    # associating the order with user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    # we add the items into the order
    items = models.ManyToManyField(OrderItem)
    # a start date to know when the order was created
    star_date = models.DateTimeField(auto_now_add=True)
    # mannually set the date date when the item was ordered
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    
    # when order is complete we attach the billing address to know where to send the order
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey('Address',related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
    
    # assign the coupon to the order
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    
    being_delivered = models.BooleanField(default=False)
    received= models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    """
    1.Item added to cart
    2.Adding a billing address
    (failed checkout)
    3. Payment
    (preprocessing, processing, packaging, etc)
    4.Beign delivered
    5.Received
    6.Refunds
    """
    
    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total = 0 
        if self.items.exists():
            for order_item in self.items.all():
                total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
            
        return total
    
    def get_total_items(self):
        total_items = 0
        for order_item in self.items.all():
            total_items += order_item.quantity
            
        if self.coupon:
                total -= self.coupon.amount
        return total_items
    
class Address(models.Model):
    # assign a user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    # any time we say use this as my default billing or shiping address
    # default field will be set to true 
    default = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = 'Addresses'
 
class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username
    
    
class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code

class Refund(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    # default = false meaning it has not been accepted yet
    
    def __str__(self):
        return f"{self.pk}"
  
#  post save signal to create user profile once the user is created 
def userprofile_receiver(sender, instance, created, *args, **kwargs):
    # if user is created call the userprofile.objects.create and pass in 
    # the user as the only required agruement  
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)
