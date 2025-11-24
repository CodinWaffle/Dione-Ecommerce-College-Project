#!/usr/bin/env python3
import os
import sys
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

def main():
    tmpl_dir = os.path.join(os.path.dirname(__file__), '..', 'project', 'templates')
    tmpl_dir = os.path.abspath(tmpl_dir)
    loader = FileSystemLoader(tmpl_dir)
    env = Environment(loader=loader)
    had_error = False
    for root, dirs, files in os.walk(tmpl_dir):
        for fn in files:
            if not fn.endswith('.html'):
                continue
            full = os.path.join(root, fn)
            rel = os.path.relpath(full, tmpl_dir).replace('\\', '/')
            try:
                src = loader.get_source(env, rel)[0]
                env.parse(src)
            except TemplateSyntaxError as e:
                had_error = True
                print(f"TEMPLATE SYNTAX ERROR: {rel}:{e.lineno}: {e.message}")
            except Exception as e:
                had_error = True
                print(f"ERROR parsing {rel}: {e}")
    if not had_error:
        print('No template syntax errors found')

if __name__ == '__main__':
    main()
