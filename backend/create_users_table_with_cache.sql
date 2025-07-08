-- Create users table with birth chart caching columns for SQLite
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    credits INTEGER DEFAULT 0,
    phone VARCHAR(20),
    birth_date DATE,
    birth_time TIME,
    birth_location VARCHAR(255),
    spiritual_level VARCHAR(50) DEFAULT 'beginner',
    preferred_language VARCHAR(10) DEFAULT 'en',
    avatar_sessions_count INTEGER DEFAULT 0,
    total_avatar_minutes INTEGER DEFAULT 0,
    preferred_avatar_style VARCHAR(50) DEFAULT 'traditional',
    voice_preference VARCHAR(50) DEFAULT 'compassionate',
    video_quality_preference VARCHAR(20) DEFAULT 'high',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    
    -- Birth chart caching columns
    birth_chart_data TEXT,
    birth_chart_hash VARCHAR(64),
    birth_chart_cached_at TIMESTAMP,
    birth_chart_expires_at TIMESTAMP,
    has_free_birth_chart BOOLEAN DEFAULT false
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_birth_chart_hash ON users(birth_chart_hash);
CREATE INDEX IF NOT EXISTS idx_users_birth_chart_expires ON users(birth_chart_expires_at);

-- Verify table creation
SELECT name FROM sqlite_master WHERE type='table' AND name='users';