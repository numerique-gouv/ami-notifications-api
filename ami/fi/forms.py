from django import forms
from django.conf import settings


class AuthorizeForm(forms.Form):
    state = forms.CharField()
    nonce = forms.CharField()
    response_type = forms.CharField()
    client_id = forms.CharField()
    redirect_uri = forms.CharField()
    scope = forms.CharField()
    acr_values = forms.CharField()
    claims = forms.JSONField(required=False)
    prompt = forms.CharField()

    def clean_response_type(self):
        value = self.cleaned_data["response_type"]
        expected = "code"
        if value != expected:
            raise forms.ValidationError(
                f"'response_type' doit être '{expected}', trouvé '{value}'", "invalid"
            )
        return value

    def clean_client_id(self):
        value = self.cleaned_data["client_id"]
        if value != settings.FI_CLIENT_ID:
            raise forms.ValidationError(
                "'client_id' invalide",
                "invalid",
            )
        return value

    def clean_redirect_uri(self):
        value = self.cleaned_data["redirect_uri"]
        expected = settings.FI_REDIRECT_URI
        if value != expected:
            raise forms.ValidationError(
                f"'redirect_uri' doit être '{expected}', trouvé '{value}'",
                "invalid",
            )
        return value

    def clean_acr_values(self):
        value = self.cleaned_data["acr_values"]
        expected = "eidas1"
        if value != expected:
            raise forms.ValidationError(
                f"'acr_values' doit être '{expected}', trouvé '{value}'", "invalid"
            )
        return value


class AuthorizeUserDataForm(forms.Form):
    fi_session_id = forms.CharField(widget=forms.HiddenInput)
    encoded_user_data = forms.CharField(widget=forms.HiddenInput)
