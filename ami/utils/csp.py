def create_settings_from_env(config):
    params = {}
    for line in config.get("CSP_SETTINGS", "").splitlines():
        if not line or line.startswith("#"):
            continue
        key, value = line.split(":", 1)
        if key.strip() == "report-uri":
            params[key.strip()] = value.strip()
        else:
            params[key.strip()] = [x.strip() for x in value.split(",")]
    return params
