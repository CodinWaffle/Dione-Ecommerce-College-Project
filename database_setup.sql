-- Dione Ecommerce Database Setup Script
-- This script works for both SQLyog and phpMyAdmin
-- For phpMyAdmin users: Replace 'dione_data' with your database name below if different

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS dione_data;

-- Use the database
USE dione_data;

-- Create users table
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(100) UNIQUE,
    `password` VARCHAR(255),
    `username` VARCHAR(150),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create oauth table for social login
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

-- Create indexes for better performance
CREATE INDEX `idx_user_email` ON `user`(`email`);
CREATE INDEX `idx_user_username` ON `user`(`username`);
CREATE INDEX `idx_oauth_provider` ON `oauth`(`provider`);
CREATE INDEX `idx_oauth_user_id` ON `oauth`(`user_id`);

-- Insert sample data for development
INSERT IGNORE INTO `user` (`username`, `email`, `password`) VALUES
('admin', 'admin@dione.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9yKzK2a'),
('testuser', 'test@dione.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/9yKzK2a');

-- Note: Default password for both users is 'admin123'

-- Verify setup
SELECT 'Database setup completed successfully!' as status;
SELECT COUNT(*) as user_count FROM `user`;
SELECT COUNT(*) as oauth_table_ready FROM `oauth` WHERE 1=0;
