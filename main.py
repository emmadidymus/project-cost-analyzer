"""
Main entry point for the Project Cost & Risk Analyzer.
"""

import csv
import os
from datetime import datetime
from src.project import Project, Task
from src.calculator import ProjectCalculator
from src.risk_simulator import RiskSimulator
from src.visualizer import ProjectVisualizer
from src.utils import (
    validate_positive_number,
    validate_risk_level,
    format_currency,
    format_duration,
    print_section_header,
    print_key_value,
    save_text_report
)


def get_user_input():
    """
    Get project information from user through CLI.

    Returns:
        Project object with user-provided data
    """
    print_section_header("PROJECT COST & RISK ANALYZER")
    print("\nWelcome! Let's analyze your project.\n")

    # Get project name
    project_name = input("Enter project name: ").strip()
    while not project_name:
        print("Project name cannot be empty.")
        project_name = input("Enter project name: ").strip()

    # Get team size
    while True:
        try:
            team_size = int(input("Enter team size (number of people): ").strip())
            validate_positive_number(team_size, "Team size")
            break
        except ValueError as e:
            print(f"Error: {e}")

    # Get risk level
    while True:
        risk_level = input("Enter risk level (low/medium/high): ").strip()
        try:
            risk_level = validate_risk_level(risk_level)
            break
        except ValueError as e:
            print(f"Error: {e}")

    # Get tasks
    print("\n" + "-" * 60)
    print("Now let's add tasks to your project.")
    print("Enter task details. Type 'done' when finished.")
    print("-" * 60 + "\n")

    tasks = []
    task_number = 1

    while True:
        print(f"\n--- Task {task_number} ---")

        task_name = input("Task name (or 'done' to finish): ").strip()
        if task_name.lower() == 'done':
            if not tasks:
                print("You must add at least one task.")
                continue
            break

        # Get estimated days
        while True:
            try:
                days = float(input("Estimated days: ").strip())
                validate_positive_number(days, "Estimated days")
                break
            except ValueError as e:
                print(f"Error: {e}")

        # Get cost per day
        while True:
            try:
                cost_per_day = float(input("Cost per day ($): ").strip())
                validate_positive_number(cost_per_day, "Cost per day")
                break
            except ValueError as e:
                print(f"Error: {e}")

        # Create task
        task = Task(
            name=task_name,
            estimated_days=days,
            cost_per_day=cost_per_day
        )
        tasks.append(task)

        print(f"✓ Task added: {task_name} ({days} days @ ${cost_per_day}/day)")
        task_number += 1

    # Ask about dependencies
    print("\n" + "-" * 60)
    add_deps = input("\nDo you want to add task dependencies? (yes/no): ").strip().lower()

    if add_deps in ['yes', 'y']:
        print("\nAvailable tasks:")
        for i, task in enumerate(tasks, 1):
            print(f"  {i}. {task.name} (ID: {task.task_id})")

        for task in tasks:
            print(f"\nTask: {task.name}")
            deps = input("  Enter dependencies (comma-separated task IDs, or press Enter for none): ").strip()

            if deps:
                task.dependencies = [d.strip() for d in deps.split(',')]

    # Create project
    project = Project(
        name=project_name,
        tasks=tasks,
        team_size=team_size,
        risk_level=risk_level
    )

    # Validate dependencies
    errors = project.validate_dependencies()
    if errors:
        print("\n⚠ Warning: Dependency validation errors:")
        for error in errors:
            print(f"  - {error}")
        print("Continuing with current dependencies...\n")

    return project


def display_basic_analysis(project: Project, calculator: ProjectCalculator):
    """Display basic project analysis."""
    print_section_header("BASIC PROJECT ANALYSIS")

    print("\nProject Information:")
    print_key_value("Name", project.name)
    print_key_value("Tasks", str(project.task_count))
    print_key_value("Team Size", str(project.team_size))
    print_key_value("Risk Level", project.risk_level.capitalize())

    cost_breakdown = calculator.calculate_cost_breakdown()
    print("\nCost Analysis:")
    print_key_value("Base Cost", format_currency(cost_breakdown['base_cost']))
    print_key_value("Risk Overhead", format_currency(cost_breakdown['risk_overhead']))
    print_key_value("Total Estimated Cost", format_currency(cost_breakdown['total_cost']))
    print_key_value("Cost per Team Member", format_currency(cost_breakdown['cost_per_resource']))

    timeline_breakdown = calculator.calculate_timeline_breakdown()
    print("\nTimeline Analysis:")
    print_key_value("Sequential (Worst Case)", format_duration(timeline_breakdown['sequential']))
    print_key_value("Critical Path (Optimistic)", format_duration(timeline_breakdown['parallel_optimistic']))
    print_key_value("Realistic Estimate", format_duration(timeline_breakdown['parallel_realistic']))

    critical_path_info = calculator.get_critical_path_analysis()
    if critical_path_info['exists']:
        print("\nCritical Path:")
        print_key_value("Tasks in Critical Path", str(critical_path_info['task_count']))
        print_key_value("Critical Path Duration", format_duration(critical_path_info['duration']))
        print_key_value("Adjusted Duration", format_duration(critical_path_info['adjusted_duration']))
        print("  Critical Path Tasks:")
        for task_name in critical_path_info['tasks']:
            print(f"    → {task_name}")


def run_monte_carlo_simulation(project: Project):
    """Run Monte Carlo simulation."""
    print_section_header("MONTE CARLO RISK SIMULATION")

    while True:
        try:
            iterations_input = input("\nEnter number of simulations (default 1000, min 100): ").strip()
            if not iterations_input:
                iterations = 1000
            else:
                iterations = int(iterations_input)
                if iterations < 100:
                    print("Minimum 100 iterations required.")
                    continue
            break
        except ValueError:
            print("Please enter a valid number.")

    print(f"\nRunning {iterations:,} simulations...")
    print("This may take a moment...\n")

    simulator = RiskSimulator(project, iterations=iterations)
    result = simulator.run_simulation()

    print("✓ Simulation complete!\n")

    print_section_header("SCENARIO ANALYSIS")
    scenarios = result.get_scenarios()

    print("\nBEST CASE (10th Percentile):")
    print_key_value("Cost", format_currency(scenarios['best_case']['cost']))
    print_key_value("Timeline", format_duration(scenarios['best_case']['timeline']))

    print("\nEXPECTED CASE (Mean):")
    print_key_value("Cost", format_currency(scenarios['expected']['cost']))
    print_key_value("Timeline", format_duration(scenarios['expected']['timeline']))

    print("\nWORST CASE (90th Percentile):")
    print_key_value("Cost", format_currency(scenarios['worst_case']['cost']))
    print_key_value("Timeline", format_duration(scenarios['worst_case']['timeline']))

    print_section_header("RISK ANALYSIS")
    risk_analysis = simulator.analyze_risk_drivers(result)

    print("\nPrimary Risk Drivers:")
    for driver in risk_analysis['primary_drivers']:
        print(f"  • {driver}")

    return result, simulator


def save_reports(project: Project, calculator: ProjectCalculator, simulation_result=None, simulator=None):
    """Save analysis reports."""
    print_section_header("SAVING REPORTS")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_slug = project.name.lower().replace(" ", "_")[:30]

    csv_filename = f"{project_slug}_analysis_{timestamp}.csv"
    csv_path = os.path.join("output/reports", csv_filename)

    os.makedirs("output/reports", exist_ok=True)

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(["PROJECT ANALYSIS REPORT"])
        writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow([])

        writer.writerow(["PROJECT INFORMATION"])
        writer.writerow(["Name", project.name])
        writer.writerow(["Tasks", project.task_count])
        writer.writerow(["Team Size", project.team_size])
        writer.writerow(["Risk Level", project.risk_level.capitalize()])
        writer.writerow([])

        cost_breakdown = calculator.calculate_cost_breakdown()
        writer.writerow(["COST ANALYSIS"])
        writer.writerow(["Base Cost", f"${cost_breakdown['base_cost']:,.2f}"])
        writer.writerow(["Total Cost", f"${cost_breakdown['total_cost']:,.2f}"])
        writer.writerow([])

        timeline_breakdown = calculator.calculate_timeline_breakdown()
        writer.writerow(["TIMELINE ANALYSIS"])
        writer.writerow(["Sequential", f"{timeline_breakdown['sequential']:.1f} days"])
        writer.writerow(["Realistic", f"{timeline_breakdown['parallel_realistic']:.1f} days"])
        writer.writerow([])

        if simulation_result:
            scenarios = simulation_result.get_scenarios()
            writer.writerow(["SIMULATION RESULTS"])
            writer.writerow(["Best Case", f"${scenarios['best_case']['cost']:,.2f}", f"{scenarios['best_case']['timeline']:.1f} days"])
            writer.writerow(["Expected", f"${scenarios['expected']['cost']:,.2f}", f"{scenarios['expected']['timeline']:.1f} days"])
            writer.writerow(["Worst Case", f"${scenarios['worst_case']['cost']:,.2f}", f"{scenarios['worst_case']['timeline']:.1f} days"])

    print(f"✓ CSV report saved: {csv_path}")

    if simulation_result and simulator:
        txt_filename = f"{project_slug}_simulation_{timestamp}.txt"
        txt_content = simulator.generate_summary_report(simulation_result)
        txt_path = save_text_report(txt_content, txt_filename)
        print(f"✓ Text report saved: {txt_path}")

    return csv_path


def main():
    """Main application flow - ALWAYS runs all features."""
    try:
        # Get project info
        project = get_user_input()

        # Create calculator
        calculator = ProjectCalculator(project)

        # Display basic analysis
        display_basic_analysis(project, calculator)

        # AUTOMATICALLY run simulation (no prompt)
        print("\n")
        input("Press Enter to run Monte Carlo simulation...")
        simulation_result, simulator = run_monte_carlo_simulation(project)

        # AUTOMATICALLY generate charts (no prompt)
        print("\n")
        input("Press Enter to generate visualization charts...")
        visualizer = ProjectVisualizer(project)
        charts = visualizer.generate_all_charts(simulation_result)

        # AUTOMATICALLY save reports (no prompt)
        print("\n")
        input("Press Enter to save analysis reports...")
        save_reports(project, calculator, simulation_result, simulator)

        # Final message
        print_section_header("ANALYSIS COMPLETE")
        print("\nThank you for using the Project Cost & Risk Analyzer!")
        print("All outputs are saved in the 'output/reports' directory.\n")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()