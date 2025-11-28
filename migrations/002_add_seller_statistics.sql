-- Migration: Add seller statistics tracking
-- This migration adds fields to track seller statistics for the product dropdown details

-- Add statistics columns to seller_profiles table
ALTER TABLE seller_profiles ADD COLUMN IF NOT EXISTS rating_count INTEGER DEFAULT 0;
ALTER TABLE seller_profiles ADD COLUMN IF NOT EXISTS products_count INTEGER DEFAULT 0;
ALTER TABLE seller_profiles ADD COLUMN IF NOT EXISTS followers_count INTEGER DEFAULT 0;
ALTER TABLE seller_profiles ADD COLUMN IF NOT EXISTS total_sales INTEGER DEFAULT 0;
ALTER TABLE seller_profiles ADD COLUMN IF NOT EXISTS last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Create followers table to track store followers
CREATE TABLE IF NOT EXISTS store_followers (
    id SERIAL PRIMARY KEY,
    follower_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    store_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    followed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(follower_id, store_id)
);

-- Create product reviews table to track ratings
CREATE TABLE IF NOT EXISTS product_reviews (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    seller_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, user_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_store_followers_store_id ON store_followers(store_id);
CREATE INDEX IF NOT EXISTS idx_store_followers_follower_id ON store_followers(follower_id);
CREATE INDEX IF NOT EXISTS idx_product_reviews_product_id ON product_reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_product_reviews_seller_id ON product_reviews(seller_id);
CREATE INDEX IF NOT EXISTS idx_product_reviews_rating ON product_reviews(rating);

-- Create function to update seller statistics
CREATE OR REPLACE FUNCTION update_seller_statistics(seller_user_id INTEGER)
RETURNS VOID AS $$
BEGIN
    -- Update products count
    UPDATE seller_profiles 
    SET products_count = (
        SELECT COUNT(*) 
        FROM products 
        WHERE seller_id = seller_user_id AND status = 'active'
    )
    WHERE user_id = seller_user_id;
    
    -- Update followers count
    UPDATE seller_profiles 
    SET followers_count = (
        SELECT COUNT(*) 
        FROM store_followers 
        WHERE store_id = seller_user_id
    )
    WHERE user_id = seller_user_id;
    
    -- Update rating count
    UPDATE seller_profiles 
    SET rating_count = (
        SELECT COUNT(*) 
        FROM product_reviews 
        WHERE seller_id = seller_user_id
    )
    WHERE user_id = seller_user_id;
    
    -- Update last active timestamp
    UPDATE seller_profiles 
    SET last_active = CURRENT_TIMESTAMP
    WHERE user_id = seller_user_id;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update statistics when products are added/removed
CREATE OR REPLACE FUNCTION trigger_update_seller_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        PERFORM update_seller_statistics(NEW.seller_id);
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        PERFORM update_seller_statistics(NEW.seller_id);
        IF OLD.seller_id != NEW.seller_id THEN
            PERFORM update_seller_statistics(OLD.seller_id);
        END IF;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        PERFORM update_seller_statistics(OLD.seller_id);
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers
DROP TRIGGER IF EXISTS trigger_product_stats ON products;
CREATE TRIGGER trigger_product_stats
    AFTER INSERT OR UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION trigger_update_seller_stats();

DROP TRIGGER IF EXISTS trigger_follower_stats ON store_followers;
CREATE TRIGGER trigger_follower_stats
    AFTER INSERT OR DELETE ON store_followers
    FOR EACH ROW EXECUTE FUNCTION trigger_update_seller_stats();

DROP TRIGGER IF EXISTS trigger_review_stats ON product_reviews;
CREATE TRIGGER trigger_review_stats
    AFTER INSERT OR UPDATE OR DELETE ON product_reviews
    FOR EACH ROW EXECUTE FUNCTION trigger_update_seller_stats();

-- Initialize statistics for existing sellers
DO $$
DECLARE
    seller_record RECORD;
BEGIN
    FOR seller_record IN SELECT user_id FROM seller_profiles LOOP
        PERFORM update_seller_statistics(seller_record.user_id);
    END LOOP;
END $$;