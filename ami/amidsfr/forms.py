from dsfr.forms import DsfrBaseForm


class AMIDsfrBaseForm(DsfrBaseForm):
    template_name = "amidsfr/form_snippet.html"  # type: ignore
