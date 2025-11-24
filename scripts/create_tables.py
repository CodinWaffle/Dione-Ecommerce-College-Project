"""Utility to create all database tables for local development.

Run this with the virtualenv's Python to create any missing tables (safe to run).
Example (PowerShell):
    .\env\Scripts\Activate.ps1; python scripts/create_tables.py
"""
from project import create_app, db
import os

app = create_app()

with app.app_context():
    print("Creating database tables (if any missing)...")
    db.create_all()
    print("Done.")
