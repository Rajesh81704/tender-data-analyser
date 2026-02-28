from app.api.utils.database import get_db

db = get_db()
conn = db.get_connection()
cursor = conn.cursor()

query = """
SELECT 
    d."DEPT_SUB_DEPT_CODE",
    d."DEPT_NAME",
    d."SUB_DEPT_NAME",
    COUNT(t."TDM_PK") as total_projects
FROM "DEPT_DTLS" d
LEFT JOIN "TENDER_DATA_DTLS" t 
    ON d.tndr_pk = t.tndr_pk 
    AND d."DEPT_SUB_DEPT_CODE" = t."DEPARTMENT_CODE"
WHERE d.tndr_pk = 14
GROUP BY d."DEPT_SUB_DEPT_CODE", d."DEPT_NAME", d."SUB_DEPT_NAME"
LIMIT 5
"""

cursor.execute(query)
results = cursor.fetchall()

for row in results:
    print(f"Dept: {row[0]}, Name: {row[1]}, Sub: {row[2]}, Projects: {row[3]}")

cursor.close()
db.release_connection(conn)
