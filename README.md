<div align="center">

# 🛒 **Dione Ecommerce (College Project)**  
### *Setup Guide — not written by AI because AI kept acting dumb 😤*

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
4️⃣ Database Magic ✨
Open MySQL / phpMyAdmin and run this script:

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

SELECT 'Database setup completed successfully!' AS status;
SELECT COUNT(*) AS user_count FROM `user`;
SELECT COUNT(*) AS oauth_table_ready FROM `oauth` WHERE 1=0;
```

5️⃣ Run It!
```bash
flask run
```

🧪 Git Cheat Sheet
```bash
Copy code
git pull origin main
git add .
git commit -m "I did something cool"
git push origin main
```
If push fails → it’s your fault 😅 Run this:

```bash
git pull --rebase origin main
git push origin main
```
