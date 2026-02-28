"""
Run this script to add database indexes for performance optimization
Usage: python run_indexes.py
"""

from app.api.utils.database import get_db

def add_indexes():
    db = get_db()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    indexes = [
        # Indexes for TENDER_DATA_DTLS table
        'CREATE INDEX IF NOT EXISTS idx_tender_data_tndr_pk ON "TENDER_DATA_DTLS"(tndr_pk)',
        'CREATE INDEX IF NOT EXISTS idx_tender_data_dept_code ON "TENDER_DATA_DTLS"("DEPARTMENT_CODE")',
        'CREATE INDEX IF NOT EXISTS idx_tender_data_district_code ON "TENDER_DATA_DTLS"("DISTRICT_CODE")',
        'CREATE INDEX IF NOT EXISTS idx_tender_data_project_name ON "TENDER_DATA_DTLS"("PROJECT_NAME")',
        'CREATE INDEX IF NOT EXISTS idx_tender_data_physical_progress ON "TENDER_DATA_DTLS"("PHYSICAL_PROGRESS")',
        
        # Indexes for DEPT_DTLS table
        'CREATE INDEX IF NOT EXISTS idx_dept_dtls_tndr_pk ON "DEPT_DTLS"(tndr_pk)',
        'CREATE INDEX IF NOT EXISTS idx_dept_dtls_code ON "DEPT_DTLS"("DEPT_SUB_DEPT_CODE")',
        'CREATE INDEX IF NOT EXISTS idx_dept_dtls_name ON "DEPT_DTLS"("DEPT_NAME")',
        
        # Indexes for DISTRICT_DETAILS table
        'CREATE INDEX IF NOT EXISTS idx_district_tndr_pk ON "DISTRICT_DETAILS"(tndr_pk)',
        'CREATE INDEX IF NOT EXISTS idx_district_code ON "DISTRICT_DETAILS"("DIST_CODE")',
        
        # Composite indexes for common JOIN patterns
        'CREATE INDEX IF NOT EXISTS idx_tender_data_composite ON "TENDER_DATA_DTLS"(tndr_pk, "DEPARTMENT_CODE")',
        'CREATE INDEX IF NOT EXISTS idx_dept_dtls_composite ON "DEPT_DTLS"(tndr_pk, "DEPT_SUB_DEPT_CODE")',
        
        # Index for tender_master
        'CREATE INDEX IF NOT EXISTS idx_tender_master_pk ON tender_master(tndr_pk)',
    ]
    
    print("Adding database indexes for performance optimization...")
    print("=" * 60)
    
    for i, index_sql in enumerate(indexes, 1):
        try:
            print(f"{i}. Executing: {index_sql[:80]}...")
            cursor.execute(index_sql)
            conn.commit()
            print(f"   ✓ Success")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            conn.rollback()
    
    cursor.close()
    db.release_connection(conn)
    
    print("=" * 60)
    print("Index creation completed!")
    print("\nYour API queries should now be much faster.")

if __name__ == "__main__":
    add_indexes()
