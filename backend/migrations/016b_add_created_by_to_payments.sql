-- Migration: 016b_add_created_by_to_payments.sql
-- Description: Add created_by column to payments table
-- Purpose: Align payments table with BaseModel expectations

-- Add created_by column to payments table
ALTER TABLE payments
ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);

-- Set existing records to use processed_by as created_by
UPDATE payments
SET created_by = processed_by
WHERE created_by IS NULL AND processed_by IS NOT NULL;

-- Comment
COMMENT ON COLUMN payments.created_by IS 'User who created this payment record (for audit trail)';
