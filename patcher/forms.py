from django import forms


class PatcherForm(forms.Form):
    patch_url = forms.CharField(max_length=255, required=False)
    patch_file = forms.FileField(required=False)
    source_url = forms.CharField(max_length=255, required=False)
    source_file = forms.FileField(required=False)

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get('patch_url') and not cleaned_data.get('patch_file'):
            raise forms.ValidationError('You must provide a patch file or specify a remote patch URL.')

        if not cleaned_data.get('source_url') and not cleaned_data.get('source_file'):
            raise forms.ValidationError('You must provide a local source file or remote source URL.')
