<div align="center">

# 🛒 **Dione Ecommerce (College Project)**

### _Setup Guide — not written by AI because AI kept acting dumb 😤_

![Banner](https://github.com/user-attachments/assets/e7fef06d-ac46-4180-8d19-b797afaea016) <!-- Optional: Replace with your own banner -->

---

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange?logo=mysql)
![License](https://img.shields.io/badge/License-GNU-green)
![Status](https://img.shields.io/badge/Project-College%20Demo-yellow)

</div>

---

## 🧠 Prerequisites (aka “Don’t be Dumb”)

Before you start, make sure you have the following:

- 🐍 **Python 3.8+**
- 🧰 **MySQL (XAMPP recommended)**
- 💾 **Git**

---

## 🚀 Setup in 5 Kinda-Simple Steps

### **1️⃣ Clone this masterpiece**

```bash
git clone https://github.com/CodinWaffle/Dione-Ecommerce-College-Project.git
cd "Dione Ecommerce (College Project)"
```

2️⃣ Create & Activate Virtual Environment

```bash
python -m venv env
```

```bash
env\Scripts\activate.ps1
```

🐧 Git Bash

```bash
source env/bin/activate
```

💡 If you don’t see (env) — activate your brain, too.

3️⃣ Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4️⃣ Database (Updated)
Open MySQL / phpMyAdmin and run this script:

```sql
CREATE DATABASE IF NOT EXISTS dione_data;
USE dione_data;
DROP TABLE IF EXISTS `oauth`;
DROP TABLE IF EXISTS `user`;

CREATE TABLE `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(100) UNIQUE,
    `password` VARCHAR(255),
    `username` VARCHAR(150),
    `role` VARCHAR(20) NOT NULL DEFAULT 'buyer',
    `role_requested` VARCHAR(20) NULL,
    `is_approved` BOOLEAN NOT NULL DEFAULT TRUE,
    `is_suspended` BOOLEAN NOT NULL DEFAULT FALSE,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `oauth` (
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

SELECT 'Database setup completed successfully!' AS status;
SELECT COUNT(*) AS user_count FROM `user`;
SELECT COUNT(*) AS oauth_count FROM `oauth` WHERE 1=0;
```

5️ Create Admin User

```sql
USE dione_data;

INSERT INTO `user` (`email`, `password`, `username`, `role`, `is_approved`, `role_requested`, `created_at`)
VALUES (
    'admin.nigger@gmail.com',
    'pbkdf2:sha256:1000000$tGiCM6ISp4PIUsWr$91b3adff596e7dd04d8ac3c544c8c3fc46560d73ce18f65594878d38cedee57e',
    'admin_1',
    'admin',
    1,
    NULL,
    NOW()
);

-- Verify admin was created
SELECT * FROM `user` WHERE `email` = 'admin.nigger@gmail.com';
```

```
• Email - admin.nigger@gmail.com
• Password - admin_123
```

env\Scripts\activate.ps1

6️⃣ Run It!

```bash2
flask run
```

🧪Test command

```bash
pytest project/tests.py -v --tb=no
```

🧪 Git Cheat Sheet

```bash
# this command is to update you current codebase so use this before ypu start working because this can Get the latest changes from GitHub
git pull origin main
```

```bash
# Stages all modified, deleted, or new files in your project for commit.
git add .
```

```bash
# This saves your work with a message describing what you did.
git commit -m "I did something cool"
```

```bash
# Updates the main branch on GitHub with your latest changes.
git push origin main
```

If push fails → it’s your fault 😅 Run this:

```bash
# get latest + reapply your commits cleanly
git pull --rebase origin main
# publish your work
git push origin main
```
