from project import create_app

app = create_app()
print('Routes:')
for rule in app.url_map.iter_rules():
    if 'signup' in rule.rule or 'login' in rule.rule or 'auth' in rule.endpoint:
        print(f'  {rule.rule} -> {rule.endpoint}')
