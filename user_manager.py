#!/usr/bin/env python3
"""
User Management System
Handles user creation, authentication, and profile management
"""

import json
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    TRAINEE = "trainee"

class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

@dataclass
class User:
    """User profile data structure"""
    user_id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    status: UserStatus
    department: str
    employee_id: Optional[str]
    created_at: str
    last_login: Optional[str]
    profile_picture: Optional[str]
    preferences: Dict[str, any]
    metadata: Dict[str, any]

@dataclass
class UserSession:
    """User session data"""
    session_id: str
    user_id: str
    created_at: str
    expires_at: str
    ip_address: str
    user_agent: str
    is_active: bool

class UserManager:
    """Manages user accounts and authentication"""
    
    def __init__(self, db_path: Path, session_duration_hours: int = 8):
        self.db_path = db_path
        self.session_duration = timedelta(hours=session_duration_hours)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL,
                department TEXT,
                employee_id TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_login TEXT,
                profile_picture TEXT,
                preferences TEXT,
                metadata TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # User permissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                permission TEXT NOT NULL,
                granted_at TEXT DEFAULT CURRENT_TIMESTAMP,
                granted_by TEXT,
                UNIQUE(user_id, permission),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Training history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS training_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                module_id TEXT NOT NULL,
                completed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                score REAL,
                certificate_id TEXT,
                instructor_id TEXT,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Password reset tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                used BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_user(self, username: str, email: str, password: str, 
                   full_name: str, role: UserRole = UserRole.TRAINEE,
                   department: str = None, employee_id: str = None) -> Optional[User]:
        """Create a new user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Generate unique user ID
            user_id = self._generate_user_id(username)
            
            # Hash password
            salt = secrets.token_hex(16)
            password_hash = self._hash_password(password, salt)
            
            # Create user
            cursor.execute('''
                INSERT INTO users (user_id, username, email, password_hash, salt,
                                 full_name, role, status, department, employee_id,
                                 preferences, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '{}', '{}')
            ''', (user_id, username, email, password_hash, salt,
                  full_name, role.value, UserStatus.ACTIVE.value, 
                  department, employee_id))
            
            conn.commit()
            
            # Create and return User object
            return User(
                user_id=user_id,
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                status=UserStatus.ACTIVE,
                department=department,
                employee_id=employee_id,
                created_at=datetime.now().isoformat(),
                last_login=None,
                profile_picture=None,
                preferences={},
                metadata={}
            )
            
        except sqlite3.IntegrityError as e:
            if "username" in str(e):
                raise ValueError("Username already exists")
            elif "email" in str(e):
                raise ValueError("Email already exists")
            else:
                raise e
                
        finally:
            conn.close()
    
    def authenticate(self, username: str, password: str, 
                    ip_address: str = None, user_agent: str = None) -> Optional[UserSession]:
        """Authenticate user and create session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user
            cursor.execute('''
                SELECT user_id, password_hash, salt, status 
                FROM users 
                WHERE username = ? OR email = ?
            ''', (username, username))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            user_id, stored_hash, salt, status = result
            
            # Check password
            if self._hash_password(password, salt) != stored_hash:
                return None
            
            # Check user status
            if status != UserStatus.ACTIVE.value:
                return None
            
            # Create session
            session = self._create_session(user_id, ip_address, user_agent, conn)
            
            # Update last login
            cursor.execute('''
                UPDATE users 
                SET last_login = ? 
                WHERE user_id = ?
            ''', (datetime.now().isoformat(), user_id))
            
            conn.commit()
            return session
            
        finally:
            conn.close()
    
    def _create_session(self, user_id: str, ip_address: str, user_agent: str,
                       conn: sqlite3.Connection) -> UserSession:
        """Create a new user session"""
        session_id = secrets.token_urlsafe(32)
        created_at = datetime.now()
        expires_at = created_at + self.session_duration
        
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (session_id, user_id, created_at, expires_at,
                                ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (session_id, user_id, created_at.isoformat(), 
              expires_at.isoformat(), ip_address, user_agent))
        
        return UserSession(
            session_id=session_id,
            user_id=user_id,
            created_at=created_at.isoformat(),
            expires_at=expires_at.isoformat(),
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True
        )
    
    def validate_session(self, session_id: str) -> Optional[User]:
        """Validate session and return user if valid"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get session
            cursor.execute('''
                SELECT user_id, expires_at, is_active 
                FROM sessions 
                WHERE session_id = ?
            ''', (session_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            user_id, expires_at, is_active = result
            
            # Check if session is active and not expired
            if not is_active or datetime.fromisoformat(expires_at) < datetime.now():
                return None
            
            # Get user
            return self.get_user(user_id)
            
        finally:
            conn.close()
    
    def logout(self, session_id: str):
        """Logout user by invalidating session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE sessions 
                SET is_active = 0 
                WHERE session_id = ?
            ''', (session_id,))
            
            conn.commit()
            
        finally:
            conn.close()
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM users WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            # Convert to User object
            return self._row_to_user(result)
            
        finally:
            conn.close()
    
    def update_user(self, user_id: str, updates: Dict[str, any]):
        """Update user profile"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Build update query
            fields = []
            values = []
            
            for field, value in updates.items():
                if field in ['preferences', 'metadata']:
                    value = json.dumps(value)
                    
                fields.append(f"{field} = ?")
                values.append(value)
            
            values.append(user_id)
            
            query = f'''
                UPDATE users 
                SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            '''
            
            cursor.execute(query, values)
            conn.commit()
            
        finally:
            conn.close()
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verify old password
            cursor.execute('''
                SELECT password_hash, salt 
                FROM users 
                WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            stored_hash, salt = result
            
            if self._hash_password(old_password, salt) != stored_hash:
                return False
            
            # Set new password
            new_salt = secrets.token_hex(16)
            new_hash = self._hash_password(new_password, new_salt)
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, salt = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (new_hash, new_salt, user_id))
            
            conn.commit()
            return True
            
        finally:
            conn.close()
    
    def create_password_reset_token(self, email: str) -> Optional[str]:
        """Create password reset token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user by email
            cursor.execute('''
                SELECT user_id FROM users WHERE email = ?
            ''', (email,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            user_id = result[0]
            
            # Create token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)
            
            cursor.execute('''
                INSERT INTO password_reset_tokens (token, user_id, expires_at)
                VALUES (?, ?, ?)
            ''', (token, user_id, expires_at.isoformat()))
            
            conn.commit()
            return token
            
        finally:
            conn.close()
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password using token"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Validate token
            cursor.execute('''
                SELECT user_id, expires_at, used 
                FROM password_reset_tokens 
                WHERE token = ?
            ''', (token,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            user_id, expires_at, used = result
            
            # Check if token is valid
            if used or datetime.fromisoformat(expires_at) < datetime.now():
                return False
            
            # Reset password
            new_salt = secrets.token_hex(16)
            new_hash = self._hash_password(new_password, new_salt)
            
            cursor.execute('''
                UPDATE users 
                SET password_hash = ?, salt = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (new_hash, new_salt, user_id))
            
            # Mark token as used
            cursor.execute('''
                UPDATE password_reset_tokens 
                SET used = 1 
                WHERE token = ?
            ''', (token,))
            
            conn.commit()
            return True
            
        finally:
            conn.close()
    
    def grant_permission(self, user_id: str, permission: str, granted_by: str):
        """Grant permission to user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO user_permissions (user_id, permission, granted_by)
                VALUES (?, ?, ?)
            ''', (user_id, permission, granted_by))
            
            conn.commit()
            
        finally:
            conn.close()
    
    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has permission"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check direct permission
            cursor.execute('''
                SELECT id FROM user_permissions 
                WHERE user_id = ? AND permission = ?
            ''', (user_id, permission))
            
            if cursor.fetchone():
                return True
            
            # Check role-based permissions
            cursor.execute('''
                SELECT role FROM users WHERE user_id = ?
            ''', (user_id,))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            role = UserRole(result[0])
            
            # Admin has all permissions
            if role == UserRole.ADMIN:
                return True
            
            # Define role-based permissions
            role_permissions = {
                UserRole.INSTRUCTOR: [
                    'view_all_progress',
                    'create_assignments',
                    'grade_submissions',
                    'view_reports'
                ],
                UserRole.TRAINEE: [
                    'view_own_progress',
                    'submit_assignments',
                    'download_certificates'
                ]
            }
            
            return permission in role_permissions.get(role, [])
            
        finally:
            conn.close()
    
    def get_users_by_role(self, role: UserRole) -> List[User]:
        """Get all users with specific role"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM users WHERE role = ?
            ''', (role.value,))
            
            users = []
            for row in cursor.fetchall():
                users.append(self._row_to_user(row))
            
            return users
            
        finally:
            conn.close()
    
    def record_training_completion(self, user_id: str, module_id: str, 
                                 score: float, instructor_id: str = None,
                                 notes: str = None) -> str:
        """Record training completion and issue certificate"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Generate certificate ID
            certificate_id = f"CERT-{user_id}-{module_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            cursor.execute('''
                INSERT INTO training_history 
                (user_id, module_id, score, certificate_id, instructor_id, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, module_id, score, certificate_id, instructor_id, notes))
            
            conn.commit()
            return certificate_id
            
        finally:
            conn.close()
    
    def get_training_history(self, user_id: str) -> List[Dict]:
        """Get user's training history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT * FROM training_history 
                WHERE user_id = ? 
                ORDER BY completed_at DESC
            ''', (user_id,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'module_id': row[2],
                    'completed_at': row[3],
                    'score': row[4],
                    'certificate_id': row[5],
                    'instructor_id': row[6],
                    'notes': row[7]
                })
            
            return history
            
        finally:
            conn.close()
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt"""
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def _generate_user_id(self, username: str) -> str:
        """Generate unique user ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"USER-{username.upper()[:5]}-{timestamp}"
    
    def _row_to_user(self, row: Tuple) -> User:
        """Convert database row to User object"""
        return User(
            user_id=row[0],
            username=row[1],
            email=row[2],
            full_name=row[5],
            role=UserRole(row[6]),
            status=UserStatus(row[7]),
            department=row[8],
            employee_id=row[9],
            created_at=row[10],
            last_login=row[11],
            profile_picture=row[12],
            preferences=json.loads(row[13] or '{}'),
            metadata=json.loads(row[14] or '{}')
        )

# Example usage
if __name__ == "__main__":
    user_mgr = UserManager(Path("training_data.db"))
    
    # Create a user
    user = user_mgr.create_user(
        username="john_doe",
        email="john.doe@company.com",
        password="secure_password123",
        full_name="John Doe",
        role=UserRole.TRAINEE,
        department="Engineering"
    )
    
    print(f"Created user: {user.username}")
    
    # Authenticate user
    session = user_mgr.authenticate("john_doe", "secure_password123",
                                   ip_address="192.168.1.100",
                                   user_agent="Mozilla/5.0")
    
    if session:
        print(f"Login successful. Session ID: {session.session_id}")
        
        # Validate session
        valid_user = user_mgr.validate_session(session.session_id)
        if valid_user:
            print(f"Session valid for user: {valid_user.full_name}")