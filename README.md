<div align="center">

# 🛒 **Dione Ecommerce (College Project)**

<img width="1828" height="878" alt="Image" src="https://github.com/user-attachments/assets/e15f3bc2-5740-42a4-bd54-429601f50b4f" />

---

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Framework-lightgrey?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-Database-orange?logo=mysql)
![License](https://img.shields.io/badge/License-GNU-green)
![Status](https://img.shields.io/badge/Project-College%20Demo-yellow)

</div>

---
Before you start, make sure you have the following:

-  **Python 3.8+**
-  **MySQL (XAMPP recommended)**
-  **Git**

---

##  Setup in 5 Kinda-Simple Steps

### ** Clone this masterpiece**
```bash
git clone https://github.com/CodinWaffle/Dione-Ecommerce-College-Project.git
cd "Dione Ecommerce (College Project)"
```
 Create & Activate Virtual Environment
```bash
python -m venv env
```
```bash
env\Scripts\activate.ps1
```
 Git Bash
```bash
source env/bin/activate
```
 If you don’t see (env) — activate your brain, too.

 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
 Database (Updated)
We now have storefront, catalog, cart, and review tables. You can either run the Alembic migrations (`flask db upgrade`) or paste the SQL below into MySQL / phpMyAdmin:

```sql
CREATE DATABASE IF NOT EXISTS dione_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dione_data;
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `order_tracking_event`;
DROP TABLE IF EXISTS `review_response`;
DROP TABLE IF EXISTS `review_media`;
DROP TABLE IF EXISTS `review`;
DROP TABLE IF EXISTS `cart_item`;
DROP TABLE IF EXISTS `cart`;
DROP TABLE IF EXISTS `product_variant`;
DROP TABLE IF EXISTS `store_profile`;
DROP TABLE IF EXISTS `order_item`;
DROP TABLE IF EXISTS `order`;
DROP TABLE IF EXISTS `inventory_transaction`;
DROP TABLE IF EXISTS `product_image`;
DROP TABLE IF EXISTS `product`;
DROP TABLE IF EXISTS `category`;
DROP TABLE IF EXISTS `site_setting`;
DROP TABLE IF EXISTS `oauth`;
DROP TABLE IF EXISTS `user`;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(100) UNIQUE,
    `password` VARCHAR(255),
    `username` VARCHAR(150),
    `role` VARCHAR(20) NOT NULL DEFAULT 'buyer',
    `role_requested` VARCHAR(20),
    `role_request_details` TEXT,
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
    UNIQUE KEY `unique_provider_user` (`provider`, `provider_user_id`),
    CONSTRAINT `fk_oauth_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `site_setting` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(64) NOT NULL UNIQUE,
    `value` TEXT NOT NULL,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `category` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(120) NOT NULL UNIQUE,
    `slug` VARCHAR(120) UNIQUE,
    `description` TEXT,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `product` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `seller_id` INT NOT NULL,
    `category_id` INT,
    `name` VARCHAR(150) NOT NULL,
    `description` TEXT,
    `price` DECIMAL(12,2) NOT NULL DEFAULT 0,
    `sku` VARCHAR(64) UNIQUE,
    `stock` INT NOT NULL DEFAULT 0,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `is_featured` BOOLEAN NOT NULL DEFAULT FALSE,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_product_seller` FOREIGN KEY (`seller_id`) REFERENCES `user`(`id`),
    CONSTRAINT `fk_product_category` FOREIGN KEY (`category_id`) REFERENCES `category`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `product_image` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL,
    `path` VARCHAR(255) NOT NULL,
    `position` INT NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_product_image_product` FOREIGN KEY (`product_id`) REFERENCES `product`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `inventory_transaction` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL,
    `change` INT NOT NULL,
    `source` VARCHAR(50) NOT NULL DEFAULT 'manual',
    `note` VARCHAR(255),
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_inventory_product` FOREIGN KEY (`product_id`) REFERENCES `product`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `store_profile` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `seller_id` INT NOT NULL UNIQUE,
    `name` VARCHAR(150) NOT NULL,
    `slug` VARCHAR(160) NOT NULL UNIQUE,
    `tagline` VARCHAR(255),
    `description` TEXT,
    `contact_email` VARCHAR(150),
    `contact_phone` VARCHAR(50),
    `theme_color` VARCHAR(20) NOT NULL DEFAULT '#111827',
    `logo_image` VARCHAR(255),
    `banner_image` VARCHAR(255),
    `social_links` TEXT,
    `shipping_policy` TEXT,
    `return_policy` TEXT,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_store_profile_seller` FOREIGN KEY (`seller_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `product_variant` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL,
    `attribute` VARCHAR(80) NOT NULL DEFAULT 'Size',
    `value` VARCHAR(80) NOT NULL,
    `price_delta` DECIMAL(12,2) NOT NULL DEFAULT 0,
    `stock` INT NOT NULL DEFAULT 0,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_product_variant_product` FOREIGN KEY (`product_id`) REFERENCES `product`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `cart` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `status` VARCHAR(20) NOT NULL DEFAULT 'active',
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_cart_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `cart_item` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `cart_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `variant_id` INT,
    `quantity` INT NOT NULL DEFAULT 1,
    `unit_price` DECIMAL(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT `fk_cart_item_cart` FOREIGN KEY (`cart_id`) REFERENCES `cart`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_cart_item_product` FOREIGN KEY (`product_id`) REFERENCES `product`(`id`),
    CONSTRAINT `fk_cart_item_variant` FOREIGN KEY (`variant_id`) REFERENCES `product_variant`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `review` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL,
    `store_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `rating` INT NOT NULL,
    `title` VARCHAR(150),
    `body` TEXT,
    `media_count` INT NOT NULL DEFAULT 0,
    `is_published` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_review_product` FOREIGN KEY (`product_id`) REFERENCES `product`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_review_store` FOREIGN KEY (`store_id`) REFERENCES `store_profile`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_review_user` FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `review_media` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `review_id` INT NOT NULL,
    `path` VARCHAR(255) NOT NULL,
    `media_type` VARCHAR(20) NOT NULL DEFAULT 'image',
    CONSTRAINT `fk_review_media_review` FOREIGN KEY (`review_id`) REFERENCES `review`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `review_response` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `review_id` INT NOT NULL UNIQUE,
    `seller_id` INT NOT NULL,
    `message` TEXT NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_review_response_review` FOREIGN KEY (`review_id`) REFERENCES `review`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_review_response_seller` FOREIGN KEY (`seller_id`) REFERENCES `user`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `order` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `seller_id` INT NOT NULL,
    `buyer_id` INT,
    `status` VARCHAR(20) NOT NULL DEFAULT 'pending',
    `total_amount` DECIMAL(12,2) NOT NULL DEFAULT 0,
    `currency` VARCHAR(8) NOT NULL DEFAULT 'PHP',
    `placed_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_order_seller` FOREIGN KEY (`seller_id`) REFERENCES `user`(`id`),
    CONSTRAINT `fk_order_buyer` FOREIGN KEY (`buyer_id`) REFERENCES `user`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `order_item` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `variant_id` INT,
    `quantity` INT NOT NULL DEFAULT 1,
    `unit_price` DECIMAL(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT `fk_order_item_order` FOREIGN KEY (`order_id`) REFERENCES `order`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_order_item_product` FOREIGN KEY (`product_id`) REFERENCES `product`(`id`),
    CONSTRAINT `fk_order_item_variant` FOREIGN KEY (`variant_id`) REFERENCES `product_variant`(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `order_tracking_event` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `status` VARCHAR(50) NOT NULL,
    `message` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_tracking_order` FOREIGN KEY (`order_id`) REFERENCES `order`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE INDEX `idx_user_username` ON `user`(`username`);
CREATE INDEX `idx_product_seller` ON `product`(`seller_id`);
CREATE INDEX `idx_product_category` ON `product`(`category_id`);
CREATE INDEX `idx_order_seller` ON `order`(`seller_id`);
CREATE INDEX `idx_order_buyer` ON `order`(`buyer_id`);
CREATE INDEX `idx_cart_user` ON `cart`(`user_id`);
CREATE INDEX `idx_review_product` ON `review`(`product_id`);
CREATE INDEX `idx_review_store` ON `review`(`store_id`);

SELECT 'Database setup completed successfully!' AS status;
```
 Create Admin User
```sql
USE dione_data;

INSERT INTO `user` (`email`, `password`, `username`, `role`, `is_approved`, `role_requested`, `created_at`)
VALUES (
    'admin@dione.local',
    'pbkdf2:sha256:1000000$tGiCM6ISp4PIUsWr$91b3adff596e7dd04d8ac3c544c8c3fc46560d73ce18f65594878d38cedee57e',
    'admin_1',
    'admin',
    1,
    NULL,
    NOW()
);

-- Verify admin was created
SELECT * FROM `user` WHERE `email` = 'admin@dione.local';
```
```
• Email - admin@dione.local
• Password - admin_123
```

 Run It!
```bash
flask run
```
Test command
```bash
pytest project/tests.py -v --tb=no
```
 
