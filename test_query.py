from app.api.utils.database import get_db

db = get_db()
conn = db.get_connection()
cursor = conn.cursor()

query = """
SELECT t."PROJECT_NAME" AS project_name, 
       ROUND(COALESCE(NULLIF(t."SANCTION_COST", 'NaN'::float), 0)::NUMERIC, 2) AS sanctioned, 
       ROUND(COALESCE(NULLIF(t."FUND_RECEIVED", 'NaN'::float), 0)::NUMERIC, 3) AS received, 
       d."DEPT_NAME" AS department, 
       COALESCE(t."PHYSICAL_PROGRESS", 0) AS completion_percentage, 
       CASE 
           WHEN COALESCE(t."PHYSICAL_PROGRESS", 0) >= 100 THEN 'Completed' 
           WHEN COALESCE(t."PHYSICAL_PROGRESS", 0) >= 75 THEN '>=75%' 
           WHEN COALESCE(t."PHYSICAL_PROGRESS", 0) >= 50 THEN '>=50%' 
           WHEN COALESCE(t."PHYSICAL_PROGRESS", 0) >= 25 THEN '>=25%' 
           ELSE '<25%' 
       END AS project_stage 
FROM "TENDER_DATA_DTLS" t 
INNER JOIN "DEPT_DTLS" d ON t.tndr_pk = d.tndr_pk AND t."DEPARTMENT_CODE" = d."DEPT_SUB_DEPT_CODE" 
WHERE d."DEPT_NAME" IS NOT NULL AND t.tndr_pk = %s
ORDER BY t."PROJECT_NAME"
"""

print("Executing query with tndr_pk=11...")
cursor.execute(query, (11,))
results = cursor.fetchall()

print(f"Found {len(results)} records")
if len(results) > 0:
    print(f"First record: {results[0]}")
    print(f"Last record: {results[-1]}")
else:
    print("No records found!")
    
    # Let's check if data exists
    print("\nChecking TENDER_DATA_DTLS...")
    cursor.execute('SELECT COUNT(*) FROM "TENDER_DATA_DTLS" WHERE tndr_pk = %s', (11,))
    count = cursor.fetchone()[0]
    print(f"TENDER_DATA_DTLS records with tndr_pk=11: {count}")
    
    print("\nChecking DEPT_DTLS...")
    cursor.execute('SELECT COUNT(*) FROM "DEPT_DTLS" WHERE tndr_pk = %s', (11,))
    count = cursor.fetchone()[0]
    print(f"DEPT_DTLS records with tndr_pk=11: {count}")
    
    print("\nChecking join...")
    cursor.execute('''
        SELECT COUNT(*) 
        FROM "TENDER_DATA_DTLS" t 
        INNER JOIN "DEPT_DTLS" d ON t.tndr_pk = d.tndr_pk AND t."DEPARTMENT_CODE" = d."DEPT_SUB_DEPT_CODE" 
        WHERE t.tndr_pk = %s
    ''', (11,))
    count = cursor.fetchone()[0]
    print(f"Join result count: {count}")

cursor.close()
db.release_connection(conn)
