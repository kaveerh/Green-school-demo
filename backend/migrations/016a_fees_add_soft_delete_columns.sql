-- Migration: 016a_fees_add_soft_delete_columns.sql
-- Description: Add missing soft delete and audit columns to fees tables
-- Purpose: Align database schema with BaseModel expectations

-- Add soft delete and audit columns to fee_structures
ALTER TABLE fee_structures
ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS deleted_by UUID REFERENCES users(id);

-- Add soft delete and audit columns to bursaries
ALTER TABLE bursaries
ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS deleted_by UUID REFERENCES users(id);

-- Add soft delete and audit columns to student_fees
ALTER TABLE student_fees
ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS deleted_by UUID REFERENCES users(id);

-- Add soft delete and audit columns to payments
ALTER TABLE payments
ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS deleted_by UUID REFERENCES users(id);

-- Add soft delete and audit columns to activity_fees
ALTER TABLE activity_fees
ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS deleted_by UUID REFERENCES users(id);

-- Add indexes for soft delete filtering (performance optimization)
CREATE INDEX IF NOT EXISTS idx_fee_structures_deleted_at ON fee_structures(deleted_at);
CREATE INDEX IF NOT EXISTS idx_bursaries_deleted_at ON bursaries(deleted_at);
CREATE INDEX IF NOT EXISTS idx_student_fees_deleted_at ON student_fees(deleted_at);
CREATE INDEX IF NOT EXISTS idx_payments_deleted_at ON payments(deleted_at);
CREATE INDEX IF NOT EXISTS idx_activity_fees_deleted_at ON activity_fees(deleted_at);

-- Comments
COMMENT ON COLUMN fee_structures.updated_by IS 'User who last updated this record';
COMMENT ON COLUMN fee_structures.deleted_at IS 'Timestamp when record was soft deleted';
COMMENT ON COLUMN fee_structures.deleted_by IS 'User who soft deleted this record';
