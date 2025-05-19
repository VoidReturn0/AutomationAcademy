#!/usr/bin/env python3
"""
GitHub Module Manager
Handles downloading and updating training modules from GitHub repository
"""

import json
import requests
import zipfile
import tempfile
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QListWidget, QListWidgetItem, QTextEdit,
    QGroupBox, QMessageBox, QLineEdit, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont

class GitHubAPIClient:
    """Client for GitHub API operations"""
    
    def __init__(self, repo_url: str, api_token: Optional[str] = None):
        from config_manager import get_config_manager
        
        self.repo_url = repo_url
        self.config_manager = get_config_manager()
        
        # Use provided token or fallback to deploy key
        self.api_token = self.config_manager.get_github_token(api_token)
        self.headers = {}
        
        if self.api_token:
            self.headers['Authorization'] = f'token {self.api_token}'
            logger.info("GitHub API client initialized with token")
        else:
            logger.warning("GitHub API client initialized without token")
        
        # Extract owner and repo from URL
        if 'github.com' in repo_url:
            parts = repo_url.split('/')[-2:]
            self.owner = parts[0]
            self.repo = parts[1].replace('.git', '')
        else:
            raise ValueError("Invalid GitHub repository URL")
    
    def get_repository_info(self) -> Dict:
        """Get repository information"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_releases(self) -> List[Dict]:
        """Get repository releases"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_latest_release(self) -> Dict:
        """Get the latest release"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_contents(self, path: str = "") -> List[Dict]:
        """Get repository contents at path"""
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{path}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_module_manifest(self) -> Optional[Dict]:
        """Get module manifest file"""
        try:
            contents = self.get_contents("modules.json")
            if contents:
                manifest_url = contents['download_url']
                response = requests.get(manifest_url)
                return response.json()
        except:
            return None
        return None

class ModuleDownloadThread(QThread):
    """Thread for downloading modules in background"""
    
    progress_updated = Signal(str, int)
    module_downloaded = Signal(str, bool, str)
    
    def __init__(self, module_info: Dict, download_path: Path):
        super().__init__()
        self.module_info = module_info
        self.download_path = download_path
    
    def run(self):
        """Download and extract module"""
        module_name = self.module_info['name']
        download_url = self.module_info.get('download_url')
        
        if not download_url:
            self.module_downloaded.emit(module_name, False, "No download URL provided")
            return
        
        try:
            # Download module
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            self.progress_updated.emit(module_name, progress)
                
                temp_file_path = temp_file.name
            
            # Extract module
            module_dir = self.download_path / module_name
            module_dir.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
                zip_ref.extractall(module_dir)
            
            # Clean up temp file
            os.unlink(temp_file_path)
            
            self.module_downloaded.emit(module_name, True, "Successfully downloaded")
            
        except Exception as e:
            self.module_downloaded.emit(module_name, False, str(e))

class GitHubModuleDialog(QDialog):
    """Dialog for managing GitHub module downloads"""
    
    def __init__(self, config: Dict, db_manager):
        super().__init__()
        self.config = config
        self.db_manager = db_manager
        self.github_client = None
        self.download_threads = []
        self.setup_ui()
        
        # Initialize GitHub client if configured
        if config.get('repository_url'):
            self.init_github_client()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("GitHub Module Manager")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # GitHub configuration
        config_group = QGroupBox("GitHub Configuration")
        config_layout = QVBoxLayout()
        
        # Repository URL
        repo_layout = QHBoxLayout()
        repo_layout.addWidget(QLabel("Repository URL:"))
        self.repo_url_edit = QLineEdit()
        self.repo_url_edit.setText(self.config.get('repository_url', ''))
        repo_layout.addWidget(self.repo_url_edit)
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_repo)
        repo_layout.addWidget(self.connect_button)
        
        config_layout.addLayout(repo_layout)
        
        # API Token (optional)
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("API Token (optional):"))
        self.api_token_edit = QLineEdit()
        self.api_token_edit.setEchoMode(QLineEdit.Password)
        self.api_token_edit.setText(self.config.get('api_token', ''))
        token_layout.addWidget(self.api_token_edit)
        config_layout.addLayout(token_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Repository status
        self.status_label = QLabel("Not connected")
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Available modules
        modules_group = QGroupBox("Available Modules")
        modules_layout = QVBoxLayout()
        
        # Module list
        self.modules_list = QListWidget()
        self.modules_list.itemSelectionChanged.connect(self.module_selected)
        modules_layout.addWidget(self.modules_list)
        
        # Module details
        self.module_details = QTextEdit()
        self.module_details.setMaximumHeight(100)
        self.module_details.setReadOnly(True)
        modules_layout.addWidget(self.module_details)
        
        # Download controls
        download_layout = QHBoxLayout()
        
        self.download_selected_button = QPushButton("Download Selected")
        self.download_selected_button.clicked.connect(self.download_selected)
        self.download_selected_button.setEnabled(False)
        download_layout.addWidget(self.download_selected_button)
        
        self.download_all_button = QPushButton("Download All")
        self.download_all_button.clicked.connect(self.download_all)
        self.download_all_button.setEnabled(False)
        download_layout.addWidget(self.download_all_button)
        
        download_layout.addStretch()
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_modules)
        self.refresh_button.setEnabled(False)
        download_layout.addWidget(self.refresh_button)
        
        modules_layout.addLayout(download_layout)
        modules_group.setLayout(modules_layout)
        layout.addWidget(modules_group)
        
        # Download progress
        progress_group = QGroupBox("Download Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel()
        progress_layout.addWidget(self.progress_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)
        
        button_layout.addStretch()
        
        self.save_config_button = QPushButton("Save Configuration")
        self.save_config_button.clicked.connect(self.save_configuration)
        button_layout.addWidget(self.save_config_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def init_github_client(self):
        """Initialize GitHub API client"""
        try:
            repo_url = self.repo_url_edit.text().strip()
            api_token = self.api_token_edit.text().strip() or None
            
            self.github_client = GitHubAPIClient(repo_url, api_token)
            
            # Test connection
            repo_info = self.github_client.get_repository_info()
            
            self.status_label.setText(f"Connected to {repo_info['full_name']}")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
            # Enable controls
            self.refresh_button.setEnabled(True)
            self.download_all_button.setEnabled(True)
            
            # Load modules
            self.refresh_modules()
            
        except Exception as e:
            self.status_label.setText(f"Connection failed: {str(e)}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.github_client = None
    
    def connect_to_repo(self):
        """Connect to GitHub repository"""
        self.init_github_client()
    
    def refresh_modules(self):
        """Refresh available modules list"""
        if not self.github_client:
            return
        
        try:
            # Clear current list
            self.modules_list.clear()
            
            # Get module manifest
            manifest = self.github_client.get_module_manifest()
            
            if manifest and 'modules' in manifest:
                for module in manifest['modules']:
                    item = QListWidgetItem()
                    item.setText(f"{module['name']} (v{module.get('version', '1.0')})")
                    item.setData(Qt.UserRole, module)
                    
                    # Check if module is already downloaded
                    module_path = Path("modules") / module['name']
                    if module_path.exists():
                        item.setText(item.text() + " [Downloaded]")
                        item.setForeground(Qt.green)
                    
                    self.modules_list.addItem(item)
            else:
                # Fallback: look for releases
                releases = self.github_client.get_releases()
                for release in releases[:5]:  # Show last 5 releases
                    item = QListWidgetItem()
                    item.setText(f"Release {release['tag_name']}")
                    
                    # Create module info from release
                    module_info = {
                        'name': f"release_{release['tag_name']}",
                        'version': release['tag_name'],
                        'description': release.get('body', ''),
                        'download_url': release.get('zipball_url')
                    }
                    item.setData(Qt.UserRole, module_info)
                    self.modules_list.addItem(item)
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh modules: {str(e)}")
    
    def module_selected(self):
        """Handle module selection"""
        current_item = self.modules_list.currentItem()
        if current_item:
            module_info = current_item.data(Qt.UserRole)
            
            details = f"""
            <h3>{module_info['name']}</h3>
            <p><strong>Version:</strong> {module_info.get('version', 'N/A')}</p>
            <p><strong>Description:</strong> {module_info.get('description', 'No description available')}</p>
            """
            
            if 'prerequisites' in module_info:
                details += f"<p><strong>Prerequisites:</strong> {module_info['prerequisites']}</p>"
            
            if 'author' in module_info:
                details += f"<p><strong>Author:</strong> {module_info['author']}</p>"
            
            self.module_details.setHtml(details)
            self.download_selected_button.setEnabled(True)
        else:
            self.module_details.clear()
            self.download_selected_button.setEnabled(False)
    
    def download_selected(self):
        """Download selected module"""
        current_item = self.modules_list.currentItem()
        if current_item:
            module_info = current_item.data(Qt.UserRole)
            self.download_module(module_info)
    
    def download_all(self):
        """Download all available modules"""
        for i in range(self.modules_list.count()):
            item = self.modules_list.item(i)
            module_info = item.data(Qt.UserRole)
            
            # Skip already downloaded modules
            if "[Downloaded]" not in item.text():
                self.download_module(module_info)
    
    def download_module(self, module_info: Dict):
        """Download a specific module"""
        module_name = module_info['name']
        download_path = Path("modules")
        download_path.mkdir(exist_ok=True)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText(f"Downloading {module_name}...")
        
        # Start download thread
        download_thread = ModuleDownloadThread(module_info, download_path)
        download_thread.progress_updated.connect(self.update_progress)
        download_thread.module_downloaded.connect(self.module_download_complete)
        download_thread.start()
        
        self.download_threads.append(download_thread)
    
    def update_progress(self, module_name: str, progress: int):
        """Update download progress"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"Downloading {module_name}... {progress}%")
    
    def module_download_complete(self, module_name: str, success: bool, message: str):
        """Handle module download completion"""
        if success:
            self.progress_label.setText(f"Downloaded {module_name} successfully")
            
            # Update module list
            for i in range(self.modules_list.count()):
                item = self.modules_list.item(i)
                if module_name in item.text() and "[Downloaded]" not in item.text():
                    item.setText(item.text() + " [Downloaded]")
                    item.setForeground(Qt.green)
                    break
            
            # Install module in database
            self.install_module_in_db(module_name)
            
        else:
            self.progress_label.setText(f"Failed to download {module_name}: {message}")
            QMessageBox.warning(self, "Download Failed", 
                              f"Failed to download {module_name}:\n{message}")
        
        # Hide progress bar after a delay
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
    
    def install_module_in_db(self, module_name: str):
        """Install downloaded module in database"""
        try:
            # Look for module metadata
            module_path = Path("modules") / module_name
            metadata_file = module_path / "metadata.json"
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                
                # Insert/update module in database
                conn = self.db_manager.get_connection()
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO modules 
                    (name, description, version, prerequisites, estimated_duration)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    metadata['name'],
                    metadata.get('description', ''),
                    metadata.get('version', '1.0'),
                    metadata.get('prerequisites', ''),
                    metadata.get('estimated_duration', 30)
                ))
                
                conn.commit()
                conn.close()
                
        except Exception as e:
            print(f"Error installing module in database: {e}")
    
    def save_configuration(self):
        """Save GitHub configuration"""
        self.config['repository_url'] = self.repo_url_edit.text().strip()
        self.config['api_token'] = self.api_token_edit.text().strip() or None
        
        # Save to config file
        config_path = Path("config") / "github_config.json"
        config_path.parent.mkdir(exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        QMessageBox.information(self, "Configuration Saved", 
                              "GitHub configuration has been saved successfully.")

def load_github_config() -> Dict:
    """Load GitHub configuration from file"""
    config_path = Path("config") / "github_config.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    
    # Default configuration
    return {
        'repository_url': '',
        'api_token': None,
        'check_interval_hours': 6,
        'auto_download': False
    }