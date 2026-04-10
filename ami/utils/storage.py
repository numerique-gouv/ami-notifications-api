from whitenoise.storage import CompressedManifestStaticFilesStorage


class AMIStorage(CompressedManifestStaticFilesStorage):
    def hashed_name(self, name, content=None, filename=None):
        # Ne pas re-hasher les fichiers déjà hashés par Svelte
        if "_app/immutable/" in name:
            return name
        return super().hashed_name(name, content, filename)
