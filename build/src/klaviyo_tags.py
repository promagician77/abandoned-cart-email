"""Stand-ins for the Klaviyo-only pieces, so previews render with the real Django engine.
Klaviyo itself provides these in production."""
from django import template
from django.utils.safestring import mark_safe
register = template.Library()

@register.filter
def lookup(d, key):                       # Klaviyo: {{ event|lookup:'$value' }}
    return d.get(key) if isinstance(d, dict) else None

LINK = '<a href="{}" style="color:#8A8F85;text-decoration:underline">{}</a>'
@register.simple_tag
def unsubscribe(text="Unsubscribe"):
    return mark_safe(LINK.format("https://fernhill.example/unsubscribe", text))
@register.simple_tag
def manage_preferences(text="Manage preferences"):
    return mark_safe(LINK.format("https://fernhill.example/preferences", text))
