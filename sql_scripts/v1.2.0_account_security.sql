-- Migration: v1.2.0 Account Security Features
-- Description: Add account lockout, failed login tracking, and force password change

-- Add security columns to user_profiles
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS locked_until TIMESTAMP WITH TIME ZONE DEFAULT NULL,
ADD COLUMN IF NOT EXISTS must_change_password BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS last_password_change TIMESTAMP WITH TIME ZONE DEFAULT NULL;

-- Create index for efficient lockout queries
CREATE INDEX IF NOT EXISTS idx_user_profiles_locked_until ON user_profiles(locked_until) WHERE locked_until IS NOT NULL;

-- Add comment for documentation
COMMENT ON COLUMN user_profiles.failed_login_attempts IS 'Number of consecutive failed login attempts';
COMMENT ON COLUMN user_profiles.locked_until IS 'Account locked until this timestamp (NULL = not locked)';
COMMENT ON COLUMN user_profiles.must_change_password IS 'User must change password on next login';
COMMENT ON COLUMN user_profiles.last_password_change IS 'Timestamp of last password change';
