"""
Calculator for project cost and timeline estimation.
"""

from typing import Dict, List, Tuple
from src.project import Project, Task
from src.utils import get_risk_multiplier, validate_positive_number


class ProjectCalculator:
    """
    Handles cost and timeline calculations for projects.
    """

    def __init__(self, project: Project):
        """
        Initialize calculator with a project.

        Args:
            project: The project to analyze
        """
        self.project = project
        self.risk_multiplier = get_risk_multiplier(project.risk_level)

    def calculate_base_cost(self) -> float:
        """
        Calculate the total base cost (no risk adjustment).

        Returns:
            Total base cost
        """
        return self.project.total_base_cost

    def calculate_adjusted_cost(self) -> float:
        """
        Calculate cost with risk adjustment.

        Returns:
            Risk-adjusted total cost
        """
        return self.project.total_base_cost * self.risk_multiplier

    def calculate_cost_per_resource(self) -> float:
        """
        Calculate average cost per team member.

        Returns:
            Cost per resource
        """
        adjusted_cost = self.calculate_adjusted_cost()
        return adjusted_cost / self.project.team_size

    def calculate_sequential_timeline(self) -> float:
        """
        Calculate timeline if all tasks run sequentially (worst case).

        Returns:
            Total days if sequential
        """
        return self.project.total_estimated_days * self.risk_multiplier

    def calculate_parallel_timeline(self) -> float:
        """
        Calculate timeline with parallel execution and resource constraints.
        Uses critical path and considers team size limitations.

        Returns:
            Estimated project duration in days
        """
        if not self.project.tasks:
            return 0.0

        # Get critical path duration (minimum possible timeline)
        critical_path = self.project.get_critical_path()
        critical_path_duration = sum(task.estimated_days for task in critical_path)

        # Calculate resource-constrained timeline
        # This simulates task scheduling with limited team members
        timeline = self._simulate_resource_constrained_schedule()

        # Apply risk multiplier
        adjusted_timeline = timeline * self.risk_multiplier

        # Timeline can't be less than critical path
        min_timeline = critical_path_duration * self.risk_multiplier

        return max(adjusted_timeline, min_timeline)

    def _simulate_resource_constrained_schedule(self) -> float:
        """
        Simulate project execution with resource constraints.

        Returns:
            Estimated duration considering resource availability
        """
        # Track when each task can start and finish
        task_start_times = {}
        task_finish_times = {}

        # Track available team members over time
        team_availability = {0: self.project.team_size}

        # Build dependency completion times
        for task in self.project.tasks:
            # Earliest this task can start based on dependencies
            earliest_start = 0.0
            for dep_id in task.dependencies:
                if dep_id in task_finish_times:
                    earliest_start = max(earliest_start, task_finish_times[dep_id])

            task_start_times[task.task_id] = earliest_start
            task_finish_times[task.task_id] = earliest_start + task.estimated_days

        # If we have enough resources for all tasks, use dependency-based timeline
        if self.project.team_size >= self.project.task_count:
            return max(task_finish_times.values()) if task_finish_times else 0.0

        # Otherwise, simulate resource contention
        # Sort tasks by earliest start time
        sorted_tasks = sorted(
            self.project.tasks,
            key=lambda t: (task_start_times[t.task_id], -t.estimated_days)
        )

        # Reschedule considering resource limits
        scheduled_start = {}
        scheduled_finish = {}
        active_tasks = []
        current_time = 0.0
        remaining_tasks = sorted_tasks.copy()

        while remaining_tasks or active_tasks:
            # Complete any finished tasks
            active_tasks = [
                t for t in active_tasks
                if scheduled_finish[t.task_id] > current_time
            ]

            # Try to start new tasks
            can_start = []
            for task in remaining_tasks:
                # Check if dependencies are complete
                deps_complete = all(
                    dep_id in scheduled_finish and scheduled_finish[dep_id] <= current_time
                    for dep_id in task.dependencies
                )

                if deps_complete and len(active_tasks) < self.project.team_size:
                    can_start.append(task)

            # Start tasks
            for task in can_start:
                scheduled_start[task.task_id] = current_time
                scheduled_finish[task.task_id] = current_time + task.estimated_days
                active_tasks.append(task)
                remaining_tasks.remove(task)

            # Advance time to next event (task completion or all tasks scheduled)
            if active_tasks:
                next_finish = min(scheduled_finish[t.task_id] for t in active_tasks)
                current_time = next_finish
            elif remaining_tasks:
                # Jump to when next task can start
                next_task = remaining_tasks[0]
                if next_task.dependencies:
                    current_time = max(
                        scheduled_finish.get(dep_id, 0)
                        for dep_id in next_task.dependencies
                    )
                else:
                    current_time += 0.1  # Small increment to avoid infinite loop
            else:
                break

        return max(scheduled_finish.values()) if scheduled_finish else 0.0

    def calculate_timeline_breakdown(self) -> Dict[str, float]:
        """
        Get a breakdown of different timeline estimates.

        Returns:
            Dictionary with various timeline calculations
        """
        return {
            'sequential': self.calculate_sequential_timeline(),
            'parallel_optimistic': sum(task.estimated_days for task in self.project.get_critical_path()),
            'parallel_realistic': self.calculate_parallel_timeline(),
        }

    def calculate_cost_breakdown(self) -> Dict[str, float]:
        """
        Get a detailed cost breakdown.

        Returns:
            Dictionary with cost components
        """
        base_cost = self.calculate_base_cost()
        adjusted_cost = self.calculate_adjusted_cost()
        risk_overhead = adjusted_cost - base_cost

        return {
            'base_cost': base_cost,
            'risk_overhead': risk_overhead,
            'total_cost': adjusted_cost,
            'cost_per_resource': self.calculate_cost_per_resource(),
        }

    def calculate_task_costs(self) -> List[Dict[str, any]]:
        """
        Calculate cost for each individual task.

        Returns:
            List of dictionaries with task cost details
        """
        task_costs = []

        for task in self.project.tasks:
            base = task.base_cost
            adjusted = base * self.risk_multiplier

            task_costs.append({
                'task_name': task.name,
                'task_id': task.task_id,
                'base_cost': base,
                'adjusted_cost': adjusted,
                'days': task.estimated_days,
                'cost_per_day': task.cost_per_day,
            })

        return task_costs

    def get_critical_path_analysis(self) -> Dict[str, any]:
        """
        Analyze the critical path.

        Returns:
            Dictionary with critical path information
        """
        critical_path = self.project.get_critical_path()

        if not critical_path:
            return {
                'exists': False,
                'tasks': [],
                'duration': 0.0,
                'cost': 0.0,
            }

        duration = sum(task.estimated_days for task in critical_path)
        cost = sum(task.base_cost for task in critical_path)

        return {
            'exists': True,
            'tasks': [task.name for task in critical_path],
            'task_count': len(critical_path),
            'duration': duration,
            'adjusted_duration': duration * self.risk_multiplier,
            'cost': cost,
            'adjusted_cost': cost * self.risk_multiplier,
        }

    def generate_summary(self) -> Dict[str, any]:
        """
        Generate a comprehensive summary of all calculations.

        Returns:
            Dictionary with complete project analysis
        """
        cost_breakdown = self.calculate_cost_breakdown()
        timeline_breakdown = self.calculate_timeline_breakdown()
        critical_path = self.get_critical_path_analysis()

        return {
            'project_name': self.project.name,
            'team_size': self.project.team_size,
            'risk_level': self.project.risk_level,
            'risk_multiplier': self.risk_multiplier,
            'task_count': self.project.task_count,
            'costs': cost_breakdown,
            'timelines': timeline_breakdown,
            'critical_path': critical_path,
        }