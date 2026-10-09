from ami.utils.csp import create_settings_from_env


def test_create_settings_from_env_empty():
    assert create_settings_from_env({}) == {}
    assert create_settings_from_env({"CSP_SETTINGS": ""}) == {}


def test_create_settings_from_env():
    csp_settings = """# comment line
default-src: 'self'
img-src: 'self', data:, example.com
report-uri: https://mysite.com/csp-report/
"""
    assert create_settings_from_env({"CSP_SETTINGS": csp_settings}) == {
        "default-src": ["'self'"],
        "img-src": ["'self'", "data:", "example.com"],
        "report-uri": "https://mysite.com/csp-report/",
    }
