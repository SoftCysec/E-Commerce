from django import template
from core.models import Order

# reg template tag
register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        #  show orders in the cart
        #  and dont show the previous orders of the user ordered=False
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            # get the only order in the query set and count the number of items in the order
            return qs[0].items.count()
    return 0