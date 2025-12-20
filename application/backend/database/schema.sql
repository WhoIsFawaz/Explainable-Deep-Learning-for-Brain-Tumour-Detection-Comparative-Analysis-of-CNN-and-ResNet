-- ==================================================================================
-- Brain MRI Classification System - Database Schema
-- ==================================================================================
-- Purpose: Store users, authentication, and MRI predictions with Grad-CAM results
-- Database: MySQL 8.0+
-- ==================================================================================

-- Drop existing database if exists (use with caution!)
-- DROP DATABASE IF EXISTS brain_mri_db;

-- Create database
CREATE DATABASE IF NOT EXISTS brain_mri_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE brain_mri_db;

-- ==================================================================================
-- Table: users
-- ==================================================================================
-- Stores user accounts (admin, doctor, patient)
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'doctor', 'patient') NOT NULL DEFAULT 'patient',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================================================================================
-- Table: images
-- ==================================================================================
-- Stores MRI scan predictions with Grad-CAM outputs
CREATE TABLE images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    original_image_uri VARCHAR(500) NOT NULL,
    gradcam_image_uri VARCHAR(500) DEFAULT NULL,
    predicted_label VARCHAR(50) NOT NULL,
    prob_tumor DECIMAL(7, 6) NOT NULL,
    prob_no_tumor DECIMAL(7, 6) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (doctor_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES users(id) ON DELETE CASCADE,
    
    INDEX idx_doctor (doctor_id),
    INDEX idx_patient (patient_id),
    INDEX idx_uploaded (uploaded_at),
    INDEX idx_label (predicted_label)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==================================================================================
-- Sample Data (Development Only)
-- ==================================================================================
-- Password: "admin123" hashed with bcrypt
INSERT INTO users (name, email, password_hash, role) VALUES
('System Administrator', 'admin@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lZJr3Z.eLJIO', 'admin'),
('Dr. Sarah Johnson', 'doctor@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lZJr3Z.eLJIO', 'doctor'),
('John Doe', 'patient@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5lZJr3Z.eLJIO', 'patient');

-- ==================================================================================
-- Verification Queries
-- ==================================================================================
-- SELECT * FROM users;
-- SELECT * FROM images;
-- SHOW TABLES;
-- DESCRIBE users;
-- DESCRIBE images;
