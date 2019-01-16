from django import forms


class PatcherForm(forms.Form):
    source_rom = forms.FileField()
    input_patch = forms.CharField(max_length=255)
