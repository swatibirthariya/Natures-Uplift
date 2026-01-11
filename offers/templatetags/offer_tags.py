from django import template
from offers.offer_engine import get_active_offer as engine_get_offer

register = template.Library()

@register.simple_tag
def active_offer():
    return engine_get_offer()
