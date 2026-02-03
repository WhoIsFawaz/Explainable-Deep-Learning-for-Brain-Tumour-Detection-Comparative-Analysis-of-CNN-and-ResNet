-- ==================================================================================
-- Database Migration: Update images table for 3 explicit image URIs
-- ==================================================================================
-- Run this if you have existing data in the images table
-- This adds the new columns and removes the old gradcam_image_uri column
-- ==================================================================================

USE brain_mri_db;

-- Step 1: Add new columns if they don't exist
ALTER TABLE images 
ADD COLUMN IF NOT EXISTS heatmap_image_uri VARCHAR(500) DEFAULT NULL,
ADD COLUMN IF NOT EXISTS overlay_image_uri VARCHAR(500) DEFAULT NULL;

-- Step 2: Migrate existing data (if gradcam_image_uri was the overlay)
-- This assumes gradcam_image_uri stored the overlay path
UPDATE images 
SET overlay_image_uri = gradcam_image_uri,
    heatmap_image_uri = REPLACE(gradcam_image_uri, '_overlay', '_heatmap'),
    original_image_uri = REPLACE(gradcam_image_uri, '_overlay', '_original')
WHERE overlay_image_uri IS NULL AND gradcam_image_uri IS NOT NULL;

-- Step 3: Drop old column (optional - run after verifying migration)
-- ALTER TABLE images DROP COLUMN gradcam_image_uri;

-- Verifyy
SELECT id, original_image_uri, heatmap_image_uri, overlay_image_uri FROM images LIMIT 5;
