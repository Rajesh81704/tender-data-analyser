from app.api.utils.database import get_db

db = get_db()
conn = db.get_connection()
cursor = conn.cursor()

# Check sample department codes from DEPT_DTLS
print("=== Sample DEPT_DTLS codes ===")
cursor.execute('SELECT "DEPT_SUB_DEPT_CODE", "DEPT_NAME", "SUB_DEPT_NAME" FROM "DEPT_DTLS" WHERE tndr_pk = 14 LIMIT 5')
for row in cursor.fetchall():
    print(f"Code: '{row[0]}', Dept: {row[1]}, Sub: {row[2]}")

print("\n=== Sample TENDER_DATA_DTLS codes ===")
cursor.execute('SELECT DISTINCT "DEPARTMENT_CODE" FROM "TENDER_DATA_DTLS" WHERE tndr_pk = 14 LIMIT 5')
for row in cursor.fetchall():
    print(f"Code: '{row[0]}'")

print("\n=== Check if codes match ===")
cursor.execute('''
    SELECT 
        d."DEPT_SUB_DEPT_CODE",
        COUNT(t."TDM_PK") as matched_projects
    FROM "DEPT_DTLS" d
    LEFT JOIN "TENDER_DATA_DTLS" t 
        ON d.tndr_pk = t.tndr_pk 
        AND d."DEPT_SUB_DEPT_CODE" = t."DEPARTMENT_CODE"
    WHERE d.tndr_pk = 14
    GROUP BY d."DEPT_SUB_DEPT_CODE"
    ORDER BY matched_projects DESC
    LIMIT 10
''')
print("Dept Code -> Project Count:")
for row in cursor.fetchall():
    print(f"  {row[0]} -> {row[1]} projects")

cursor.close()
db.release_connection(conn)
