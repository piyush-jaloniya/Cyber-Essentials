"""
HTML Report Generator for Cyber Essentials Scanner
Generates user-friendly HTML reports with visual status indicators.
"""

import json
import datetime
from typing import Dict, Any

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cyber Essentials Scan Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            line-height: 1.6;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .header .meta {{
            opacity: 0.9;
            font-size: 14px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }}
        .summary-card {{
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .summary-card .label {{
            color: #6c757d;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .status-pass {{ color: #28a745; }}
        .status-warn {{ color: #ffc107; }}
        .status-fail {{ color: #dc3545; }}
        .status-unknown {{ color: #6c757d; }}
        .controls {{
            padding: 30px;
        }}
        .control {{
            margin-bottom: 25px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            overflow: hidden;
        }}
        .control-header {{
            background: #f8f9fa;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            user-select: none;
        }}
        .control-header:hover {{
            background: #e9ecef;
        }}
        .control-name {{
            font-size: 18px;
            font-weight: 600;
        }}
        .control-status {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .status-badge {{
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .status-badge.pass {{
            background: #d4edda;
            color: #155724;
        }}
        .status-badge.warn {{
            background: #fff3cd;
            color: #856404;
        }}
        .status-badge.fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        .status-badge.unknown {{
            background: #e2e3e5;
            color: #383d41;
        }}
        .score {{
            font-weight: bold;
            color: #6c757d;
        }}
        .control-details {{
            padding: 20px;
            display: none;
        }}
        .control.expanded .control-details {{
            display: block;
        }}
        .control.expanded .control-header {{
            border-bottom: 1px solid #dee2e6;
        }}
        .section {{
            margin-bottom: 20px;
        }}
        .section h4 {{
            color: #495057;
            margin-bottom: 10px;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .findings, .recommendations {{
            list-style-type: none;
        }}
        .findings li, .recommendations li {{
            padding: 8px 12px;
            margin-bottom: 5px;
            border-left: 3px solid;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .findings li {{
            border-color: #ffc107;
        }}
        .findings li.pass {{
            border-color: #28a745;
        }}
        .findings li.fail {{
            border-color: #dc3545;
        }}
        .recommendations li {{
            border-color: #17a2b8;
        }}
        .details-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
        }}
        .detail-item {{
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .detail-label {{
            font-weight: 600;
            color: #6c757d;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .detail-value {{
            margin-top: 5px;
            color: #2c3e50;
        }}
        .footer {{
            padding: 20px 30px;
            background: #f8f9fa;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
            border-top: 1px solid #dee2e6;
        }}
        .expand-icon {{
            transition: transform 0.3s;
        }}
        .control.expanded .expand-icon {{
            transform: rotate(180deg);
        }}
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                box-shadow: none;
            }}
            .control-details {{
                display: block !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Cyber Essentials Compliance Report</h1>
            <div class="meta">
                <div>Scanner Version: {scanner_version}</div>
                <div>Generated: {timestamp}</div>
                <div>System: {os_platform} {os_version}</div>
                <div>Compliance Mode: <strong>{compliance_mode}</strong></div>
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <div class="label">Overall Status</div>
                <div class="value status-{overall_status_class}">{overall_status}</div>
            </div>
            <div class="summary-card">
                <div class="label">Compliance Score</div>
                <div class="value">{overall_score}/100</div>
            </div>
            <div class="summary-card">
                <div class="label">Controls Passed</div>
                <div class="value status-pass">{controls_passed}/{total_controls}</div>
            </div>
            <div class="summary-card">
                <div class="label">Critical Issues</div>
                <div class="value status-fail">{controls_failed}</div>
            </div>
        </div>
        
        <div class="controls">
            <h2 style="margin-bottom: 20px;">Control Assessment Details</h2>
            {controls_html}
        </div>
        
        <div class="footer">
            <p>This report was generated by Cyber Essentials Scanner v{scanner_version}</p>
            <p>UK Cyber Essentials v3.2 (2025) "Willow" Compliance Framework</p>
        </div>
    </div>
    
    <script>
        // Toggle control details
        document.querySelectorAll('.control-header').forEach(header => {{
            header.addEventListener('click', () => {{
                header.parentElement.classList.toggle('expanded');
            }});
        }});
        
        // Expand failed controls by default
        document.querySelectorAll('.control').forEach(control => {{
            const status = control.querySelector('.status-badge').textContent.toLowerCase();
            if (status === 'fail' || status === 'warn') {{
                control.classList.add('expanded');
            }}
        }});
    </script>
</body>
</html>
"""

def generate_control_html(control: Dict[str, Any]) -> str:
    """Generate HTML for a single control"""
    name = control.get("name", "Unknown")
    status = control.get("status", "unknown")
    score = control.get("score", 0)
    findings = control.get("findings", [])
    recommendations = control.get("recommendations", [])
    details = control.get("details", {})
    
    # Generate findings HTML
    findings_html = ""
    if findings:
        findings_items = "\n".join([f'<li>{finding}</li>' for finding in findings])
        findings_html = f"""
        <div class="section">
            <h4>📋 Findings</h4>
            <ul class="findings">{findings_items}</ul>
        </div>
        """
    
    # Generate recommendations HTML
    recommendations_html = ""
    if recommendations:
        rec_items = "\n".join([f'<li>{rec}</li>' for rec in recommendations])
        recommendations_html = f"""
        <div class="section">
            <h4>💡 Recommendations</h4>
            <ul class="recommendations">{rec_items}</ul>
        </div>
        """
    
    # Generate details HTML
    details_html = ""
    if details:
        detail_items = ""
        for key, value in details.items():
            if value is not None:
                # Format key: remove underscores, capitalize
                label = key.replace('_', ' ').title()
                # Format value
                if isinstance(value, bool):
                    value_str = "✓ Enabled" if value else "✗ Disabled"
                elif isinstance(value, list):
                    value_str = ", ".join(str(v) for v in value) if value else "None"
                else:
                    value_str = str(value)
                
                detail_items += f"""
                <div class="detail-item">
                    <div class="detail-label">{label}</div>
                    <div class="detail-value">{value_str}</div>
                </div>
                """
        
        if detail_items:
            details_html = f"""
            <div class="section">
                <h4>📊 Technical Details</h4>
                <div class="details-grid">{detail_items}</div>
            </div>
            """
    
    return f"""
    <div class="control">
        <div class="control-header">
            <div class="control-name">{name}</div>
            <div class="control-status">
                <span class="score">{score:.0f}/100</span>
                <span class="status-badge {status}">{status}</span>
                <span class="expand-icon">▼</span>
            </div>
        </div>
        <div class="control-details">
            {findings_html}
            {recommendations_html}
            {details_html}
        </div>
    </div>
    """

def generate_html_report(json_data: Dict[str, Any]) -> str:
    """
    Generate HTML report from JSON scan data.
    
    Args:
        json_data: Parsed JSON scan report
    
    Returns:
        HTML string
    """
    # Extract data
    scanner_version = json_data.get("scanner_version", "0.2.0")
    timestamp_utc = json_data.get("timestamp_utc", "")
    compliance_mode = json_data.get("compliance_mode", "standard").title()
    os_info = json_data.get("os", {})
    os_platform = os_info.get("platform", "Unknown")
    os_version = os_info.get("version", "")
    controls = json_data.get("controls", [])
    overall = json_data.get("overall", {})
    overall_status = overall.get("status", "unknown").upper()
    overall_score = overall.get("score", 0)
    
    # Calculate statistics
    total_controls = len(controls)
    controls_passed = sum(1 for c in controls if c.get("status") == "pass")
    controls_failed = sum(1 for c in controls if c.get("status") == "fail")
    
    # Map status to CSS class
    status_class_map = {
        "PASS": "pass",
        "WARN": "warn",
        "FAIL": "fail",
        "UNKNOWN": "unknown"
    }
    overall_status_class = status_class_map.get(overall_status, "unknown")
    
    # Format timestamp
    try:
        dt = datetime.datetime.fromisoformat(timestamp_utc.replace('Z', '+00:00'))
        timestamp = dt.strftime("%B %d, %Y at %H:%M UTC")
    except:
        timestamp = timestamp_utc
    
    # Generate controls HTML
    controls_html = "\n".join([generate_control_html(control) for control in controls])
    
    # Fill template
    html = HTML_TEMPLATE.format(
        scanner_version=scanner_version,
        timestamp=timestamp,
        os_platform=os_platform,
        os_version=os_version,
        compliance_mode=compliance_mode,
        overall_status=overall_status,
        overall_status_class=overall_status_class,
        overall_score=f"{overall_score:.1f}",
        controls_passed=controls_passed,
        total_controls=total_controls,
        controls_failed=controls_failed,
        controls_html=controls_html
    )
    
    return html

def save_html_report(json_file: str, html_file: str = None) -> str:
    """
    Convert JSON report to HTML and save to file.
    
    Args:
        json_file: Path to JSON report
        html_file: Output HTML file path (optional, auto-generates from json_file if not provided)
    
    Returns:
        Path to generated HTML file
    """
    # Read JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Generate HTML
    html = generate_html_report(json_data)
    
    # Determine output file
    if html_file is None:
        html_file = json_file.replace('.json', '.html')
    
    # Write HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return html_file
