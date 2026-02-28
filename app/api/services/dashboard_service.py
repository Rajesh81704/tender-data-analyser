from app.api.dao.dashboard_dao import DashboardDAO


class DashboardService:
    def __init__(self):
        self.dashboard_dao = DashboardDAO()

    def get_statistics(self, id: int):
        """Get dashboard statistics"""
        try:
            stats = self.dashboard_dao.get_dashboard_stats(id)
            return {
                "success": True,
                "data": stats
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_department_wise_stats(self, tndr_pk: int, dept_code: str = None, page: int = 1, page_size: int = 10):
        """Get department-wise statistics with pagination"""
        try:
            data = self.dashboard_dao.get_department_wise_stats(tndr_pk, dept_code, page, page_size)
            return {
                "success": True,
                "data": data.get("items", []),
                "pagination": {
                    "page": data.get("page", page),
                    "page_size": data.get("page_size", page_size),
                    "total_items": data.get("total_items", 0),
                    "total_pages": data.get("total_pages", 0)
                }
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    def get_department_projects(self, tndr_pk: int, dept_code: str = None, page: int = 1, page_size: int = 10):
        """Get all project details department-wise with pagination"""
        try:
            data = self.dashboard_dao.get_department_projects(tndr_pk, dept_code, page, page_size)
            return {
                "success": True,
                "data": data.get("items", []),
                "pagination": {
                    "page": data.get("page", page),
                    "page_size": data.get("page_size", page_size),
                    "total_items": data.get("total_items", 0),
                    "total_pages": data.get("total_pages", 0)
                }
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    def get_fund_flow(self, tndr_pk: int):
        """Get fund flow summary"""
        try:
            data = self.dashboard_dao.get_fund_flow(tndr_pk)
            return {
                "success": True,
                "data": data
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    def get_department_completion_status(self, tndr_pk: int):
        """Get project count by department and completion status"""
        try:
            data = self.dashboard_dao.get_department_completion_status(tndr_pk)
            return {
                "success": True,
                "data": data
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    def get_project_wise_details(self, tndr_pk: int):
        """Get project-wise details with department, costs, and completion status"""
        try:
            data = self.dashboard_dao.get_project_wise_details(tndr_pk)
            return {
                "success": True,
                "data": data
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    def get_project_stage_summary(self, tndr_pk: int, project_name: str = None, dept_code: str = None, page: int = 1, page_size: int = 10):
        """Get project stage summary with completion percentage and stage categorization with pagination"""
        try:
            data = self.dashboard_dao.get_project_stage_summary(tndr_pk, project_name, dept_code, page, page_size)
            return {
                "success": True,
                "data": data.get("items", []),
                "pagination": {
                    "page": data.get("page", page),
                    "page_size": data.get("page_size", page_size),
                    "total_items": data.get("total_items", 0),
                    "total_pages": data.get("total_pages", 0)
                }
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    def get_all_tender_masters(self):
        """Get all tender master records"""
        try:
            data = self.dashboard_dao.get_all_tender_masters()
            return {
                "success": True,
                "data": data
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    def get_department_completion_summary(self, tndr_pk: int, page: int = 1, page_size: int = 10):
        """Get department-wise project count by completion stages with pagination"""
        try:
            result = self.dashboard_dao.get_department_completion_summary(tndr_pk, page, page_size)
            return {
                "success": True,
                "data": result.get("data", []),
                "pagination": result.get("pagination", {})
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

