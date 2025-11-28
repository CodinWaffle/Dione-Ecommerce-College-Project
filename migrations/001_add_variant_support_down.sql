-- Migration: Remove variant support (rollback)
-- Down migration

-- Drop tables in reverse order
DROP TABLE IF EXISTS variant_sizes;
DROP TABLE IF EXISTS product_variants;
DROP TABLE IF EXISTS product_descriptions;

-- Remove added columns
ALTER TABLE seller_product_management 
DROP COLUMN IF EXISTS base_sku,
DROP COLUMN IF EXISTS draft_data,
DROP COLUMN IF EXISTS is_draft;

COMMIT;