from app.api.utils.database import get_db
from app.api.utils.query_loader import query_loader
from app.api.utils.redis_client import redis_client
import json
from decimal import Decimal


def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [decimal_to_float(item) for item in obj]
    return obj


class DashboardDAO:
    def __init__(self):
        self.db = get_db()
        self.cache_ttl = 300  # 5 minutes cache
    
    def get_dashboard_stats(self, tndr_pk: int):
        """Get overall dashboard statistics for a specific tender"""
        cache_key = f"dashboard:stats:{tndr_pk}"
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            query = query_loader.get_query("query.dashboard.get_stats")
            cursor.execute(query, (tndr_pk,))
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                return {}
            
            response = {
                "total_projects": result[0] if result else 0,
                "total_departments": result[1] if result else 0,
                "total_sanction_cost": float(result[2]) if result and result[2] else 0,
                "total_fund_received": float(result[3]) if result and result[3] else 0,
                "total_fund_pending": float(result[4]) if result and result[4] else 0,
                "total_fund_pending_to_utilize": float(result[5]) if result and result[5] else 0,
                "total_fund_utilized": float(round(result[6],3)) if result and result[6] else 0,
                "avg_physical_progress": float(result[7]) if result and result[7] else 0
            }
            
            # Cache the result
            redis_client.set(cache_key, json.dumps(response), ex=self.cache_ttl)
            
            return response
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
        finally:
            if conn:
                self.db.release_connection(conn)
        
                

    def get_department_wise_stats(self, tndr_pk: int, dept_name: str = None):
        """Get department-wise statistics for a specific tender"""
        cache_key = f"dashboard:dept_stats:{tndr_pk}:{dept_name or 'all'}"
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = query_loader.get_query("query.dashboard.get_dept_wise_stats")
            
            if dept_name:
                query += ' AND d."DEPT_NAME" = %s'
                cursor.execute(query, (tndr_pk, dept_name))
            else:
                cursor.execute(query, (tndr_pk,))
            
            results = cursor.fetchall()
            cursor.close()
            
            columns = ['dept_code', 'dept_name', 'sub_dept_name', 'total_projects', 
                      'total_departments', 'total_sanction_cost', 'total_fund_received',
                      'total_fund_pending', 'total_fund_pending_to_utilize', 
                      'total_fund_utilized', 'avg_physical_progress']
            
            data = [dict(zip(columns, row)) for row in results]
            
            # Convert Decimal to float before caching
            data = decimal_to_float(data)
            
            # Cache the result
            redis_client.set(cache_key, json.dumps(data), ex=self.cache_ttl)
            
            return data
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_department_projects(self, tndr_pk: int, dept_code: str = None):
        """Get all project details department-wise"""
        cache_key = f"dashboard:dept_projects:{tndr_pk}:{dept_code or 'all'}"
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = query_loader.get_query("query.dashboard.get_dept_projects")
            
            if dept_code:
                query = query.replace(' ORDER BY', ' AND d."DEPT_NAME" = %s ORDER BY')
                cursor.execute(query, (tndr_pk, tndr_pk, tndr_pk, dept_code))
            else:
                cursor.execute(query, (tndr_pk, tndr_pk, tndr_pk))
            
            results = cursor.fetchall()
            cursor.close()
            
            columns = [
                'tndr_pk', 'tndr_source_file', 'dst_source_file', 'dept_source_file', 
                'created_date', 'created_user',
                'dept_code', 'dept_name', 'sub_dept_name', 'project_id',
                'district_name', 'work_code', 'department_code', 'project_name',
                'sanction_cost', 'sanction_date', 'fund_received', 'fund_received_date',
                'land_received_date', 'wip_previous_year', 'wip_current_year',
                'wip_current_month', 'wip_total', 'physical_progress', 'physical_progress_remark'
            ]
            
            data = [dict(zip(columns, row)) for row in results]
            
            # Convert Decimal to float before caching
            data = decimal_to_float(data)
            
            # Cache the result (use default=str for dates)
            redis_client.set(cache_key, json.dumps(data, default=str), ex=self.cache_ttl)
            
            return data
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_fund_flow(self, tndr_pk: int):
        """Get fund flow summary for a specific tender"""
        cache_key = f"dashboard:fund_flow:{tndr_pk}"
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = query_loader.get_query("query.dashboard.get_fund_flow")
            cursor.execute(query, (tndr_pk,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                return {}
            
            response = {
                "sanctioned": float(result[0]) if result[0] else 0,
                "received": float(result[1]) if result[1] else 0,
                "utilized_previous": float(result[2]) if result[2] else 0,
                "utilized_current": float(result[3]) if result[3] else 0,
                "total_utilized": float(result[4]) if result[4] else 0,
                "amount_to_be_received": float(result[5]) if result[5] else 0,
                "amount_to_be_utilized": float(result[6]) if result[6] else 0
            }
            
            # Cache the result
            redis_client.set(cache_key, json.dumps(response), ex=self.cache_ttl)
            
            return response
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {}
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_department_completion_status(self, tndr_pk: int):
        """Get project count by department and completion status"""
        cache_key = f"dashboard:dept_completion:{tndr_pk}"
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = query_loader.get_query("query.dashboard.get_dept_completion_status")
            cursor.execute(query, (tndr_pk,))
            
            results = cursor.fetchall()
            cursor.close()
            
            columns = ['department', 'status_remark', 'completion_status', 'project_count']
            data = [dict(zip(columns, row)) for row in results]
            
            # Cache the result
            redis_client.set(cache_key, json.dumps(data), ex=self.cache_ttl)
            
            return data
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_project_wise_details(self, tndr_pk: int):
        """Get project-wise details with department, costs, and completion status"""
        cache_key = f"dashboard:project_details:{tndr_pk}"
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = query_loader.get_query("query.dashboard.get_project_wise_details")
            cursor.execute(query, (tndr_pk,))
            
            results = cursor.fetchall()
            cursor.close()
            
            columns = ['work_code', 'work_name', 'department', 'completion_status', 
                      'sanction_cost', 'fund_received', 'total_wip']
            
            data = [dict(zip(columns, row)) for row in results]
            
            # Convert Decimal to float before caching
            data = decimal_to_float(data)
            
            # Cache the result
            redis_client.set(cache_key, json.dumps(data), ex=self.cache_ttl)
            
            return data
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_project_stage_summary(self, tndr_pk: int, project_name: str = None, department_name: str = None):
        """Get project stage summary with completion percentage and stage categorization"""
        cache_key = f"dashboard:project_stage:{tndr_pk}:{project_name or 'all'}:{department_name or 'all'}"
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = query_loader.get_query("query.dashboard.get_project_stage_summary")
            params = [tndr_pk]
            
            if project_name:
                query += ' AND t."PROJECT_NAME" ILIKE %s'
                params.append(f'%{project_name}%')
            elif department_name:
                query += ' AND d."DEPT_NAME" ILIKE %s'
                params.append(f'%{department_name}%')
            
            query += ' GROUP BY t."PROJECT_NAME", d."DEPT_NAME", t."PHYSICAL_PROGRESS" ORDER BY completion_percentage DESC'
            
            cursor.execute(query, tuple(params))
            
            results = cursor.fetchall()
            cursor.close()
            
            columns = ['project_name', 'sanctioned', 'received', 'department', 
                      'completion_percentage', 'project_stage']
            
            data = [dict(zip(columns, row)) for row in results]
            
            # Convert Decimal to float before caching
            data = decimal_to_float(data)
            
            # Cache the result
            redis_client.set(cache_key, json.dumps(data), ex=self.cache_ttl)
            
            return data
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_all_tender_masters(self):
        """Get all tender master records"""
        cache_key = "dashboard:all_tender_masters"
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            query = query_loader.get_query("query.dashboard.get_all_tender_masters")
            cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            
            columns = ['tndr_pk', 'tndr_source_file', 'dst_source_file', 
                      'dept_source_file', 'created_date', 'created_user']
            
            data = [dict(zip(columns, row)) for row in results]
            
            # Convert Decimal to float before caching
            data = decimal_to_float(data)
            
            # Cache the result (use default=str for dates)
            redis_client.set(cache_key, json.dumps(data, default=str), ex=self.cache_ttl)
            
            return data
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return []
        finally:
            if conn:
                self.db.release_connection(conn)
