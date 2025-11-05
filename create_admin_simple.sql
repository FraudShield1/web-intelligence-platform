-- Simple Admin User Creation
-- Run this in Supabase SQL Editor
-- Works with existing table structure from supabase_schema.sql

-- Create admin user
-- Password: SecurePassword123
INSERT INTO users (
    user_id,
    username,
    email,
    password_hash,
    role,
    is_active,
    created_at,
    updated_at
) VALUES (
    gen_random_uuid(),
    'admin@example.com',
    'admin@example.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqRX0JQFCm',
    'admin',
    true,
    NOW(),
    NOW()
)
ON CONFLICT (email) DO UPDATE SET
    password_hash = EXCLUDED.password_hash,
    role = EXCLUDED.role,
    is_active = EXCLUDED.is_active,
    updated_at = NOW();

-- Verify the user was created
SELECT 
    user_id,
    username,
    email,
    role,
    is_active,
    created_at
FROM users
WHERE email = 'admin@example.com';

-- Success message
SELECT 'Admin user ready!' as status;
SELECT 'Login: admin@example.com / SecurePassword123' as credentials;

