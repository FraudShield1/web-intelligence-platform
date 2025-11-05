-- Create Admin User Directly
-- Run this in Supabase SQL Editor after running supabase_schema.sql

-- First, check if tables exist
DO $$ 
BEGIN
    -- Create admin user with hashed password
    -- Password: SecurePassword123
    -- Hash generated with bcrypt
    INSERT INTO users (
        user_id,
        username,
        email,
        password_hash,
        full_name,
        role,
        is_active,
        created_at,
        updated_at
    ) VALUES (
        gen_random_uuid(),
        'admin@example.com',
        'admin@example.com',
        '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqRX0JQFCm', -- SecurePassword123
        'Admin User',
        'admin',
        true,
        NOW(),
        NOW()
    )
    ON CONFLICT (email) DO NOTHING;
    
    RAISE NOTICE 'Admin user created successfully!';
    RAISE NOTICE 'Email: admin@example.com';
    RAISE NOTICE 'Password: SecurePassword123';
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        RAISE NOTICE 'Make sure you ran supabase_schema.sql first!';
END $$;

-- Verify the user was created
SELECT 
    user_id,
    username,
    email,
    full_name,
    role,
    is_active,
    created_at
FROM users
WHERE email = 'admin@example.com';

