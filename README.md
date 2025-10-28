# Dione Ecommerce - Private Project

A Flask-based e-commerce application with user authentication, social login, and email functionality.

## Quick Setup for Contributors

### Prerequisites
- Python 3.8 or higher
- MySQL server running locally
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd dione-ecommerce
   ```

2. **Run the automated setup**
   ```bash
   python setup.py
   ```
   This will:
   - Install all dependencies
   - Create the .env file with project credentials
   - Set up the MySQL database automatically
   - Verify everything is working

3. **Run the application**
   ```bash
   flask run
   ```

4. **Open your browser**
   Navigate to `http://localhost:5000`

## What the Setup Does

The `setup.py` script automates everything:

- ✅ **Dependencies**: Installs all required packages from `requirements.txt`
- ✅ **Environment**: Creates `.env` file with all necessary credentials
- ✅ **Database**: Connects to MySQL and runs `database_setup.sql`
- ✅ **Verification**: Tests that Flask app can start and connect to database

## Manual Database Setup (if needed)

If the automated database setup fails, you can set it up manually:

### Using SQLyog
1. Open SQLyog
2. Connect to your MySQL server
3. Run the `database_setup.sql` script

### Using phpMyAdmin
1. Open phpMyAdmin in your browser
2. Create a database named `dione_data` (or change the name in the SQL script)
3. Run the `database_setup.sql` script

## Project Structure

```
dione-ecommerce/
├── app.py                    # Flask application entry point
├── setup.py                  # Automated setup script
├── database_setup.sql        # Database creation script
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (created by setup)
├── project/                  # Main application code
│   ├── routes/              # Route handlers
│   ├── services/            # Business logic
│   ├── utils/               # Utilities
│   └── templates/           # HTML templates
└── migrations/              # Database migrations
```

## Development

### Running Tests
```bash
python -m pytest project/tests.py -v
```

### Running with Debug Mode
```bash
flask --debug run
```

### Database Migrations
```bash
flask db migrate -m "Description"
flask db upgrade
```

## Features

- 🔐 User authentication (login, signup, password reset)
- 🌐 Social login (Google, Facebook OAuth)
- 📧 Email functionality (password reset)
- 🗄️ MySQL database with SQLAlchemy ORM
- 🧪 Comprehensive test suite
- 📱 Responsive Bootstrap design

## Default Test Accounts

After setup, you can use these test accounts:

- **Admin**: `admin@dione.com` / `admin123`
- **Test User**: `test@dione.com` / `admin123`

## Troubleshooting

### MySQL Connection Issues
- Ensure MySQL server is running
- Check that you can connect with the credentials in `.env`
- Verify the database `dione_data` exists

### Flask Import Errors
- Make sure you're in the project directory
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Port Already in Use
```bash
flask run --port 5001
```

## Contributing

1. Make your changes
2. Run tests: `python -m pytest project/tests.py -v`
3. Ensure `flask run` works without errors
4. Submit your pull request

---

**Ready to develop! 🚀**
