from fastapi import APIRouter, Query, Depends
from app.api.services.dashboard_service import DashboardService

router = APIRouter()

def get_dashboard_service():
    return DashboardService()

@router.get("/stats")
def get_dashboard_stats(
    tndr_id: int,
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get overall dashboard statistics"""
    result = dashboard_service.get_statistics(tndr_id)
    return result

@router.get("/department-wise")
def get_department_wise_stats(
    tndr_id: int = Query(..., description="Tender primary key"),
    dept_code: str = Query(None, description="Optional department code filter"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get department-wise tender statistics with pagination"""
    result = dashboard_service.get_department_wise_stats(tndr_id, dept_code, page, page_size)
    return result

@router.get("/department-projects")
def get_department_projects(
    tndr_id: int = Query(..., description="Tender primary key"),
    dept_code: str = Query(None, description="Optional department code"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get all project details department-wise with pagination"""
    result = dashboard_service.get_department_projects(tndr_id, dept_code, page, page_size)
    return result

@router.get("/fund-flow")
def get_fund_flow(
    tndr_id: int = Query(..., description="Tender primary key"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get fund flow summary - sanctioned, received, utilized amounts"""
    result = dashboard_service.get_fund_flow(tndr_id)
    return result

@router.get("/department-completion-status")
def get_department_completion_status(
    tndr_id: int = Query(..., description="Tender primary key"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get project count grouped by department and completion status"""
    result = dashboard_service.get_department_completion_status(tndr_id)
    return result

@router.get("/project-wise-details")
def get_project_wise_details(
    tndr_id: int = Query(..., description="Tender primary key"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get project-wise details with department, costs, and completion status"""
    result = dashboard_service.get_project_wise_details(tndr_id)
    return result

@router.get("/projects/by-completion")
def get_projects_by_completion(
    tndr_id: int = Query(..., description="Tender primary key"),
    project_name: str = Query(None, description="Filter by project name"),
    dept_code: str = Query(None, description="Filter by department code"),
    page: int = Query(1, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page (max 100)"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get project stage summary with completion percentage and stage categorization (Completed, >=75%, >=50%, >=25%, <25%) with pagination"""
    result = dashboard_service.get_project_stage_summary(tndr_id, project_name, dept_code, page, page_size)
    return result

