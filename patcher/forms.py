from django import forms


class PatcherForm(forms.Form):
    patch_file = forms.FileField(required=False)
    patch_url = forms.CharField(max_length=255, required=False)
    source_url = forms.CharField(max_length=255, required=False)
    source_file = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('patch_file') and not cleaned_data.get('patch_url'):
            raise forms.ValidationError('You must provide a patch file or specify a remote patch URL.')

        if not cleaned_data.get('source_url') and not cleaned_data.get('source_file'):
            raise forms.ValidationError('You must provide a local or remote source ROM.')
