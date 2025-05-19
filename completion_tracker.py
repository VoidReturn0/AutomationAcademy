#!/usr/bin/env python3
"""
Completion Tracking System
Handles screenshot organization and GitHub synchronization for training completions
"""

import os
import json
import base64
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

class CompletionTracker:
    """Manages training completion data and GitHub synchronization"""
    
    def __init__(self, github_config: Dict):
        self.github_config = github_config
        self.local_storage = Path("completion_data")
        self.local_storage.mkdir(exist_ok=True)
        
        # Create organized directory structure
        self.screenshots_dir = self.local_storage / "screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        self.reports_dir = self.local_storage / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def save_screenshot(self, username: str, module_name: str, task_id: str, 
                       screenshot_data: bytes) -> str:
        """Save screenshot with organized naming"""
        # Create user and module directories
        user_dir = self.screenshots_dir / username.lower().replace(" ", "_")
        module_dir = user_dir / module_name.lower().replace(" ", "_").replace("/", "_")
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{task_id}_{timestamp}.png"
        filepath = module_dir / filename
        
        # Save screenshot
        with open(filepath, 'wb') as f:
            f.write(screenshot_data)
        
        return str(filepath)
    
    def create_completion_report(self, user_data: Dict, module_data: Dict, 
                               completion_data: Dict, screenshot_paths: List[str]) -> Dict:
        """Create a comprehensive completion report"""
        report = {
            "user": {
                "username": user_data['username'],
                "full_name": user_data['full_name'],
                "role": user_data['role']
            },
            "module": {
                "id": module_data['id'],
                "name": module_data['name'],
                "version": module_data.get('version', '1.0')
            },
            "completion": {
                "timestamp": datetime.now().isoformat(),
                "score": completion_data['score'],
                "elapsed_time": completion_data['elapsed_time'],
                "tasks_completed": completion_data['tasks_completed']
            },
            "screenshots": screenshot_paths,
            "signature": completion_data.get('signature', ''),
            "notes": completion_data.get('notes', ''),
            "verification_hash": self._generate_verification_hash(user_data, module_data, completion_data)
        }
        
        # Save report locally
        report_filename = f"{user_data['username']}_{module_data['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = self.reports_dir / report_filename
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _generate_verification_hash(self, user_data: Dict, module_data: Dict, 
                                   completion_data: Dict) -> str:
        """Generate a verification hash for the completion"""
        data_string = f"{user_data['username']}_{module_data['id']}_{completion_data['score']}_{datetime.now().isoformat()}"
        return hashlib.sha256(data_string.encode()).hexdigest()
    
    def upload_to_github(self, report: Dict, screenshot_files: List[str]) -> bool:
        """Upload completion data to GitHub repository"""
        try:
            # GitHub API configuration
            owner = self.github_config.get('owner')
            repo = self.github_config.get('repository')
            token = self.github_config.get('token')
            branch = self.github_config.get('branch', 'main')
            
            if not all([owner, repo, token]):
                print("GitHub configuration incomplete")
                return False
            
            headers = {
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            # Create directory structure in GitHub
            base_path = f"completion_tracking/{report['user']['username']}/{report['module']['id']}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Upload report JSON
            report_path = f"{base_path}/report_{timestamp}.json"
            report_content = base64.b64encode(json.dumps(report, indent=2).encode()).decode()
            
            report_upload = {
                'message': f"Add completion report for {report['user']['username']} - {report['module']['name']}",
                'content': report_content,
                'branch': branch
            }
            
            report_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{report_path}"
            response = requests.put(report_url, json=report_upload, headers=headers)
            
            if response.status_code not in [200, 201]:
                print(f"Failed to upload report: {response.status_code}")
                return False
            
            # Upload screenshots
            for screenshot_path in screenshot_files:
                with open(screenshot_path, 'rb') as f:
                    screenshot_data = f.read()
                
                screenshot_filename = Path(screenshot_path).name
                github_screenshot_path = f"{base_path}/screenshots/{screenshot_filename}"
                
                screenshot_upload = {
                    'message': f"Add screenshot {screenshot_filename}",
                    'content': base64.b64encode(screenshot_data).decode(),
                    'branch': branch
                }
                
                screenshot_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{github_screenshot_path}"
                response = requests.put(screenshot_url, json=screenshot_upload, headers=headers)
                
                if response.status_code not in [200, 201]:
                    print(f"Failed to upload screenshot {screenshot_filename}: {response.status_code}")
            
            # Create/update summary dashboard
            self._update_dashboard(report, headers, owner, repo, branch)
            
            return True
            
        except Exception as e:
            print(f"Error uploading to GitHub: {e}")
            return False
    
    def _update_dashboard(self, report: Dict, headers: Dict, owner: str, 
                         repo: str, branch: str):
        """Update the completion dashboard on GitHub"""
        try:
            dashboard_path = "completion_tracking/dashboard.json"
            dashboard_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{dashboard_path}"
            
            # Try to get existing dashboard
            response = requests.get(dashboard_url, headers=headers)
            
            if response.status_code == 200:
                # Dashboard exists, update it
                content = response.json()
                dashboard_data = json.loads(base64.b64decode(content['content']).decode())
                sha = content['sha']
            else:
                # Create new dashboard
                dashboard_data = {
                    "last_updated": datetime.now().isoformat(),
                    "total_completions": 0,
                    "users": {},
                    "modules": {}
                }
                sha = None
            
            # Update dashboard data
            username = report['user']['username']
            module_id = report['module']['id']
            
            if username not in dashboard_data['users']:
                dashboard_data['users'][username] = {
                    "full_name": report['user']['full_name'],
                    "completions": []
                }
            
            dashboard_data['users'][username]['completions'].append({
                "module": module_id,
                "timestamp": report['completion']['timestamp'],
                "score": report['completion']['score']
            })
            
            if module_id not in dashboard_data['modules']:
                dashboard_data['modules'][module_id] = {
                    "name": report['module']['name'],
                    "completions": 0,
                    "average_score": 0
                }
            
            dashboard_data['modules'][module_id]['completions'] += 1
            dashboard_data['total_completions'] += 1
            dashboard_data['last_updated'] = datetime.now().isoformat()
            
            # Upload updated dashboard
            dashboard_content = base64.b64encode(json.dumps(dashboard_data, indent=2).encode()).decode()
            
            upload_data = {
                'message': f"Update dashboard - {username} completed {report['module']['name']}",
                'content': dashboard_content,
                'branch': branch
            }
            
            if sha:
                upload_data['sha'] = sha
            
            response = requests.put(dashboard_url, json=upload_data, headers=headers)
            
            if response.status_code not in [200, 201]:
                print(f"Failed to update dashboard: {response.status_code}")
                
        except Exception as e:
            print(f"Error updating dashboard: {e}")
    
    def get_user_history(self, username: str) -> List[Dict]:
        """Get completion history for a specific user"""
        user_reports = []
        
        # Check local reports
        for report_file in self.reports_dir.glob(f"{username}_*.json"):
            with open(report_file, 'r') as f:
                user_reports.append(json.load(f))
        
        return sorted(user_reports, key=lambda x: x['completion']['timestamp'], reverse=True)
    
    def get_module_statistics(self, module_id: str) -> Dict:
        """Get statistics for a specific module"""
        module_stats = {
            "total_completions": 0,
            "average_score": 0,
            "average_time": 0,
            "completion_rate": 0
        }
        
        scores = []
        times = []
        
        for report_file in self.reports_dir.glob(f"*_{module_id}_*.json"):
            with open(report_file, 'r') as f:
                report = json.load(f)
                scores.append(report['completion']['score'])
                times.append(report['completion']['elapsed_time'])
        
        if scores:
            module_stats['total_completions'] = len(scores)
            module_stats['average_score'] = sum(scores) / len(scores)
            module_stats['average_time'] = sum(times) / len(times)
        
        return module_stats