"""User profile management."""

import sqlite3
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ProfileManager:
    """Manages user profiles and preferences."""
    
    def __init__(self, db_path: str, profile_dir: str = "user_management/profiles"):
        self.db_path = db_path
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        
    def get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get complete user profile information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get basic user info
            cursor.execute('''
            SELECT username, email, full_name, department, role, created_date,
                   last_login, profile_picture, preferences
            FROM users WHERE id = ?
            ''', (user_id,))
            
            user_data = cursor.fetchone()
            if not user_data:
                return None
                
            # Get training statistics
            cursor.execute('''
            SELECT COUNT(DISTINCT module_id) as modules_started,
                   COUNT(DISTINCT CASE WHEN status = 'completed' THEN module_id END) as modules_completed,
                   SUM(points_earned) as total_points
            FROM user_progress WHERE user_id = ?
            ''', (user_id,))
            
            stats_data = cursor.fetchone()
            
            # Get certifications count
            cursor.execute('''
            SELECT COUNT(*) FROM certifications WHERE user_id = ?
            ''', (user_id,))
            
            cert_count = cursor.fetchone()[0]
            
            # Get recent activity
            cursor.execute('''
            SELECT m.name, p.last_activity, p.progress_percentage
            FROM user_progress p
            JOIN modules m ON p.module_id = m.module_id
            WHERE p.user_id = ?
            ORDER BY p.last_activity DESC
            LIMIT 5
            ''', (user_id,))
            
            recent_activities = cursor.fetchall()
            
            # Compile profile
            profile = {
                'user_id': user_id,
                'username': user_data[0],
                'email': user_data[1],
                'full_name': user_data[2],
                'department': user_data[3],
                'role': user_data[4],
                'created_date': user_data[5],
                'last_login': user_data[6],
                'profile_picture': user_data[7],
                'preferences': json.loads(user_data[8] or '{}'),
                'statistics': {
                    'modules_started': stats_data[0],
                    'modules_completed': stats_data[1],
                    'total_points': stats_data[2] or 0,
                    'certifications': cert_count
                },
                'recent_activities': [
                    {
                        'module': activity[0],
                        'last_activity': activity[1],
                        'progress': activity[2]
                    }
                    for activity in recent_activities
                ]
            }
            
            return profile
            
        finally:
            conn.close()
            
    def update_user_profile(self, user_id: int, profile_data: Dict) -> bool:
        """Update user profile information."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Build update query dynamically
            allowed_fields = ['email', 'full_name', 'department', 'profile_picture']
            update_fields = []
            values = []
            
            for field in allowed_fields:
                if field in profile_data:
                    update_fields.append(f"{field} = ?")
                    values.append(profile_data[field])
            
            if not update_fields:
                return False
                
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(query, values)
            conn.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Failed to update profile: {e}")
            return False
            
        finally:
            conn.close()
            
    def update_preferences(self, user_id: int, preferences: Dict) -> bool:
        """Update user preferences."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get current preferences
            cursor.execute('SELECT preferences FROM users WHERE id = ?', (user_id,))
            current_prefs = json.loads(cursor.fetchone()[0] or '{}')
            
            # Merge with new preferences
            current_prefs.update(preferences)
            
            # Update preferences
            cursor.execute('''
            UPDATE users SET preferences = ? WHERE id = ?
            ''', (json.dumps(current_prefs), user_id))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update preferences: {e}")
            return False
            
        finally:
            conn.close()
            
    def upload_profile_picture(self, user_id: int, image_data: bytes, filename: str) -> Optional[str]:
        """Upload a profile picture for a user."""
        try:
            # Create user directory
            user_dir = self.profile_dir / str(user_id)
            user_dir.mkdir(exist_ok=True)
            
            # Save image
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_filename = f"profile_{timestamp}_{filename}"
            image_path = user_dir / image_filename
            
            with open(image_path, 'wb') as f:
                f.write(image_data)
            
            # Update database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            relative_path = str(image_path.relative_to(self.profile_dir.parent))
            cursor.execute('''
            UPDATE users SET profile_picture = ? WHERE id = ?
            ''', (relative_path, user_id))
            
            conn.commit()
            conn.close()
            
            return relative_path
            
        except Exception as e:
            logger.error(f"Failed to upload profile picture: {e}")
            return None
            
    def get_user_settings(self, user_id: int) -> Dict:
        """Get user-specific settings."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT preferences FROM users WHERE id = ?
            ''', (user_id,))
            
            prefs_data = cursor.fetchone()
            if not prefs_data:
                return {}
                
            preferences = json.loads(prefs_data[0] or '{}')
            
            # Default settings
            default_settings = {
                'notifications': {
                    'email': True,
                    'in_app': True,
                    'module_complete': True,
                    'certificate_earned': True
                },
                'ui': {
                    'theme': 'light',
                    'language': 'en',
                    'dashboard_layout': 'grid'
                },
                'training': {
                    'auto_advance': False,
                    'show_hints': True,
                    'difficulty_preference': 'adaptive'
                }
            }
            
            # Merge with user preferences
            for category, settings in default_settings.items():
                if category not in preferences:
                    preferences[category] = settings
                else:
                    for key, value in settings.items():
                        if key not in preferences[category]:
                            preferences[category][key] = value
                            
            return preferences
            
        finally:
            conn.close()
            
    def get_training_history(self, user_id: int, limit: int = 50) -> List[Dict]:
        """Get detailed training history for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT s.start_time, s.end_time, s.duration/60.0 as duration_minutes,
                   m.name as module_name, s.activity_type
            FROM training_sessions s
            JOIN modules m ON s.module_id = m.module_id
            WHERE s.user_id = ?
            ORDER BY s.start_time DESC
            LIMIT ?
            ''', (user_id, limit))
            
            sessions = cursor.fetchall()
            
            history = []
            for session in sessions:
                history.append({
                    'start_time': session[0],
                    'end_time': session[1],
                    'duration_minutes': session[2],
                    'module_name': session[3],
                    'activity_type': session[4]
                })
                
            return history
            
        finally:
            conn.close()
            
    def get_skill_profile(self, user_id: int) -> Dict:
        """Get a user's skill profile based on completed modules."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get completed modules and their categories
            cursor.execute('''
            SELECT m.category, COUNT(*) as count, SUM(p.points_earned) as points
            FROM user_progress p
            JOIN modules m ON p.module_id = m.module_id
            WHERE p.user_id = ? AND p.status = 'completed'
            GROUP BY m.category
            ''', (user_id,))
            
            skill_data = cursor.fetchall()
            
            skills = {}
            for category, count, points in skill_data:
                skills[category] = {
                    'modules_completed': count,
                    'points_earned': points or 0,
                    'skill_level': self._calculate_skill_level(points or 0)
                }
                
            # Get current modules in progress
            cursor.execute('''
            SELECT m.category, COUNT(*) as count
            FROM user_progress p
            JOIN modules m ON p.module_id = m.module_id
            WHERE p.user_id = ? AND p.status = 'in_progress'
            GROUP BY m.category
            ''', (user_id,))
            
            in_progress = cursor.fetchall()
            
            for category, count in in_progress:
                if category not in skills:
                    skills[category] = {
                        'modules_completed': 0,
                        'points_earned': 0,
                        'skill_level': 'Beginner'
                    }
                skills[category]['modules_in_progress'] = count
                
            return skills
            
        finally:
            conn.close()
            
    def _calculate_skill_level(self, points: int) -> str:
        """Calculate skill level based on points."""
        if points < 50:
            return 'Beginner'
        elif points < 150:
            return 'Intermediate'
        elif points < 300:
            return 'Advanced'
        else:
            return 'Expert'
            
    def export_user_data(self, user_id: int) -> Dict:
        """Export all user data for GDPR compliance."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            export_data = {
                'profile': self.get_user_profile(user_id),
                'settings': self.get_user_settings(user_id),
                'training_history': self.get_training_history(user_id),
                'skill_profile': self.get_skill_profile(user_id)
            }
            
            # Get all progress records
            cursor.execute('''
            SELECT * FROM user_progress WHERE user_id = ?
            ''', (user_id,))
            
            columns = [desc[0] for desc in cursor.description]
            export_data['progress_records'] = [
                dict(zip(columns, row)) for row in cursor.fetchall()
            ]
            
            # Get all task completions
            cursor.execute('''
            SELECT * FROM task_completions WHERE user_id = ?
            ''', (user_id,))
            
            columns = [desc[0] for desc in cursor.description]
            export_data['task_completions'] = [
                dict(zip(columns, row)) for row in cursor.fetchall()
            ]
            
            # Get all certifications
            cursor.execute('''
            SELECT * FROM certifications WHERE user_id = ?
            ''', (user_id,))
            
            columns = [desc[0] for desc in cursor.description]
            export_data['certifications'] = [
                dict(zip(columns, row)) for row in cursor.fetchall()
            ]
            
            export_data['export_date'] = datetime.now().isoformat()
            
            return export_data
            
        finally:
            conn.close()
            
    def get_user_achievements(self, user_id: int) -> List[Dict]:
        """Get user achievements and milestones."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            achievements = []
            
            # Check milestone achievements
            cursor.execute('''
            SELECT COUNT(*) as modules_completed, SUM(points_earned) as total_points
            FROM user_progress
            WHERE user_id = ? AND status = 'completed'
            ''', (user_id,))
            
            stats = cursor.fetchone()
            modules_completed = stats[0]
            total_points = stats[1] or 0
            
            # Module completion milestones
            if modules_completed >= 1:
                achievements.append({
                    'type': 'first_module',
                    'title': 'First Steps',
                    'description': 'Completed your first module',
                    'icon': '🎯'
                })
                
            if modules_completed >= 5:
                achievements.append({
                    'type': 'five_modules',
                    'title': 'Getting Serious',
                    'description': 'Completed 5 modules',
                    'icon': '📚'
                })
                
            if modules_completed >= 10:
                achievements.append({
                    'type': 'ten_modules',
                    'title': 'Knowledge Seeker',
                    'description': 'Completed 10 modules',
                    'icon': '🎓'
                })
                
            # Points milestones
            if total_points >= 100:
                achievements.append({
                    'type': 'hundred_points',
                    'title': 'Century Club',
                    'description': 'Earned 100 points',
                    'icon': '💯'
                })
                
            if total_points >= 500:
                achievements.append({
                    'type': 'five_hundred_points',
                    'title': 'High Achiever',
                    'description': 'Earned 500 points',
                    'icon': '🏆'
                })
                
            # Check for perfect scores
            cursor.execute('''
            SELECT COUNT(*) FROM user_progress
            WHERE user_id = ? AND progress_percentage = 100
            ''', (user_id,))
            
            perfect_scores = cursor.fetchone()[0]
            if perfect_scores >= 1:
                achievements.append({
                    'type': 'perfectionist',
                    'title': 'Perfectionist',
                    'description': 'Achieved 100% on a module',
                    'icon': '⭐'
                })
                
            # Check for streak achievements
            cursor.execute('''
            SELECT DATE(start_time) as session_date
            FROM training_sessions
            WHERE user_id = ?
            GROUP BY DATE(start_time)
            ORDER BY session_date DESC
            ''', (user_id,))
            
            session_dates = [row[0] for row in cursor.fetchall()]
            
            # Calculate current streak
            if session_dates:
                current_streak = 1
                for i in range(1, len(session_dates)):
                    date1 = datetime.fromisoformat(session_dates[i-1])
                    date2 = datetime.fromisoformat(session_dates[i])
                    
                    if (date1 - date2).days == 1:
                        current_streak += 1
                    else:
                        break
                        
                if current_streak >= 7:
                    achievements.append({
                        'type': 'week_streak',
                        'title': 'Week Warrior',
                        'description': '7-day training streak',
                        'icon': '🔥'
                    })
                    
                if current_streak >= 30:
                    achievements.append({
                        'type': 'month_streak',
                        'title': 'Dedicated Learner',
                        'description': '30-day training streak',
                        'icon': '💪'
                    })
                    
            return achievements
            
        finally:
            conn.close()
