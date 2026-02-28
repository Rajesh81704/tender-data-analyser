from app.api.dao.dashboard_dao import DashboardDAO

dao = DashboardDAO()

print("=" * 80)
print("Test 1: Get all projects for tndr_pk=11")
print("=" * 80)
result = dao.get_project_stage_summary(11)
print(f"Total records: {len(result)}")
if result:
    print(f"First project: {result[0]['project_name']}")
    print(f"First department: {result[0]['department']}")

print("\n" + "=" * 80)
print("Test 2: Filter by project_name='school'")
print("=" * 80)
result = dao.get_project_stage_summary(11, project_name='school')
print(f"Total records: {len(result)}")
if result:
    for r in result[:3]:  # Show first 3
        print(f"  - {r['project_name']} ({r['department']})")

print("\n" + "=" * 80)
print("Test 3: Filter by department_name='POLYTECHNICS'")
print("=" * 80)
result = dao.get_project_stage_summary(11, department_name='POLYTECHNICS')
print(f"Total records: {len(result)}")
if result:
    for r in result[:3]:  # Show first 3
        print(f"  - {r['project_name']} ({r['department']})")
