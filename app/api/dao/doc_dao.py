from app.api.utils.s3_client import s3_client
from app.api.utils.database import get_db
from app.api.utils.query_loader import query_loader
import tempfile
import os
from dbfread import DBF
from datetime import datetime
import pandas as pd
from psycopg2.extras import execute_batch

class DocDAO:
    def __init__(self):
        self.db = get_db()
    
    def upload_to_s3(self, file, object_name: str):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                chunk_size = 8 * 1024 * 1024  
                while chunk := file.file.read(chunk_size):
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            success = s3_client.upload_file(temp_file_path, object_name)
            os.unlink(temp_file_path)
            return success

        except Exception as e:
            print(f"Error in upload_to_s3: {e}")
            return False
    
    def create_master_record(self, master_records: dict):
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            insert_query = query_loader.get_query("query.tender.insert_tender_main")
            cursor.execute(insert_query, (
                master_records.get("tender"),
                master_records.get("district"),
                master_records.get("department"),
                datetime.now(),
                master_records.get("created_by")
            ))
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            return result[0] if result else None
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error in create_master_record: {e}")
            return None
        finally:
            if conn:
                self.db.release_connection(conn)

    def bulk_insert_tender(self, df, tndr_pk):
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            insert_query = query_loader.get_query("query.tender.insert_tender_dtls")
            
            print(f"DEBUG: DataFrame shape: {df.shape}")
            print(f"DEBUG: DataFrame columns: {df.columns.tolist()}")
            print(f"DEBUG: First row sample: {df.head(1).to_dict('records') if not df.empty else 'Empty'}")
            print(f"DEBUG: Insert query: {insert_query}")
            
            # Replace NaT and NaN with None
            df = df.replace({pd.NaT: None, float('nan'): None})
            
            # Calculate Physical Progress and prepare rows
            rows = []
            for row in df.itertuples(index=False, name=None):
                row_list = list(row)
                sanction_cost = row_list[4]
                wip_total = row_list[11]
                
                if sanction_cost and sanction_cost > 0 and wip_total is not None:
                    physical_progress = round((wip_total / sanction_cost) * 100, 2)
                else:
                    physical_progress = None
                final_row = [tndr_pk] + row_list[:-1] + [physical_progress, row_list[-1]]
                rows.append(final_row)
            
            print(f"DEBUG: Number of rows to insert: {len(rows)}")
            if rows:
                print(f"DEBUG: First row sample (cleaned): {rows[0]}")
            
            execute_batch(cursor, insert_query, rows, page_size=100)
            
            conn.commit()
            cursor.close()
            return len(rows)
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error in bulk_insert_tender: {e}")
            import traceback
            traceback.print_exc()
            return 0
        finally:
            if conn:
                self.db.release_connection(conn)

    def bulk_insert_district(self, df, tndr_pk):
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            insert_query = query_loader.get_query("query.tender.insert_district_dtls")

            print(f"DEBUG District: DataFrame shape: {df.shape}")
            print(f"DEBUG District: DataFrame columns: {df.columns.tolist()}")

            # Replace NaT and NaN with None
            df = df.replace({pd.NaT: None, float('nan'): None})

            # Add tndr_pk as first column to each row
            rows = [[tndr_pk] + list(row) for row in df.itertuples(index=False, name=None)]
            print(f"DEBUG District: Number of rows to insert: {len(rows)}")

            execute_batch(cursor, insert_query, rows, page_size=100)

            conn.commit()
            cursor.close()
            return len(rows)
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error in bulk_insert_district: {e}")
            import traceback
            traceback.print_exc()
            return 0
        finally:
            if conn:
                self.db.release_connection(conn)

    
    def bulk_insert_dept(self, df, tndr_pk):
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            insert_query = query_loader.get_query("query.tender.insert_dept_dtls")

            # Replace NaT and NaN with None
            df = df.replace({pd.NaT: None, float('nan'): None})

            # Add tndr_pk as first column to each row
            rows = [[tndr_pk] + list(row) for row in df.itertuples(index=False, name=None)]
            execute_batch(cursor, insert_query, rows, page_size=100)

            conn.commit()
            cursor.close()
            return len(rows)
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error in bulk_insert_dept: {e}")
            import traceback
            traceback.print_exc()
            return 0
        finally:
            if conn:
                self.db.release_connection(conn)


