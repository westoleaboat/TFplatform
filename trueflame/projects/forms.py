# Formsets are an abstraction layer to work with multiple forms on same page
# Formsets manage multiple instances of a certain Form or ModelForm.

# Inline formsets are a small abstraction on top of formsets
# that simplify working with related objects.
# The ModuleFormSet function allows you to build a model
# formset dynamically for the Content objects related to a Structure object.


from django import forms
from django.forms.models import inlineformset_factory
from .models import Structure, Content

ModuleFormSet = inlineformset_factory(
    Structure, Content, fields=["title", "description"], extra=2, can_delete=True
)
