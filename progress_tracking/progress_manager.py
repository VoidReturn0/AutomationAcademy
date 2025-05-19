"""Progress tracking and management for training modules."""

import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ProgressManager:
    """Manages user progress tracking for training modules."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ensure_tables_exist()
        
    def ensure_tables_exist(self):
        """Ensure all required tables exist in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Extended user_progress table with more details
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module_id TEXT NOT NULL,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_date TIMESTAMP,
            progress_percentage REAL DEFAULT 0,
            points_earned INTEGER DEFAULT 0,
            status TEXT DEFAULT 'not_started',
            time_spent INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (module_id) REFERENCES modules(module_id),
            UNIQUE(user_id, module_id)
        )
        ''')
        
        # Task completion tracking
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            completed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            points_earned INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 1,
            verification_status TEXT DEFAULT 'pending',
            screenshot_path TEXT,
            notes TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (module_id) REFERENCES modules(module_id),
            UNIQUE(user_id, module_id, task_id)
        )
        ''')
        
        # Session tracking for time spent
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module_id TEXT NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            duration INTEGER DEFAULT 0,
            activity_type TEXT DEFAULT 'learning',
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (module_id) REFERENCES modules(module_id)
        )
        ''')
        
        # Certifications earned
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            module_id TEXT NOT NULL,
            certificate_name TEXT NOT NULL,
            issued_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            score REAL NOT NULL,
            certificate_path TEXT,
            expiry_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (module_id) REFERENCES modules(module_id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def start_module(self, user_id: int, module_id: str) -> bool:
        """Start tracking progress for a module."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO user_progress 
            (user_id, module_id, status, start_date, last_activity)
            VALUES (?, ?, 'in_progress', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ''', (user_id, module_id))
            
            # Start a new session
            cursor.execute('''
            INSERT INTO training_sessions (user_id, module_id, start_time)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (user_id, module_id))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Failed to start module: {e}")
            return False
            
        finally:
            conn.close()
            
    def complete_task(self, user_id: int, module_id: str, task_id: str, 
                     points: int, screenshot_path: str = None) -> bool:
        """Mark a task as completed and update progress."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Record task completion
            cursor.execute('''
            INSERT OR REPLACE INTO task_completions 
            (user_id, module_id, task_id, points_earned, screenshot_path, verification_status)
            VALUES (?, ?, ?, ?, ?, 'verified')
            ''', (user_id, module_id, task_id, points, screenshot_path))
            
            # Update module progress
            self.update_module_progress(user_id, module_id)
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Failed to complete task: {e}")
            return False
            
        finally:
            conn.close()
            
    def update_module_progress(self, user_id: int, module_id: str):
        """Update the overall progress for a module."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get total points for the module
            cursor.execute('''
            SELECT SUM(points) FROM module_tasks WHERE module_id = ?
            ''', (module_id,))
            total_points = cursor.fetchone()[0] or 0
            
            # Get earned points
            cursor.execute('''
            SELECT SUM(points_earned) FROM task_completions 
            WHERE user_id = ? AND module_id = ?
            ''', (user_id, module_id))
            earned_points = cursor.fetchone()[0] or 0
            
            # Calculate progress percentage
            progress_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
            
            # Update progress
            status = 'completed' if progress_percentage >= 100 else 'in_progress'
            cursor.execute('''
            UPDATE user_progress 
            SET progress_percentage = ?, points_earned = ?, status = ?, 
                last_activity = CURRENT_TIMESTAMP,
                completion_date = CASE WHEN ? = 'completed' THEN CURRENT_TIMESTAMP ELSE NULL END
            WHERE user_id = ? AND module_id = ?
            ''', (progress_percentage, earned_points, status, status, user_id, module_id))
            
            conn.commit()
            
        except sqlite3.Error as e:
            logger.error(f"Failed to update module progress: {e}")
            
        finally:
            conn.close()
            
    def get_user_progress(self, user_id: int) -> List[Dict]:
        """Get all progress records for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT p.*, m.name as module_name, m.difficulty, m.estimated_duration
            FROM user_progress p
            JOIN modules m ON p.module_id = m.module_id
            WHERE p.user_id = ?
            ORDER BY p.last_activity DESC
            ''', (user_id,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        finally:
            conn.close()
            
    def get_module_progress(self, user_id: int, module_id: str) -> Dict:
        """Get detailed progress for a specific module."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get module progress
            cursor.execute('''
            SELECT * FROM user_progress 
            WHERE user_id = ? AND module_id = ?
            ''', (user_id, module_id))
            
            progress_row = cursor.fetchone()
            if not progress_row:
                return {'status': 'not_started', 'progress_percentage': 0}
                
            columns = [desc[0] for desc in cursor.description]
            progress = dict(zip(columns, progress_row))
            
            # Get completed tasks
            cursor.execute('''
            SELECT task_id, points_earned, completed_date 
            FROM task_completions 
            WHERE user_id = ? AND module_id = ?
            ORDER BY completed_date
            ''', (user_id, module_id))
            
            progress['completed_tasks'] = cursor.fetchall()
            
            # Get total time spent
            cursor.execute('''
            SELECT SUM(duration) FROM training_sessions 
            WHERE user_id = ? AND module_id = ?
            ''', (user_id, module_id))
            
            total_time = cursor.fetchone()[0] or 0
            progress['total_time_spent'] = total_time
            
            return progress
            
        finally:
            conn.close()
            
    def get_certifications(self, user_id: int) -> List[Dict]:
        """Get all certifications earned by a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT c.*, m.name as module_name 
            FROM certifications c
            JOIN modules m ON c.module_id = m.module_id
            WHERE c.user_id = ?
            ORDER BY c.issued_date DESC
            ''', (user_id,))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        finally:
            conn.close()
            
    def issue_certification(self, user_id: int, module_id: str, 
                          certificate_name: str, score: float) -> bool:
        """Issue a certification for completing a module."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO certifications 
            (user_id, module_id, certificate_name, score)
            VALUES (?, ?, ?, ?)
            ''', (user_id, module_id, certificate_name, score))
            
            conn.commit()
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Failed to issue certification: {e}")
            return False
            
        finally:
            conn.close()
            
    def record_session_end(self, user_id: int, module_id: str):
        """End the current training session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Find the most recent open session
            cursor.execute('''
            SELECT id, start_time FROM training_sessions 
            WHERE user_id = ? AND module_id = ? AND end_time IS NULL
            ORDER BY start_time DESC LIMIT 1
            ''', (user_id, module_id))
            
            session = cursor.fetchone()
            if session:
                session_id, start_time = session
                
                # Update session with end time and duration
                cursor.execute('''
                UPDATE training_sessions 
                SET end_time = CURRENT_TIMESTAMP,
                    duration = CAST((julianday(CURRENT_TIMESTAMP) - julianday(start_time)) * 86400 AS INTEGER)
                WHERE id = ?
                ''', (session_id,))
                
                # Update total time spent in user_progress
                cursor.execute('''
                UPDATE user_progress 
                SET time_spent = (
                    SELECT SUM(duration) FROM training_sessions 
                    WHERE user_id = ? AND module_id = ?
                )
                WHERE user_id = ? AND module_id = ?
                ''', (user_id, module_id, user_id, module_id))
                
            conn.commit()
            
        except sqlite3.Error as e:
            logger.error(f"Failed to record session end: {e}")
            
        finally:
            conn.close()
            
    def get_learning_statistics(self, user_id: int) -> Dict:
        """Get overall learning statistics for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            stats = {}
            
            # Total modules started/completed
            cursor.execute('''
            SELECT 
                COUNT(*) as total_modules,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_modules,
                SUM(points_earned) as total_points,
                AVG(progress_percentage) as avg_progress
            FROM user_progress
            WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            stats.update({
                'total_modules': result[0],
                'completed_modules': result[1],
                'total_points': result[2] or 0,
                'average_progress': result[3] or 0
            })
            
            # Total time spent
            cursor.execute('''
            SELECT SUM(duration) FROM training_sessions
            WHERE user_id = ?
            ''', (user_id,))
            
            total_time = cursor.fetchone()[0] or 0
            stats['total_time_spent'] = total_time
            
            # Certifications earned
            cursor.execute('''
            SELECT COUNT(*) FROM certifications
            WHERE user_id = ?
            ''', (user_id,))
            
            stats['certifications_earned'] = cursor.fetchone()[0]
            
            return stats
            
        finally:
            conn.close()
