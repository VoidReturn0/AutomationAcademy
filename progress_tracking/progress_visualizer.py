"""Progress visualization for training modules."""

import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

class ProgressVisualizer:
    """Create visual representations of training progress."""
    
    def __init__(self, db_path: str, output_dir: str = "progress_tracking/visualizations"):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style for matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def create_user_progress_chart(self, user_id: int, save_path: str = None) -> Figure:
        """Create a progress chart for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get user progress data
            cursor.execute('''
            SELECT m.name, p.progress_percentage, p.status
            FROM user_progress p
            JOIN modules m ON p.module_id = m.module_id
            WHERE p.user_id = ?
            ORDER BY p.progress_percentage DESC
            ''', (user_id,))
            
            data = cursor.fetchall()
            if not data:
                logger.warning(f"No progress data found for user {user_id}")
                return None
                
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Prepare data
            modules = [row[0] for row in data]
            progress = [row[1] for row in data]
            status = [row[2] for row in data]
            
            # Create horizontal bar chart
            colors = ['#27AE60' if s == 'completed' else '#3498DB' if s == 'in_progress' else '#95A5A6' 
                     for s in status]
            
            bars = ax.barh(modules, progress, color=colors)
            
            # Customize chart
            ax.set_xlabel('Progress (%)')
            ax.set_title(f'Module Progress Overview', fontsize=16, fontweight='bold')
            ax.set_xlim(0, 100)
            
            # Add value labels
            for bar, prog in zip(bars, progress):
                ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, 
                       f'{prog:.1f}%', ha='left', va='center')
            
            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#27AE60', label='Completed'),
                Patch(facecolor='#3498DB', label='In Progress'),
                Patch(facecolor='#95A5A6', label='Not Started')
            ]
            ax.legend(handles=legend_elements, loc='lower right')
            
            plt.tight_layout()
            
            if save_path:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        finally:
            conn.close()
            
    def create_time_spent_chart(self, user_id: int, save_path: str = None) -> Figure:
        """Create a chart showing time spent on each module."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get time spent data
            cursor.execute('''
            SELECT m.name, p.time_spent/3600.0 as hours_spent
            FROM user_progress p
            JOIN modules m ON p.module_id = m.module_id
            WHERE p.user_id = ? AND p.time_spent > 0
            ORDER BY p.time_spent DESC
            ''', (user_id,))
            
            data = cursor.fetchall()
            if not data:
                logger.warning(f"No time data found for user {user_id}")
                return None
                
            # Create figure
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Prepare data
            modules = [row[0] for row in data]
            hours = [row[1] for row in data]
            
            # Create bar chart
            bars = ax.bar(modules, hours, color='#E74C3C')
            
            # Customize chart
            ax.set_ylabel('Time Spent (hours)')
            ax.set_title('Time Investment by Module', fontsize=16, fontweight='bold')
            ax.set_xticklabels(modules, rotation=45, ha='right')
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{height:.1f}h', ha='center', va='bottom')
            
            plt.tight_layout()
            
            if save_path:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        finally:
            conn.close()
            
    def create_learning_timeline(self, user_id: int, save_path: str = None) -> Figure:
        """Create a timeline showing learning progression."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get session data
            cursor.execute('''
            SELECT s.start_time, s.duration/3600.0, m.name
            FROM training_sessions s
            JOIN modules m ON s.module_id = m.module_id
            WHERE s.user_id = ? AND s.duration > 0
            ORDER BY s.start_time
            ''', (user_id,))
            
            data = cursor.fetchall()
            if not data:
                logger.warning(f"No session data found for user {user_id}")
                return None
                
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Prepare data
            dates = [datetime.fromisoformat(row[0]) for row in data]
            durations = [row[1] for row in data]
            modules = [row[2] for row in data]
            
            # Create scatter plot
            unique_modules = list(set(modules))
            colors = plt.cm.tab10(range(len(unique_modules)))
            module_colors = {mod: colors[i] for i, mod in enumerate(unique_modules)}
            
            for i, (date, duration, module) in enumerate(zip(dates, durations, modules)):
                ax.scatter(date, duration, color=module_colors[module], 
                          s=100, alpha=0.7, label=module if module not in ax.get_legend_handles_labels()[1] else "")
            
            # Customize chart
            ax.set_xlabel('Date')
            ax.set_ylabel('Session Duration (hours)')
            ax.set_title('Learning Timeline', fontsize=16, fontweight='bold')
            
            # Format x-axis
            import matplotlib.dates as mdates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=7))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Add legend
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            plt.tight_layout()
            
            if save_path:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        finally:
            conn.close()
            
    def create_department_comparison(self, department: str, save_path: str = None) -> Figure:
        """Create a comparison chart for department members."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get department user statistics
            cursor.execute('''
            SELECT u.username, 
                   COUNT(DISTINCT p.module_id) as modules_started,
                   COUNT(DISTINCT CASE WHEN p.status = 'completed' THEN p.module_id END) as modules_completed,
                   SUM(p.points_earned) as total_points
            FROM users u
            LEFT JOIN user_progress p ON u.id = p.user_id
            WHERE u.department = ?
            GROUP BY u.id
            ORDER BY total_points DESC
            ''', (department,))
            
            data = cursor.fetchall()
            if not data:
                logger.warning(f"No data found for department {department}")
                return None
                
            # Create figure with subplots
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # Prepare data
            df = pd.DataFrame(data, columns=['username', 'modules_started', 'modules_completed', 'total_points'])
            
            # Plot 1: Module completion
            x = range(len(df))
            width = 0.35
            
            ax1.bar([i - width/2 for i in x], df['modules_started'], width, 
                    label='Started', color='#3498DB', alpha=0.8)
            ax1.bar([i + width/2 for i in x], df['modules_completed'], width,
                    label='Completed', color='#27AE60', alpha=0.8)
            
            ax1.set_ylabel('Number of Modules')
            ax1.set_title(f'{department} Department - Module Progress', fontsize=16, fontweight='bold')
            ax1.set_xticks(x)
            ax1.set_xticklabels(df['username'], rotation=45, ha='right')
            ax1.legend()
            ax1.grid(axis='y', alpha=0.3)
            
            # Plot 2: Points earned
            ax2.bar(x, df['total_points'], color='#E74C3C', alpha=0.8)
            ax2.set_ylabel('Total Points')
            ax2.set_xlabel('User')
            ax2.set_title('Points Earned', fontsize=14, fontweight='bold')
            ax2.set_xticks(x)
            ax2.set_xticklabels(df['username'], rotation=45, ha='right')
            ax2.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for i, v in enumerate(df['total_points']):
                ax2.text(i, v + 5, str(v), ha='center', va='bottom')
            
            plt.tight_layout()
            
            if save_path:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        finally:
            conn.close()
            
    def create_module_statistics(self, module_id: str, save_path: str = None) -> Figure:
        """Create statistics visualization for a specific module."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get module statistics
            cursor.execute('''
            SELECT 
                p.status,
                COUNT(*) as count,
                AVG(p.progress_percentage) as avg_progress,
                AVG(p.time_spent/3600.0) as avg_hours
            FROM user_progress p
            WHERE p.module_id = ?
            GROUP BY p.status
            ''', (module_id,))
            
            data = cursor.fetchall()
            if not data:
                logger.warning(f"No data found for module {module_id}")
                return None
                
            # Get module name
            cursor.execute('SELECT name FROM modules WHERE module_id = ?', (module_id,))
            module_name = cursor.fetchone()[0]
            
            # Create figure with subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
            fig.suptitle(f'{module_name} - Module Statistics', fontsize=16, fontweight='bold')
            
            # Prepare data
            df = pd.DataFrame(data, columns=['status', 'count', 'avg_progress', 'avg_hours'])
            
            # Plot 1: Status distribution (pie chart)
            colors = {'completed': '#27AE60', 'in_progress': '#3498DB', 'not_started': '#95A5A6'}
            status_colors = [colors.get(s, '#95A5A6') for s in df['status']]
            
            ax1.pie(df['count'], labels=df['status'], colors=status_colors, autopct='%1.1f%%')
            ax1.set_title('User Status Distribution')
            
            # Plot 2: Average progress by status
            ax2.bar(df['status'], df['avg_progress'], color=status_colors)
            ax2.set_ylabel('Average Progress (%)')
            ax2.set_title('Average Progress by Status')
            ax2.set_ylim(0, 100)
            
            for i, v in enumerate(df['avg_progress']):
                ax2.text(i, v + 2, f'{v:.1f}%', ha='center', va='bottom')
            
            # Plot 3: Average time spent
            ax3.bar(df['status'], df['avg_hours'], color=status_colors)
            ax3.set_ylabel('Average Time (hours)')
            ax3.set_title('Average Time Investment')
            
            for i, v in enumerate(df['avg_hours']):
                ax3.text(i, v + 0.1, f'{v:.1f}h', ha='center', va='bottom')
            
            # Plot 4: Task completion rates
            cursor.execute('''
            SELECT mt.name, 
                   COUNT(tc.user_id) as completions,
                   (SELECT COUNT(*) FROM user_progress WHERE module_id = ?) as total_users
            FROM module_tasks mt
            LEFT JOIN task_completions tc ON mt.task_id = tc.task_id AND tc.module_id = ?
            WHERE mt.module_id = ?
            GROUP BY mt.task_id
            ORDER BY mt.id
            ''', (module_id, module_id, module_id))
            
            task_data = cursor.fetchall()
            if task_data:
                tasks = [row[0] for row in task_data]
                completion_rates = [row[1]/row[2]*100 if row[2] > 0 else 0 for row in task_data]
                
                ax4.barh(tasks, completion_rates, color='#9B59B6')
                ax4.set_xlabel('Completion Rate (%)')
                ax4.set_title('Task Completion Rates')
                ax4.set_xlim(0, 100)
                
                for i, v in enumerate(completion_rates):
                    ax4.text(v + 1, i, f'{v:.1f}%', ha='left', va='center')
            
            plt.tight_layout()
            
            if save_path:
                fig.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        finally:
            conn.close()

class ProgressVisualizationWidget(QWidget):
    """Qt widget for displaying progress visualizations."""
    
    def __init__(self, db_path: str, parent=None):
        super().__init__(parent)
        self.db_path = db_path
        self.visualizer = ProgressVisualizer(db_path)
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure canvas
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
    def display_user_progress(self, user_id: int):
        """Display user progress chart."""
        self.figure.clear()
        
        # Create the visualization
        fig = self.visualizer.create_user_progress_chart(user_id)
        if fig:
            # Copy the figure to our canvas
            self.figure = fig
            self.canvas.figure = self.figure
            self.canvas.draw()
            
    def display_time_spent(self, user_id: int):
        """Display time spent chart."""
        self.figure.clear()
        
        fig = self.visualizer.create_time_spent_chart(user_id)
        if fig:
            self.figure = fig
            self.canvas.figure = self.figure
            self.canvas.draw()
            
    def display_learning_timeline(self, user_id: int):
        """Display learning timeline."""
        self.figure.clear()
        
        fig = self.visualizer.create_learning_timeline(user_id)
        if fig:
            self.figure = fig
            self.canvas.figure = self.figure
            self.canvas.draw()
            
    def display_department_comparison(self, department: str):
        """Display department comparison."""
        self.figure.clear()
        
        fig = self.visualizer.create_department_comparison(department)
        if fig:
            self.figure = fig
            self.canvas.figure = self.figure
            self.canvas.draw()
            
    def display_module_statistics(self, module_id: str):
        """Display module statistics."""
        self.figure.clear()
        
        fig = self.visualizer.create_module_statistics(module_id)
        if fig:
            self.figure = fig
            self.canvas.figure = self.figure
            self.canvas.draw()
