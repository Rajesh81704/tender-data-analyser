from app.api.dao.doc_dao import DocDAO
from app.api.utils.s3_client import s3_client
import os
import uuid
import tempfile
import pandas as pd
from dbfread import DBF

class DocService:
    def __init__(self):
        self.doc_dao = DocDAO()
    
    def upload_document(self, file, file_type: str):
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"tender/{file_type}/{uuid.uuid4()}{file_extension}"
        
        # Upload to S3
        result = self.doc_dao.upload_to_s3(file, unique_filename)
        
        if result:
            return {
                "success": True,
                "filename": unique_filename,
                "original_filename": file.filename,
                "message": "File uploaded successfully"
            }
        return None

    def create_master_record(self, tender_s3_path, district_s3_path, dept_s3_path, username):
        master_records = {
            "tender": tender_s3_path,
            "district": district_s3_path,
            "department": dept_s3_path,
            "created_by": username
        }
        return self.doc_dao.create_master_record(master_records)

    def process_tender_file(self, s3_path: str, tndr_pk: int, username: str = "system"):
        """Stream file from S3 and process tender data"""
        try:
            print(f"DEBUG Service: Starting tender file processing for {s3_path}")
            file_ext = os.path.splitext(s3_path)[1].lower()
            file_stream = s3_client.get_file_stream(s3_path)
            if not file_stream:
                return {"error": "Failed to stream file from S3"}
            
            df = pd.DataFrame()
            if file_ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_stream)
            elif file_ext == '.dbf':
                with tempfile.NamedTemporaryFile(delete=False, suffix='.dbf') as temp_file:
                    temp_file.write(file_stream.read())
                    temp_file_path = temp_file.name
                try:
                    table = DBF(temp_file_path, load=True)
                    df = pd.DataFrame(iter(table))
                finally:
                    os.unlink(temp_file_path)
            else:
                return {"error": "Unsupported file format"}
            
            print(f"DEBUG Service: DataFrame loaded, shape: {df.shape}")
            print(f"DEBUG Service: Columns: {df.columns.tolist()}")
            
            if df.empty:
                return {"error": "Excel file is empty, no data rows found"}
            
            required_cols = [
                'DST_CD,N,4,0', 'WRK_CD,N,4,0', 'DPT_CD,C,5', 'WRK_NM,C,32',
                'SAN_COST,N,7,2', 'SAN_DT,D', 'F_CL,N,7,2', 'F_CL_DT,D',
                'LND_DT,D', 'WIP_31,N,7,2', 'WIP_1,N,7,2', 'WIP_CM,N,7,2',
                'WIP_CR,N,7,2', 'PHY1,C,15'
            ]
            
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"DEBUG Service: Missing columns: {missing_cols}")
                print(f"DEBUG Service: Available columns: {df.columns.tolist()}")
                return {"error": "Column mismatch", "missing_columns": missing_cols, "available_columns": df.columns.tolist()}
            
            tender_df = df[required_cols]
            print(f"DEBUG Service: Filtered DataFrame shape: {tender_df.shape}")
            
            if tender_df.empty:
                return {"error": "No data after filtering columns"}
            
            print(f"DEBUG Service: Calling DAO with tndr_pk={tndr_pk}")
            
            inserted_count = self.doc_dao.bulk_insert_tender(tender_df, tndr_pk)
            
            return {"message": "Tender file processed", "rows_inserted": inserted_count}
        except Exception as e:
            print(f"DEBUG Service: Exception in process_tender_file: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

    def process_district_file(self, s3_path: str, tndr_pk: int, username: str = "system"):
        """Stream file from S3 and process district data"""
        try:
            file_ext = os.path.splitext(s3_path)[1].lower()
            file_stream = s3_client.get_file_stream(s3_path)
            if not file_stream:
                return {"error": "Failed to stream file from S3"}
            
            df = pd.DataFrame()
            if file_ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_stream)
            elif file_ext == '.dbf':
                with tempfile.NamedTemporaryFile(delete=False, suffix='.dbf') as temp_file:
                    temp_file.write(file_stream.read())
                    temp_file_path = temp_file.name
                try:
                    table = DBF(temp_file_path, load=True)
                    df = pd.DataFrame(iter(table))
                finally:
                    os.unlink(temp_file_path)
            else:
                return {"error": "Unsupported file format"}
            
            required_cols = ['Dst CD', 'Dst _Name', 'zone']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {"error": "Column mismatch", "missing_columns": missing_cols}
            
            district_df = df[required_cols]
            inserted_count = self.doc_dao.bulk_insert_district(district_df, tndr_pk)
            
            return {"message": "District file processed", "rows_inserted": inserted_count}
        except Exception as e:
            return {"error": str(e)}
    
    def process_department_file(self, s3_path: str, tndr_pk: int, username: str = "system"):
        """Stream file from S3 and process department data"""
        try:
            file_ext = os.path.splitext(s3_path)[1].lower()
            file_stream = s3_client.get_file_stream(s3_path)
            if not file_stream:
                return {"error": "Failed to stream file from S3"}
            
            df = pd.DataFrame()
            if file_ext in ['.xls', '.xlsx']:
                df = pd.read_excel(file_stream)
            elif file_ext == '.dbf':
                with tempfile.NamedTemporaryFile(delete=False, suffix='.dbf') as temp_file:
                    temp_file.write(file_stream.read())
                    temp_file_path = temp_file.name
                try:
                    table = DBF(temp_file_path, load=True)
                    df = pd.DataFrame(iter(table))
                finally:
                    os.unlink(temp_file_path)
            else:
                return {"error": "Unsupported file format"}
            
            required_cols = ['Sr.N.', 'Dept. Name', 'Sub. Dept. Name', 'Dept./Sub. Dept.  Code']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                return {"error": "Column mismatch", "missing_columns": missing_cols}
            
            dept_df = df[required_cols]
            inserted_count = self.doc_dao.bulk_insert_dept(dept_df, tndr_pk)
            
            return {"message": "Department file processed", "rows_inserted": inserted_count}
        except Exception as e:
            return {"error": str(e)}