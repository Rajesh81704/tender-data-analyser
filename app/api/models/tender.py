from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TenderMaster(BaseModel):
    tenderPk: Optional[int] = Field(None, alias="tndr_pk")
    tenderSourceFile: Optional[str] = Field(None, alias="tndr_source_file")
    districtSourceFile: Optional[str] = Field(None, alias="dst_source_file")
    departmentSourceFile: Optional[str] = Field(None, alias="dept_source_file")
    createdDate: Optional[datetime] = Field(None, alias="crt_dt")
    createdUser: Optional[str] = Field(None, alias="crt_user")
    
    class Config:
        populate_by_name = True

class DeptDetails(BaseModel):
    deptDetailsPk: Optional[int] = Field(None, alias="DEPT_DTLS_PK")
    serialNo: Optional[str] = Field(None, alias="SR_NO")
    deptName: Optional[str] = Field(None, alias="DEPT_NAME")
    subDeptName: Optional[str] = Field(None, alias="SUB_DEPT_NAME")
    deptSubDeptCode: Optional[str] = Field(None, alias="DEPT_SUB_DEPT_CODE")
    
    class Config:
        populate_by_name = True

class DistrictDetails(BaseModel):
    districtDetailsPk: Optional[int] = Field(None, alias="DIST_DTLS_PK")
    districtCode: Optional[int] = Field(None, alias="DIST_CODE")
    districtName: Optional[str] = Field(None, alias="DIST_NAME")
    zone: Optional[str] = Field(None, alias="ZONE")
    
    class Config:
        populate_by_name = True

class TenderDataDetails(BaseModel):
    tenderDataPk: Optional[int] = Field(None, alias="TDM_PK")
    districtCode: Optional[int] = Field(None, alias="DISTRICT_CODE")
    workCode: Optional[int] = Field(None, alias="WORK_CODE")
    departmentCode: Optional[str] = Field(None, alias="DEPARTMENT_CODE")
    projectName: Optional[str] = Field(None, alias="PROJECT_NAME")
    sanctionCost: Optional[float] = Field(None, alias="SANCTION_COST")
    sanctionDate: Optional[str] = Field(None, alias="SANCTION_DATE")
    fundReceived: Optional[float] = Field(None, alias="FUND_RECEIVED")
    fundReceivedDate: Optional[str] = Field(None, alias="FUND_RECEIVED_DATE")
    landReceivedDate: Optional[str] = Field(None, alias="LAND_RECEIVED_DATE")
    wipPreviousYear: Optional[float] = Field(None, alias="WIP_PREVIOUS_YEAR")
    wipCurrentYear: Optional[float] = Field(None, alias="WIP_CURRENT_YEAR")
    wipCurrentMonth: Optional[float] = Field(None, alias="WIP_CURRENT_MONTH")
    wipTotal: Optional[float] = Field(None, alias="WIP_TOTAL")
    physicalProgress: Optional[float] = Field(None, alias="PHYSICAL_PROGRESS")
    physicalProgressRemark: Optional[str] = Field(None, alias="PHYSICAL_PROGRESS_REMARK")
    
    class Config:
        populate_by_name = True
