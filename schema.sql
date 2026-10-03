-- LifePilot AI Database Schema Initialization Script

CREATE DATABASE IF NOT EXISTS lifepilot_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE lifepilot_db;

-- 1. Users Table (Secure password hashes, no plain text)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Daily Records Table
CREATE TABLE IF NOT EXISTS daily_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    record_date DATE NOT NULL,
    sleep_hours DECIMAL(4,2) NOT NULL,
    work_hours DECIMAL(4,2) NOT NULL,
    screen_time DECIMAL(4,2) NOT NULL,
    exercise_mins INT NOT NULL DEFAULT 0,
    stress_level INT NOT NULL DEFAULT 5, -- Scale 1 to 10
    mood VARCHAR(20) NOT NULL DEFAULT 'Neutral', -- Happy, Focused, Neutral, Tired, Stressed
    productivity_score DECIMAL(5,2) DEFAULT NULL, -- 0.00 to 100.00
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (user_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    priority VARCHAR(10) DEFAULT 'Medium', -- Low, Medium, High
    status VARCHAR(15) DEFAULT 'Pending', -- Pending, In Progress, Completed
    estimated_hours DECIMAL(4,2) DEFAULT 1.0,
    due_date DATE DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Expenses Table
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    expense_date DATE NOT NULL,
    category VARCHAR(50) NOT NULL, -- Food, Transport, Utilities, Entertainment, Health, Shopping, Other
    amount DECIMAL(10,2) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Predictions Table
CREATE TABLE IF NOT EXISTS predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    record_date DATE NOT NULL,
    predicted_productivity_score DECIMAL(5,2) NOT NULL,
    predicted_productivity_level VARCHAR(20) NOT NULL, -- Low, Medium, High
    regression_model_version VARCHAR(50) DEFAULT 'v1.0',
    classification_model_version VARCHAR(50) DEFAULT 'v1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. AI Interactions Table
CREATE TABLE IF NOT EXISTS ai_interactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    intent VARCHAR(50) DEFAULT 'general',
    recommendations_json JSON DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
