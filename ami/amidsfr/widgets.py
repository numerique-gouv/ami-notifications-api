from django.forms import CheckboxInput


class ToggleInput(CheckboxInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing = set(self.attrs.get("class", "").split(" "))
        existing.add("fr-toggle__input")
        self.attrs["class"] = " ".join(existing)
