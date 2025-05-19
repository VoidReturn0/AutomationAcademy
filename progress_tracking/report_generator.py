"""Report generation for progress tracking."""

import json
import csv
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import pandas as pd

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate various types of progress reports."""
    
    def __init__(self, db_path: str, output_dir: str = "progress_tracking/reports"):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_user_report(self, user_id: int, format: str = 'json') -> str:
        """Generate a comprehensive report for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user info
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user_data = cursor.fetchone()
            if not user_data:
                raise ValueError(f"User {user_id} not found")
                
            user_columns = [desc[0] for desc in cursor.description]
            user_info = dict(zip(user_columns, user_data))
            
            # Get progress data
            cursor.execute('''
            SELECT p.*, m.name as module_name, m.difficulty
            FROM user_progress p
            JOIN modules m ON p.module_id = m.module_id
            WHERE p.user_id = ?
            ''', (user_id,))
            
            progress_columns = [desc[0] for desc in cursor.description]
            progress_data = [dict(zip(progress_columns, row)) for row in cursor.fetchall()]
            
            # Get certifications
            cursor.execute('''
            SELECT c.*, m.name as module_name
            FROM certifications c
            JOIN modules m ON c.module_id = m.module_id
            WHERE c.user_id = ?
            ''', (user_id,))
            
            cert_columns = [desc[0] for desc in cursor.description]
            certifications = [dict(zip(cert_columns, row)) for row in cursor.fetchall()]
            
            # Get statistics
            cursor.execute('''
            SELECT 
                COUNT(DISTINCT module_id) as modules_started,
                COUNT(DISTINCT CASE WHEN status = 'completed' THEN module_id END) as modules_completed,
                SUM(points_earned) as total_points,
                SUM(time_spent) as total_time
            FROM user_progress
            WHERE user_id = ?
            ''', (user_id,))
            
            stats = cursor.fetchone()
            statistics = {
                'modules_started': stats[0],
                'modules_completed': stats[1],
                'total_points': stats[2] or 0,
                'total_time_hours': (stats[3] or 0) / 3600
            }
            
            # Compile report data
            report_data = {
                'user': user_info,
                'statistics': statistics,
                'progress': progress_data,
                'certifications': certifications,
                'generated_at': datetime.now().isoformat()
            }
            
            # Generate report in requested format
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"user_report_{user_id}_{timestamp}"
            
            if format == 'json':
                return self._save_json_report(report_data, filename)
            elif format == 'csv':
                return self._save_csv_report(report_data, filename)
            elif format == 'pdf':
                return self._save_pdf_report(report_data, filename)
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        finally:
            conn.close()
            
    def _save_json_report(self, data: Dict, filename: str) -> str:
        """Save report as JSON."""
        filepath = self.output_dir / f"{filename}.json"
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
            
        return str(filepath)
        
    def _save_csv_report(self, data: Dict, filename: str) -> str:
        """Save report as CSV files."""
        base_path = self.output_dir / filename
        base_path.mkdir(exist_ok=True)
        
        # Save progress data
        progress_file = base_path / "progress.csv"
        if data['progress']:
            df = pd.DataFrame(data['progress'])
            df.to_csv(progress_file, index=False)
            
        # Save certifications
        cert_file = base_path / "certifications.csv"
        if data['certifications']:
            df = pd.DataFrame(data['certifications'])
            df.to_csv(cert_file, index=False)
            
        # Save summary
        summary_file = base_path / "summary.csv"
        summary_data = [
            {'metric': 'Modules Started', 'value': data['statistics']['modules_started']},
            {'metric': 'Modules Completed', 'value': data['statistics']['modules_completed']},
            {'metric': 'Total Points', 'value': data['statistics']['total_points']},
            {'metric': 'Total Time (hours)', 'value': data['statistics']['total_time_hours']}
        ]
        df = pd.DataFrame(summary_data)
        df.to_csv(summary_file, index=False)
        
        return str(base_path)
        
    def _save_pdf_report(self, data: Dict, filename: str) -> str:
        """Save report as PDF."""
        filepath = self.output_dir / f"{filename}.pdf"
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86C1'),
            spaceAfter=30,
            alignment=1
        )
        
        title = Paragraph(f"Training Progress Report", title_style)
        story.append(title)
        
        # User info
        user_info = data['user']
        user_para = Paragraph(
            f"<b>User:</b> {user_info['username']}<br/>"
            f"<b>Name:</b> {user_info.get('full_name', 'N/A')}<br/>"
            f"<b>Department:</b> {user_info.get('department', 'N/A')}<br/>"
            f"<b>Generated:</b> {data['generated_at'][:10]}",
            styles['Normal']
        )
        story.append(user_para)
        story.append(Paragraph("<br/><br/>", styles['Normal']))
        
        # Statistics
        stats_data = [
            ['Metric', 'Value'],
            ['Modules Started', str(data['statistics']['modules_started'])],
            ['Modules Completed', str(data['statistics']['modules_completed'])],
            ['Total Points', str(data['statistics']['total_points'])],
            ['Total Time', f"{data['statistics']['total_time_hours']:.1f} hours"]
        ]
        
        stats_table = Table(stats_data)
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86C1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("<b>Summary Statistics</b>", styles['Heading2']))
        story.append(stats_table)
        story.append(Paragraph("<br/><br/>", styles['Normal']))
        
        # Progress details
        if data['progress']:
            progress_data = [['Module', 'Status', 'Progress', 'Points']]
            for module in data['progress']:
                progress_data.append([
                    module['module_name'],
                    module['status'],
                    f"{module['progress_percentage']:.1f}%",
                    str(module['points_earned'])
                ])
                
            progress_table = Table(progress_data)
            progress_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86C1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(Paragraph("<b>Module Progress</b>", styles['Heading2']))
            story.append(progress_table)
            
        # Certifications
        if data['certifications']:
            story.append(Paragraph("<br/><br/>", styles['Normal']))
            story.append(Paragraph("<b>Certifications Earned</b>", styles['Heading2']))
            
            cert_data = [['Module', 'Certificate', 'Score', 'Date']]
            for cert in data['certifications']:
                cert_data.append([
                    cert['module_name'],
                    cert['certificate_name'],
                    f"{cert['score']:.1f}%",
                    cert['issued_date'][:10]
                ])
                
            cert_table = Table(cert_data)
            cert_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27AE60')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(cert_table)
            
        doc.build(story)
        return str(filepath)
        
    def generate_module_report(self, module_id: str) -> str:
        """Generate a report for a specific module."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get module info
            cursor.execute('SELECT * FROM modules WHERE module_id = ?', (module_id,))
            module_data = cursor.fetchone()
            if not module_data:
                raise ValueError(f"Module {module_id} not found")
                
            module_columns = [desc[0] for desc in cursor.description]
            module_info = dict(zip(module_columns, module_data))
            
            # Get completion statistics
            cursor.execute('''
            SELECT 
                COUNT(DISTINCT user_id) as total_users,
                COUNT(DISTINCT CASE WHEN status = 'completed' THEN user_id END) as completed_users,
                AVG(progress_percentage) as avg_progress,
                AVG(time_spent) as avg_time
            FROM user_progress
            WHERE module_id = ?
            ''', (module_id,))
            
            stats = cursor.fetchone()
            statistics = {
                'total_users': stats[0],
                'completed_users': stats[1],
                'average_progress': stats[2] or 0,
                'average_time_hours': (stats[3] or 0) / 3600 if stats[3] else 0
            }
            
            # Get task completion rates
            cursor.execute('''
            SELECT 
                mt.task_id,
                mt.name,
                COUNT(tc.user_id) as completions,
                AVG(tc.attempts) as avg_attempts
            FROM module_tasks mt
            LEFT JOIN task_completions tc ON mt.task_id = tc.task_id
            WHERE mt.module_id = ?
            GROUP BY mt.task_id
            ''', (module_id,))
            
            task_columns = [desc[0] for desc in cursor.description]
            tasks = [dict(zip(task_columns, row)) for row in cursor.fetchall()]
            
            report_data = {
                'module': module_info,
                'statistics': statistics,
                'tasks': tasks,
                'generated_at': datetime.now().isoformat()
            }
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"module_report_{module_id}_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
                
            return str(filepath)
            
        finally:
            conn.close()
            
    def generate_department_report(self, department: str) -> str:
        """Generate a report for a specific department."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get department users
            cursor.execute('''
            SELECT id, username, full_name FROM users 
            WHERE department = ?
            ''', (department,))
            
            users = cursor.fetchall()
            if not users:
                raise ValueError(f"No users found in department: {department}")
                
            user_ids = [user[0] for user in users]
            
            # Get overall statistics
            placeholders = ','.join('?' * len(user_ids))
            cursor.execute(f'''
            SELECT 
                COUNT(DISTINCT module_id) as modules_used,
                COUNT(DISTINCT CASE WHEN status = 'completed' THEN module_id END) as modules_completed,
                SUM(points_earned) as total_points,
                AVG(progress_percentage) as avg_progress
            FROM user_progress
            WHERE user_id IN ({placeholders})
            ''', user_ids)
            
            stats = cursor.fetchone()
            
            report_data = {
                'department': department,
                'user_count': len(users),
                'statistics': {
                    'modules_used': stats[0],
                    'modules_completed': stats[1],
                    'total_points': stats[2] or 0,
                    'average_progress': stats[3] or 0
                },
                'users': [{'id': u[0], 'username': u[1], 'full_name': u[2]} for u in users],
                'generated_at': datetime.now().isoformat()
            }
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"department_report_{department}_{timestamp}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
                
            return str(filepath)
            
        finally:
            conn.close()
