#!/usr/bin/env python3
"""
Migration script to add variant support to the database
"""

import os
import sys
from project import create_app, db

def run_migration():
    """Run the database migration"""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("Running database migration...")
            
            # Read and execute the migration SQL
            migration_file = 'migrations/001_add_variant_support.sql'
            
            if not os.path.exists(migration_file):
                print(f"Error: Migration file {migration_file} not found")
                return False
            
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            # Split by statements and execute
            statements = [stmt.strip() for stmt in migration_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement.upper().startswith(('CREATE', 'ALTER', 'INSERT')):
                    print(f"Executing: {statement[:50]}...")
                    db.session.execute(db.text(statement))
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            return False

def rollback_migration():
    """Rollback the database migration"""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("Rolling back database migration...")
            
            # Read and execute the rollback SQL
            rollback_file = 'migrations/001_add_variant_support_down.sql'
            
            if not os.path.exists(rollback_file):
                print(f"Error: Rollback file {rollback_file} not found")
                return False
            
            with open(rollback_file, 'r') as f:
                rollback_sql = f.read()
            
            # Split by statements and execute
            statements = [stmt.strip() for stmt in rollback_sql.split(';') if stmt.strip()]
            
            for statement in statements:
                if statement.upper().startswith(('DROP', 'ALTER')):
                    print(f"Executing: {statement[:50]}...")
                    db.session.execute(db.text(statement))
            
            db.session.commit()
            print("✅ Rollback completed successfully!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Rollback failed: {e}")
            return False

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'rollback':
        rollback_migration()
    else:
        run_migration()