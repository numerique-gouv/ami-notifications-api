from django.forms import CheckboxInput, TextInput


class AutocompleteInput(TextInput):
    class Media:
        js = ["js/amidsfr-autocomplete.js"]
        css = {"all": ["css/amidsfr-autocomplete.css"]}

    def __init__(self, autocomplete_url=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.group_class = "fr-input-group amidsfr-autocomplete"
        self.attrs["data-autocomplete-url"] = autocomplete_url or ""


class ToggleInput(CheckboxInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing = set(self.attrs.get("class", "").split(" "))
        existing.add("fr-toggle__input")
        self.attrs["class"] = " ".join(existing)
