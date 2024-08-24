from django import template

register=template.Library()

@register.filter
def calculate_cart_total(orders):
    total = 0
    for order in orders:
        total += order.product.price*order.quantity
    return total

@register.filter
def multiply(value,arg):
    try:
        return float(value) * float(arg)
    except(ValueError, TypeError):
        return''