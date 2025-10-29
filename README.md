
🛒 Dione Ecommerce (College Project)

Setup guide — not written by AI because AI kept acting dumb.

🧠 Prerequisites (aka “Don’t be Dumb”)

Python 3.8+

MySQL (like XAMPP) running

Git installed

🚀 Setup in 5 Kinda-Simple Steps
1. Clone this masterpiece
git clone https://github.com/CodinWaffle/Dione-Ecommerce-College-Project.git
cd "Dione Ecommerce (College Project)"

2. Virtual Environment (be smart, use one)
python -m venv env
# Windows
env\Scripts\activate.ps1
# Run This if You Using Git comand prompt
source env/bin/activate


If you don’t see (env) — activate your brain, too.

3. Install Dependencies
pip install --upgrade pip
pip install -r requirements.txt

4. Database Magic - Just Copy paste this
```sql

CREATE DATABASE IF NOT EXISTS dione_data;
USE dione_data;

CREATE TABLE IF NOT EXISTS `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(100) UNIQUE,
    `password` VARCHAR(255),
    `username` VARCHAR(150),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `oauth` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `provider` VARCHAR(50) NOT NULL,
    `provider_user_id` VARCHAR(256) NOT NULL,
    `provider_user_login` VARCHAR(256),
    `user_id` INT NOT NULL,
    `token` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE,
    UNIQUE KEY `unique_provider_user` (`provider`, `provider_user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX `idx_user_email` ON `user`(`email`);
CREATE INDEX `idx_user_username` ON `user`(`username`);
CREATE INDEX `idx_oauth_provider` ON `oauth`(`provider`);
CREATE INDEX `idx_oauth_user_id` ON `oauth`(`user_id`);

SELECT 'Database setup completed successfully!' as status;
SELECT COUNT(*) as user_count FROM `user`;
SELECT COUNT(*) as oauth_table_ready FROM `oauth` WHERE 1=0;
```

5. Make .env File (or cry later)
FLASK_APP=app.py
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://root:@localhost:3306/dione_data
DB_USER=root
DB_PASSWORD=
DB_NAME=dione_data
SECRET_KEY=some_secret_key

6. Run It
flask run


Then open http://127.0.0.1:5000
 and pretend it’s production-ready.

🧪 Git Cheat Sheet
git pull origin main
git add .
git commit -m "I did something cool"
git push origin main


If push fails → it’s your fault. Run:

git pull --rebase origin main
git push origin main

🩺 Common Issues

❌ flask not found → activate the virtual env

❌ DB errors → open XAMPP, genius

❌ Port busy → flask run --port 5001

❌ AI didn’t help → that’s why you’re reading this 😅

Now go run it. Don’t break it. 🚀
