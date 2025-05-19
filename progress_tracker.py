#!/usr/bin/env python3
"""
Progress Tracking System
Tracks user progress through training modules
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import csv

@dataclass
class TaskProgress:
    """Individual task progress"""
    task_id: str
    module_id: str
    user_id: str
    status: str  # not_started, in_progress, completed
    score: Optional[float]
    attempts: int
    started_at: Optional[str]
    completed_at: Optional[str]
    duration_seconds: Optional[int]
    screenshot_path: Optional[str]
    notes: Optional[str]

@dataclass
class ModuleProgress:
    """Module progress summary"""
    module_id: str
    user_id: str
    status: str  # not_started, in_progress, completed
    overall_score: float
    completion_percentage: float
    total_tasks: int
    completed_tasks: int
    started_at: Optional[str]
    completed_at: Optional[str]
    total_duration_seconds: int
    certificate_issued: bool

class ProgressTracker:
    """Manages user progress tracking"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Task progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                module_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                status TEXT NOT NULL,
                score REAL,
                attempts INTEGER DEFAULT 0,
                started_at TEXT,
                completed_at TEXT,
                duration_seconds INTEGER,
                screenshot_path TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(task_id, module_id, user_id)
            )
        ''')
        
        # Module progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                status TEXT NOT NULL,
                overall_score REAL DEFAULT 0,
                completion_percentage REAL DEFAULT 0,
                total_tasks INTEGER DEFAULT 0,
                completed_tasks INTEGER DEFAULT 0,
                started_at TEXT,
                completed_at TEXT,
                total_duration_seconds INTEGER DEFAULT 0,
                certificate_issued BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(module_id, user_id)
            )
        ''')
        
        # Progress milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS progress_milestones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                milestone_type TEXT NOT NULL,
                milestone_value TEXT NOT NULL,
                achieved_at TEXT DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_task(self, task_id: str, module_id: str, user_id: str):
        """Mark a task as started"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO task_progress 
                (task_id, module_id, user_id, status, started_at, attempts)
                VALUES (?, ?, ?, 'in_progress', ?, 
                    COALESCE((SELECT attempts FROM task_progress 
                     WHERE task_id=? AND module_id=? AND user_id=?) + 1, 1))
            ''', (task_id, module_id, user_id, datetime.now().isoformat(),
                  task_id, module_id, user_id))
            
            conn.commit()
            
            # Update module progress
            self._update_module_progress(module_id, user_id, conn)
            
        finally:
            conn.close()
    
    def complete_task(self, task_id: str, module_id: str, user_id: str, 
                     score: float = None, screenshot_path: str = None):
        """Mark a task as completed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get task start time
            cursor.execute('''
                SELECT started_at FROM task_progress 
                WHERE task_id=? AND module_id=? AND user_id=?
            ''', (task_id, module_id, user_id))
            
            result = cursor.fetchone()
            started_at = result[0] if result else datetime.now().isoformat()
            
            # Calculate duration
            start_time = datetime.fromisoformat(started_at)
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds())
            
            # Update task progress
            cursor.execute('''
                UPDATE task_progress 
                SET status='completed', 
                    score=?, 
                    completed_at=?, 
                    duration_seconds=?,
                    screenshot_path=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE task_id=? AND module_id=? AND user_id=?
            ''', (score, end_time.isoformat(), duration, screenshot_path,
                  task_id, module_id, user_id))
            
            conn.commit()
            
            # Update module progress
            self._update_module_progress(module_id, user_id, conn)
            
            # Check for milestones
            self._check_milestones(user_id, conn)
            
        finally:
            conn.close()
    
    def _update_module_progress(self, module_id: str, user_id: str, conn: sqlite3.Connection):
        """Update module progress based on task completions"""
        cursor = conn.cursor()
        
        # Get task statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN status='completed' THEN 1 END) as completed_tasks,
                AVG(CASE WHEN status='completed' THEN score END) as avg_score,
                SUM(CASE WHEN status='completed' THEN duration_seconds ELSE 0 END) as total_duration,
                MIN(started_at) as first_started,
                MAX(completed_at) as last_completed
            FROM task_progress
            WHERE module_id=? AND user_id=?
        ''', (module_id, user_id))
        
        stats = cursor.fetchone()
        total_tasks, completed_tasks, avg_score, total_duration, first_started, last_completed = stats
        
        completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        status = 'completed' if completion_percentage == 100 else 'in_progress'
        
        # Insert or update module progress
        cursor.execute('''
            INSERT OR REPLACE INTO module_progress
            (module_id, user_id, status, overall_score, completion_percentage,
             total_tasks, completed_tasks, started_at, completed_at, total_duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (module_id, user_id, status, avg_score or 0, completion_percentage,
              total_tasks, completed_tasks, first_started, last_completed, total_duration or 0))
        
        conn.commit()
    
    def _check_milestones(self, user_id: str, conn: sqlite3.Connection):
        """Check and record any achieved milestones"""
        cursor = conn.cursor()
        
        # Check for various milestones
        milestones_to_check = [
            ("first_task", "SELECT COUNT(*) FROM task_progress WHERE user_id=? AND status='completed'", 1),
            ("10_tasks", "SELECT COUNT(*) FROM task_progress WHERE user_id=? AND status='completed'", 10),
            ("first_module", "SELECT COUNT(*) FROM module_progress WHERE user_id=? AND status='completed'", 1),
            ("5_modules", "SELECT COUNT(*) FROM module_progress WHERE user_id=? AND status='completed'", 5),
            ("perfect_score", "SELECT COUNT(*) FROM task_progress WHERE user_id=? AND score=100", 1),
        ]
        
        for milestone_type, query, threshold in milestones_to_check:
            cursor.execute(query, (user_id,))
            count = cursor.fetchone()[0]
            
            if count >= threshold:
                # Check if milestone already achieved
                cursor.execute('''
                    SELECT id FROM progress_milestones 
                    WHERE user_id=? AND milestone_type=?
                ''', (user_id, milestone_type))
                
                if not cursor.fetchone():
                    cursor.execute('''
                        INSERT INTO progress_milestones 
                        (user_id, milestone_type, milestone_value, description)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, milestone_type, str(count), 
                          f"Achieved {milestone_type} milestone"))
                    conn.commit()
    
    def get_user_progress(self, user_id: str) -> Dict:
        """Get complete progress report for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get module progress
            cursor.execute('''
                SELECT * FROM module_progress WHERE user_id=?
            ''', (user_id,))
            
            modules = []
            for row in cursor.fetchall():
                modules.append({
                    'module_id': row[1],
                    'status': row[3],
                    'overall_score': row[4],
                    'completion_percentage': row[5],
                    'total_tasks': row[6],
                    'completed_tasks': row[7],
                    'started_at': row[8],
                    'completed_at': row[9],
                    'total_duration_seconds': row[10],
                    'certificate_issued': bool(row[11])
                })
            
            # Get task progress
            cursor.execute('''
                SELECT * FROM task_progress WHERE user_id=?
            ''', (user_id,))
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append({
                    'task_id': row[1],
                    'module_id': row[2],
                    'status': row[4],
                    'score': row[5],
                    'attempts': row[6],
                    'started_at': row[7],
                    'completed_at': row[8],
                    'duration_seconds': row[9],
                    'screenshot_path': row[10]
                })
            
            # Get milestones
            cursor.execute('''
                SELECT * FROM progress_milestones WHERE user_id=?
                ORDER BY achieved_at DESC
            ''', (user_id,))
            
            milestones = []
            for row in cursor.fetchall():
                milestones.append({
                    'milestone_type': row[2],
                    'milestone_value': row[3],
                    'achieved_at': row[4],
                    'description': row[5]
                })
            
            return {
                'user_id': user_id,
                'modules': modules,
                'tasks': tasks,
                'milestones': milestones,
                'statistics': self._calculate_statistics(user_id, cursor)
            }
            
        finally:
            conn.close()
    
    def _calculate_statistics(self, user_id: str, cursor: sqlite3.Cursor) -> Dict:
        """Calculate user statistics"""
        # Total modules and completion
        cursor.execute('''
            SELECT 
                COUNT(*) as total_modules,
                COUNT(CASE WHEN status='completed' THEN 1 END) as completed_modules,
                AVG(completion_percentage) as avg_completion,
                AVG(overall_score) as avg_score,
                SUM(total_duration_seconds) as total_time
            FROM module_progress
            WHERE user_id=?
        ''', (user_id,))
        
        module_stats = cursor.fetchone()
        
        # Total tasks
        cursor.execute('''
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN status='completed' THEN 1 END) as completed_tasks,
                AVG(CASE WHEN status='completed' THEN score END) as avg_task_score,
                MAX(attempts) as max_attempts
            FROM task_progress
            WHERE user_id=?
        ''', (user_id,))
        
        task_stats = cursor.fetchone()
        
        return {
            'total_modules': module_stats[0] or 0,
            'completed_modules': module_stats[1] or 0,
            'average_completion': module_stats[2] or 0,
            'average_score': module_stats[3] or 0,
            'total_time_seconds': module_stats[4] or 0,
            'total_tasks': task_stats[0] or 0,
            'completed_tasks': task_stats[1] or 0,
            'average_task_score': task_stats[2] or 0,
            'max_attempts': task_stats[3] or 0
        }
    
    def export_progress_report(self, user_id: str, format: str = 'json') -> Path:
        """Export progress report in specified format"""
        progress = self.get_user_progress(user_id)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            output_path = Path(f'progress_{user_id}_{timestamp}.json')
            with open(output_path, 'w') as f:
                json.dump(progress, f, indent=2)
                
        elif format == 'csv':
            output_path = Path(f'progress_{user_id}_{timestamp}.csv')
            
            # Export module progress
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Module Progress'])
                writer.writerow(['Module ID', 'Status', 'Score', 'Completion %', 
                               'Tasks Completed', 'Total Tasks', 'Duration (sec)'])
                
                for module in progress['modules']:
                    writer.writerow([
                        module['module_id'],
                        module['status'],
                        module['overall_score'],
                        module['completion_percentage'],
                        module['completed_tasks'],
                        module['total_tasks'],
                        module['total_duration_seconds']
                    ])
                
                writer.writerow([])  # Empty row
                writer.writerow(['Task Progress'])
                writer.writerow(['Task ID', 'Module ID', 'Status', 'Score', 
                               'Attempts', 'Duration (sec)'])
                
                for task in progress['tasks']:
                    writer.writerow([
                        task['task_id'],
                        task['module_id'],
                        task['status'],
                        task['score'],
                        task['attempts'],
                        task['duration_seconds']
                    ])
        
        return output_path

# Example usage
if __name__ == "__main__":
    tracker = ProgressTracker(Path("training_data.db"))
    
    # Start a task
    tracker.start_task("task_1", "network_module", "user_123")
    
    # Complete a task
    tracker.complete_task("task_1", "network_module", "user_123", 
                         score=95.0, screenshot_path="/screenshots/task_1.png")
    
    # Get user progress
    progress = tracker.get_user_progress("user_123")
    print(json.dumps(progress, indent=2))
    
    # Export progress report
    report_path = tracker.export_progress_report("user_123", format='json')
    print(f"Progress report exported to: {report_path}")