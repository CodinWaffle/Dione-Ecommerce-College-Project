#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import mysql.connector
from pathlib import Path

def print_header():
    print("=" * 60)
    print("Welcome My Nigga")
    print("=" * 60)
    print("Setting up the Flask project for development...")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    print("\n[1/6] Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR:You Idiot Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        sys.exit(1)
    print(f"SUCCESS: Python {version.major}.{version.minor}.{version.micro} detected")

def install_dependencies():
    """Install required dependencies"""
    print("\n[2/6] It's Fucking time for Installing dependencies...")

    try:
        # Install requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("SUCCESS: All dependencies installed")

    except subprocess.CalledProcessError as e:
        print(f"ERROR: You Idiot Failed to install dependencies: {e}")
        print("   Please check your internet connection and try again")
        sys.exit(1)

def create_env_file():
    """Create .env file with actual credentials"""
    print("\n[3/6] Setting up environment configuration...")

    if os.path.exists(".env"):
        print("SUCCESS: .env file already exists")
        return

    # Create .env file with actual credentials for contributors
    env_content = """# Dione Ecommerce Environment Configuration
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=60976a5747100e32f8206121d5aefa5f

# Database Configuration
DATABASE_URL=mysql+pymysql://root:@localhost:3306/dione_data
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=dione_data

# Email Configuration
MAIL_SERVER=smtp.googlemail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=dnxncpcx@gmail.com
MAIL_PASSWORD=otxu kxyl gomk qnyi

# OAuth Configuration
GOOGLE_CLIENT_ID=570919329793-qrilq0ut8fmqla4r1giar48g0c1e2v8d.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
FACEBOOK_CLIENT_ID=YOUR_FACEBOOK_APP_ID
FACEBOOK_CLIENT_SECRET=YOUR_FACEBOOK_APP_SECRET

# Development Settings
DEBUG=True
TESTING=False
"""

    with open(".env", "w") as f:
        f.write(env_content)

    print("SUCCESS: yay .env file created with project credentials")

def load_env_variables():
    """Load environment variables from .env file"""
    print("\n[4/6] Loading environment variables...")

    if not os.path.exists(".env"):
        print("ERROR: You Idiot .env file not found")
        sys.exit(1)

    env_vars = {}
    with open(".env", "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()

    for key, value in env_vars.items():
        os.environ[key] = value

    print("SUCCESS: yay Environment variables loaded")
    return env_vars

def setup_database(env_vars):
    """Set up MySQL database using SQL script"""
    print("\n[5/6] Setting up MySQL database...")

    # Get database credentials from environment
    db_host = env_vars.get('DB_HOST', 'localhost')
    db_user = env_vars.get('DB_USER', 'root')
    db_password = env_vars.get('DB_PASSWORD', '')
    db_name = env_vars.get('DB_NAME', 'dione_data')

    try:
        # Connect to MySQL server (without specifying database)
        print(f"   Connecting to MySQL server at {db_host}...")
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password
        )
        cursor = connection.cursor()

        # Read and execute SQL script
        print("   Executing database setup script...")
        with open("database_setup.sql", "r") as f:
            sql_script = f.read()

        # Split script into individual statements
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]

        for statement in statements:
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    # Consume any results to avoid "Unread result found" error
                    try:
                        cursor.fetchall()
                    except:
                        pass
                except mysql.connector.Error as stmt_error:
                    print(f"   Warning: Bruh Statement failed: {stmt_error}")
                    continue

        connection.commit()
        cursor.close()
        connection.close()

        print("SUCCESS: Yay Database setup completed")
        print(f"   Database '{db_name}' created with all tables")

    except mysql.connector.Error as e:
        print(f"ERROR: You Idiot Database setup failed: {e}")
        print("   Please ensure MySQL server is running and credentials are correct")
        print("   You can set up the database manually using database_setup.sql")
        return False

    except FileNotFoundError:
        print("ERROR: You Idiot database_setup.sql file not found")
        sys.exit(1)

    return True

def test_flask_app():
    """Test if Flask app can be imported and run"""
    print("\n[6/6] Testing Flask application...")

    try:
        # Test if we can import the app
        from project import create_app
        app = create_app('development')
        print("SUCCESS: yay Flask application imports successfully")

        # Test database connection
        with app.app_context():
            from project import db
            db.create_all()
            print("SUCCESS: yay Database connection verified")

        return True

    except Exception as e:
        print(f"WARNING: Oh No My Nigga Flask app test failed: {e}")
        print("   The setup is complete, but there might be configuration issues")
        return False

def print_final_instructions():
    """Print final setup instructions"""
    print("\n" + "=" * 60)
    print("SETUP COMPLETE!")
    print("=" * 60)
    print("\nYour development environment is ready!")
    print("\nTo run the application:")
    print("   flask run")
    print("\nThe application will be available at:")
    print("   http://localhost:5000")
    print("\nFor development with auto-reload:")
    print("   flask --debug run")
    print("\n" + "=" * 60)

def main():
    """Main setup function"""
    print_header()

    # Check Python version
    check_python_version()

    # Install dependencies
    install_dependencies()

    # Create environment file
    create_env_file()

    # Load environment variables
    env_vars = load_env_variables()

    # Setup database
    db_success = setup_database(env_vars)

    # Test Flask app
    app_success = test_flask_app()

    # Print final instructions
    print_final_instructions()

    if db_success and app_success:
        print("SUCCESS: Everything is set up and ready to go!")
    else:
        print("PARTIAL SUCCESS: Setup completed with some warnings.")
        print("Check the messages above and run 'flask run' to test.")

if __name__ == "__main__":
    main()
