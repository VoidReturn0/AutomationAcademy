#!/usr/bin/env python3
"""
Broetje Automation Training Application
Interactive training modules for controls engineers
Author: Site Manager Training Initiative
"""

import sys
import json
import sqlite3
import os
import datetime
import hashlib
import requests
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QProgressBar, QTabWidget,
    QListWidget, QListWidgetItem, QTextEdit, QLineEdit, QComboBox,
    QCheckBox, QGroupBox, QFrame, QScrollArea, QDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QSpinBox, QDateEdit, QTimeEdit,
    QTextBrowser, QSplitter, QTreeWidget, QTreeWidgetItem, QMessageBox,
    QFileDialog, QInputDialog
)
from PySide6.QtCore import (
    Qt, QTimer, QThread, QObject, Signal, QPropertyAnimation,
    QEasingCurve, QRect, QSize, QDate, QTime, QDateTime
)
from PySide6.QtGui import (
    QFont, QPixmap, QIcon, QPalette, QColor, QLinearGradient,
    QBrush, QPainter, QAction, QKeySequence
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ModuleDownloader(QThread):
    """Thread for downloading training modules from GitHub"""
    progress_updated = Signal(str, int)
    download_complete = Signal(str, bool)
    
    def __init__(self, github_url: str, module_name: str):
        super().__init__()
        self.github_url = github_url
        self.module_name = module_name
        
    def run(self):
        try:
            # Download module from GitHub
            response = requests.get(self.github_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded += len(chunk)
                        progress = int((downloaded / total_size) * 100)
                        self.progress_updated.emit(self.module_name, progress)
                
                # Extract module
                with zipfile.ZipFile(temp_file.name, 'r') as zip_ref:
                    zip_ref.extractall(f'modules/{self.module_name}')
                
                os.unlink(temp_file.name)
                self.download_complete.emit(self.module_name, True)
                
        except Exception as e:
            logger.error(f"Error downloading module {self.module_name}: {e}")
            self.download_complete.emit(self.module_name, False)

class DatabaseManager:
    """Handle all database operations"""
    
    def __init__(self, db_path: str = "training_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                role TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        ''')
        
        # Training modules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                version TEXT,
                prerequisites TEXT,
                estimated_duration INTEGER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # User progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                module_id INTEGER,
                status TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                score INTEGER,
                verification_signature TEXT,
                trainer_id INTEGER,
                notes TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (module_id) REFERENCES modules (id),
                FOREIGN KEY (trainer_id) REFERENCES users (id)
            )
        ''')
        
        # Module tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_tasks (
                id INTEGER PRIMARY KEY,
                module_id INTEGER,
                task_name TEXT NOT NULL,
                task_description TEXT,
                required BOOLEAN DEFAULT True,
                order_index INTEGER,
                FOREIGN KEY (module_id) REFERENCES modules (id)
            )
        ''')
        
        # Task completions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_completions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                task_id INTEGER,
                completed BOOLEAN DEFAULT False,
                completion_time TIMESTAMP,
                screenshot_path TEXT,
                signature_path TEXT,
                verified_by INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (task_id) REFERENCES module_tasks (id),
                FOREIGN KEY (verified_by) REFERENCES users (id)
            )
        ''')
        
        # System settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                description TEXT
            )
        ''')
        
        # Database migrations
        self.run_migrations(conn)
        
        conn.commit()
        conn.close()
        
        # Create default admin user if not exists
        self.create_default_admin()
    
    def run_migrations(self, conn):
        """Run database migrations to add missing columns"""
        cursor = conn.cursor()
        
        # Check if github_token column exists in users table
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'github_token' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN github_token TEXT')
            print("Added github_token column to users table")
        
        if 'has_github_access' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN has_github_access BOOLEAN DEFAULT 0')
            print("Added has_github_access column to users table")
    
    def create_default_admin(self):
        """Create default admin user"""
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users (username, full_name, role, password_hash)
            VALUES (?, ?, ?, ?)
        ''', ("admin", "System Administrator", "admin", admin_password))
        
        conn.commit()
        conn.close()
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user login"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, full_name, role, github_token, has_github_access
            FROM users 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'full_name': result[2],
                'role': result[3],
                'github_token': result[4],
                'has_github_access': result[5] if len(result) > 5 else bool(result[4])
            }
        return None
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def get_user_progress(self, user_id: int) -> List[Dict]:
        """Get training progress for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT m.name, up.status, up.start_time, up.end_time, up.score
            FROM user_progress up
            JOIN modules m ON up.module_id = m.id
            WHERE up.user_id = ?
            ORDER BY up.start_time DESC
        ''', (user_id,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'module': row[0],
                'status': row[1],
                'start_time': row[2],
                'end_time': row[3],
                'score': row[4]
            }
            for row in results
        ]

class StyleManager:
    """Manage application styling and themes"""
    
    @staticmethod
    def apply_broetje_theme(app: QApplication):
        """Apply professional Broetje-style theme"""
        app.setStyle('Fusion')
        
        # Define color palette
        palette = QPalette()
        
        # Primary colors - Professional blue and grey
        primary_blue = QColor(41, 128, 185)  # Broetje blue
        dark_grey = QColor(52, 73, 94)
        light_grey = QColor(236, 240, 241)
        white = QColor(255, 255, 255)
        
        # Apply colors
        palette.setColor(QPalette.Window, light_grey)
        palette.setColor(QPalette.WindowText, dark_grey)
        palette.setColor(QPalette.Base, white)
        palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
        palette.setColor(QPalette.ToolTipBase, white)
        palette.setColor(QPalette.ToolTipText, dark_grey)
        palette.setColor(QPalette.Text, dark_grey)
        palette.setColor(QPalette.Button, QColor(230, 230, 230))
        palette.setColor(QPalette.ButtonText, dark_grey)
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, primary_blue)
        palette.setColor(QPalette.Highlight, primary_blue)
        palette.setColor(QPalette.HighlightedText, white)
        
        app.setPalette(palette)
        
        # Set application-wide stylesheet
        stylesheet = """
        QMainWindow {
            background-color: #ecf0f1;
        }
        
        QLineEdit {
            border: 2px solid #cccccc;
            border-radius: 4px;
            padding: 5px;
            font-size: 14px;
        }
        
        QLineEdit:focus {
            border: 2px solid #ED1C24;
        }
        
        QPushButton {
            background-color: #ED1C24;
            border: none;
            color: white;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            border-radius: 4px;
        }
        
        QPushButton:hover {
            background-color: #CC0000;
        }
        
        QPushButton:pressed {
            background-color: #990000;
        }
        
        QPushButton:disabled {
            background-color: #bdc3c7;
            color: #7f8c8d;
        }
        
        QTabWidget::pane {
            border: 1px solid #bdc3c7;
            background-color: white;
        }
        
        QTabBar::tab {
            background-color: #ecf0f1;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: #3498db;
            color: white;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            margin: 10px 0;
            padding-top: 15px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 10px 0 10px;
        }
        
        QProgressBar {
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #ED1C24;
            border-radius: 3px;
        }
        
        QListWidget {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            background-color: white;
        }
        
        QListWidget::item {
            padding: 8px;
            border-bottom: 1px solid #ecf0f1;
        }
        
        QListWidget::item:selected {
            background-color: #3498db;
            color: white;
        }
        
        QLineEdit, QTextEdit, QComboBox {
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            padding: 5px;
            background-color: white;
        }
        
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
            border: 2px solid #3498db;
        }
        """
        
        app.setStyleSheet(stylesheet)

class LoginDialog(QDialog):
    """Professional login dialog"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.user_data = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("Broetje Training System - Login")
        self.setFixedSize(720, 600)  # Increased size by 20%
        self.setModal(True)
        
        # Set dialog icon
        icon_path = Path("resources/icons/broetje_icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        layout = QVBoxLayout()
        
        # Logo/Header with logo image
        header_layout = QVBoxLayout()
        
        # Add the Broetje logo if available
        logo_path = Path("resources/icons/broetje_icon.png")
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            # Scale the logo to a reasonable size
            scaled_pixmap = pixmap.scaled(300, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(logo_label)
            header_layout.addSpacing(10)
        
        header = QLabel("Training System")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #000000;
                padding: 20px;
            }
        """)
        header_layout.addWidget(header)
        layout.addLayout(header_layout)
        
        # Login form
        form_group = QGroupBox("Login Credentials")
        form_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
                margin: 20px;
            }
        """)
        form_layout = QVBoxLayout()
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username")
        self.username_edit.setMinimumHeight(40)
        self.username_edit.setStyleSheet("font-size: 16px; padding: 5px;")
        username_label = QLabel("Username:")
        username_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        form_layout.addWidget(username_label)
        form_layout.addWidget(self.username_edit)
        form_layout.addSpacing(35)  # Increased spacing between username and password
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(40)
        self.password_edit.setStyleSheet("font-size: 16px; padding: 5px;")
        password_label = QLabel("Password:")
        password_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        form_layout.addWidget(password_label)
        form_layout.addWidget(self.password_edit)
        form_layout.addSpacing(30)  # Additional spacing after password field
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.authenticate)
        self.login_button.setDefault(True)
        self.login_button.setMinimumHeight(45)
        self.login_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #ED1C24;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #CC0000;
            }
            QPushButton:pressed {
                background-color: #990000;
            }
        """)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setMinimumHeight(45)
        cancel_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
        """)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(self.login_button)
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        self.status_label.setMinimumHeight(30)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        # Connect enter key
        self.password_edit.returnPressed.connect(self.authenticate)
        
    def authenticate(self):
        """Authenticate user"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            self.status_label.setText("Please enter both username and password")
            return
        
        self.user_data = self.db_manager.authenticate_user(username, password)
        
        if self.user_data:
            self.accept()
        else:
            self.status_label.setText("Invalid credentials")
            self.password_edit.clear()
            self.password_edit.setFocus()

class ModuleManager:
    """Manage training modules"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.modules_dir = Path("modules")
        self.modules_dir.mkdir(exist_ok=True)
        self.init_default_modules()
    
    def init_default_modules(self):
        """Initialize default training modules"""
        default_modules = [
            {
                "name": "Network File Sharing & Mapping",
                "description": "Learn to map network drives and share files across the automation network",
                "version": "1.0",
                "prerequisites": "",
                "estimated_duration": 30
            },
            {
                "name": "Command Line Network Diagnostics",
                "description": "Master command line tools for network troubleshooting",
                "version": "1.0",
                "prerequisites": "Network File Sharing & Mapping",
                "estimated_duration": 45
            },
            {
                "name": "IP Address Configuration",
                "description": "Configure IP addresses for automation networks (192.168.214.x, 192.168.213.x, 192.168.1.x)",
                "version": "1.0",
                "prerequisites": "Command Line Network Diagnostics",
                "estimated_duration": 40
            },
            {
                "name": "Hard Drive Management",
                "description": "Manage hard drives, partitions, and storage systems",
                "version": "1.0",
                "prerequisites": "",
                "estimated_duration": 35
            },
            {
                "name": "Backup/Restore Operations",
                "description": "Perform backup and restore operations using Paragon software",
                "version": "1.0",
                "prerequisites": "Hard Drive Management",
                "estimated_duration": 60
            },
            {
                "name": "Hard Drive Replacement",
                "description": "Replace SSDs using proper Torx tools and procedures",
                "version": "1.0",
                "prerequisites": "Hard Drive Management,Backup/Restore Operations",
                "estimated_duration": 45
            },
            {
                "name": "Remote Access Configuration",
                "description": "Set up UltraVNC for remote access (password: ae746)",
                "version": "1.0",
                "prerequisites": "IP Address Configuration",
                "estimated_duration": 30
            },
            {
                "name": "Batch File Scripting",
                "description": "Create and execute batch files for automation tasks",
                "version": "1.0",
                "prerequisites": "Command Line Network Diagnostics",
                "estimated_duration": 50
            },
            {
                "name": "PowerShell Scripting",
                "description": "Advanced scripting with PowerShell for system administration",
                "version": "1.0",
                "prerequisites": "Batch File Scripting",
                "estimated_duration": 75
            },
            {
                "name": "OneDrive Integration",
                "description": "Integrate OneDrive with automation systems for cloud backup",
                "version": "1.0",
                "prerequisites": "Backup/Restore Operations",
                "estimated_duration": 25
            }
        ]
        
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        for module in default_modules:
            cursor.execute('''
                INSERT OR IGNORE INTO modules 
                (name, description, version, prerequisites, estimated_duration)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                module["name"],
                module["description"],
                module["version"],
                module["prerequisites"],
                module["estimated_duration"]
            ))
        
        conn.commit()
        conn.close()

class AddUserDialog(QDialog):
    """Dialog for adding new users"""
    
    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Add New User")
        self.setFixedSize(450, 400)
        
        layout = QVBoxLayout()
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Username")
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_edit)
        
        # Full name
        self.fullname_edit = QLineEdit()
        self.fullname_edit.setPlaceholderText("Full Name")
        layout.addWidget(QLabel("Full Name:"))
        layout.addWidget(self.fullname_edit)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["trainee", "trainer", "admin"])
        layout.addWidget(QLabel("Role:"))
        layout.addWidget(self.role_combo)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Password")
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_edit)
        
        # GitHub Access Token
        self.github_token_edit = QLineEdit()
        self.github_token_edit.setEchoMode(QLineEdit.Password)
        self.github_token_edit.setPlaceholderText("GitHub Personal Access Token (optional)")
        layout.addWidget(QLabel("GitHub Access Token:"))
        layout.addWidget(self.github_token_edit)
        info_label = QLabel("Note: Without a GitHub token, only default modules will be available")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_user)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def save_user(self):
        """Save the new user"""
        username = self.username_edit.text().strip()
        fullname = self.fullname_edit.text().strip()
        role = self.role_combo.currentText()
        password = self.password_edit.text()
        github_token = self.github_token_edit.text().strip()
        
        if not all([username, fullname, password]):
            QMessageBox.warning(self, "Invalid Input", "Please fill all fields")
            return
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            has_github_access = bool(github_token)
            cursor.execute('''
                INSERT INTO users (username, full_name, role, password_hash, github_token, has_github_access)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (username, fullname, role, password_hash, github_token, has_github_access))
            conn.commit()
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add user: {e}")
        finally:
            conn.close()

class EditUserDialog(QDialog):
    """Dialog for editing existing users"""
    
    def __init__(self, db_manager: DatabaseManager, username: str):
        super().__init__()
        self.db_manager = db_manager
        self.original_username = username
        self.setup_ui()
        self.load_user_data()
    
    def setup_ui(self):
        self.setWindowTitle("Edit User")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Username (read-only)
        self.username_edit = QLineEdit()
        self.username_edit.setReadOnly(True)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_edit)
        
        # Full name
        self.fullname_edit = QLineEdit()
        layout.addWidget(QLabel("Full Name:"))
        layout.addWidget(self.fullname_edit)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["trainee", "trainer", "admin"])
        layout.addWidget(QLabel("Role:"))
        layout.addWidget(self.role_combo)
        
        # New password (optional)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("New Password (optional)")
        layout.addWidget(QLabel("New Password:"))
        layout.addWidget(self.password_edit)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_user)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def load_user_data(self):
        """Load existing user data"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, full_name, role 
            FROM users 
            WHERE username = ?
        ''', (self.original_username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            self.username_edit.setText(result[0])
            self.fullname_edit.setText(result[1])
            self.role_combo.setCurrentText(result[2])
    
    def save_user(self):
        """Save the updated user data"""
        fullname = self.fullname_edit.text().strip()
        role = self.role_combo.currentText()
        password = self.password_edit.text()
        
        if not fullname:
            QMessageBox.warning(self, "Invalid Input", "Full name cannot be empty")
            return
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            if password:
                # Update with new password
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute('''
                    UPDATE users 
                    SET full_name = ?, role = ?, password_hash = ?
                    WHERE username = ?
                ''', (fullname, role, password_hash, self.original_username))
            else:
                # Update without changing password
                cursor.execute('''
                    UPDATE users 
                    SET full_name = ?, role = ?
                    WHERE username = ?
                ''', (fullname, role, self.original_username))
            
            conn.commit()
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update user: {e}")
        finally:
            conn.close()

class TrainingDashboard(QMainWindow):
    """Main training application window"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.module_manager = ModuleManager(self.db_manager)
        self.current_user = None
        self.setup_ui()
        self.setup_menu()
        self.login_user()
        
    def setup_ui(self):
        """Setup main UI"""
        self.setWindowTitle("Broetje Automation Training System")
        self.setMinimumSize(1200, 800)
        
        # Set application icon
        icon_path = Path("resources/icons/broetje_icon.png")
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header with Broetje branding
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #ED1C24;
                color: white;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        
        # Add logo to header if available
        logo_path = Path("resources/icons/broetje_icon.png")
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            scaled_pixmap = pixmap.scaled(180, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            header_layout.addWidget(logo_label)
            header_layout.addSpacing(20)
        
        title_label = QLabel("Training System")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # User info
        self.user_label = QLabel()
        self.user_label.setStyleSheet("color: white; font-size: 14px;")
        header_layout.addWidget(self.user_label)
        
        main_layout.addWidget(header_frame)
        
        # Tab widget with Broetje styling
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: black;
                padding: 10px 20px;
                margin-right: 2px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #ED1C24;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #ffcccc;
            }
        """)
        main_layout.addWidget(self.tabs)
        
        # Dashboard tab
        self.setup_dashboard_tab()
        
        # Training modules tab
        self.setup_modules_tab()
        
        # Progress tab
        self.setup_progress_tab()
        
        # Admin tab (only for admin users)
        self.admin_tab = None
        
    def setup_menu(self):
        """Setup application menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        
        download_modules_action = QAction('Download Modules', self)
        download_modules_action.triggered.connect(self.show_module_download)
        tools_menu.addAction(download_modules_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_dashboard_tab(self):
        """Setup dashboard tab"""
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Create content widget
        dashboard_widget = QWidget()
        layout = QVBoxLayout(dashboard_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Welcome message
        welcome_group = QGroupBox("Welcome")
        welcome_layout = QVBoxLayout(welcome_group)
        
        welcome_text = QTextBrowser()
        welcome_text.setMaximumHeight(150)
        welcome_text.setHtml("""
        <h2>Welcome to Broetje Automation Training System</h2>
        <p>This system provides comprehensive training for controls engineers working with our advanced automation systems.</p>
        <p><strong>Company Systems:</strong></p>
        <ul>
            <li>12 PowerRACe robotic drilling arms</li>
            <li>11 MPAC systems (Multi Panel Assembly Cells)</li>
            <li>2 IPAC systems (Integrated Panel Assembly Cells)</li>
        </ul>
        """)
        welcome_layout.addWidget(welcome_text)
        layout.addWidget(welcome_group)
        
        # Quick stats
        stats_group = QGroupBox("Training Overview")
        stats_layout = QGridLayout(stats_group)
        
        self.total_modules_label = QLabel("10")
        self.completed_modules_label = QLabel("0")
        self.in_progress_label = QLabel("0")
        self.remaining_label = QLabel("10")
        
        stats_layout.addWidget(QLabel("Total Modules:"), 0, 0)
        stats_layout.addWidget(self.total_modules_label, 0, 1)
        stats_layout.addWidget(QLabel("Completed:"), 0, 2)
        stats_layout.addWidget(self.completed_modules_label, 0, 3)
        stats_layout.addWidget(QLabel("In Progress:"), 1, 0)
        stats_layout.addWidget(self.in_progress_label, 1, 1)
        stats_layout.addWidget(QLabel("Remaining:"), 1, 2)
        stats_layout.addWidget(self.remaining_label, 1, 3)
        
        layout.addWidget(stats_group)
        
        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        start_next_button = QPushButton("Start Next Module")
        start_next_button.clicked.connect(self.start_next_module)
        actions_layout.addWidget(start_next_button)
        
        view_progress_button = QPushButton("View Progress")
        view_progress_button.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        actions_layout.addWidget(view_progress_button)
        
        actions_layout.addStretch()
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        # Set the content widget for the scroll area
        scroll_area.setWidget(dashboard_widget)
        
        # Add the scroll area to the tab widget
        self.tabs.addTab(scroll_area, "Dashboard")
    
    def setup_modules_tab(self):
        """Setup training modules tab"""
        modules_widget = QWidget()
        layout = QVBoxLayout(modules_widget)
        
        # Module list
        self.modules_list = QListWidget()
        self.modules_list.itemDoubleClicked.connect(self.open_module)
        layout.addWidget(self.modules_list)
        
        # Module details
        details_group = QGroupBox("Module Details")
        details_layout = QVBoxLayout(details_group)
        
        self.module_description = QTextBrowser()
        self.module_description.setMaximumHeight(100)
        details_layout.addWidget(self.module_description)
        
        # Module actions
        actions_layout = QHBoxLayout()
        
        self.start_module_button = QPushButton("Start Module")
        self.start_module_button.clicked.connect(self.start_selected_module)
        self.start_module_button.setEnabled(False)
        actions_layout.addWidget(self.start_module_button)
        
        actions_layout.addStretch()
        details_layout.addLayout(actions_layout)
        
        layout.addWidget(details_group)
        self.tabs.addTab(modules_widget, "Training Modules")
        
        # Load modules
        self.load_modules()
    
    def setup_progress_tab(self):
        """Setup progress tracking tab"""
        progress_widget = QWidget()
        layout = QVBoxLayout(progress_widget)
        
        # Progress table
        self.progress_table = QTableWidget()
        self.progress_table.setColumnCount(5)
        self.progress_table.setHorizontalHeaderLabels([
            "Module", "Status", "Start Time", "End Time", "Score"
        ])
        self.progress_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.progress_table)
        
        # Overall progress
        overall_group = QGroupBox("Overall Progress")
        overall_layout = QHBoxLayout(overall_group)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setTextVisible(True)
        overall_layout.addWidget(QLabel("Completion:"))
        overall_layout.addWidget(self.overall_progress)
        
        layout.addWidget(overall_group)
        self.tabs.addTab(progress_widget, "Progress")
    
    def setup_admin_tab(self):
        """Setup admin tab (only for admin users)"""
        if self.current_user and self.current_user['role'] == 'admin':
            admin_widget = QWidget()
            layout = QVBoxLayout(admin_widget)
            
            # User management
            user_group = QGroupBox("User Management")
            user_layout = QVBoxLayout(user_group)
            
            # User actions
            user_actions = QHBoxLayout()
            
            add_user_button = QPushButton("Add User")
            add_user_button.clicked.connect(self.add_user)
            user_actions.addWidget(add_user_button)
            
            edit_user_button = QPushButton("Edit User")
            edit_user_button.clicked.connect(self.edit_user)
            user_actions.addWidget(edit_user_button)
            
            user_actions.addStretch()
            user_layout.addLayout(user_actions)
            
            # Users table
            self.users_table = QTableWidget()
            self.users_table.setColumnCount(4)
            self.users_table.setHorizontalHeaderLabels([
                "Username", "Full Name", "Role", "Last Login"
            ])
            user_layout.addWidget(self.users_table)
            
            layout.addWidget(user_group)
            
            # System settings
            settings_group = QGroupBox("System Settings")
            settings_layout = QVBoxLayout(settings_group)
            
            # GitHub settings
            github_layout = QHBoxLayout()
            github_layout.addWidget(QLabel("GitHub Repository:"))
            self.github_url_edit = QLineEdit("https://github.com/your-org/training-modules")
            github_layout.addWidget(self.github_url_edit)
            
            save_settings_button = QPushButton("Save Settings")
            save_settings_button.clicked.connect(self.save_settings)
            github_layout.addWidget(save_settings_button)
            
            settings_layout.addLayout(github_layout)
            layout.addWidget(settings_group)
            
            self.tabs.addTab(admin_widget, "Administration")
            self.load_users()
    
    def login_user(self):
        """Handle user login"""
        login_dialog = LoginDialog(self.db_manager)
        if login_dialog.exec() == QDialog.Accepted:
            self.current_user = login_dialog.user_data
            self.user_label.setText(f"Welcome, {self.current_user['full_name']} ({self.current_user['role']})")
            
            # Setup admin tab if admin user
            if self.current_user['role'] == 'admin':
                self.setup_admin_tab()
            
            # Load user-specific data
            self.load_user_progress()
            
            # Show window in full screen after successful login
            self.showFullScreen()
        else:
            sys.exit()
    
    def load_modules(self):
        """Load available training modules"""
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        # Define default modules available without GitHub access
        # When using API token or deploy key, all modules are available
        from config_manager import get_config_manager
        config_manager = get_config_manager()
        
        # Check if we have any form of GitHub access (API token or deploy key)
        has_api_access = bool(config_manager.get('github.api_token') or config_manager.get_deploy_key())
        
        if has_api_access:
            default_modules = []  # All modules available with API access
        else:
            default_modules = [
                'Network File Sharing & Mapping',
                'Command Line Network Diagnostics',
                'IP Address Configuration'
            ]
        
        cursor.execute('''
            SELECT id, name, description, prerequisites, estimated_duration
            FROM modules
            ORDER BY id
        ''')
        
        modules = cursor.fetchall()
        conn.close()
        
        self.modules_list.clear()
        
        # Check if user has GitHub access (default to True if no user logged in yet)
        # If API token or deploy key is available, treat all users as having GitHub access
        if has_api_access:
            has_github_access = True
        else:
            has_github_access = True if self.current_user is None else self.current_user.get('has_github_access', False)
        
        for module in modules:
            module_name = module[1]
            
            # Filter modules based on GitHub access
            if not has_github_access and module_name not in default_modules:
                continue
                
            item = QListWidgetItem(f"{module[1]} ({module[4]} min)")
            item.setData(Qt.UserRole, module)
            
            # Add visual indicator for premium modules
            if module_name not in default_modules:
                item.setText(f"⭐ {module[1]} ({module[4]} min)")
            
            self.modules_list.addItem(item)
        
        # Add message if user doesn't have full access
        if not has_github_access:
            no_access_item = QListWidgetItem("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            no_access_item.setFlags(Qt.NoItemFlags)
            self.modules_list.addItem(no_access_item)
            
            info_item = QListWidgetItem("🔒 Additional modules require GitHub access")
            info_item.setFlags(Qt.NoItemFlags)
            self.modules_list.addItem(info_item)
        
        # Connect selection handler
        self.modules_list.itemSelectionChanged.connect(self.module_selected)
    
    def module_selected(self):
        """Handle module selection"""
        current_item = self.modules_list.currentItem()
        if current_item:
            module_data = current_item.data(Qt.UserRole)
            description = f"""
            <h3>{module_data[1]}</h3>
            <p>{module_data[2]}</p>
            <p><strong>Prerequisites:</strong> {module_data[3] or 'None'}</p>
            <p><strong>Estimated Duration:</strong> {module_data[4]} minutes</p>
            """
            self.module_description.setHtml(description)
            self.start_module_button.setEnabled(True)
    
    def start_selected_module(self):
        """Start the selected training module"""
        current_item = self.modules_list.currentItem()
        if current_item:
            module_data = current_item.data(Qt.UserRole)
            self.open_module(current_item)
    
    def start_next_module(self):
        """Start the next available module"""
        # Find the first incomplete module
        if self.modules_list.count() > 0:
            self.modules_list.setCurrentRow(0)
            self.start_selected_module()
    
    def load_module_metadata(self, module_dict):
        """Load complete module data including tasks from metadata.json"""
        import json
        
        # Map module names to directory names
        module_dir_map = {
            'Network File Sharing & Mapping': 'network_file_sharing',
            'Command Line Network Diagnostics': 'cli_diagnostics',
            'IP Address Configuration': 'ip_configuration',
            'Backup/Restore Operations': 'backup_restore',
            'Hard Drive Replacement': 'drive_replacement',
            'Remote Access Configuration': 'remote_access',
            'PowerShell Scripting': 'powershell_scripting'
        }
        
        dir_name = module_dir_map.get(module_dict['name'])
        if dir_name:
            # Try to load metadata.json
            metadata_path = Path(f"modules/{dir_name}/metadata.json")
            if metadata_path.exists():
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        # Merge metadata with module_dict
                        module_dict.update(metadata)
                except Exception as e:
                    print(f"Error loading metadata for {module_dict['name']}: {e}")
        
        # Ensure tasks key exists
        if 'tasks' not in module_dict:
            module_dict['tasks'] = []
        
        return module_dict
    
    def open_module(self, item):
        """Open a training module"""
        module_data = item.data(Qt.UserRole)
        
        # Convert tuple to dict for easier handling
        module_dict = {
            'id': module_data[0],
            'name': module_data[1],
            'description': module_data[2],
            'prerequisites': module_data[3],
            'estimated_duration': module_data[4]
        }
        
        # Load additional module data including tasks from metadata.json
        module_dict = self.load_module_metadata(module_dict)
        
        # Import and create module window
        from module_window import ModuleWindow
        
        self.module_window = ModuleWindow(module_dict, self.current_user, self.db_manager)
        self.module_window.module_completed.connect(self.on_module_completed)
        self.module_window.module_closed.connect(self.on_module_closed)
        # Module window now shows itself in full screen in its __init__ method
        
        # Hide main window while module is running
        self.hide()
    
    def on_module_completed(self, module_name: str, completion_data: dict):
        """Handle module completion"""
        # Refresh progress data
        self.load_user_progress()
        
        # Show main window again
        self.show()
        
        # Show completion notification
        QMessageBox.information(
            self,
            "Module Completed",
            f"Module '{module_name}' completed successfully!\n"
            f"Score: {completion_data.get('score', 0)}%"
        )
    
    def on_module_closed(self):
        """Handle module window closing"""
        # Show main window again
        self.show()
        
        # Refresh progress data
        self.load_user_progress()
    
    def load_user_progress(self):
        """Load current user's progress"""
        if not self.current_user:
            return
        
        progress = self.db_manager.get_user_progress(self.current_user['id'])
        
        # Update dashboard stats
        completed = len([p for p in progress if p['status'] == 'completed'])
        in_progress = len([p for p in progress if p['status'] == 'in_progress'])
        total = 10  # Total modules
        
        self.completed_modules_label.setText(str(completed))
        self.in_progress_label.setText(str(in_progress))
        self.remaining_label.setText(str(total - completed - in_progress))
        
        # Update progress table
        self.progress_table.setRowCount(len(progress))
        for i, item in enumerate(progress):
            self.progress_table.setItem(i, 0, QTableWidgetItem(item['module']))
            self.progress_table.setItem(i, 1, QTableWidgetItem(item['status'].title()))
            self.progress_table.setItem(i, 2, QTableWidgetItem(item['start_time'] or ''))
            self.progress_table.setItem(i, 3, QTableWidgetItem(item['end_time'] or ''))
            self.progress_table.setItem(i, 4, QTableWidgetItem(str(item['score'] or '')))
        
        # Update overall progress bar
        completion_percentage = int((completed / total) * 100)
        self.overall_progress.setValue(completion_percentage)
    
    def load_users(self):
        """Load users for admin view"""
        if not hasattr(self, 'users_table'):
            return
        
        conn = sqlite3.connect(self.db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT username, full_name, role, last_login
            FROM users
            ORDER BY username
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        self.users_table.setRowCount(len(users))
        for i, user in enumerate(users):
            self.users_table.setItem(i, 0, QTableWidgetItem(user[0]))
            self.users_table.setItem(i, 1, QTableWidgetItem(user[1]))
            self.users_table.setItem(i, 2, QTableWidgetItem(user[2]))
            self.users_table.setItem(i, 3, QTableWidgetItem(user[3] or 'Never'))
    
    def add_user(self):
        """Add new user"""
        dialog = AddUserDialog(self.db_manager)
        if dialog.exec() == QDialog.Accepted:
            self.load_users()
            QMessageBox.information(self, "Success", "User added successfully!")
    
    def edit_user(self):
        """Edit existing user"""
        current_row = self.users_table.currentRow()
        if current_row >= 0:
            username = self.users_table.item(current_row, 0).text()
            dialog = EditUserDialog(self.db_manager, username)
            if dialog.exec() == QDialog.Accepted:
                self.load_users()
                QMessageBox.information(self, "Success", "User updated successfully!")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a user to edit.")
    
    def save_settings(self):
        """Save system settings"""
        QMessageBox.information(self, "Settings", "Settings saved successfully.")
    
    def show_module_download(self):
        """Show module download dialog"""
        from github_integration import GitHubModuleDialog, load_github_config
        
        github_config = load_github_config()
        dialog = GitHubModuleDialog(github_config, self.db_manager)
        
        if dialog.exec() == QDialog.Accepted:
            # Refresh modules list if any were downloaded
            self.load_modules()
            QMessageBox.information(
                self,
                "Modules Updated",
                "Module list has been refreshed with any newly downloaded modules."
            )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About",
            """
            <h2>Broetje Automation Training System</h2>
            <p>Version 1.0</p>
            <p>A comprehensive training platform for controls engineers.</p>
            <p>Developed for Broetje Automation USA, Savannah, GA</p>
            """
        )
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.close()
    
    def closeEvent(self, event):
        """Handle application close"""
        logger.info("Application shutting down")
        event.accept()

def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Broetje Training System")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Broetje Automation USA")
    
    # Apply custom styling
    StyleManager.apply_broetje_theme(app)
    
    # Create main window (it will show itself after login)
    window = TrainingDashboard()
    
    # Run application
    sys.exit(app.exec())

if __name__ == "__main__":
    main()