from django import template
from dsfr.templatetags.dsfr_tags import dsfr_form_field

register = template.Library()


@register.inclusion_tag("amidsfr/form_field_snippets/field_snippet.html", takes_context=True)
def amidsfr_form_field(context, field) -> dict:
    return dsfr_form_field(field)
