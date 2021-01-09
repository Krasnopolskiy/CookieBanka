def load_template_string(template: str) -> str:
    with open(f'app/templates/{template}.html', 'r') as f:
        return f.read()
