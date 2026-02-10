"""
Project and Task data models.
"""

from typing import List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class Task:
    """
    Represents a single task in a project.
    """
    name: str
    estimated_days: float
    cost_per_day: float
    dependencies: List[str] = field(default_factory=list)
    task_id: Optional[str] = None

    def __post_init__(self):
        """Generate task_id if not provided."""
        if self.task_id is None:
            # Create a simple ID from the task name
            self.task_id = self.name.lower().replace(" ", "_")[:20]

    @property
    def base_cost(self) -> float:
        """Calculate the base cost for this task."""
        return self.estimated_days * self.cost_per_day

    def __str__(self) -> str:
        """String representation of the task."""
        deps = f" (depends on: {', '.join(self.dependencies)})" if self.dependencies else ""
        return f"{self.name}: {self.estimated_days} days @ ${self.cost_per_day}/day{deps}"

    def has_dependencies(self) -> bool:
        """Check if this task has dependencies."""
        return len(self.dependencies) > 0


@dataclass
class Project:
    """
    Represents a complete project with tasks and configuration.
    """
    name: str
    tasks: List[Task]
    team_size: int
    risk_level: str
    description: str = ""

    def __post_init__(self):
        """Validate project data after initialization."""
        if self.team_size <= 0:
            raise ValueError("Team size must be at least 1")

        if not self.tasks:
            raise ValueError("Project must have at least one task")

        # Validate risk level
        valid_risk_levels = ['low', 'medium', 'high']
        if self.risk_level.lower() not in valid_risk_levels:
            raise ValueError(f"Risk level must be one of {valid_risk_levels}")

        self.risk_level = self.risk_level.lower()

    @property
    def total_base_cost(self) -> float:
        """Calculate total base cost across all tasks."""
        return sum(task.base_cost for task in self.tasks)

    @property
    def total_estimated_days(self) -> float:
        """Calculate total estimated days (sum of all tasks, no parallelization)."""
        return sum(task.estimated_days for task in self.tasks)

    @property
    def task_count(self) -> int:
        """Get the number of tasks in the project."""
        return len(self.tasks)

    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        """
        Get a task by its ID.

        Args:
            task_id: The task ID to search for

        Returns:
            The task if found, None otherwise
        """
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def get_task_by_name(self, name: str) -> Optional[Task]:
        """
        Get a task by its name.

        Args:
            name: The task name to search for

        Returns:
            The task if found, None otherwise
        """
        for task in self.tasks:
            if task.name.lower() == name.lower():
                return task
        return None

    def validate_dependencies(self) -> List[str]:
        """
        Validate that all task dependencies exist and check for circular dependencies.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        task_ids = {task.task_id for task in self.tasks}

        # Check that all dependencies exist
        for task in self.tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    errors.append(
                        f"Task '{task.name}' depends on non-existent task '{dep_id}'"
                    )

        # Check for circular dependencies
        if self._has_circular_dependency():
            errors.append("Project has circular dependencies")

        return errors

    def _has_circular_dependency(self) -> bool:
        """
        Check if the project has circular dependencies using DFS.

        Returns:
            True if circular dependency exists, False otherwise
        """
        # Build adjacency list
        graph = {task.task_id: task.dependencies for task in self.tasks}
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for task in self.tasks:
            if task.task_id not in visited:
                if has_cycle(task.task_id):
                    return True

        return False

    def get_critical_path(self) -> List[Task]:
        """
        Calculate the critical path (longest path) through the project.
        Uses topological sort and longest path algorithm.

        Returns:
            List of tasks in the critical path
        """
        # Build adjacency list and in-degree count
        graph = {task.task_id: task.dependencies for task in self.tasks}
        in_degree = {task.task_id: len(task.dependencies) for task in self.tasks}

        # Calculate earliest start times
        earliest_start = {task.task_id: 0 for task in self.tasks}
        queue = [task.task_id for task in self.tasks if in_degree[task.task_id] == 0]

        while queue:
            current_id = queue.pop(0)
            current_task = self.get_task_by_id(current_id)

            # Update dependent tasks
            for task in self.tasks:
                if current_id in task.dependencies:
                    # Update earliest start time
                    earliest_start[task.task_id] = max(
                        earliest_start[task.task_id],
                        earliest_start[current_id] + current_task.estimated_days
                    )

                    # Decrease in-degree and add to queue if ready
                    in_degree[task.task_id] -= 1
                    if in_degree[task.task_id] == 0:
                        queue.append(task.task_id)

        # Find the task with the latest finish time (end of critical path)
        end_task_id = max(
            earliest_start.keys(),
            key=lambda tid: earliest_start[tid] + self.get_task_by_id(tid).estimated_days
        )

        # Backtrack to find the critical path
        critical_path = []
        current_id = end_task_id

        while current_id:
            current_task = self.get_task_by_id(current_id)
            critical_path.insert(0, current_task)

            # Find the predecessor on the critical path
            if not current_task.dependencies:
                break

            # Find dependency that determines earliest start
            current_id = None
            for dep_id in current_task.dependencies:
                dep_task = self.get_task_by_id(dep_id)
                if earliest_start[dep_id] + dep_task.estimated_days == earliest_start[current_task.task_id]:
                    current_id = dep_id
                    break

        return critical_path

    def get_independent_tasks(self) -> List[Task]:
        """
        Get all tasks that have no dependencies.

        Returns:
            List of tasks with no dependencies
        """
        return [task for task in self.tasks if not task.has_dependencies()]

    def __str__(self) -> str:
        """String representation of the project."""
        return (
            f"Project: {self.name}\n"
            f"Tasks: {self.task_count}\n"
            f"Team Size: {self.team_size}\n"
            f"Risk Level: {self.risk_level.capitalize()}\n"
            f"Base Cost: ${self.total_base_cost:,.2f}\n"
            f"Total Estimated Days: {self.total_estimated_days:.1f}"
        )