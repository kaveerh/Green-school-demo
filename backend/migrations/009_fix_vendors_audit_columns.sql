-- Migration: Fix Vendors Audit Columns
-- Description: Rename audit columns to match BaseModel pattern

-- Rename created_by_id to created_by
ALTER TABLE vendors RENAME COLUMN created_by_id TO created_by;

-- Rename updated_by_id to updated_by
ALTER TABLE vendors RENAME COLUMN updated_by_id TO updated_by;

-- Add deleted_by column (missing from original migration)
ALTER TABLE vendors ADD COLUMN deleted_by UUID REFERENCES users(id);
