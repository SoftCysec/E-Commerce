from django.shortcuts import render, redirect, get_object_or_404
from .models import Item, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, userprofile_receiver
from django.views.generic import DetailView, ListView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, CouponForm, RefundForm, PaymentForm
import stripe
from django.conf import settings
import random 
import string
from django.contrib.auth.models import User
# Create your views here.


stripe.api_key = settings.STRIPE_SECRET_KEY

def create_ref_code():
     return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

def product(request):
     context ={
          'items':Item.objects.all()
     }
     return render(request, "pages/product.html", context)

class HomeView(ListView):
     model = Item
     paginate_by = 9
     template_name = "pages/home.html"
    
     def get_queryset(self):
        return Item.objects.order_by('-created_at')

 

class ProductDetailView(DetailView):
    model = Item 
    template_name = "pages/productdetails.html"     
    
class ShopView(ListView):
     model = Item
     paginate_by = 10
     template_name = "pages/shop.html" 
    
     def get_queryset(self):
        return Item.objects.order_by('-created_at')

     

class CartView(LoginRequiredMixin, View):
     # order summary
    def get(self, request, *args, **kwargs):
          try:
               order = Order.objects.get(user=self.request.user, ordered=False )
               context = {
                    'object':order,
                    
               }
               return render(self.request, 'pages/cart.html', context)
          except ObjectDoesNotExist:
               messages.warning(self.request, "You do not have an acive order")
               return redirect("/")
         
# validates a checkout form if a new one is created
def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


class CheckoutView(View):
       
     def get(self, request, *args, **kwargs):
          try:
               #  displaying the product summary list in checkout view
               order = Order.objects.get(user=request.user, ordered=False)
               form = CheckoutForm()
               context ={
                    'form':form,
                    'couponform':CouponForm(),
                    'order':order,
                    'DISPLAY_COUPON_FORM':True
                    }
               
               # if we have default shipping address
               shipping_address_qs = Address.objects.filter(
                                             user= self.request.user,
                                             address_type = 'S',
                                             default = True,
                                             
                                        )
               if shipping_address_qs.exists():
                    context.update({'default_shipping_address': shipping_address_qs[0]})
               
               billing_address_qs = Address.objects.filter(
                                             user= self.request.user,
                                             address_type = 'B',
                                             default = True,
                                             
                                        )
               if billing_address_qs.exists():
                    context.update({'default_billing_address': billing_address_qs[0]})
                  
               return render(self.request,'pages/checkout.html', context)
          except ObjectDoesNotExist:
               messages.info(request, "Ypu dont have an active order")
               return redirect("core:checkout")
          
     
     def post(self, request, *args, **kwargs):
          form = CheckoutForm(self.request.POST or None)
          # check if the the order exists inorder to add the billing address
          # try to get the order based on the user
          try:
               order = Order.objects.get(user=self.request.user, ordered=False )
               print(self.request.POST)
               if form.is_valid():
                    print(form.changed_data)
                    print("Form is valid ")
                    #  NOTE: shipping 
                    use_default_shipping = form.cleaned_data.get('use_default_shipping')
                    if use_default_shipping:
                         print('Using the default shipping address')
                         address_qs = Address.objects.filter(
                                             user= self.request.user,
                                             address_type = 'S',
                                             default = True,
                                             
                                        )
                         # check if the user has a default shipping address
                         if address_qs.exists():
                              shipping_address = address_qs[0]
                              order.shipping_address = shipping_address
                              order.save()
                         else:
                              messages.info(self.request,"No default shipping address available")
                              return redirect("core:checkout")
                    else:
                         print("User is entering a new shipping address")
                    
                         first_name = form.cleaned_data.get('first_name')
                         last_name = form.cleaned_data.get('last_name')
                         email  = form.cleaned_data.get('email ')
                         mobile_number = form.cleaned_data.get('mobile_number')
                         shipping_street_address = form.cleaned_data.get('shipping_street_address')
                         shipping_apartment_address = form.cleaned_data.get('shipping_apartment_address')
                         shipping_country = form.cleaned_data.get('shipping_country')
                         shipping_city = form.cleaned_data.get('shipping_city')
                         shipping_state  = form.cleaned_data.get('shipping_state')
                         shipping_zip_code = form.cleaned_data.get('shipping_zip_code')
                         
                         if is_valid_form([shipping_street_address, 
                                           shipping_country,
                                            shipping_zip_code 
                                           ]):
                              #
                                   shipping_address= Address(
                                        user = self.request.user,
                                        street_address = shipping_street_address,
                                        apartment_address =shipping_apartment_address,
                                        country = shipping_country,
                                        city = shipping_city,
                                        state = shipping_state,
                                        zip_code = shipping_zip_code,
                                        address_type = 'S',
                                   )
                                   shipping_address.save()
                                   
                                   order.shipping_address = shipping_address
                                   order.save()
                                        
                                   # check if we are setting the current shipping address above to be the new default
                                   
                                   set_default_shipping = form.cleaned_data.get('et_default_shipping')
                                   if set_default_shipping:
                                        shipping_address.default  = True
                                        shipping_address.save()
                    
                         else:
                              messages.info(self.request,"Please fill in the required shipping address fields")
                              
                              
                              # NOTE: billing 
                              
                    use_default_billing = form.cleaned_data.get('use_default_billing')
                    
                    # NOTE: same   address field 
                    
                    same_billing_address = form.cleaned_data.get(' same_billing_address')
                    
                    if  same_billing_address:
                         billing_address = shipping_address
                         billing_address.pk = None
                         billing_address.save()
                         billing_address.address_type = 'B'
                         billing_address.save()
                         order.billing_address = billing_address
                         order.save()
                    
                    # NOTE: use default billing field 
                    elif use_default_billing:
                         print("Using the defualt billing address")
                         address_qs = Address.objects.filter(
                         user=self.request.user,
                         address_type='B',
                         default=True
                         )
                         # check if the user has a default shipping address
                         if address_qs.exists():
                              billing_address = address_qs[0]
                              order.billing_address = billing_address
                              order.save()
                         else:
                              messages.info(
                                   self.request, "No default billing address available")
                              return redirect('core:checkout')
                    else:
                         print("User is entering a new shipping address")
                    
                         first_name = form.cleaned_data.get('first_name')
                         last_name = form.cleaned_data.get('last_name')
                         email  = form.cleaned_data.get('email ')
                         mobile_number = form.cleaned_data.get('mobile_number')
                         billing_street_address = form.cleaned_data.get('billing_street_address')
                         billing_apartment_address = form.cleaned_data.get('billing_apartment_address')
                         billing_country = form.cleaned_data.get('billing_country')
                         billing_city = form.cleaned_data.get('billing_city')
                         billing_state  = form.cleaned_data.get('billing_state')
                         billing_zip_code = form.cleaned_data.get('billing_zip_code')
                         
                         # TODO: add functionality for these fields 
                         # same_shipping_address = form.cleaned_data.get('same_billing_address')
                         # save_info = form.cleaned_data.get('save_info')
                         # create_account  = form.cleaned_data.get('create_account')
                         # ship_to_different_address = form.cleaned_data.get('ship_to_different_address')
                        
                         if is_valid_form([billing_street_address, billing_country, billing_zip_code]):
                              billing_address = Address(
                                  user = self.request.user,
                                        street_address = billing_street_address,
                                        apartment_address = billing_apartment_address,
                                        country = billing_country,
                                        city = billing_city,
                                        state = billing_state,
                                        zip_code = billing_zip_code,
                                        address_type = 'B',
                    
                              )
                              billing_address.save()

                              order.billing_address = billing_address
                              order.save()

                              set_default_billing = form.cleaned_data.get(
                                   'set_default_billing')
                              
                              if set_default_billing:
                                   billing_address.default = True
                                   billing_address.save()

                         else:
                              messages.warning(
                                   self.request, "Please fill in the required billing address fields")


                    payment_option = form.cleaned_data.get('payment_option')
  
                    if payment_option == 'S':
                         return redirect('core:payment', payment_option = 'stripe')
                    elif payment_option == 'P':
                         return redirect('core:payment',payment_option='paypal')
                    else:
                         messages.warning(self.request, "Inavalid payment option selected")
                         return redirect('core:checkout')
                         
          except ObjectDoesNotExist:
               messages.warning(self.request, "You do not have an acive order")
               return redirect("core:CartView")
         
     #     TODO: fix stripe  raise AttributeError(*err.args)AttributeError: sources
class PaymentView(View):
      def get(self, request, *args, **kwargs):
          #  order
          order = Order.objects.get(user=self.request.user, ordered=False)
          if order.billing_address:
               context ={
                    'order':order,
                    'DISPLAY_COUPON_FORM':False,
                    'STRIPE_PUBLISHABLE_KEY ' : settings.STRIPE_PUBLISHABLE_KEY 
               }

               #  grab the userprofile and check if one_click_purchasing is activated
               userprofile = self.request.user.userprofile
               if userprofile.one_click_purchasing:
                    # fetch the users card list
                    cards = stripe.Customer.list_sources(
                         userprofile.stripe_customer_id,
                         # number of results you want to get back
                         limit=3,
                         object='card'
                    )
                    card_list = cards['data']
                    if len(card_list) > 0:
                         # update the context with the default card
                         context.update({
                         'card': card_list[0]
                         })
               return render(self.request, "pages/payment.html", context)
          else:
               messages.warning(self.request, "You have not added a billing address")
               return redirect("core:checkout")
         
      
      def post(self, request, *args, **kwargs):
               order = Order.objects.get(user=self.request.user, ordered=False)
                        # TODO
               form = PaymentForm(self.request.POST)
               userprofile = UserProfile.objects.get(user=self.request.user)
               
               if form.is_valid():
                    token = form.cleaned_data.get('stripeToken')
                    save = form.cleaned_data.get('save')
                    use_default = form.cleaned_data.get('use_default')

                    if save:
                         # allow to fetch cards
                         # check if there is a stripe customer id associated to the userprofile 
                         # if there is no one 
                         if not userprofile.stripe_customer_id:
                              # there are saving the stripe customer id  for the first 
                              # so we create the stripe customer

                              customer = stripe.Customer.create(
                                             email = self.request.user.email,
                                             source=token
                                             )
                              userprofile.stripe_customer_id = customer['id']
                              userprofile.one_click_purchasing = True
                              userprofile.save()

                         else:
                              # TODO: source  raise AttributeError(*err.args)AttributeError: sources
                              stripe.Customer.create_source(
                                   userprofile.stripe_customer_id,
                                   source=token
                              )
                              
               # token = self.request.POST.get('pk_test_51N1SOOE6ACnWqjEtxux8DSU1KIcrkVcMylEw4vTiS4n7O6llZeUIcYtNF7VyqhsmUMXhr7GYP73yFHIejomQOIeC00dGiBxNaV')
                    amount = int(order.get_total()*100) # *100 bcs the value is in cents
                    try:
                         if use_default or save:
                         # charge the customer because we cannot charge the token more than once
                              charge = stripe.Charge.create(
                                   amount=amount,  # cents
                                   currency="usd",
                                   customer=userprofile.stripe_customer_id
                                   )
                         else:
                              # charge once off on the token
                              charge = stripe.Charge.create(
                                   amount=amount,  # cents
                                   currency="usd",
                                   source=token
                                   )
                         
                         # create the payment
                         payment = Payment()
                         payment.stripe_charge_id = charge['id']
                         payment.user = self.request.user
                         payment.amount = order.get_total()
                         payment.save()
                         
                    
                         # creating a new order when one is complete
                         # assign the payment to the order
                         order_items = order.items.all()
                         order_items.update(ordered=True)
                         for item in order_items:
                              item.save()
                         # assign the payment to the order
                         
                         order.ordered = True
                         order.payment = payment
                         order.ref_code = create_ref_code()
                         order.save()
                         
                         messages.success(self.request, "Your order was successfull! ")
                         return redirect("/")

                    except stripe.error.CardError as e:
                         body = e.json_body
                         err = body.get('error', {})
                         messages.warning(self.request, f"{err.get('messages')}")
                         return redirect("/")
                         
                    except stripe.error.RateLimitError as e:
                         # Too many requests made to the API  too quickly
                         messages.warning(self.request, 'Rate limit error')
                         return redirect("/")
               
                    except stripe.error.InvalidRequestError as e:
                         # Invalid parameters were supplied to Stripe's API
                         messages.warning(self.request,'Invalid parameters')
                         return redirect("/")
                         
                    except stripe.error.AuthenticationError as e:
                         # Authentication with Stripe's API failed 
                         # (maybe you changed APIkeys recently)
                         messages.warning(self.request, 'Not authenticated')
                         return redirect("/")
                         
                    except stripe.error.APIConnectionError as e:
                         # Network communtion with Stripe failed
                         messages.warning(self.request, 'Something went wrong or the connection is poor. You were not charged. Please try again')
                         return redirect("/")
                         
                    except stripe.error.StripeError as e:
                         # Display a very generic eeror to the user, and maybe send
                         # yourself an email
                         messages.warning(self.request, f"{err.get('messages')}")
                         
                    except Exception as e:
                    # Something else happened, completely unrelated to Stripe
                    # send an email to ourselves 
                       messages.warning(self.request, "A serious error occurred. We have been notified. ")     
                       return redirect("/")
             
               messages.warning(self.request, "Invalid data received")
               return redirect('/payment/stripe/')
               
             
             
     
def contact(request):
     return render(request, "pages/contact.html")
     
#  slug of the item
@login_required
def add_to_cart(request, slug):
     item = get_object_or_404(Item, slug=slug)
     # see if user has an order
     # use get_or_create() function instead of create ot avoid creating a new item every time 
     # the cart button is clicked 
     order_item, created = OrderItem.objects.get_or_create(
          item=item, 
          user=request.user, 
          ordered=False
          )
     # check if order is completed 
     order_qs = Order.objects.filter(user=request.user, ordered=False)
     if order_qs.exists():
          # grab the order from the order_qs 
          order = order_qs[0]
          # check if the order item is in the order 
          # meaning if the item is in the cart
          if order.items.filter(item__slug=item.slug).exists():
               order_item.quantity += 1
               order_item.save()
               messages.success(request,"This item quantity was updated")
               return redirect("core:productdetails", slug=slug)
          else:
               order.items.add(order_item)
               messages.success(request,"This item was added to your cart")
               return redirect("core:productdetails", slug=slug)
     
     else:
          ordered_date = timezone.now()
          order = Order.objects.create(user=request.user, ordered_date = ordered_date)
          order.items.add(order_item)
          messages.success(request,"This item was added to your cart")
          return redirect("core:productdetails", slug=slug)
               
@login_required
def remove_from_cart(request, slug):
     item = get_object_or_404(Item, slug=slug)
          
     order_qs = Order.objects.filter(user=request.user, ordered=False)
     if order_qs.exists():
          # grab the order from the order_qs 
          order = order_qs[0]
          # check if the order item is in the order 
          # meaning if the item is in the cart
          if order.items.filter(item__slug=item.slug).exists():
               order_item = OrderItem.objects.filter(
                    item=item, 
                    user=request.user, 
                    ordered=False
               )[0]
               if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                    messages.warning(request,"This item was removed to your cart")
                    return redirect("core:productdetails", slug=slug)
               else:
                    order.items.remove(order_item)
                    messages.warning(request, "Item quantity was updated.")
                    return redirect("core:productdetails", slug=slug)

          else:
               # add a message saying the order does not contain the order item
               messages.warning(request,"This item is not in your cart")
               return redirect("core:productdetails", slug=slug) 
     
     else:
          # add a message saying the user doesn't have an order
          messages.info(request,"You dont have an order")
          return redirect("core:productdetails", slug=slug)

# deleting item function
def delete_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order_item.delete()
            messages.warning(request, "Item was removed from your cart.")
            return redirect("core:cartview")
        else:
            messages.warning(request, "This item was not in your cart.")
            return redirect("core:cartview")
    else:
        messages.warning(request, "You do not have an active order.")
        return redirect("core:cartview")


def get_coupon(request, code):
     try:
          coupon = Coupon.objects.get(cope=code)
          return coupon
          
     except ObjectDoesNotExist:
          messages.info(request, "This coupon does not exist")
          return redirect("core:checkout")

class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout")
               
class RequestRefundView(View):
     
     def get(self, request, *args, **kwargs):
          form = RefundForm()
          context = {
               'form':form, 
          }
          return render(self.request,"pages/request_refund.html", context)
     
     def post(self, request, *args, **kwargs):
          form = RefundForm(self.request.POST)
          if form.is_valid():
               ref_code = form.cleaned_data.get('ref_code')
               email = form.cleaned_data.get('email')
               message = form.cleaned_data.get('message')
               # edit the order
               try:
                    order = Order.objects.get(ref_code=ref_code)
                    order.refund_requested = True
                    order.save()
               # customized refund model to store 
                    refund = Refund()
                    refund.order = order
                    refund.reason = message
                    refund.email = email
                    refund.save()
                    messages.info(self.request,"Your request was received")

                    return redirect("core:request-refund")
               except ObjectDoesNotExist:
                    messages.info(self.request,"This order does not exist")
                    return redirect("core:request-refund")