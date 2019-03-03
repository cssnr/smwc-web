from django import forms


class PatcherForm(forms.Form):
    source_rom = forms.FileField()
    input_file = forms.FileField(required=False)
    input_patch = forms.CharField(max_length=255, required=False)

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('input_file') and not cleaned_data.get('input_patch'):
            raise forms.ValidationError('You must provide a patch file or specify a remote patch URL.')
