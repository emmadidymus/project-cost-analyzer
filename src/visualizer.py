"""
Visualization tools for project analysis results.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import List, Dict
import os
from src.risk_simulator import SimulationResult
from src.calculator import ProjectCalculator
from src.project import Project
from src.utils import ensure_output_directory


class ProjectVisualizer:
    """
    Creates charts and visualizations for project analysis.
    """

    def __init__(self, project: Project, output_dir: str = "output/reports"):
        """
        Initialize the visualizer.

        Args:
            project: The project to visualize
            output_dir: Directory to save charts
        """
        self.project = project
        self.output_dir = ensure_output_directory(output_dir)
        self.calculator = ProjectCalculator(project)

        # Set style for professional-looking charts
        plt.style.use('seaborn-v0_8-darkgrid')

    def create_cost_breakdown_chart(self, filename: str = "cost_breakdown.png") -> str:
        """
        Create a pie chart showing cost breakdown by task.

        Args:
            filename: Name for the output file

        Returns:
            Full path to saved chart
        """
        task_costs = self.calculator.calculate_task_costs()

        # Prepare data
        labels = [tc['task_name'] for tc in task_costs]
        sizes = [tc['adjusted_cost'] for tc in task_costs]
        colors = plt.cm.Set3(range(len(labels)))

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90
        )

        # Styling
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

        ax.set_title(
            f'Cost Breakdown by Task\n{self.project.name}\nTotal: ${sum(sizes):,.2f}',
            fontsize=14,
            fontweight='bold',
            pad=20
        )

        plt.tight_layout()

        # Save
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def create_timeline_comparison_chart(self, filename: str = "timeline_comparison.png") -> str:
        """
        Create a bar chart comparing different timeline scenarios.

        Args:
            filename: Name for the output file

        Returns:
            Full path to saved chart
        """
        timeline_breakdown = self.calculator.calculate_timeline_breakdown()

        # Prepare data
        scenarios = ['Sequential\n(Worst Case)', 'Critical Path\n(Optimistic)', 'Realistic\n(With Resources)']
        durations = [
            timeline_breakdown['sequential'],
            timeline_breakdown['parallel_optimistic'],
            timeline_breakdown['parallel_realistic']
        ]
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1']

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create bars
        bars = ax.bar(scenarios, durations, color=colors, edgecolor='black', linewidth=1.5)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{height:.1f} days',
                ha='center',
                va='bottom',
                fontweight='bold',
                fontsize=11
            )

        # Styling
        ax.set_ylabel('Duration (days)', fontsize=12, fontweight='bold')
        ax.set_title(
            f'Timeline Comparison\n{self.project.name}',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        # Save
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def create_risk_distribution_chart(
            self,
            simulation_result: SimulationResult,
            filename: str = "risk_distribution.png"
    ) -> str:
        """
        Create histograms showing cost and timeline distributions.

        Args:
            simulation_result: Results from Monte Carlo simulation
            filename: Name for the output file

        Returns:
            Full path to saved chart
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Cost distribution
        ax1.hist(
            simulation_result.costs,
            bins=50,
            color='#45b7d1',
            edgecolor='black',
            alpha=0.7
        )

        # Add mean line
        mean_cost = simulation_result.cost_mean
        ax1.axvline(
            mean_cost,
            color='red',
            linestyle='--',
            linewidth=2,
            label=f'Mean: ${mean_cost:,.0f}'
        )

        # Add percentile lines
        p10 = simulation_result.get_cost_percentile(10)
        p90 = simulation_result.get_cost_percentile(90)
        ax1.axvline(p10, color='green', linestyle=':', linewidth=2, label=f'P10: ${p10:,.0f}')
        ax1.axvline(p90, color='orange', linestyle=':', linewidth=2, label=f'P90: ${p90:,.0f}')

        ax1.set_xlabel('Cost ($)', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax1.set_title('Cost Distribution', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(alpha=0.3)

        # Timeline distribution
        ax2.hist(
            simulation_result.timelines,
            bins=50,
            color='#f39c12',
            edgecolor='black',
            alpha=0.7
        )

        # Add mean line
        mean_timeline = simulation_result.timeline_mean
        ax2.axvline(
            mean_timeline,
            color='red',
            linestyle='--',
            linewidth=2,
            label=f'Mean: {mean_timeline:.1f} days'
        )

        # Add percentile lines
        t10 = simulation_result.get_timeline_percentile(10)
        t90 = simulation_result.get_timeline_percentile(90)
        ax2.axvline(t10, color='green', linestyle=':', linewidth=2, label=f'P10: {t10:.1f} days')
        ax2.axvline(t90, color='orange', linestyle=':', linewidth=2, label=f'P90: {t90:.1f} days')

        ax2.set_xlabel('Timeline (days)', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax2.set_title('Timeline Distribution', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(alpha=0.3)

        # Overall title
        fig.suptitle(
            f'Monte Carlo Risk Analysis - {self.project.name}\n{simulation_result.iterations:,} Simulations',
            fontsize=14,
            fontweight='bold',
            y=1.02
        )

        plt.tight_layout()

        # Save
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def create_scenario_comparison_chart(
            self,
            simulation_result: SimulationResult,
            filename: str = "scenario_comparison.png"
    ) -> str:
        """
        Create a chart comparing best, expected, and worst case scenarios.

        Args:
            simulation_result: Results from Monte Carlo simulation
            filename: Name for the output file

        Returns:
            Full path to saved chart
        """
        scenarios = simulation_result.get_scenarios()

        # Prepare data
        scenario_names = ['Best Case\n(P10)', 'Expected\n(Mean)', 'P75', 'Worst Case\n(P90)']
        scenario_keys = ['best_case', 'expected', 'p75', 'worst_case']

        costs = [scenarios[key]['cost'] for key in scenario_keys]
        timelines = [scenarios[key]['timeline'] for key in scenario_keys]

        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Cost comparison
        colors_cost = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
        bars1 = ax1.bar(scenario_names, costs, color=colors_cost, edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar in bars1:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'${height:,.0f}',
                ha='center',
                va='bottom',
                fontweight='bold',
                fontsize=10
            )

        ax1.set_ylabel('Cost ($)', fontsize=12, fontweight='bold')
        ax1.set_title('Cost Scenarios', fontsize=13, fontweight='bold')
        ax1.grid(axis='y', alpha=0.3)

        # Timeline comparison
        colors_time = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
        bars2 = ax2.bar(scenario_names, timelines, color=colors_time, edgecolor='black', linewidth=1.5)

        # Add value labels
        for bar in bars2:
            height = bar.get_height()
            ax2.text(
                bar.get_x() + bar.get_width() / 2.,
                height,
                f'{height:.1f} days',
                ha='center',
                va='bottom',
                fontweight='bold',
                fontsize=10
            )

        ax2.set_ylabel('Timeline (days)', fontsize=12, fontweight='bold')
        ax2.set_title('Timeline Scenarios', fontsize=13, fontweight='bold')
        ax2.grid(axis='y', alpha=0.3)

        # Overall title
        fig.suptitle(
            f'Scenario Comparison - {self.project.name}',
            fontsize=14,
            fontweight='bold',
            y=1.02
        )

        plt.tight_layout()

        # Save
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def create_critical_path_chart(self, filename: str = "critical_path.png") -> str:
        """
        Create a horizontal bar chart showing critical path tasks.

        Args:
            filename: Name for the output file

        Returns:
            Full path to saved chart
        """
        critical_path = self.project.get_critical_path()

        if not critical_path:
            return None

        # Prepare data
        task_names = [task.name for task in critical_path]
        durations = [task.estimated_days for task in critical_path]

        # Create figure
        fig, ax = plt.subplots(figsize=(10, max(6, len(critical_path) * 0.5)))

        # Create horizontal bars
        y_pos = range(len(task_names))
        bars = ax.barh(y_pos, durations, color='#e74c3c', edgecolor='black', linewidth=1.5)

        # Add value labels
        for i, (bar, duration) in enumerate(zip(bars, durations)):
            width = bar.get_width()
            ax.text(
                width,
                bar.get_y() + bar.get_height() / 2.,
                f' {duration:.1f} days',
                ha='left',
                va='center',
                fontweight='bold',
                fontsize=10
            )

        # Styling
        ax.set_yticks(y_pos)
        ax.set_yticklabels(task_names)
        ax.set_xlabel('Duration (days)', fontsize=12, fontweight='bold')
        ax.set_title(
            f'Critical Path Tasks - {self.project.name}\nTotal Duration: {sum(durations):.1f} days',
            fontsize=14,
            fontweight='bold',
            pad=20
        )
        ax.grid(axis='x', alpha=0.3)

        plt.tight_layout()

        # Save
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()

        return filepath

    def generate_all_charts(self, simulation_result: SimulationResult = None) -> Dict[str, str]:
        """
        Generate all available charts.

        Args:
            simulation_result: Optional simulation result for risk charts

        Returns:
            Dictionary mapping chart names to file paths
        """
        charts = {}

        print("Generating visualizations...")

        # Always generate these
        charts['cost_breakdown'] = self.create_cost_breakdown_chart()
        print("  ✓ Cost breakdown chart created")

        charts['timeline_comparison'] = self.create_timeline_comparison_chart()
        print("  ✓ Timeline comparison chart created")

        charts['critical_path'] = self.create_critical_path_chart()
        if charts['critical_path']:
            print("  ✓ Critical path chart created")

        # Generate simulation charts if result provided
        if simulation_result:
            charts['risk_distribution'] = self.create_risk_distribution_chart(simulation_result)
            print("  ✓ Risk distribution chart created")

            charts['scenario_comparison'] = self.create_scenario_comparison_chart(simulation_result)
            print("  ✓ Scenario comparison chart created")

        print(f"\nAll charts saved to: {self.output_dir}\n")

        return charts