"""Role and permission management."""

import sqlite3
import json
from typing import Dict, List, Optional, Set
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RoleManager:
    """Manages user roles and permissions."""
    
    # Default role definitions
    DEFAULT_ROLES = {
        'admin': {
            'name': 'Administrator',
            'description': 'Full system access',
            'permissions': [
                'user.create', 'user.read', 'user.update', 'user.delete',
                'module.create', 'module.read', 'module.update', 'module.delete',
                'report.generate', 'report.export',
                'system.config', 'system.backup',
                'training.view_all', 'training.manage_all'
            ],
            'level': 100
        },
        'instructor': {
            'name': 'Instructor',
            'description': 'Can manage training content and view reports',
            'permissions': [
                'user.read', 'user.update_own',
                'module.create', 'module.read', 'module.update',
                'report.generate', 'report.export',
                'training.view_all', 'training.evaluate'
            ],
            'level': 50
        },
        'trainee': {
            'name': 'Trainee',
            'description': 'Can access training modules and view own progress',
            'permissions': [
                'user.read_own', 'user.update_own',
                'module.read',
                'training.view_own', 'training.participate'
            ],
            'level': 10
        },
        'guest': {
            'name': 'Guest',
            'description': 'Limited read-only access',
            'permissions': [
                'module.read',
                'training.view_demo'
            ],
            'level': 1
        }
    }
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ensure_tables_exist()
        self._initialize_default_roles()
        
    def ensure_tables_exist(self):
        """Ensure role-related tables exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Roles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            permissions TEXT NOT NULL,
            level INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # User role assignments
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role_id TEXT NOT NULL,
            assigned_by INTEGER,
            assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (role_id) REFERENCES roles(role_id),
            FOREIGN KEY (assigned_by) REFERENCES users(id),
            UNIQUE(user_id, role_id)
        )
        ''')
        
        # Permission overrides
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS permission_overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            permission TEXT NOT NULL,
            granted BOOLEAN DEFAULT 1,
            reason TEXT,
            granted_by INTEGER,
            granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (granted_by) REFERENCES users(id),
            UNIQUE(user_id, permission)
        )
        ''')
        
        # Audit log for role changes
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            role_id TEXT,
            permission TEXT,
            performed_by INTEGER,
            performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (performed_by) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def _initialize_default_roles(self):
        """Initialize default roles in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for role_id, role_data in self.DEFAULT_ROLES.items():
            cursor.execute('''
            INSERT OR IGNORE INTO roles (role_id, name, description, permissions, level)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                role_id,
                role_data['name'],
                role_data['description'],
                json.dumps(role_data['permissions']),
                role_data['level']
            ))
            
        conn.commit()
        conn.close()
        
    def assign_role(self, user_id: int, role_id: str, assigned_by: int = None, 
                   expires_at: datetime = None) -> bool:
        """Assign a role to a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if role exists
            cursor.execute('SELECT role_id FROM roles WHERE role_id = ?', (role_id,))
            if not cursor.fetchone():
                logger.error(f"Role {role_id} not found")
                return False
                
            # Update the user's role in the users table
            cursor.execute('''
            UPDATE users SET role = ? WHERE id = ?
            ''', (role_id, user_id))
            
            # Add to user_roles table
            cursor.execute('''
            INSERT OR REPLACE INTO user_roles (user_id, role_id, assigned_by, expires_at)
            VALUES (?, ?, ?, ?)
            ''', (user_id, role_id, assigned_by, expires_at))
            
            # Log the action
            self._log_role_action(user_id, 'role_assigned', role_id, None, assigned_by)
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to assign role: {e}")
            return False
            
        finally:
            conn.close()
            
    def revoke_role(self, user_id: int, role_id: str, revoked_by: int = None) -> bool:
        """Revoke a role from a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Remove from user_roles
            cursor.execute('''
            DELETE FROM user_roles WHERE user_id = ? AND role_id = ?
            ''', (user_id, role_id))
            
            # If this was their primary role, set to 'trainee'
            cursor.execute('''
            UPDATE users SET role = 'trainee' 
            WHERE id = ? AND role = ?
            ''', (user_id, role_id))
            
            # Log the action
            self._log_role_action(user_id, 'role_revoked', role_id, None, revoked_by)
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke role: {e}")
            return False
            
        finally:
            conn.close()
            
    def get_user_permissions(self, user_id: int) -> Set[str]:
        """Get all permissions for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            permissions = set()
            
            # Get permissions from user's roles
            cursor.execute('''
            SELECT r.permissions
            FROM user_roles ur
            JOIN roles r ON ur.role_id = r.role_id
            WHERE ur.user_id = ? AND (ur.expires_at IS NULL OR ur.expires_at > CURRENT_TIMESTAMP)
            ''', (user_id,))
            
            for row in cursor.fetchall():
                role_permissions = json.loads(row[0])
                permissions.update(role_permissions)
                
            # Also get from the users table primary role
            cursor.execute('''
            SELECT r.permissions
            FROM users u
            JOIN roles r ON u.role = r.role_id
            WHERE u.id = ?
            ''', (user_id,))
            
            primary_role = cursor.fetchone()
            if primary_role:
                primary_permissions = json.loads(primary_role[0])
                permissions.update(primary_permissions)
                
            # Apply permission overrides
            cursor.execute('''
            SELECT permission, granted
            FROM permission_overrides
            WHERE user_id = ? AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
            ''', (user_id,))
            
            for permission, granted in cursor.fetchall():
                if granted:
                    permissions.add(permission)
                else:
                    permissions.discard(permission)
                    
            return permissions
            
        finally:
            conn.close()
            
    def has_permission(self, user_id: int, permission: str) -> bool:
        """Check if a user has a specific permission."""
        permissions = self.get_user_permissions(user_id)
        
        # Check exact permission
        if permission in permissions:
            return True
            
        # Check wildcard permissions
        permission_parts = permission.split('.')
        for i in range(len(permission_parts)):
            wildcard = '.'.join(permission_parts[:i+1]) + '.*'
            if wildcard in permissions:
                return True
                
        return False
        
    def grant_permission(self, user_id: int, permission: str, granted_by: int = None,
                       reason: str = None, expires_at: datetime = None) -> bool:
        """Grant a specific permission to a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO permission_overrides 
            (user_id, permission, granted, reason, granted_by, expires_at)
            VALUES (?, ?, 1, ?, ?, ?)
            ''', (user_id, permission, reason, granted_by, expires_at))
            
            # Log the action
            self._log_role_action(user_id, 'permission_granted', None, permission, granted_by)
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to grant permission: {e}")
            return False
            
        finally:
            conn.close()
            
    def revoke_permission(self, user_id: int, permission: str, revoked_by: int = None,
                        reason: str = None) -> bool:
        """Revoke a specific permission from a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO permission_overrides 
            (user_id, permission, granted, reason, granted_by)
            VALUES (?, ?, 0, ?, ?)
            ''', (user_id, permission, reason, revoked_by))
            
            # Log the action
            self._log_role_action(user_id, 'permission_revoked', None, permission, revoked_by)
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to revoke permission: {e}")
            return False
            
        finally:
            conn.close()
            
    def get_role_info(self, role_id: str) -> Optional[Dict]:
        """Get information about a specific role."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT * FROM roles WHERE role_id = ?
            ''', (role_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
                
            columns = [desc[0] for desc in cursor.description]
            role_info = dict(zip(columns, row))
            role_info['permissions'] = json.loads(role_info['permissions'])
            
            # Get user count for this role
            cursor.execute('''
            SELECT COUNT(*) FROM users WHERE role = ?
            ''', (role_id,))
            
            role_info['user_count'] = cursor.fetchone()[0]
            
            return role_info
            
        finally:
            conn.close()
            
    def get_all_roles(self) -> List[Dict]:
        """Get all available roles."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM roles ORDER BY level DESC')
            
            roles = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                role_info = dict(zip(columns, row))
                role_info['permissions'] = json.loads(role_info['permissions'])
                roles.append(role_info)
                
            return roles
            
        finally:
            conn.close()
            
    def create_custom_role(self, role_id: str, name: str, description: str,
                         permissions: List[str], level: int = 0) -> bool:
        """Create a custom role."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO roles (role_id, name, description, permissions, level)
            VALUES (?, ?, ?, ?, ?)
            ''', (role_id, name, description, json.dumps(permissions), level))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to create role: {e}")
            return False
            
        finally:
            conn.close()
            
    def update_role(self, role_id: str, name: str = None, description: str = None,
                   permissions: List[str] = None, level: int = None) -> bool:
        """Update an existing role."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Build update query
            updates = []
            values = []
            
            if name is not None:
                updates.append("name = ?")
                values.append(name)
                
            if description is not None:
                updates.append("description = ?")
                values.append(description)
                
            if permissions is not None:
                updates.append("permissions = ?")
                values.append(json.dumps(permissions))
                
            if level is not None:
                updates.append("level = ?")
                values.append(level)
                
            if not updates:
                return False
                
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(role_id)
            
            query = f"UPDATE roles SET {', '.join(updates)} WHERE role_id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            logger.error(f"Failed to update role: {e}")
            return False
            
        finally:
            conn.close()
            
    def delete_role(self, role_id: str) -> bool:
        """Delete a custom role."""
        # Prevent deletion of default roles
        if role_id in self.DEFAULT_ROLES:
            logger.error(f"Cannot delete default role: {role_id}")
            return False
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if any users have this role
            cursor.execute('SELECT COUNT(*) FROM users WHERE role = ?', (role_id,))
            if cursor.fetchone()[0] > 0:
                logger.error(f"Cannot delete role {role_id}: users still assigned")
                return False
                
            # Delete the role
            cursor.execute('DELETE FROM roles WHERE role_id = ?', (role_id,))
            
            # Delete any user_roles assignments
            cursor.execute('DELETE FROM user_roles WHERE role_id = ?', (role_id,))
            
            conn.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete role: {e}")
            return False
            
        finally:
            conn.close()
            
    def _log_role_action(self, user_id: int, action: str, role_id: str = None,
                        permission: str = None, performed_by: int = None):
        """Log role-related actions for audit trail."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            details = json.dumps({
                'action': action,
                'role_id': role_id,
                'permission': permission,
                'timestamp': datetime.now().isoformat()
            })
            
            cursor.execute('''
            INSERT INTO role_audit_log 
            (user_id, action, role_id, permission, performed_by, details)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, action, role_id, permission, performed_by, details))
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Failed to log role action: {e}")
            
        finally:
            conn.close()
            
    def get_audit_log(self, user_id: int = None, limit: int = 100) -> List[Dict]:
        """Get audit log entries."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if user_id:
                cursor.execute('''
                SELECT * FROM role_audit_log 
                WHERE user_id = ?
                ORDER BY performed_at DESC
                LIMIT ?
                ''', (user_id, limit))
            else:
                cursor.execute('''
                SELECT * FROM role_audit_log 
                ORDER BY performed_at DESC
                LIMIT ?
                ''', (limit,))
                
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        finally:
            conn.close()
