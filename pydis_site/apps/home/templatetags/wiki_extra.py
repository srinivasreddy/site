from typing import Union

from django import template
from django.forms import (
    BooleanField, BoundField, CharField, ChoiceField, ComboField, DateField, DateTimeField, DecimalField, DurationField,
    EmailField, Field, FileField, FilePathField, FloatField, GenericIPAddressField, ImageField, IntegerField,
    ModelChoiceField, ModelMultipleChoiceField, MultiValueField, MultipleChoiceField, NullBooleanField, RegexField,
    SlugField, SplitDateTimeField, TimeField, TypedChoiceField, TypedMultipleChoiceField, URLField, UUIDField)
from django.template import Template
from django.template.loader import get_template
from django.utils.safestring import mark_safe
from wiki.editors.markitup import MarkItUpWidget
from wiki.forms import WikiSlugField
from wiki.models import URLPath
from wiki.plugins.notifications.forms import SettingsModelChoiceField

TEMPLATE_PATH = "wiki/forms/fields/{0}.html"

TEMPLATES = {
    BooleanField: TEMPLATE_PATH.format("boolean"),
    CharField: TEMPLATE_PATH.format("char"),
    ChoiceField: TEMPLATE_PATH.format("choice"),
    TypedChoiceField: TEMPLATE_PATH.format("typed_choice"),
    DateField: TEMPLATE_PATH.format("date"),
    DateTimeField: TEMPLATE_PATH.format("date_time"),
    DecimalField: TEMPLATE_PATH.format("decimal"),
    DurationField: TEMPLATE_PATH.format("duration"),
    EmailField: TEMPLATE_PATH.format("email"),
    FileField: TEMPLATE_PATH.format("file"),
    FilePathField: TEMPLATE_PATH.format("file_path"),
    FloatField: TEMPLATE_PATH.format("float"),
    ImageField: TEMPLATE_PATH.format("image"),
    IntegerField: TEMPLATE_PATH.format("integer"),
    GenericIPAddressField: TEMPLATE_PATH.format("generic_ip_address"),
    MultipleChoiceField: TEMPLATE_PATH.format("multiple_choice"),
    TypedMultipleChoiceField: TEMPLATE_PATH.format("typed_multiple_choice"),
    NullBooleanField: TEMPLATE_PATH.format("null_boolean"),
    RegexField: TEMPLATE_PATH.format("regex"),
    SlugField: TEMPLATE_PATH.format("slug"),
    TimeField: TEMPLATE_PATH.format("time"),
    URLField: TEMPLATE_PATH.format("url"),
    UUIDField: TEMPLATE_PATH.format("uuid"),

    ComboField: TEMPLATE_PATH.format("combo"),
    MultiValueField: TEMPLATE_PATH.format("multi_value"),
    SplitDateTimeField: TEMPLATE_PATH.format("split_date_time"),

    ModelChoiceField: TEMPLATE_PATH.format("model_choice"),
    ModelMultipleChoiceField: TEMPLATE_PATH.format("model_multiple_choice"),

    SettingsModelChoiceField: TEMPLATE_PATH.format("model_choice"),
    WikiSlugField: TEMPLATE_PATH.format("wiki_slug_render"),
}


register = template.Library()


def get_unbound_field(field: BoundField):
    while isinstance(field, BoundField):
        field = field.field

    return field


@register.simple_tag
def render_field(field: Field, render_labels: bool = True):
    if isinstance(field, BoundField):
        unbound_field = get_unbound_field(field)
    else:
        unbound_field = field

    if not isinstance(render_labels, bool):
        render_labels = True

    template_path = TEMPLATES.get(unbound_field.__class__)
    is_markitup = isinstance(unbound_field.widget, MarkItUpWidget)

    if not template_path:
        raise NotImplementedError(f"Unknown field type: {unbound_field.__class__}")

    template_obj: Template = get_template(template_path)
    context = {"field": field, "is_markitup": is_markitup, "render_labels": render_labels}

    return mark_safe(template_obj.render(context))


@register.simple_tag(takes_context=True)
def get_field_options(context, field: BoundField):
    widget = field.field.widget

    if field.value() is None:
        value = []
    else:
        value = [str(field.value())]

    context["options"] = widget.optgroups(field.name, value)
    return ""


@register.filter
def render_urlpath(value: Union[URLPath, str]):
    if isinstance(value, str):
        return value or "/"

    return value.path or "/"
