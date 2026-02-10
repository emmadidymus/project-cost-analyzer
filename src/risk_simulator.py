"""
Monte Carlo risk simulation for project cost and timeline analysis.
"""

import random
from typing import Dict, List, Tuple
from dataclasses import dataclass
from src.project import Project
from src.calculator import ProjectCalculator
from src.utils import calculate_percentile


@dataclass
class SimulationResult:
    """
    Results from a Monte Carlo simulation run.
    """
    costs: List[float]
    timelines: List[float]
    iterations: int

    @property
    def cost_mean(self) -> float:
        """Average cost across all simulations."""
        return sum(self.costs) / len(self.costs) if self.costs else 0.0

    @property
    def timeline_mean(self) -> float:
        """Average timeline across all simulations."""
        return sum(self.timelines) / len(self.timelines) if self.timelines else 0.0

    @property
    def cost_std(self) -> float:
        """Standard deviation of costs."""
        if not self.costs:
            return 0.0
        mean = self.cost_mean
        variance = sum((x - mean) ** 2 for x in self.costs) / len(self.costs)
        return variance ** 0.5

    @property
    def timeline_std(self) -> float:
        """Standard deviation of timelines."""
        if not self.timelines:
            return 0.0
        mean = self.timeline_mean
        variance = sum((x - mean) ** 2 for x in self.timelines) / len(self.timelines)
        return variance ** 0.5

    def get_cost_percentile(self, percentile: float) -> float:
        """Get cost at specific percentile (0-100)."""
        return calculate_percentile(self.costs, percentile)

    def get_timeline_percentile(self, percentile: float) -> float:
        """Get timeline at specific percentile (0-100)."""
        return calculate_percentile(self.timelines, percentile)

    def get_scenarios(self) -> Dict[str, Dict[str, float]]:
        """
        Get best, average, and worst case scenarios.

        Returns:
            Dictionary with scenario data
        """
        return {
            'best_case': {
                'cost': self.get_cost_percentile(10),
                'timeline': self.get_timeline_percentile(10),
                'probability': '10% chance of being this good or better'
            },
            'expected': {
                'cost': self.cost_mean,
                'timeline': self.timeline_mean,
                'probability': 'Most likely outcome (mean)'
            },
            'worst_case': {
                'cost': self.get_cost_percentile(90),
                'timeline': self.get_timeline_percentile(90),
                'probability': '10% chance of being this bad or worse'
            },
            'p50': {
                'cost': self.get_cost_percentile(50),
                'timeline': self.get_timeline_percentile(50),
                'probability': '50% confidence level (median)'
            },
            'p75': {
                'cost': self.get_cost_percentile(75),
                'timeline': self.get_timeline_percentile(75),
                'probability': '25% chance of exceeding this'
            }
        }


class RiskSimulator:
    """
    Monte Carlo simulator for project risk analysis.
    """

    def __init__(self, project: Project, iterations: int = 1000):
        """
        Initialize the risk simulator.

        Args:
            project: The project to simulate
            iterations: Number of Monte Carlo iterations (default 1000)
        """
        self.project = project
        self.iterations = max(100, iterations)  # Minimum 100 iterations
        self.calculator = ProjectCalculator(project)

    def run_simulation(self) -> SimulationResult:
        """
        Run Monte Carlo simulation.

        Returns:
            SimulationResult with cost and timeline distributions
        """
        costs = []
        timelines = []

        for _ in range(self.iterations):
            # Simulate one scenario
            scenario_cost, scenario_timeline = self._simulate_single_scenario()
            costs.append(scenario_cost)
            timelines.append(scenario_timeline)

        return SimulationResult(
            costs=costs,
            timelines=timelines,
            iterations=self.iterations
        )

    def _simulate_single_scenario(self) -> Tuple[float, float]:
        """
        Simulate a single project scenario with random variations.

        Returns:
            Tuple of (total_cost, total_timeline)
        """
        total_cost = 0.0
        total_timeline = 0.0

        # Simulate each task with random variation
        task_durations = {}

        for task in self.project.tasks:
            # Random variation based on risk level
            variation_range = self._get_variation_range()

            # Cost variation (labor rate fluctuation, resource availability)
            cost_multiplier = random.uniform(
                1.0 - variation_range * 0.5,
                1.0 + variation_range
            )
            task_cost = task.base_cost * cost_multiplier
            total_cost += task_cost

            # Timeline variation (delays, unexpected issues, efficiency)
            time_multiplier = random.uniform(
                1.0 - variation_range * 0.3,
                1.0 + variation_range * 1.2
            )
            task_duration = task.estimated_days * time_multiplier
            task_durations[task.task_id] = task_duration

        # Calculate timeline considering dependencies and resources
        total_timeline = self._calculate_scenario_timeline(task_durations)

        # Add risk-based overhead
        risk_factor = self._get_risk_factor()
        total_cost *= risk_factor
        total_timeline *= risk_factor

        return total_cost, total_timeline

    def _get_variation_range(self) -> float:
        """
        Get the variation range based on project risk level.

        Returns:
            Variation range (0.0 to 1.0+)
        """
        risk_variations = {
            'low': 0.15,  # ±15% variation
            'medium': 0.30,  # ±30% variation
            'high': 0.50  # ±50% variation
        }
        return risk_variations.get(self.project.risk_level, 0.30)

    def _get_risk_factor(self) -> float:
        """
        Generate a random risk factor for this scenario.

        Returns:
            Risk multiplier
        """
        # Base risk multiplier with some randomness
        base_multiplier = {
            'low': 1.05,
            'medium': 1.15,
            'high': 1.30
        }.get(self.project.risk_level, 1.15)

        # Add random variation (normally distributed around base)
        variation = random.gauss(0, 0.1)  # Mean 0, std 0.1
        return max(1.0, base_multiplier + variation)

    def _calculate_scenario_timeline(self, task_durations: Dict[str, float]) -> float:
        """
        Calculate project timeline for a scenario with specific task durations.

        Args:
            task_durations: Dictionary mapping task_id to simulated duration

        Returns:
            Total project duration
        """
        # Track when each task finishes
        task_finish_times = {}

        # Calculate finish times considering dependencies
        for task in self.project.tasks:
            # Earliest this task can start
            earliest_start = 0.0
            for dep_id in task.dependencies:
                if dep_id in task_finish_times:
                    earliest_start = max(earliest_start, task_finish_times[dep_id])

            # Task finishes after its duration
            task_finish_times[task.task_id] = earliest_start + task_durations[task.task_id]

        # If we have limited resources, add queuing delays
        if self.project.team_size < self.project.task_count:
            # Simulate resource contention with random delays
            contention_factor = 1.0 + (0.1 * (self.project.task_count / self.project.team_size - 1))
            contention_factor *= random.uniform(0.8, 1.2)  # Add randomness
            return max(task_finish_times.values()) * contention_factor if task_finish_times else 0.0

        return max(task_finish_times.values()) if task_finish_times else 0.0

    def analyze_risk_drivers(self, result: SimulationResult) -> Dict[str, any]:
        """
        Analyze what's driving the risk in the project.

        Args:
            result: Simulation result to analyze

        Returns:
            Dictionary with risk driver analysis
        """
        # Calculate variability metrics
        cost_cv = (result.cost_std / result.cost_mean) if result.cost_mean > 0 else 0
        timeline_cv = (result.timeline_std / result.timeline_mean) if result.timeline_mean > 0 else 0

        # Determine primary risk drivers
        drivers = []

        if self.project.risk_level == 'high':
            drivers.append("High inherent project risk level")

        if self.project.team_size < self.project.task_count / 2:
            drivers.append("Limited team resources relative to task count")

        if cost_cv > 0.2:
            drivers.append("High cost variability")

        if timeline_cv > 0.2:
            drivers.append("High timeline uncertainty")

        # Check for complex dependencies
        critical_path = self.project.get_critical_path()
        if len(critical_path) > self.project.task_count * 0.6:
            drivers.append("Long critical path with many dependencies")

        return {
            'cost_variability': cost_cv,
            'timeline_variability': timeline_cv,
            'primary_drivers': drivers if drivers else ["Low risk project with stable estimates"],
            'risk_level': self.project.risk_level,
            'confidence_80_percent': {
                'cost_range': (
                    result.get_cost_percentile(10),
                    result.get_cost_percentile(90)
                ),
                'timeline_range': (
                    result.get_timeline_percentile(10),
                    result.get_timeline_percentile(90)
                )
            }
        }

    def generate_summary_report(self, result: SimulationResult) -> str:
        """
        Generate a text summary of simulation results.

        Args:
            result: Simulation result

        Returns:
            Formatted text report
        """
        scenarios = result.get_scenarios()
        risk_analysis = self.analyze_risk_drivers(result)

        report = []
        report.append("=" * 70)
        report.append("MONTE CARLO RISK SIMULATION REPORT")
        report.append("=" * 70)
        report.append(f"Project: {self.project.name}")
        report.append(f"Iterations: {result.iterations:,}")
        report.append(f"Risk Level: {self.project.risk_level.capitalize()}")
        report.append("")

        report.append("SCENARIO ANALYSIS:")
        report.append("-" * 70)
        for scenario_name, data in scenarios.items():
            report.append(f"\n{scenario_name.upper().replace('_', ' ')}:")
            report.append(f"  Cost: ${data['cost']:,.2f}")
            report.append(f"  Timeline: {data['timeline']:.1f} days")
            report.append(f"  Note: {data['probability']}")

        report.append("\n" + "=" * 70)
        report.append("STATISTICAL SUMMARY:")
        report.append("-" * 70)
        report.append(f"Cost Mean: ${result.cost_mean:,.2f}")
        report.append(f"Cost Std Dev: ${result.cost_std:,.2f}")
        report.append(f"Timeline Mean: {result.timeline_mean:.1f} days")
        report.append(f"Timeline Std Dev: {result.timeline_std:.1f} days")

        report.append("\n" + "=" * 70)
        report.append("RISK DRIVERS:")
        report.append("-" * 70)
        for driver in risk_analysis['primary_drivers']:
            report.append(f"  • {driver}")

        report.append(f"\nCost Variability: {risk_analysis['cost_variability']:.1%}")
        report.append(f"Timeline Variability: {risk_analysis['timeline_variability']:.1%}")

        cost_range = risk_analysis['confidence_80_percent']['cost_range']
        time_range = risk_analysis['confidence_80_percent']['timeline_range']
        report.append(f"\n80% Confidence Interval:")
        report.append(f"  Cost: ${cost_range[0]:,.2f} - ${cost_range[1]:,.2f}")
        report.append(f"  Timeline: {time_range[0]:.1f} - {time_range[1]:.1f} days")

        report.append("\n" + "=" * 70)

        return "\n".join(report)