with open('app/api/dao/queries.properties', 'r') as f:
    content = f.read()
    
lines = content.split('\n')
for line in lines:
    if 'get_project_stage_summary' in line:
        print("Found query line:")
        print(line)
        print(f"\nCount of %s: {line.count('%s')}")
        print(f"Length: {len(line)}")
        
        # Find all %s positions
        import re
        matches = [(m.start(), m.group()) for m in re.finditer(r'%s', line)]
        print(f"Positions of %s: {matches}")
