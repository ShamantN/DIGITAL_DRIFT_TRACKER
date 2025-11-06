-- Authentication Migration Script
-- This script adds authentication support to the existing database schema

-- Add password_hash column to user table
ALTER TABLE `user` 
ADD COLUMN `password_hash` VARCHAR(255) DEFAULT NULL AFTER `email`,
ADD COLUMN `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER `created_at`;

-- Make email unique
ALTER TABLE `user` 
ADD UNIQUE KEY `unique_email` (`email`);

-- Update existing users (if any) to have a default password
-- You should manually set proper passwords for existing users
UPDATE `user` SET `password_hash` = '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW' WHERE `password_hash` IS NULL;
-- Default password is 'password' - CHANGE THIS FOR PRODUCTION!

-- Modify user table to make timezone optional for new users
ALTER TABLE `user` 
MODIFY COLUMN `timezone` VARCHAR(50) DEFAULT 'UTC';

-- Create sessions table for authentication tokens (optional, JWT tokens are stateless)
-- This table can be used for token blacklisting if needed later

-- Add indexes for better performance
CREATE INDEX `idx_user_email` ON `user` (`email`);
CREATE INDEX `idx_user_created_at` ON `user` (`created_at`);