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

    def get_department_wise_stats(self, tndr_pk: int, dept_code: str = None, page: int = 1, page_size: int = 10):
        """Get department-wise statistics for a specific tender with pagination"""
        cache_key = f"dashboard:dept_stats:{tndr_pk}:{dept_code or 'all'}:{page}:{page_size}"
        
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Build query with all tender fields aggregated per department
            query = f"""
            SELECT 
                d."DEPT_SUB_DEPT_CODE",
                d."DEPT_NAME",
                d."SUB_DEPT_NAME",
                COUNT(t."TDM_PK") as total_projects,
                round(COALESCE(SUM(t."SANCTION_COST"), 0)::numeric/100, 3) as total_sanction_cost,
                round(COALESCE(SUM(t."FUND_RECEIVED"), 0)::numeric/100, 3) as total_fund_received,
                round((COALESCE(SUM(t."SANCTION_COST"), 0)::numeric - COALESCE(SUM(t."FUND_RECEIVED"), 0)::numeric)::numeric, 3) as total_fund_pending,
                round((COALESCE(SUM(t."FUND_RECEIVED"), 0)::numeric - COALESCE(SUM(t."WIP_TOTAL"), 0)::numeric)::numeric, 3) as total_fund_pending_to_utilize,
                round(COALESCE(SUM(t."WIP_PREVIOUS_YEAR"), 0)::numeric/100, 3) as total_wip_previous_year,
                round(COALESCE(SUM(t."WIP_CURRENT_YEAR"), 0)::numeric/100, 3) as total_wip_current_year,
                round(COALESCE(SUM(t."WIP_CURRENT_MONTH"), 0)::numeric/100, 3) as total_wip_current_month,
                round(COALESCE(SUM(t."WIP_TOTAL"), 0)::numeric/100, 3) as total_wip_total,
                round(COALESCE(AVG(t."PHYSICAL_PROGRESS"), 0)::numeric, 3) as avg_physical_progress,
                MIN(t."SANCTION_DATE") as earliest_sanction_date,
                MAX(t."SANCTION_DATE") as latest_sanction_date,
                MIN(t."FUND_RECEIVED_DATE") as earliest_fund_received_date,
                MAX(t."FUND_RECEIVED_DATE") as latest_fund_received_date,
                MIN(t."LAND_RECEIVED_DATE") as earliest_land_received_date,
                MAX(t."LAND_RECEIVED_DATE") as latest_land_received_date,
                COUNT(DISTINCT t."DISTRICT_CODE") as total_districts,
                COUNT(DISTINCT t."WORK_CODE") as total_work_codes
            FROM "DEPT_DTLS" d
            LEFT JOIN "TENDER_DATA_DTLS" t 
                ON d.tndr_pk = t.tndr_pk 
                AND d."DEPT_SUB_DEPT_CODE" = t."DEPARTMENT_CODE"
            WHERE d.tndr_pk = {tndr_pk}
            """
            
            if dept_code:
                query += f" AND d.\"DEPT_SUB_DEPT_CODE\" = '{dept_code}'"
            
            group_by = ' GROUP BY d."DEPT_SUB_DEPT_CODE", d."DEPT_NAME", d."SUB_DEPT_NAME"'
            
            # Count total items
            count_query = f"SELECT COUNT(*) FROM ({query}{group_by}) as count_table"
            cursor.execute(count_query)
            total_items = cursor.fetchone()[0]
            
            # Calculate pagination
            total_pages = (total_items + page_size - 1) // page_size
            offset = (page - 1) * page_size
            
            # Build final query with pagination
            query += group_by
            query += f' LIMIT {page_size} OFFSET {offset}'
            
            cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            
            columns = [
                'dept_code', 'dept_name', 'sub_dept_name', 'total_projects',
                'total_sanction_cost', 'total_fund_received', 'total_fund_pending',
                'total_fund_pending_to_utilize', 'total_wip_previous_year',
                'total_wip_current_year', 'total_wip_current_month', 'total_wip_total',
                'avg_physical_progress', 'earliest_sanction_date', 'latest_sanction_date',
                'earliest_fund_received_date', 'latest_fund_received_date',
                'earliest_land_received_date', 'latest_land_received_date',
                'total_districts', 'total_work_codes'
            ]
            
            items = [dict(zip(columns, row)) for row in results]
            
            # Convert Decimal to float before caching
            items = decimal_to_float(items)
            
            response = {
                "items": items,
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages
            }
            
            # Cache the result
            redis_client.set(cache_key, json.dumps(response, default=str), ex=self.cache_ttl)
            
            return response
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "items": [],
                "page": page,
                "page_size": page_size,
                "total_items": 0,
                "total_pages": 0
            }
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_department_projects(self, tndr_pk: int, dept_code: str = None, page: int = 1, page_size: int = 10):
        """Get all project details department-wise with pagination"""
        cache_key = f"dashboard:dept_projects:{tndr_pk}:{dept_code or 'all'}:{page}:{page_size}"
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Get base query from properties file
            base_query = query_loader.get_query("query.dashboard.get_dept_projects")
            
            # Build WHERE clause with direct parameter insertion
            where_clause = f' WHERE mst.tndr_pk = {tndr_pk} AND d.tndr_pk = {tndr_pk} AND dist.tndr_pk = {tndr_pk}'
            
            if dept_code:
                where_clause += f" AND d.\"DEPT_SUB_DEPT_CODE\" = '{dept_code}'"
            
            # Count total items
            count_query = f"SELECT COUNT(*) FROM ({base_query}{where_clause}) as count_table"
            cursor.execute(count_query)
            total_items = cursor.fetchone()[0]
            
            # Calculate pagination
            total_pages = (total_items + page_size - 1) // page_size
            offset = (page - 1) * page_size
            
            # Build final query with pagination
            query = base_query + where_clause
            query += ' ORDER BY d."DEPT_SUB_DEPT_CODE", t."PROJECT_NAME"'
            query += f' LIMIT {page_size} OFFSET {offset}'
            
            cursor.execute(query)
            
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
            
            items = [dict(zip(columns, row)) for row in results]
            
            # Convert Decimal to float before caching
            items = decimal_to_float(items)
            
            response = {
                "items": items,
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages
            }
            
            # Cache the result (use default=str for dates)
            redis_client.set(cache_key, json.dumps(response, default=str), ex=self.cache_ttl)
            
            return response
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "items": [],
                "page": page,
                "page_size": page_size,
                "total_items": 0,
                "total_pages": 0
            }
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
            
            # Get base query from properties file
            query = query_loader.get_query("query.dashboard.get_dept_completion_status")
            
            # Build WHERE clause with direct parameter insertion
            query += f' WHERE d."DEPT_NAME" IS NOT NULL AND t.tndr_pk = {tndr_pk}'
            query += ' GROUP BY d."DEPT_NAME", t."PHYSICAL_PROGRESS_REMARK", t."PHYSICAL_PROGRESS"'
            query += ' ORDER BY d."DEPT_NAME", t."PHYSICAL_PROGRESS_REMARK"'
            
            cursor.execute(query)
            
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

    def get_project_stage_summary(self, tndr_pk: int, project_name: str = None, dept_code: str = None, page: int = 1, page_size: int = 10):
        """Get project stage summary with completion percentage and stage categorization with pagination"""
        cache_key = f"dashboard:project_stage:{tndr_pk}:{project_name or 'all'}:{dept_code or 'all'}:{page}:{page_size}"
        
        # Try cache first
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            # Build query with dept_code and dept_name included
            query = f"""
            SELECT 
                t."PROJECT_NAME" AS project_name,
                ROUND(COALESCE(SUM(NULLIF(t."SANCTION_COST", 'NaN'::float)), 0)::NUMERIC, 2) AS sanctioned,
                ROUND(COALESCE(SUM(NULLIF(t."FUND_RECEIVED", 'NaN'::float)), 0)::NUMERIC, 3) AS received,
                d."DEPT_SUB_DEPT_CODE" AS dept_code,
                d."DEPT_NAME" AS dept_name,
                COALESCE(t."PHYSICAL_PROGRESS", 0) AS completion_percentage,
                CASE 
                    WHEN COALESCE(t."PHYSICAL_PROGRESS", 0) >= 100 THEN 'Completed'
                    WHEN COALESCE(t."PHYSICAL_PROGRESS", 0) >= 75 THEN '>=75%'
                    WHEN COALESCE(t."PHYSICAL_PROGRESS", 0) >= 50 THEN '>=50%'
                    WHEN COALESCE(t."PHYSICAL_PROGRESS", 0) >= 25 THEN '>=25%'
                    ELSE '<25%'
                END AS project_stage
            FROM "TENDER_DATA_DTLS" t
            INNER JOIN "DEPT_DTLS" d 
                ON t.tndr_pk = d.tndr_pk 
                AND t."DEPARTMENT_CODE" = d."DEPT_SUB_DEPT_CODE"
            WHERE d."DEPT_NAME" IS NOT NULL 
                AND t.tndr_pk = {tndr_pk}
            """
            
            if project_name:
                query += f' AND t."PROJECT_NAME" ILIKE \'%{project_name}%\''
            
            if dept_code:
                query += f' AND d."DEPT_SUB_DEPT_CODE" = \'{dept_code}\''
            
            group_by = ' GROUP BY t."PROJECT_NAME", d."DEPT_SUB_DEPT_CODE", d."DEPT_NAME", t."PHYSICAL_PROGRESS"'
            
            # Count total items
            count_query = f"SELECT COUNT(*) FROM ({query}{group_by}) as count_table"
            cursor.execute(count_query)
            total_items = cursor.fetchone()[0]
            
            # Calculate pagination
            total_pages = (total_items + page_size - 1) // page_size
            offset = (page - 1) * page_size
            
            # Build final query with pagination
            query += group_by
            query += ' ORDER BY completion_percentage DESC'
            query += f' LIMIT {page_size} OFFSET {offset}'
            
            cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            
            columns = ['project_name', 'sanctioned', 'received', 'dept_code', 'dept_name',
                      'completion_percentage', 'project_stage']
            
            items = [dict(zip(columns, row)) for row in results]
            
            # Convert Decimal to float before caching
            items = decimal_to_float(items)
            
            response = {
                "items": items,
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages
            }
            
            # Cache the result
            redis_client.set(cache_key, json.dumps(response), ex=self.cache_ttl)
            
            return response
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "items": [],
                "page": page,
                "page_size": page_size,
                "total_items": 0,
                "total_pages": 0
            }
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

    def get_department_completion_summary(self, tndr_pk: int, page: int = 1, page_size: int = 10):
        """Get department-wise project count by completion stages with all project details"""
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Calculate offset
            offset = (page - 1) * page_size

            # Count query
            count_query = f"""
            SELECT COUNT(*)
            FROM "TENDER_DATA_DTLS" t
            WHERE t.tndr_pk = {tndr_pk}
            """

            cursor.execute(count_query)
            total_count = cursor.fetchone()[0]

            # Data query with pagination
            query = f"""
            SELECT
                t."TDM_PK",
                t."DISTRICT_CODE",
                t."WORK_CODE",
                t."DEPARTMENT_CODE",
                t."PROJECT_NAME",
                t."SANCTION_COST",
                t."SANCTION_DATE",
                t."FUND_RECEIVED",
                t."FUND_RECEIVED_DATE",
                t."WIP_PREVIOUS_YEAR",
                t."WIP_CURRENT_YEAR",
                t."WIP_CURRENT_MONTH",
                t."WIP_TOTAL",
                t."LAND_RECEIVED_DATE",
                ROUND(COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0)::numeric, 2) AS completion_percentage,
                CASE
                    WHEN (t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100 < 25 THEN 'Below 25%'
                    WHEN (t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100 < 50 THEN '25–50%'
                    WHEN (t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100 < 75 THEN '50–75%'
                    WHEN (t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100 < 100 THEN '75–100%'
                    ELSE 'Completed'
                END AS progress_category
            FROM "TENDER_DATA_DTLS" t
            WHERE t.tndr_pk = {tndr_pk}
            ORDER BY t."DEPARTMENT_CODE", t."PROJECT_NAME"
            LIMIT {page_size} OFFSET {offset}
            """

            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            columns = ['tdm_pk', 'district_code', 'work_code', 'department_code', 'project_name',
                      'sanction_cost', 'sanction_date', 'fund_received', 'fund_received_date',
                      'wip_previous_year', 'wip_current_year', 'wip_current_month', 'wip_total',
                      'land_received_date', 'completion_percentage', 'progress_category']

            data = [dict(zip(columns, row)) for row in results]

            # Convert Decimal to float before returning
            data = decimal_to_float(data)

            return {
                'data': data,
                'pagination': {
                    'total': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size
                }
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {'data': [], 'pagination': {'total': 0, 'page': page, 'page_size': page_size, 'total_pages': 0}}
        finally:
            if conn:
                self.db.release_connection(conn)

