"""
Generate architecture diagram for the Broetje Training System.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch
import numpy as np

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(16, 12))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Define colors
colors = {
    'module': '#3498DB',
    'progress': '#27AE60',
    'user': '#E74C3C',
    'database': '#F39C12',
    'ui': '#9B59B6',
    'config': '#95A5A6'
}

# Main components
components = {
    'ui': {'pos': (50, 85), 'size': (40, 10), 'label': 'User Interface\n(PySide6)'},
    'modules': {'pos': (15, 60), 'size': (25, 15), 'label': 'Module System'},
    'progress': {'pos': (50, 60), 'size': (25, 15), 'label': 'Progress Tracking'},
    'users': {'pos': (85, 60), 'size': (25, 15), 'label': 'User Management'},
    'database': {'pos': (50, 30), 'size': (30, 10), 'label': 'SQLite Database'},
    'config': {'pos': (85, 30), 'size': (20, 10), 'label': 'Configuration'}
}

# Draw components
for name, comp in components.items():
    color = colors.get(name[:6], '#95A5A6')
    box = FancyBboxPatch((comp['pos'][0] - comp['size'][0]/2, comp['pos'][1] - comp['size'][1]/2),
                         comp['size'][0], comp['size'][1],
                         boxstyle="round,pad=0.3",
                         facecolor=color,
                         edgecolor='black',
                         linewidth=2,
                         alpha=0.8)
    ax.add_patch(box)
    ax.text(comp['pos'][0], comp['pos'][1], comp['label'],
            ha='center', va='center', fontsize=12, fontweight='bold', color='white')

# Sub-components
subcomponents = {
    'module_loader': {'parent': 'modules', 'offset': (-5, -5), 'label': 'Module\nLoader'},
    'metadata': {'parent': 'modules', 'offset': (5, -5), 'label': 'Metadata\nJSON'},
    'resources': {'parent': 'modules', 'offset': (0, -10), 'label': 'Resources'},
    
    'progress_mgr': {'parent': 'progress', 'offset': (-5, -5), 'label': 'Progress\nManager'},
    'report_gen': {'parent': 'progress', 'offset': (5, -5), 'label': 'Report\nGenerator'},
    'visualizer': {'parent': 'progress', 'offset': (0, -10), 'label': 'Visualizer'},
    
    'auth': {'parent': 'users', 'offset': (-5, -5), 'label': 'Auth\nManager'},
    'profile': {'parent': 'users', 'offset': (5, -5), 'label': 'Profile\nManager'},
    'roles': {'parent': 'users', 'offset': (0, -10), 'label': 'Role\nManager'},
}

# Draw sub-components
for name, sub in subcomponents.items():
    parent = components[sub['parent']]
    pos = (parent['pos'][0] + sub['offset'][0], parent['pos'][1] + sub['offset'][1])
    
    box = FancyBboxPatch((pos[0] - 4, pos[1] - 2), 8, 4,
                         boxstyle="round,pad=0.1",
                         facecolor='white',
                         edgecolor='black',
                         linewidth=1)
    ax.add_patch(box)
    ax.text(pos[0], pos[1], sub['label'],
            ha='center', va='center', fontsize=9)

# Draw connections
connections = [
    ('ui', 'modules'),
    ('ui', 'progress'),
    ('ui', 'users'),
    ('modules', 'database'),
    ('progress', 'database'),
    ('users', 'database'),
    ('users', 'config'),
    ('modules', 'config'),
]

for start, end in connections:
    start_comp = components[start]
    end_comp = components[end]
    
    arrow = ConnectionPatch(start_comp['pos'], end_comp['pos'], "data", "data",
                           arrowstyle="->", shrinkA=5, shrinkB=5,
                           mutation_scale=20, fc="black", lw=2)
    ax.add_artist(arrow)

# Database tables
db_tables = [
    'users', 'sessions', 'user_progress', 'task_completions',
    'modules', 'module_tasks', 'certifications', 'roles'
]

# Draw database tables
table_y = 15
for i, table in enumerate(db_tables):
    x = 35 + (i % 4) * 10
    y = table_y - (i // 4) * 5
    
    box = FancyBboxPatch((x - 4, y - 1.5), 8, 3,
                         boxstyle="round,pad=0.1",
                         facecolor='#FEF5E7',
                         edgecolor='#F39C12',
                         linewidth=1)
    ax.add_patch(box)
    ax.text(x, y, table, ha='center', va='center', fontsize=8)

# Add title
ax.text(50, 95, 'Broetje Training System Architecture', 
        ha='center', va='center', fontsize=20, fontweight='bold')

# Add legend
legend_elements = [
    mpatches.Rectangle((0, 0), 1, 1, facecolor=colors['module'], label='Module System'),
    mpatches.Rectangle((0, 0), 1, 1, facecolor=colors['progress'], label='Progress Tracking'),
    mpatches.Rectangle((0, 0), 1, 1, facecolor=colors['user'], label='User Management'),
    mpatches.Rectangle((0, 0), 1, 1, facecolor=colors['database'], label='Database'),
    mpatches.Rectangle((0, 0), 1, 1, facecolor=colors['ui'], label='User Interface'),
    mpatches.Rectangle((0, 0), 1, 1, facecolor=colors['config'], label='Configuration')
]

ax.legend(handles=legend_elements, loc='lower left', fontsize=10)

# Add file structure representation
file_struct = """
File Structure:
├── modules/
│   ├── module_loader/
│   ├── basic_plc/
│   ├── advanced_plc/
│   └── hmi_development/
├── progress_tracking/
│   ├── progress_manager.py
│   ├── report_generator.py
│   └── progress_visualizer.py
└── user_management/
    ├── authentication.py
    ├── profile_manager.py
    └── role_manager.py
"""

ax.text(5, 40, file_struct, fontsize=9, fontfamily='monospace',
        bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray', alpha=0.8))

plt.tight_layout()
plt.savefig('/media/ros2_ws/cross_platform/Projects Folder/AutomationAcademy/docs/architecture_diagram.png', 
            dpi=300, bbox_inches='tight')
plt.close()

# Create a module flow diagram
fig2, ax2 = plt.subplots(1, 1, figsize=(14, 10))
ax2.set_xlim(0, 100)
ax2.set_ylim(0, 100)
ax2.axis('off')

# Module lifecycle
lifecycle_stages = {
    'discovery': {'pos': (20, 80), 'label': 'Module\nDiscovery'},
    'loading': {'pos': (40, 80), 'label': 'Dynamic\nLoading'},
    'init': {'pos': (60, 80), 'label': 'Module\nInitialization'},
    'execute': {'pos': (80, 80), 'label': 'Module\nExecution'},
    'track': {'pos': (40, 50), 'label': 'Progress\nTracking'},
    'report': {'pos': (60, 50), 'label': 'Report\nGeneration'},
    'cert': {'pos': (80, 50), 'label': 'Certification'},
}

# Draw lifecycle stages
for stage, info in lifecycle_stages.items():
    color = colors['module'] if stage in ['discovery', 'loading', 'init', 'execute'] else colors['progress']
    
    circle = plt.Circle(info['pos'], 8, color=color, ec='black', linewidth=2)
    ax2.add_patch(circle)
    ax2.text(info['pos'][0], info['pos'][1], info['label'],
            ha='center', va='center', fontsize=10, fontweight='bold', color='white')

# Draw flow arrows
flows = [
    ('discovery', 'loading'),
    ('loading', 'init'),
    ('init', 'execute'),
    ('execute', 'track'),
    ('track', 'report'),
    ('report', 'cert')
]

for start, end in flows:
    start_pos = lifecycle_stages[start]['pos']
    end_pos = lifecycle_stages[end]['pos']
    
    arrow = ConnectionPatch(start_pos, end_pos, "data", "data",
                           arrowstyle="->", shrinkA=8, shrinkB=8,
                           mutation_scale=20, fc="black", lw=2)
    ax2.add_artist(arrow)

# Add user journey
user_steps = [
    {'pos': (20, 20), 'label': 'Login'},
    {'pos': (35, 20), 'label': 'Select\nModule'},
    {'pos': (50, 20), 'label': 'Complete\nTasks'},
    {'pos': (65, 20), 'label': 'View\nProgress'},
    {'pos': (80, 20), 'label': 'Earn\nCertificate'},
]

for i, step in enumerate(user_steps):
    color = colors['user']
    box = FancyBboxPatch((step['pos'][0] - 5, step['pos'][1] - 3), 10, 6,
                         boxstyle="round,pad=0.3",
                         facecolor=color,
                         edgecolor='black',
                         linewidth=1)
    ax2.add_patch(box)
    ax2.text(step['pos'][0], step['pos'][1], step['label'],
            ha='center', va='center', fontsize=9, color='white')
    
    if i < len(user_steps) - 1:
        arrow = ConnectionPatch(step['pos'], user_steps[i+1]['pos'], "data", "data",
                               arrowstyle="->", shrinkA=5, shrinkB=5,
                               mutation_scale=15, fc="black", lw=1.5)
        ax2.add_artist(arrow)

ax2.text(50, 95, 'Module Lifecycle & User Journey', 
        ha='center', va='center', fontsize=18, fontweight='bold')

plt.tight_layout()
plt.savefig('/media/ros2_ws/cross_platform/Projects Folder/AutomationAcademy/docs/module_flow_diagram.png', 
            dpi=300, bbox_inches='tight')
plt.close()

print("Architecture diagrams created successfully!")