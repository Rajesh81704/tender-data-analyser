from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.api.services.doc_service import DocService
from app.api.services.auth_service import get_current_user
import asyncio

router = APIRouter()

def get_doc_service():
    return DocService()

@router.post("/upload-doc")
async def upload_document(
    tender_file: UploadFile = File(..., description="Tender file (.xls, .xlsx, .dbf)"),
    district_file: UploadFile = File(..., description="District file (.xls, .xlsx, .dbf)"),
    dept_file: UploadFile = File(..., description="Department file (.xls, .xlsx, .dbf)"),
    doc_service: DocService = Depends(get_doc_service)
):
    MAX_FILE_SIZE = 1 * 1024 * 1024 * 1024  
    allowed_extensions = ['.xls', '.xlsx', '.dbf']
    
    files = {
        "tender": tender_file,
        "district": district_file,
        "department": dept_file
    }
    
    # Validate all files
    for file_type, file in files.items():
        file_ext = file.filename[file.filename.rfind('.'):].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"{file_type.capitalize()} file type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"{file_type.capitalize()} file too large. Maximum size is 1GB"
            )
    
    # Upload all files
    results = {}
    for file_type, file in files.items():
        result = doc_service.upload_document(file, file_type)
        if not result:
            raise HTTPException(
                status_code=500, 
                detail=f"{file_type.capitalize()} file upload failed"
            )
        results[file_type] = result
    
    return {
        "message": "All files uploaded successfully",
        "tender": results["tender"],
        "district": results["district"],
        "department": results["department"]
    }


@router.post("/process-all-doc")
async def process_tender_document(
    tender_s3_path: str,
    district_s3_path: str,
    dept_s3_path: str,
    doc_service: DocService = Depends(get_doc_service)
):
    allowed_ext = ('.dbf', '.xls', '.xlsx')
    for path in [tender_s3_path, district_s3_path, dept_s3_path]:
        if not path.lower().endswith(allowed_ext):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format for {path}. Only .dbf, .xls, .xlsx allowed"
            )
    
    username = "system"
    
    # Step 1: Create master record and get tndr_pk
    tndr_pk = doc_service.create_master_record(
        tender_s3_path, district_s3_path, dept_s3_path, username
    )

    if not tndr_pk:
        raise HTTPException(status_code=500, detail="Failed to create master record")
    
    # Step 2: Process all three files with the shared tndr_pk
    try:
        tender_result = doc_service.process_tender_file(tender_s3_path, tndr_pk, username)
        district_result = doc_service.process_district_file(district_s3_path, tndr_pk, username)
        dept_result = doc_service.process_department_file(dept_s3_path, tndr_pk, username)
        
        # Check for errors in results
        for result, name in [(tender_result, "tender"), (district_result, "district"), (dept_result, "department")]:
            if isinstance(result, dict) and result.get("error"):
                raise HTTPException(
                    status_code=500, 
                    detail=f"{name.capitalize()} processing failed: {result.get('error')}"
                )
        
        return {
            "message": "All documents processed successfully",
            "tndr_pk": tndr_pk,
            "tender_result": tender_result,
            "district_result": district_result,
            "department_result": dept_result,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}") 