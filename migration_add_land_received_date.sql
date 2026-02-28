-- Migration: Add LAND_RECEIVED_DATE column to TENDER_DATA_DTLS table
-- Run this if your database already exists

ALTER TABLE tender."TENDER_DATA_DTLS" 
ADD COLUMN IF NOT EXISTS "LAND_RECEIVED_DATE" varchar NULL;
