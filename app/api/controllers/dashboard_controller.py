from fastapi import APIRouter, Query, Depends
from app.api.services.dashboard_service import DashboardService

router = APIRouter()

def get_dashboard_service():
    return DashboardService()

@router.get("/stats")
def get_overview(
    tndr_id: int = Query(..., description="Tender primary key"),
    dept_name: str = Query(None, description="Optional department name filter"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get overall tender stats, optionally filtered by department name"""
    return dashboard_service.get_overview(tndr_id, dept_name)

@router.get("/tender-masters")
def get_all_tender_masters(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get all tender master records"""
    return dashboard_service.get_all_tender_masters()

@router.get("/tender-details-deptwise")
def get_tender_details_deptwise(
    tndr_id: int = Query(..., description="Tender primary key"),
    dept_name: str = Query(None, description="Optional department name filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get tender details department-wise with optional dept_name filter and pagination"""
    return dashboard_service.get_tender_details_deptwise(tndr_id, dept_name, page, page_size)

@router.get("/fund-flow")
def get_fund_flow(
    tndr_id: int = Query(..., description="Tender primary key"),
    dept_name: str = Query(None, description="Optional department name filter"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get fund flow summary - sanctioned, received, utilized amounts, optionally filtered by department"""
    return dashboard_service.get_fund_flow(tndr_id, dept_name)

@router.get("/projects-by-completion")
def get_projects_by_completion(
    tndr_id: int = Query(..., description="Tender primary key"),
    completion: str = Query(None, description="Optional filter: 25, 50, 75, completed"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """Get project details filtered by completion stage. completion: 25, 50, 75, completed. Leave empty for all."""
    return dashboard_service.get_projects_by_completion(tndr_id, completion, page, page_size)
