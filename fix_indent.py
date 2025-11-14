#!/usr/bin/env python
"""Fix indentation issues in windows.py"""

with open('scanner/os/windows.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the mfa_status function and fix indentation
fixed_lines = []
in_mfa_function = False
function_start = -1

for i, line in enumerate(lines):
    if 'def mfa_status() -> dict:' in line:
        in_mfa_function = True
        function_start = i
        fixed_lines.append(line)
        continue
    
    if in_mfa_function:
        # Check if we've reached the next function
        if line.startswith('def ') and 'mfa_status' not in line:
            in_mfa_function = False
            fixed_lines.append(line)
            continue
        
        # Fix indentation: remove extra spaces
        if line.startswith('        #') or line.startswith('        ps') or line.startswith('        ngc') or line.startswith('        code') or line.startswith('        hello') or line.startswith('        pin') or line.startswith('        results') or line.startswith('        if ') or line.startswith('            '):
            # Line has 8 or 12 spaces, reduce to 4 or 8
            stripped = line.lstrip()
            if line.startswith('            '):
                # 12 spaces -> 8 spaces
                fixed_lines.append('        ' + stripped)
            else:
                # 8 spaces -> 4 spaces
                fixed_lines.append('    ' + stripped)
        else:
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Write fixed content
with open('scanner/os/windows.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed indentation in windows.py")
