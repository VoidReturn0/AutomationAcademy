#!/usr/bin/env python3
"""
Integration Example
Shows how to use the module loader, progress tracker, and user manager together
"""

from pathlib import Path
from module_loader import ModuleLoader
from progress_tracker import ProgressTracker
from user_manager import UserManager, UserRole
import json

def main():
    """Demonstrate integrated system usage"""
    
    # Initialize components
    db_path = Path("training_data.db")
    modules_dir = Path("modules")
    
    module_loader = ModuleLoader(modules_dir)
    progress_tracker = ProgressTracker(db_path)
    user_manager = UserManager(db_path)
    
    print("=== Broetje Training System Integration Demo ===\n")
    
    # 1. Create a new user
    print("1. Creating new user...")
    try:
        user = user_manager.create_user(
            username="test_user",
            email="test@broetje.com",
            password="SecurePass123!",
            full_name="Test User",
            role=UserRole.TRAINEE,
            department="Engineering"
        )
        print(f"✓ Created user: {user.full_name} ({user.username})")
    except ValueError as e:
        print(f"User already exists, continuing...")
        user = user_manager.get_user("test_user")
    
    # 2. Authenticate user
    print("\n2. Authenticating user...")
    session = user_manager.authenticate(
        username="test_user",
        password="SecurePass123!",
        ip_address="192.168.1.100"
    )
    
    if session:
        print(f"✓ Authentication successful. Session ID: {session.session_id[:10]}...")
    else:
        print("✗ Authentication failed")
        return
    
    # 3. Load available modules
    print("\n3. Loading training modules...")
    available_modules = module_loader.discover_modules()
    print(f"✓ Found {len(available_modules)} modules:")
    
    for module_name in available_modules:
        metadata = module_loader.load_module_metadata(module_name)
        if metadata:
            print(f"  - {metadata.name} (v{metadata.version})")
            print(f"    Category: {metadata.category}")
            print(f"    Difficulty: {metadata.difficulty}")
            print(f"    Time: {metadata.estimated_time}")
    
    # 4. Start a module
    print("\n4. Starting a training module...")
    if available_modules:
        first_module = available_modules[0]
        module_class = module_loader.load_module(first_module)
        
        if module_class:
            print(f"✓ Loaded module: {first_module}")
            
            # Get module metadata
            metadata = module_loader.module_metadata[first_module]
            
            # Start first task
            if metadata and hasattr(metadata, 'tasks'):
                first_task = metadata.tasks[0] if metadata.tasks else None
                if first_task:
                    task_id = first_task.get('id', 'task_1')
                    progress_tracker.start_task(
                        task_id=task_id,
                        module_id=first_module,
                        user_id=user.user_id
                    )
                    print(f"✓ Started task: {task_id}")
    
    # 5. Simulate task completion
    print("\n5. Completing a task...")
    progress_tracker.complete_task(
        task_id="task_1",
        module_id=first_module,
        user_id=user.user_id,
        score=95.0,
        screenshot_path="/screenshots/task_1.png"
    )
    print("✓ Task completed with score: 95.0")
    
    # 6. Check user progress
    print("\n6. Checking user progress...")
    user_progress = progress_tracker.get_user_progress(user.user_id)
    
    print("Progress Summary:")
    print(f"  Total Modules: {user_progress['statistics']['total_modules']}")
    print(f"  Completed Modules: {user_progress['statistics']['completed_modules']}")
    print(f"  Average Score: {user_progress['statistics']['average_score']:.1f}")
    print(f"  Total Tasks: {user_progress['statistics']['total_tasks']}")
    print(f"  Completed Tasks: {user_progress['statistics']['completed_tasks']}")
    
    # 7. Check user permissions
    print("\n7. Checking user permissions...")
    permissions_to_check = [
        'view_own_progress',
        'submit_assignments',
        'create_assignments',
        'view_all_progress'
    ]
    
    for permission in permissions_to_check:
        has_perm = user_manager.has_permission(user.user_id, permission)
        print(f"  {permission}: {'✓' if has_perm else '✗'}")
    
    # 8. Export progress report
    print("\n8. Exporting progress report...")
    report_path = progress_tracker.export_progress_report(
        user_id=user.user_id,
        format='json'
    )
    print(f"✓ Progress report exported to: {report_path}")
    
    # 9. Record training completion
    print("\n9. Recording training completion...")
    certificate_id = user_manager.record_training_completion(
        user_id=user.user_id,
        module_id=first_module,
        score=95.0,
        notes="Completed with excellence"
    )
    print(f"✓ Certificate issued: {certificate_id}")
    
    # 10. Get training history
    print("\n10. Retrieving training history...")
    history = user_manager.get_training_history(user.user_id)
    
    for record in history:
        print(f"  Module: {record['module_id']}")
        print(f"  Completed: {record['completed_at']}")
        print(f"  Score: {record['score']}")
        print(f"  Certificate: {record['certificate_id']}")
    
    print("\n=== Integration Demo Complete ===")

if __name__ == "__main__":
    main()