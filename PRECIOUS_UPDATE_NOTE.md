**UPDATES I MADE**

### **1️⃣ List of Changes**

1. Login UI
2. Signup - UI then instead of accordion ginawa ko siyang role card na iseselect ni user
3. Signup pages for each roles (buyer, seller, rider)

### **2️⃣ Updated Database**

#Original DB query

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

**CREATE ADMIN USER**

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
```

**NEW DB TABLES - updated**

```sql
CREATE DATABASE IF NOT EXISTS dione_data;
USE dione_data;

SET FOREIGN_KEY_CHECKS = 0;

-- ========================
-- TABLE: buyer
-- ========================
DROP TABLE IF EXISTS `buyer`;
CREATE TABLE `buyer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `address` text DEFAULT NULL,
  `city` varchar(100) DEFAULT NULL,
  `zip_code` varchar(20) DEFAULT NULL,
  `country` varchar(100) DEFAULT NULL,
  `preferred_language` varchar(50) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `buyer_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ========================
-- TABLE: seller
-- ========================
DROP TABLE IF EXISTS `seller`;
CREATE TABLE `seller` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `business_name` varchar(255) NOT NULL,
  `business_type` varchar(100) DEFAULT NULL,
  `business_address` text DEFAULT NULL,
  `business_city` varchar(100) DEFAULT NULL,
  `business_zip` varchar(20) DEFAULT NULL,
  `business_country` varchar(100) DEFAULT NULL,
  `bank_account` varchar(100) DEFAULT NULL,
  `bank_holder_name` varchar(255) DEFAULT NULL,
  `tax_id` varchar(50) DEFAULT NULL,
  `store_description` text DEFAULT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `seller_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ========================
-- TABLE: rider
-- ========================
DROP TABLE IF EXISTS `rider`;
CREATE TABLE `rider` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `license_number` varchar(50) DEFAULT NULL,
  `vehicle_type` varchar(50) DEFAULT NULL,
  `vehicle_number` varchar(50) DEFAULT NULL,
  `availability_status` varchar(20) DEFAULT NULL,
  `current_location` varchar(255) DEFAULT NULL,
  `delivery_zones` text DEFAULT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `verification_date` datetime DEFAULT NULL,
  `rating` float DEFAULT NULL,
  `total_deliveries` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `rider_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- ========================
-- TABLE: site_setting
-- ========================
DROP TABLE IF EXISTS `site_setting`;
CREATE TABLE `site_setting` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `key` varchar(64) NOT NULL,
  `value` text NOT NULL,
  `updated_at` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `site_setting` VALUES
(1,'support_email','support@example.com','2025-11-16 19:44:12'),
(2,'support_phone','+63 900 000 0000','2025-11-16 19:44:12'),
(3,'auto_approve_sellers','false','2025-11-16 19:44:12'),
(4,'auto_approve_riders','false','2025-11-16 19:44:12'),
(5,'maintenance_mode','false','2025-11-16 19:44:12');

SET FOREIGN_KEY_CHECKS = 1;
```

**LOGIC or Pano siya Nagwowork**

1. Need magsignup ni user and pumili which role (buyer, seller, rider)
2. Need ni user kumpletuhin yung mga hinihingi na requirements before masubmit yung form
3. Need ng approval ni admin (maliban sa buyer) before makapaglogin

**PROBLEM na need i Fix**

1. Walang email na nagsesend sa nagaapply as seller or rider (pending approval email)
2. At email once approved na ni admin yung account
