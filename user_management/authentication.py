"""Authentication and session management."""

import sqlite3
import hashlib
import secrets
import json
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging
from pathlib import Path
import jwt

logger = logging.getLogger(__name__)

class AuthenticationManager:
    """Manages user authentication and sessions."""
    
    def __init__(self, db_path: str, config_path: str = "config/app_config.json"):
        self.db_path = db_path
        self.config = self._load_config(config_path)
        self.secret_key = self.config.get('security', {}).get('secret_key', secrets.token_hex(32))
        self.ensure_tables_exist()
        
    def _load_config(self, config_path: str) -> dict:
        """Load application configuration."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
            
    def ensure_tables_exist(self):
        """Ensure authentication-related tables exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table with extended fields
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT UNIQUE,
            full_name TEXT,
            department TEXT,
            role TEXT DEFAULT 'trainee',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            profile_picture TEXT,
            preferences TEXT DEFAULT '{}',
            two_factor_enabled BOOLEAN DEFAULT 0,
            two_factor_secret TEXT
        )
        ''')
        
        # Sessions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        # Login attempts tracking
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            ip_address TEXT,
            attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT 0,
            error_message TEXT
        )
        ''')
        
        # Password reset tokens
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            used BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        ''')
        
        conn.commit()
        conn.close()
        
        # Create default admin if doesn't exist
        self._create_default_admin()
        
    def _create_default_admin(self):
        """Create default admin account if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        if not cursor.fetchone():
            password_hash = self._hash_password('admin123')
            cursor.execute('''
            INSERT INTO users (username, password_hash, email, full_name, role)
            VALUES (?, ?, ?, ?, ?)
            ''', ('admin', password_hash, 'admin@broetje.com', 'System Administrator', 'admin'))
            conn.commit()
            logger.info("Created default admin account")
            
        conn.close()
        
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256."""
        salt = self.config.get('security', {}).get('password_salt', 'broetje_salt')
        return hashlib.sha256((password + salt).encode()).hexdigest()
        
    def authenticate(self, username: str, password: str, ip_address: str = None) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Authenticate a user and create a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if user is locked out (too many failed attempts)
            if self._is_user_locked_out(username, ip_address):
                self._log_login_attempt(username, ip_address, False, "Account temporarily locked")
                return False, None, "Account temporarily locked due to multiple failed login attempts"
                
            # Get user info
            cursor.execute('''
            SELECT id, password_hash, role, is_active, full_name, email, department
            FROM users WHERE username = ?
            ''', (username,))
            
            user_data = cursor.fetchone()
            if not user_data:
                self._log_login_attempt(username, ip_address, False, "User not found")
                return False, None, "Invalid username or password"
                
            user_id, stored_hash, role, is_active, full_name, email, department = user_data
            
            # Check if account is active
            if not is_active:
                self._log_login_attempt(username, ip_address, False, "Account inactive")
                return False, None, "Account is inactive"
                
            # Verify password
            if self._hash_password(password) != stored_hash:
                self._log_login_attempt(username, ip_address, False, "Invalid password")
                return False, None, "Invalid username or password"
                
            # Create session
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=8)
            
            cursor.execute('''
            INSERT INTO sessions (user_id, token, expires_at, ip_address)
            VALUES (?, ?, ?, ?)
            ''', (user_id, session_token, expires_at, ip_address))
            
            # Update last login
            cursor.execute('''
            UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?
            ''', (user_id,))
            
            conn.commit()
            
            # Log successful login
            self._log_login_attempt(username, ip_address, True, None)
            
            user_info = {
                'id': user_id,
                'username': username,
                'role': role,
                'full_name': full_name,
                'email': email,
                'department': department,
                'session_token': session_token
            }
            
            return True, user_info, None
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None, "Authentication failed"
            
        finally:
            conn.close()
            
    def _is_user_locked_out(self, username: str, ip_address: str) -> bool:
        """Check if user is locked out due to failed attempts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check recent failed attempts
        lockout_period = self.config.get('security', {}).get('lockout_period_minutes', 30)
        max_attempts = self.config.get('security', {}).get('max_login_attempts', 5)
        
        cursor.execute('''
        SELECT COUNT(*) FROM login_attempts
        WHERE username = ? AND success = 0
        AND attempt_time > datetime('now', '-{} minutes')
        '''.format(lockout_period), (username,))
        
        failed_attempts = cursor.fetchone()[0]
        conn.close()
        
        return failed_attempts >= max_attempts
        
    def _log_login_attempt(self, username: str, ip_address: str, success: bool, error_message: str = None):
        """Log a login attempt."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO login_attempts (username, ip_address, success, error_message)
        VALUES (?, ?, ?, ?)
        ''', (username, ip_address, success, error_message))
        
        conn.commit()
        conn.close()
        
    def validate_session(self, session_token: str) -> Tuple[bool, Optional[Dict]]:
        """Validate a session token and return user info."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT s.user_id, s.expires_at, u.username, u.role, u.full_name, u.email, u.department
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ? AND s.is_active = 1
            ''', (session_token,))
            
            session_data = cursor.fetchone()
            if not session_data:
                return False, None
                
            user_id, expires_at, username, role, full_name, email, department = session_data
            
            # Check if session is expired
            if datetime.fromisoformat(expires_at) < datetime.now():
                # Invalidate expired session
                cursor.execute('''
                UPDATE sessions SET is_active = 0 WHERE token = ?
                ''', (session_token,))
                conn.commit()
                return False, None
                
            user_info = {
                'id': user_id,
                'username': username,
                'role': role,
                'full_name': full_name,
                'email': email,
                'department': department
            }
            
            return True, user_info
            
        finally:
            conn.close()
            
    def logout(self, session_token: str) -> bool:
        """Invalidate a session."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            UPDATE sessions SET is_active = 0 WHERE token = ?
            ''', (session_token,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        finally:
            conn.close()
            
    def change_password(self, user_id: int, old_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """Change a user's password."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verify old password
            cursor.execute('SELECT password_hash FROM users WHERE id = ?', (user_id,))
            stored_hash = cursor.fetchone()[0]
            
            if self._hash_password(old_password) != stored_hash:
                return False, "Current password is incorrect"
                
            # Update password
            new_hash = self._hash_password(new_password)
            cursor.execute('''
            UPDATE users SET password_hash = ? WHERE id = ?
            ''', (new_hash, user_id))
            
            conn.commit()
            return True, None
            
        except Exception as e:
            logger.error(f"Password change error: {e}")
            return False, "Failed to change password"
            
        finally:
            conn.close()
            
    def create_password_reset_token(self, email: str) -> Optional[str]:
        """Create a password reset token for a user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user by email
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            user_data = cursor.fetchone()
            
            if not user_data:
                return None
                
            user_id = user_data[0]
            
            # Create reset token
            reset_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=1)
            
            cursor.execute('''
            INSERT INTO password_reset_tokens (user_id, token, expires_at)
            VALUES (?, ?, ?)
            ''', (user_id, reset_token, expires_at))
            
            conn.commit()
            return reset_token
            
        except Exception as e:
            logger.error(f"Password reset token error: {e}")
            return None
            
        finally:
            conn.close()
            
    def reset_password(self, reset_token: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """Reset a user's password using a reset token."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Validate reset token
            cursor.execute('''
            SELECT user_id, expires_at, used FROM password_reset_tokens WHERE token = ?
            ''', (reset_token,))
            
            token_data = cursor.fetchone()
            if not token_data:
                return False, "Invalid reset token"
                
            user_id, expires_at, used = token_data
            
            # Check if token is used or expired
            if used:
                return False, "Reset token has already been used"
                
            if datetime.fromisoformat(expires_at) < datetime.now():
                return False, "Reset token has expired"
                
            # Update password
            new_hash = self._hash_password(new_password)
            cursor.execute('''
            UPDATE users SET password_hash = ? WHERE id = ?
            ''', (new_hash, user_id))
            
            # Mark token as used
            cursor.execute('''
            UPDATE password_reset_tokens SET used = 1 WHERE token = ?
            ''', (reset_token,))
            
            conn.commit()
            return True, None
            
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            return False, "Failed to reset password"
            
        finally:
            conn.close()
            
    def enable_two_factor(self, user_id: int) -> str:
        """Enable two-factor authentication for a user."""
        import pyotp
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Generate secret
            secret = pyotp.random_base32()
            
            # Enable 2FA
            cursor.execute('''
            UPDATE users SET two_factor_enabled = 1, two_factor_secret = ?
            WHERE id = ?
            ''', (secret, user_id))
            
            conn.commit()
            return secret
            
        finally:
            conn.close()
            
    def verify_two_factor(self, user_id: int, token: str) -> bool:
        """Verify a two-factor authentication token."""
        import pyotp
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            SELECT two_factor_secret FROM users
            WHERE id = ? AND two_factor_enabled = 1
            ''', (user_id,))
            
            secret_data = cursor.fetchone()
            if not secret_data:
                return False
                
            secret = secret_data[0]
            totp = pyotp.TOTP(secret)
            return totp.verify(token)
            
        finally:
            conn.close()
