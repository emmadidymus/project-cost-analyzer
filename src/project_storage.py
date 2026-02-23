"""
Project storage functionality for saving and loading projects.
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from src.project import Project, Task


class ProjectStorage:
    """Handles saving and loading projects to/from JSON files."""

    def __init__(self, storage_dir: str = "data/saved_projects"):
        """
        Initialize project storage.

        Args:
            storage_dir: Directory to store saved projects
        """
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_project(self, project: Project) -> str:
        """
        Save a project to a JSON file.

        Args:
            project: The project to save

        Returns:
            Path to the saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_slug = project.name.lower().replace(" ", "_")[:30]
        filename = f"{project_slug}_{timestamp}.json"
        filepath = os.path.join(self.storage_dir, filename)

        # Convert project to dictionary
        project_data = {
            'name': project.name,
            'team_size': project.team_size,
            'risk_level': project.risk_level,
            'description': project.description,
            'saved_at': datetime.now().isoformat(),
            'tasks': [
                {
                    'name': task.name,
                    'estimated_days': task.estimated_days,
                    'cost_per_day': task.cost_per_day,
                    'task_id': task.task_id,
                    'dependencies': task.dependencies
                }
                for task in project.tasks
            ]
        }

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(project_data, f, indent=2)

        return filepath

    def load_project(self, filepath: str) -> Project:
        """
        Load a project from a JSON file.

        Args:
            filepath: Path to the project file

        Returns:
            The loaded Project object
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            project_data = json.load(f)

        # Recreate tasks
        tasks = [
            Task(
                name=task_data['name'],
                estimated_days=task_data['estimated_days'],
                cost_per_day=task_data['cost_per_day'],
                task_id=task_data['task_id'],
                dependencies=task_data['dependencies']
            )
            for task_data in project_data['tasks']
        ]

        # Recreate project
        project = Project(
            name=project_data['name'],
            tasks=tasks,
            team_size=project_data['team_size'],
            risk_level=project_data['risk_level'],
            description=project_data.get('description', '')
        )

        return project

    def list_saved_projects(self) -> List[Dict]:
        """
        List all saved projects.

        Returns:
            List of dictionaries with project metadata
        """
        projects = []

        if not os.path.exists(self.storage_dir):
            return projects

        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.storage_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)

                    projects.append({
                        'filename': filename,
                        'filepath': filepath,
                        'name': project_data['name'],
                        'team_size': project_data['team_size'],
                        'risk_level': project_data['risk_level'],
                        'task_count': len(project_data['tasks']),
                        'saved_at': project_data.get('saved_at', 'Unknown')
                    })
                except Exception as e:
                    print(f"Error reading {filename}: {e}")

        # Sort by saved_at descending (newest first)
        projects.sort(key=lambda x: x['saved_at'], reverse=True)

        return projects

    def delete_project(self, filepath: str) -> bool:
        """
        Delete a saved project file.

        Args:
            filepath: Path to the project file

        Returns:
            True if deleted successfully
        """
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Error deleting project: {e}")
            return False