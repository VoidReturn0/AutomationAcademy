#!/usr/bin/env python3
"""
Module Window - Individual training module execution
Handles the interactive training session for a specific module
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import qrcode
import io

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QProgressBar, QTabWidget, QTextEdit, QFrame, QGroupBox,
    QListWidget, QListWidgetItem, QScrollArea, QFileDialog, QApplication,
    QCheckBox, QSpinBox, QComboBox, QTimeEdit, QDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, QTime, QThread
from PySide6.QtGui import QFont, QPixmap, QCloseEvent

from training_module import get_module_class, TrainingModule
from completion_tracker import CompletionTracker

class ScreenshotHandler(QThread):
    """Handle screenshot capture in background thread"""
    screenshot_captured = Signal(str, str)  # task_id, file_path
    
    def __init__(self, task_id: str):
        super().__init__()
        self.task_id = task_id
    
    def run(self):
        """Capture desktop screenshot"""
        try:
            # Get primary screen
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0)
            
            # Create screenshots directory
            screenshots_dir = Path("screenshots")
            screenshots_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.task_id}_{timestamp}.png"
            file_path = screenshots_dir / filename
            
            # Save screenshot
            screenshot.save(str(file_path), "PNG")
            
            self.screenshot_captured.emit(self.task_id, str(file_path))
            
        except Exception as e:
            print(f"Screenshot error: {e}")

class QRCodeGenerator:
    """Generate QR codes for quick module access"""
    
    @staticmethod
    def generate_module_qr(module_name: str, module_id: str) -> str:
        """Generate QR code for module quick access"""
        qr_data = f"broetje://module/{module_id}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for storage
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return img_str

class ModuleWindow(QMainWindow):
    """Window for individual training module execution"""
    module_completed = Signal(str, dict)
    module_closed = Signal()
    
    def __init__(self, module_data: Dict, user_data: Dict, db_manager):
        super().__init__()
        self.module_data = module_data
        self.user_data = user_data
        self.db_manager = db_manager
        self.training_module = None
        self.screenshots = {}
        self.screenshot_paths = []
        self.start_time = datetime.now()
        
        # Initialize completion tracker
        self.init_completion_tracker()
        
        self.setup_ui()
        self.load_module()
        
        # Show window in full screen
        self.showFullScreen()
        
        # Track window state
        self.module_completed.connect(self.on_module_completed)
    
    def init_completion_tracker(self):
        """Initialize the completion tracking system"""
        import json
        
        # Load GitHub configuration
        try:
            with open('config/github_config.json', 'r') as f:
                github_config = json.load(f)
                
            completion_config = github_config.get('completion_tracking', {})
            
            if completion_config.get('enabled', False):
                self.completion_tracker = CompletionTracker(completion_config)
            else:
                self.completion_tracker = None
        except Exception as e:
            print(f"Error initializing completion tracker: {e}")
            self.completion_tracker = None
    
    def setup_ui(self):
        """Setup the module window UI"""
        self.setWindowTitle(f"Training Module: {self.module_data['name']}")
        self.setMinimumSize(1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Header with module info
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                color: white;
                padding: 15px;
                border-radius: 5px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        # Title
        title_label = QLabel(self.module_data['name'])
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)
        
        # Module info
        info_layout = QHBoxLayout()
        
        info_text = (
            f"Duration: {self.module_data.get('estimated_duration', 0)} minutes | "
            f"User: {self.user_data['full_name']} | "
            f"Started: {self.start_time.strftime('%H:%M:%S')}"
        )
        info_label = QLabel(info_text)
        info_label.setStyleSheet("color: #ecf0f1; font-size: 12px;")
        info_layout.addWidget(info_label)
        
        info_layout.addStretch()
        
        # QR Code button
        qr_button = QPushButton("Generate QR Code")
        qr_button.clicked.connect(self.show_qr_code)
        qr_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
        """)
        info_layout.addWidget(qr_button)
        
        header_layout.addLayout(info_layout)
        layout.addWidget(header_frame)
        
        # Module content area
        self.module_container = QWidget()
        layout.addWidget(self.module_container)
        
        # Footer with controls
        footer_layout = QHBoxLayout()
        
        # Exit button
        exit_button = QPushButton("Exit Module")
        exit_button.clicked.connect(self.confirm_exit)
        exit_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        footer_layout.addWidget(exit_button)
        
        footer_layout.addStretch()
        
        # Help button
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.show_help)
        footer_layout.addWidget(help_button)
        
        layout.addLayout(footer_layout)
    
    def load_module(self):
        """Load and initialize the training module"""
        module_class = get_module_class(self.module_data['name'])
        
        if module_class:
            # Create module instance with db_manager if it's required
            try:
                import inspect
                sig = inspect.signature(module_class.__init__)
                if 'db_manager' in sig.parameters:
                    self.training_module = module_class(self.module_data, self.user_data, self.db_manager)
                else:
                    self.training_module = module_class(self.module_data, self.user_data)
            except Exception as e:
                print(f"Error creating module instance: {e}")
                # Fallback to basic instantiation
                self.training_module = module_class(self.module_data, self.user_data)
            
            # Connect signals
            self.training_module.module_completed.connect(self.module_completed)
            self.training_module.progress_updated.connect(self.on_progress_updated)
            
            # Add to container
            container_layout = QVBoxLayout(self.module_container)
            container_layout.addWidget(self.training_module)
            
            # Connect screenshot handler
            if hasattr(self.training_module, 'tasks'):
                for task_id, task_data in self.training_module.tasks.items():
                    task_widget = task_data['widget']
                    task_widget.screenshot_requested.connect(self.handle_screenshot)
            
            # Start module session in database
            self.start_module_session()
        else:
            QMessageBox.warning(
                self,
                "Module Error",
                f"Could not load module '{self.module_data['name']}'"
            )
            self.close()
    
    def start_module_session(self):
        """Start a new module session in the database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_progress (user_id, module_id, status, start_time)
                VALUES (?, ?, ?, ?)
            ''', (
                self.user_data['id'],
                self.module_data['id'],
                'in_progress',
                self.start_time.isoformat()
            ))
            conn.commit()
            self.session_id = cursor.lastrowid
            
        except Exception as e:
            print(f"Error starting module session: {e}")
        finally:
            conn.close()
    
    def handle_screenshot(self, task_id: str):
        """Handle screenshot capture request"""
        # Capture screenshot immediately without initial popup
        self.screenshot_thread = ScreenshotHandler(task_id)
        self.screenshot_thread.screenshot_captured.connect(self.on_screenshot_captured)
        self.screenshot_thread.start()
    
    def on_screenshot_captured(self, task_id: str, file_path: str):
        """Handle screenshot capture completion"""
        final_path = file_path
        
        # Use completion tracker for organized storage
        if self.completion_tracker:
            # Read the screenshot file
            with open(file_path, 'rb') as f:
                screenshot_data = f.read()
            
            # Save with organized naming
            new_path = self.completion_tracker.save_screenshot(
                self.user_data['username'],
                self.module_data['name'],
                task_id,
                screenshot_data
            )
            
            self.screenshots[task_id] = new_path
            self.screenshot_paths.append(new_path)
            final_path = new_path
        else:
            self.screenshots[task_id] = file_path
        
        # Update database with screenshot path
        self.save_task_screenshot(task_id, final_path)
        
        # Single informative message
        task_name = self.get_task_name(task_id)
        filename = Path(final_path).name
        folder = Path(final_path).parent
        
        QMessageBox.information(
            self,
            "Screenshot Captured",
            f"Screenshot for '{task_name}' has been captured.\n\n"
            f"Filename: {filename}\n"
            f"Location: {folder}\n\n"
            f"Your progress has been automatically saved."
        )
    
    def get_task_name(self, task_id: str) -> str:
        """Get the human-readable task name"""
        if hasattr(self.training_module, 'tasks') and task_id in self.training_module.tasks:
            return self.training_module.tasks[task_id]['definition'].get('name', task_id)
        return task_id
    
    def save_task_screenshot(self, task_id: str, file_path: str):
        """Save screenshot path to database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Find or create task completion record
            cursor.execute('''
                INSERT OR REPLACE INTO task_completions 
                (user_id, task_id, screenshot_path, completion_time)
                VALUES (?, ?, ?, ?)
            ''', (
                self.user_data['id'],
                task_id,
                file_path,
                datetime.now().isoformat()
            ))
            conn.commit()
            
        except Exception as e:
            print(f"Error saving screenshot: {e}")
        finally:
            conn.close()
    
    def on_progress_updated(self, progress: int):
        """Handle progress updates from the module"""
        # Could update window title with progress
        self.setWindowTitle(
            f"Training Module: {self.module_data['name']} ({progress}%)"
        )
    
    def on_module_completed(self, module_name: str, completion_data: dict):
        """Handle module completion"""
        # Update database with completion
        self.save_module_completion(completion_data)
        
        # Upload to GitHub if tracker is enabled
        if self.completion_tracker:
            # Create completion report
            report = self.completion_tracker.create_completion_report(
                self.user_data,
                self.module_data,
                completion_data,
                self.screenshot_paths
            )
            
            # Upload to GitHub
            upload_success = self.completion_tracker.upload_to_github(
                report,
                self.screenshot_paths
            )
            
            if upload_success:
                QMessageBox.information(
                    self,
                    "Upload Successful",
                    "Your completion data has been uploaded successfully!"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Upload Failed",
                    "Failed to upload completion data to GitHub.\n"
                    "Your progress has been saved locally."
                )
        
        # Show completion dialog
        QMessageBox.information(
            self,
            "Module Completed",
            f"Congratulations! You have successfully completed the module:\n"
            f"{module_name}\n\n"
            f"Score: {completion_data.get('score', 0)}%\n"
            f"Time taken: {completion_data.get('elapsed_time', 0)} seconds"
        )
        
        # Close the window
        self.close()
    
    def save_module_completion(self, completion_data: dict):
        """Save module completion to database"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE user_progress 
                SET status = 'completed', 
                    end_time = ?, 
                    score = ?,
                    verification_signature = ?,
                    notes = ?
                WHERE user_id = ? AND module_id = ?
            ''', (
                completion_data['completion_time'],
                completion_data['score'],
                completion_data['signature'],
                completion_data['notes'],
                self.user_data['id'],
                self.module_data['id']
            ))
            conn.commit()
            
        except Exception as e:
            print(f"Error saving completion: {e}")
        finally:
            conn.close()
    
    def show_qr_code(self):
        """Show QR code for quick module access"""
        qr_data = QRCodeGenerator.generate_module_qr(
            self.module_data['name'],
            str(self.module_data['id'])
        )
        
        # Create QR code display dialog
        qr_dialog = QRCodeDialog(self.module_data['name'], qr_data)
        qr_dialog.exec()
    
    def show_help(self):
        """Show help for the current module"""
        help_text = f"""
        <h2>Module Help: {self.module_data['name']}</h2>
        <p><strong>Description:</strong> {self.module_data.get('description', '')}</p>
        <p><strong>Estimated Duration:</strong> {self.module_data.get('estimated_duration', 0)} minutes</p>
        
        <h3>General Instructions:</h3>
        <ul>
            <li>Complete all required tasks (marked in red)</li>
            <li>Take screenshots when requested</li>
            <li>Sign the completion form when all tasks are done</li>
            <li>Add any notes or observations</li>
        </ul>
        
        <h3>Need Help?</h3>
        <p>Contact your trainer or system administrator for assistance.</p>
        """
        
        QMessageBox.information(self, "Module Help", help_text)
    
    def confirm_exit(self):
        """Confirm exit from module"""
        reply = QMessageBox.question(
            self,
            "Exit Module",
            "Are you sure you want to exit this training module?\n"
            "Your progress will be saved, but the module will be marked as incomplete.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.close()
    
    def closeEvent(self, event: QCloseEvent):
        """Handle window close event"""
        # Save current progress
        if self.training_module:
            self.save_current_progress()
        
        # Emit signal that module was closed
        self.module_closed.emit()
        
        event.accept()
    
    def save_current_progress(self):
        """Save current module progress"""
        if not hasattr(self, 'session_id'):
            return
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Calculate current progress
            if hasattr(self.training_module, 'tasks'):
                total_tasks = len(self.training_module.tasks)
                completed_tasks = sum(
                    1 for task in self.training_module.tasks.values() 
                    if task['completed']
                )
                progress_score = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0
            else:
                progress_score = 0
            
            # Update database
            cursor.execute('''
                UPDATE user_progress 
                SET score = ?, notes = ?
                WHERE id = ?
            ''', (
                progress_score,
                f"Progress saved at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                self.session_id
            ))
            conn.commit()
            
        except Exception as e:
            print(f"Error saving progress: {e}")
        finally:
            conn.close()

class QRCodeDialog(QDialog):
    """Dialog to display QR code for module access"""
    
    def __init__(self, module_name: str, qr_data: str):
        super().__init__()
        self.module_name = module_name
        self.qr_data = qr_data
        self.setup_ui()
    
    def setup_ui(self):
        """Setup QR code display UI"""
        self.setWindowTitle(f"QR Code - {self.module_name}")
        self.setFixedSize(300, 400)
        self.setWindowModality(Qt.ApplicationModal)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(f"QR Code for\n{self.module_name}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # Generate actual QR code
        qr_frame = QFrame()
        qr_frame.setFixedSize(200, 200)
        qr_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #bdc3c7;
                background-color: white;
            }
        """)
        qr_layout = QVBoxLayout(qr_frame)
        
        # Generate QR code with module information
        qr_code = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=1,
        )
        
        # Create URL or data for the QR code (can be customized)
        qr_data = f"Broetje Training Module: {self.module_name}\nUser: {self.username}"
        qr_code.add_data(qr_data)
        qr_code.make(fit=True)
        
        # Create QR code image
        qr_img = qr_code.make_image(fill='black', back_color='white')
        
        # Convert PIL image to QPixmap
        if hasattr(qr_img, '_img'):  # pillow >= 10.0.0
            qr_img = qr_img._img
        
        # Save to bytes buffer
        import io
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        
        # Create QPixmap from buffer
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        
        # Scale to fit the frame
        scaled_pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Display the QR code
        qr_label = QLabel()
        qr_label.setPixmap(scaled_pixmap)
        qr_label.setAlignment(Qt.AlignCenter)
        qr_layout.addWidget(qr_label)
        
        layout.addWidget(qr_frame, 0, Qt.AlignCenter)
        
        # Instructions
        instructions = QLabel(
            "Scan this QR code with a mobile device\n"
            "for quick access to this training module."
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Save button
        save_button = QPushButton("Save QR Code")
        save_button.clicked.connect(self.save_qr_code)
        layout.addWidget(save_button)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)
    
    def save_qr_code(self):
        """Save QR code as image file"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save QR Code",
            f"{self.module_name}_QR.png",
            "PNG Files (*.png);;All Files (*)"
        )
        
        if filename:
            # In real implementation, would save the actual QR code image
            QMessageBox.information(
                self,
                "QR Code Saved",
                f"QR code saved to: {filename}"
            )