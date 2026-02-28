-- Fix the schema to add proper foreign key columns

-- Drop existing foreign key constraints
ALTER TABLE "TENDER_DATA_DTLS" DROP CONSTRAINT IF EXISTS tndr_fk;
ALTER TABLE "DISTRICT_DETAILS" DROP CONSTRAINT IF EXISTS dist_dtls_fk;
ALTER TABLE "DEPT_DTLS" DROP CONSTRAINT IF EXISTS dept_dtls_fk;

-- Add LAND_RECEIVED_DATE column to TENDER_DATA_DTLS if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='TENDER_DATA_DTLS' AND column_name='LAND_RECEIVED_DATE') THEN
        ALTER TABLE "TENDER_DATA_DTLS" ADD COLUMN "LAND_RECEIVED_DATE" varchar;
    END IF;
END $$;

-- Add tndr_pk column to TENDER_DATA_DTLS if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='TENDER_DATA_DTLS' AND column_name='tndr_pk') THEN
        ALTER TABLE "TENDER_DATA_DTLS" ADD COLUMN tndr_pk bigint;
    END IF;
END $$;

-- Add tndr_pk column to DISTRICT_DETAILS if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='DISTRICT_DETAILS' AND column_name='tndr_pk') THEN
        ALTER TABLE "DISTRICT_DETAILS" ADD COLUMN tndr_pk bigint;
    END IF;
END $$;

-- Add tndr_pk column to DEPT_DTLS if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name='DEPT_DTLS' AND column_name='tndr_pk') THEN
        ALTER TABLE "DEPT_DTLS" ADD COLUMN tndr_pk bigint;
    END IF;
END $$;

-- Add proper foreign key constraints
ALTER TABLE "TENDER_DATA_DTLS" 
    ADD CONSTRAINT tndr_fk FOREIGN KEY (tndr_pk) REFERENCES tender_master(tndr_pk);

ALTER TABLE "DISTRICT_DETAILS" 
    ADD CONSTRAINT dist_dtls_fk FOREIGN KEY (tndr_pk) REFERENCES tender_master(tndr_pk);

ALTER TABLE "DEPT_DTLS" 
    ADD CONSTRAINT dept_dtls_fk FOREIGN KEY (tndr_pk) REFERENCES tender_master(tndr_pk);
