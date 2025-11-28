-- Rollback migration: Remove seller statistics tracking

-- Drop triggers
DROP TRIGGER IF EXISTS trigger_product_stats ON products;
DROP TRIGGER IF EXISTS trigger_follower_stats ON store_followers;
DROP TRIGGER IF EXISTS trigger_review_stats ON product_reviews;

-- Drop functions
DROP FUNCTION IF EXISTS trigger_update_seller_stats();
DROP FUNCTION IF EXISTS update_seller_statistics(INTEGER);

-- Drop indexes
DROP INDEX IF EXISTS idx_store_followers_store_id;
DROP INDEX IF EXISTS idx_store_followers_follower_id;
DROP INDEX IF EXISTS idx_product_reviews_product_id;
DROP INDEX IF EXISTS idx_product_reviews_seller_id;
DROP INDEX IF EXISTS idx_product_reviews_rating;

-- Drop tables
DROP TABLE IF EXISTS product_reviews;
DROP TABLE IF EXISTS store_followers;

-- Remove columns from seller_profiles
ALTER TABLE seller_profiles DROP COLUMN IF EXISTS rating_count;
ALTER TABLE seller_profiles DROP COLUMN IF EXISTS products_count;
ALTER TABLE seller_profiles DROP COLUMN IF EXISTS followers_count;
ALTER TABLE seller_profiles DROP COLUMN IF EXISTS total_sales;
ALTER TABLE seller_profiles DROP COLUMN IF EXISTS last_active;