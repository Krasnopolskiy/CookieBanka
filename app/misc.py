from string import ascii_letters, digits


def sanitize(s: str) -> str:
    alpha = ascii_letters + digits + '_-'
    res = ''.join([ch if ch in alpha else '' for ch in s])
    return res


def load_template_string(template: str) -> str:
    template = sanitize(template)
    with open(f'app/templates/{template}.html', 'r') as f:
        return f.read()
