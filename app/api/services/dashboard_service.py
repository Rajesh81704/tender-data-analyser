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
    
    def get_department_wise_stats(self, tndr_pk: int, dept_code: str = None):
        """Get department-wise statistics"""
        try:
            data = self.dashboard_dao.get_department_wise_stats(tndr_pk, dept_code)
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

    def get_department_projects(self, tndr_pk: int, dept_code: str = None):
        """Get all project details department-wise"""
        try:
            data = self.dashboard_dao.get_department_projects(tndr_pk, dept_code)
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

    def get_project_stage_summary(self, tndr_pk: int, project_name: str = None, department_name: str = None):
        """Get project stage summary with completion percentage and stage categorization"""
        try:
            data = self.dashboard_dao.get_project_stage_summary(tndr_pk, project_name, department_name)
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

