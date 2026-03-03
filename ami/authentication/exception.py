class FCError(Exception):
    def __init__(self, code: str | None, *args, **kwargs):
        self.code = code
        super().__init__(*args, **kwargs)
