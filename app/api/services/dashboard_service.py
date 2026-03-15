from app.api.utils.database import get_db
from decimal import Decimal


def decimal_to_float(obj):
    if isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    if isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return float(obj)
    return obj


class DashboardService:
    def __init__(self):
        self.db = get_db()

    def get_overview(self, tndr_pk: int, dept_name: str = None):
        dept_join = ""
        dept_filter = ""
        if dept_name:
            dept_join = f"""
            INNER JOIN "DEPT_DTLS" d
                ON t.tndr_pk = d.tndr_pk
                AND t."DEPARTMENT_CODE" = d."DEPT_SUB_DEPT_CODE"
            """
            dept_filter = f"AND d.\"DEPT_NAME\" ILIKE '%{dept_name}%'"

        query = f"""
        WITH calc AS (
            SELECT
                t."SANCTION_COST",
                t."FUND_RECEIVED",
                t."WIP_PREVIOUS_YEAR",
                t."WIP_CURRENT_YEAR",
                t."WIP_CURRENT_MONTH",
                t."WIP_TOTAL",
                t."DEPARTMENT_CODE",
                t."DISTRICT_CODE",
                ROUND(COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0)::numeric, 2) AS physical_progress
            FROM "TENDER_DATA_DTLS" t
            {dept_join}
            WHERE t.tndr_pk = {tndr_pk}
            {dept_filter}
        )
        SELECT
            COUNT(*) AS total_projects,
            COUNT(DISTINCT "DEPARTMENT_CODE") AS total_departments,
            COUNT(DISTINCT "DISTRICT_CODE") AS total_districts,
            ROUND(COALESCE(SUM("SANCTION_COST"), 0)::numeric / 100, 3) AS total_sanction_cost,
            ROUND(COALESCE(SUM("FUND_RECEIVED"), 0)::numeric / 100, 3) AS total_fund_received,
            ROUND((COALESCE(SUM("SANCTION_COST"), 0) - COALESCE(SUM("FUND_RECEIVED"), 0))::numeric / 100, 3) AS total_fund_pending,
            ROUND((COALESCE(SUM("FUND_RECEIVED"), 0) - COALESCE(SUM("WIP_TOTAL"), 0))::numeric / 100, 3) AS total_fund_pending_to_utilize,
            ROUND(COALESCE(SUM("WIP_TOTAL"), 0)::numeric / 100, 3) AS total_fund_utilized,
            ROUND(COALESCE(SUM("WIP_PREVIOUS_YEAR"), 0)::numeric / 100, 3) AS total_wip_previous_year,
            ROUND(COALESCE(SUM("WIP_CURRENT_YEAR"), 0)::numeric / 100, 3) AS total_wip_current_year,
            ROUND(COALESCE(SUM("WIP_CURRENT_MONTH"), 0)::numeric / 100, 3) AS total_wip_current_month,
            ROUND(COALESCE(SUM("WIP_TOTAL") / NULLIF(SUM("SANCTION_COST"), 0), 0)::numeric * 100, 2) AS overall_physical_progress,
            COUNT(*) FILTER (WHERE physical_progress < 25) AS below_25,
            COUNT(*) FILTER (WHERE physical_progress >= 25 AND physical_progress < 50) AS between_25_50,
            COUNT(*) FILTER (WHERE physical_progress >= 50 AND physical_progress < 75) AS between_50_75,
            COUNT(*) FILTER (WHERE physical_progress >= 75 AND physical_progress < 100) AS between_75_100,
            COUNT(*) FILTER (WHERE physical_progress >= 100) AS completed
        FROM calc
        """
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            if not row:
                return {"success": False, "error": "No data found"}
            return {"success": True, "data": decimal_to_float(dict(zip(columns, row)))}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_tender_details_deptwise(self, tndr_pk: int, dept_name: str = None, page: int = 1, page_size: int = 10):
        where = f'WHERE d.tndr_pk = {tndr_pk} AND t.tndr_pk = {tndr_pk}'
        if dept_name:
            where += f" AND d.\"DEPT_NAME\" ILIKE '%{dept_name}%'"

        offset = (page - 1) * page_size

        count_query = f"""
        SELECT COUNT(*)
        FROM "DEPT_DTLS" d
        INNER JOIN "TENDER_DATA_DTLS" t
            ON d.tndr_pk = t.tndr_pk
            AND d."DEPT_SUB_DEPT_CODE" = t."DEPARTMENT_CODE"
        {where}
        """

        query = f"""
        SELECT
            d."DEPT_SUB_DEPT_CODE" AS dept_code,
            d."DEPT_NAME" AS dept_name,
            d."SUB_DEPT_NAME" AS sub_dept_name,
            t."TDM_PK" AS tdm_pk,
            t."WORK_CODE" AS work_code,
            t."PROJECT_NAME" AS project_name,
            t."DISTRICT_CODE" AS district_code,
            dist."DIST_NAME" AS district_name,
            ROUND(COALESCE(t."SANCTION_COST", 0)::numeric / 100, 3) AS sanction_cost,
            t."SANCTION_DATE" AS sanction_date,
            ROUND(COALESCE(t."FUND_RECEIVED", 0)::numeric / 100, 3) AS fund_received,
            t."FUND_RECEIVED_DATE" AS fund_received_date,
            t."LAND_RECEIVED_DATE" AS land_received_date,
            t."WIP_PREVIOUS_YEAR" AS wip_previous_year,
            t."WIP_CURRENT_YEAR" AS wip_current_year,
            t."WIP_CURRENT_MONTH" AS wip_current_month,
            t."WIP_TOTAL" AS wip_total,
            t."PHYSICAL_PROGRESS" AS physical_progress,
            t."PHYSICAL_PROGRESS_REMARK" AS physical_progress_remark
        FROM "DEPT_DTLS" d
        INNER JOIN "TENDER_DATA_DTLS" t
            ON d.tndr_pk = t.tndr_pk
            AND d."DEPT_SUB_DEPT_CODE" = t."DEPARTMENT_CODE"
        LEFT JOIN "DISTRICT_DETAILS" dist
            ON t."DISTRICT_CODE" = dist."DIST_CODE"
            AND dist.tndr_pk = {tndr_pk}
        {where}
        ORDER BY d."DEPT_NAME", t."PROJECT_NAME"
        LIMIT {page_size} OFFSET {offset}
        """

        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute(count_query)
            total = cursor.fetchone()[0]

            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()

            return {
                "success": True,
                "data": decimal_to_float([dict(zip(columns, row)) for row in rows]),
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size
                }
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_fund_flow(self, tndr_pk: int, dept_name: str = None):
        dept_join = ""
        dept_filter = ""
        if dept_name:
            dept_join = f"""
            INNER JOIN "DEPT_DTLS" d
                ON t.tndr_pk = d.tndr_pk
                AND t."DEPARTMENT_CODE" = d."DEPT_SUB_DEPT_CODE"
            """
            dept_filter = f"AND d.\"DEPT_NAME\" ILIKE '%{dept_name}%'"

        query = f"""
        SELECT
            ROUND(COALESCE(SUM(NULLIF(t."SANCTION_COST", 'NaN'::float)), 0)::numeric, 2) AS sanctioned,
            ROUND(COALESCE(SUM(NULLIF(t."FUND_RECEIVED", 'NaN'::float)), 0)::numeric, 2) AS received,
            ROUND(COALESCE(SUM(NULLIF(t."WIP_PREVIOUS_YEAR", 'NaN'::float)), 0)::numeric, 2) AS utilized_previous,
            ROUND(COALESCE(SUM(NULLIF(t."WIP_CURRENT_YEAR", 'NaN'::float)), 0)::numeric, 2) AS utilized_current,
            ROUND(COALESCE(SUM(NULLIF(t."WIP_TOTAL", 'NaN'::float)), 0)::numeric, 2) AS total_utilized,
            ROUND((COALESCE(SUM(NULLIF(t."SANCTION_COST", 'NaN'::float)), 0) - COALESCE(SUM(NULLIF(t."FUND_RECEIVED", 'NaN'::float)), 0))::numeric, 2) AS amount_to_be_received,
            ROUND((COALESCE(SUM(NULLIF(t."FUND_RECEIVED", 'NaN'::float)), 0) - COALESCE(SUM(NULLIF(t."WIP_TOTAL", 'NaN'::float)), 0))::numeric, 2) AS amount_to_be_utilized
        FROM "TENDER_DATA_DTLS" t
        {dept_join}
        WHERE t.tndr_pk = {tndr_pk}
        {dept_filter}
        """

        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            row = cursor.fetchone()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            if not row:
                return {"success": False, "error": "No data found"}
            return {"success": True, "data": decimal_to_float(dict(zip(columns, row)))}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_all_tender_masters(self):
        query = """
        SELECT
            tndr_pk,
            tndr_source_file,
            dst_source_file,
            dept_source_file,
            crt_dt,
            crt_user
        FROM tender_master
        ORDER BY crt_dt DESC
        """
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return {"success": True, "data": [dict(zip(columns, row)) for row in rows]}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_projects_by_completion(self, tndr_pk: int, completion: str = None, page: int = 1, page_size: int = 10):
        completion_filter = ""
        if completion == "25":
            completion_filter = 'AND COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) < 25'
        elif completion == "50":
            completion_filter = 'AND COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) >= 25 AND COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) < 50'
        elif completion == "75":
            completion_filter = 'AND COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) >= 50 AND COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) < 75'
        elif completion == "100":
            completion_filter = 'AND COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) >= 75 AND COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) < 100'
        elif completion == "completed":
            completion_filter = 'AND COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) >= 100'

        offset = (page - 1) * page_size

        count_query = f"""
        SELECT COUNT(*)
        FROM "TENDER_DATA_DTLS" t
        WHERE t.tndr_pk = {tndr_pk}
        {completion_filter}
        """

        query = f"""
        SELECT
            t."TDM_PK" AS tdm_pk,
            t."WORK_CODE" AS work_code,
            t."DEPARTMENT_CODE" AS department_code,
            t."PROJECT_NAME" AS project_name,
            t."DISTRICT_CODE" AS district_code,
            dist."DIST_NAME" AS district_name,
            t."SANCTION_COST" AS sanction_cost,
            t."SANCTION_DATE" AS sanction_date,
            t."FUND_RECEIVED" AS fund_received,
            t."FUND_RECEIVED_DATE" AS fund_received_date,
            t."LAND_RECEIVED_DATE" AS land_received_date,
            t."WIP_PREVIOUS_YEAR" AS wip_previous_year,
            t."WIP_CURRENT_YEAR" AS wip_current_year,
            t."WIP_CURRENT_MONTH" AS wip_current_month,
            t."WIP_TOTAL" AS wip_total,
            t."PHYSICAL_PROGRESS_REMARK" AS physical_progress_remark,
            ROUND(COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0)::numeric, 2) AS physical_progress,
            CASE
                WHEN COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) < 25 THEN 'Below 25%'
                WHEN COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) < 50 THEN '25-50%'
                WHEN COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) < 75 THEN '50-75%'
                WHEN COALESCE((t."WIP_TOTAL" / NULLIF(t."SANCTION_COST", 0)) * 100, 0) < 100 THEN '75-100%'
                ELSE 'Completed'
            END AS completion_stage
        FROM "TENDER_DATA_DTLS" t
        LEFT JOIN "DISTRICT_DETAILS" dist
            ON t."DISTRICT_CODE" = dist."DIST_CODE"
            AND dist.tndr_pk = {tndr_pk}
        WHERE t.tndr_pk = {tndr_pk}
        {completion_filter}
        ORDER BY t."DEPARTMENT_CODE", t."PROJECT_NAME"
        LIMIT {page_size} OFFSET {offset}
        """

        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(count_query)
            total = cursor.fetchone()[0]
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return {
                "success": True,
                "data": decimal_to_float([dict(zip(columns, row)) for row in rows]),
                "pagination": {
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size
                }
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                self.db.release_connection(conn)

    def get_all_tender_masters(self):
        query = """
        SELECT
            tndr_pk,
            tndr_source_file,
            dst_source_file,
            dept_source_file,
            crt_dt,
            crt_user
        FROM tender_master
        ORDER BY crt_dt DESC
        """
        conn = None
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            cursor.close()
            return {"success": True, "data": [dict(zip(columns, row)) for row in rows]}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            if conn:
                self.db.release_connection(conn)
