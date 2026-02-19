"""
Streamlit web interface for Project Cost & Risk Analyzer.
"""

import streamlit as st
import pandas as pd
from src.project import Project, Task
from src.calculator import ProjectCalculator
from src.risk_simulator import RiskSimulator
from src.visualizer import ProjectVisualizer
from src.pdf_generator import PDFReportGenerator
from src.gantt_chart import GanttChartGenerator
import os


def main():
    st.set_page_config(page_title="Project Cost & Risk Analyzer", page_icon="📊", layout="wide")

    st.title("📊 Engineering Project Cost & Risk Analyzer")
    st.markdown("### Estimate costs, timelines, and risks using Monte Carlo simulation")

    # Sidebar for project inputs
    st.sidebar.header("Project Configuration")

    project_name = st.sidebar.text_input("Project Name", value="My Project")
    team_size = st.sidebar.number_input("Team Size", min_value=1, max_value=50, value=3)
    risk_level = st.sidebar.selectbox("Risk Level", ["low", "medium", "high"], index=1)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Add Tasks")

    # Initialize session state for tasks
    if 'tasks' not in st.session_state:
        st.session_state.tasks = []

    # Task input form
    with st.sidebar.form("task_form", clear_on_submit=True):
        task_name = st.text_input("Task Name")
        col1, col2 = st.columns(2)
        with col1:
            estimated_days = st.number_input("Days", min_value=0.1, value=5.0, step=0.5)
        with col2:
            cost_per_day = st.number_input("$/Day", min_value=1, value=1000, step=100)

        dependencies = st.multiselect(
            "Dependencies",
            options=[t['name'] for t in st.session_state.tasks],
            help="Select tasks that must be completed before this one"
        )

        submitted = st.form_submit_button("➕ Add Task")

        if submitted and task_name:
            # Convert dependency names to IDs
            dep_ids = []
            for dep_name in dependencies:
                for t in st.session_state.tasks:
                    if t['name'] == dep_name:
                        dep_ids.append(t['id'])
                        break

            task_id = task_name.lower().replace(" ", "_")[:20]
            st.session_state.tasks.append({
                'name': task_name,
                'id': task_id,
                'days': estimated_days,
                'cost_per_day': cost_per_day,
                'dependencies': dep_ids
            })
            st.rerun()

    # Display current tasks
    if st.session_state.tasks:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Current Tasks")
        for idx, task in enumerate(st.session_state.tasks):
            col1, col2 = st.sidebar.columns([4, 1])
            with col1:
                st.text(f"{task['name']} ({task['days']}d @ ${task['cost_per_day']}/d)")
            with col2:
                if st.button("🗑️", key=f"del_{idx}"):
                    st.session_state.tasks.pop(idx)
                    st.rerun()

    # Main content area
    if not st.session_state.tasks:
        st.info("👈 Add tasks in the sidebar to begin analysis")
        return

    # Create Project object
    try:
        task_objects = [
            Task(
                name=t['name'],
                estimated_days=t['days'],
                cost_per_day=t['cost_per_day'],
                task_id=t['id'],
                dependencies=t['dependencies']
            )
            for t in st.session_state.tasks
        ]

        project = Project(
            name=project_name,
            tasks=task_objects,
            team_size=team_size,
            risk_level=risk_level
        )

        # Validate dependencies
        errors = project.validate_dependencies()
        if errors:
            st.warning("⚠️ Dependency Issues:\n" + "\n".join(f"- {e}" for e in errors))

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📋 Overview", "📈 Analysis", "🎲 Monte Carlo", "📊 Charts"])

        # TAB 1: Overview
        with tab1:
            col1, col2, col3 = st.columns(3)

            calculator = ProjectCalculator(project)
            cost_breakdown = calculator.calculate_cost_breakdown()
            timeline_breakdown = calculator.calculate_timeline_breakdown()

            with col1:
                st.metric("Total Tasks", project.task_count)
                st.metric("Team Size", project.team_size)
                st.metric("Risk Level", risk_level.capitalize())

            with col2:
                st.metric("Base Cost", f"${cost_breakdown['base_cost']:,.0f}")
                st.metric("Total Cost", f"${cost_breakdown['total_cost']:,.0f}")
                st.metric("Cost/Member", f"${cost_breakdown['cost_per_resource']:,.0f}")

            with col3:
                st.metric("Sequential Timeline", f"{timeline_breakdown['sequential']:.1f} days")
                st.metric("Realistic Timeline", f"{timeline_breakdown['parallel_realistic']:.1f} days")
                st.metric("Critical Path", f"{timeline_breakdown['parallel_optimistic']:.1f} days")

            # Task table
            st.subheader("Task Breakdown")
            task_costs = calculator.calculate_task_costs()
            df = pd.DataFrame(task_costs)
            df = df[['task_name', 'days', 'cost_per_day', 'base_cost', 'adjusted_cost']]
            df.columns = ['Task', 'Days', '$/Day', 'Base Cost', 'Adjusted Cost']
            df['Base Cost'] = df['Base Cost'].apply(lambda x: f"${x:,.0f}")
            df['Adjusted Cost'] = df['Adjusted Cost'].apply(lambda x: f"${x:,.0f}")
            df['$/Day'] = df['$/Day'].apply(lambda x: f"${x:,.0f}")
            st.dataframe(df, use_container_width=True, hide_index=True)

        # TAB 2: Detailed Analysis
        with tab2:
            st.subheader("Cost Analysis")
            col1, col2 = st.columns(2)

            with col1:
                st.write("**Cost Breakdown**")
                st.write(f"- Base Cost: ${cost_breakdown['base_cost']:,.2f}")
                st.write(f"- Risk Overhead: ${cost_breakdown['risk_overhead']:,.2f}")
                st.write(f"- **Total Cost: ${cost_breakdown['total_cost']:,.2f}**")

            with col2:
                st.write("**Timeline Breakdown**")
                st.write(f"- Sequential: {timeline_breakdown['sequential']:.1f} days")
                st.write(f"- Optimistic: {timeline_breakdown['parallel_optimistic']:.1f} days")
                st.write(f"- **Realistic: {timeline_breakdown['parallel_realistic']:.1f} days**")

            # Critical Path
            critical_path_info = calculator.get_critical_path_analysis()
            if critical_path_info['exists']:
                st.subheader("Critical Path Analysis")
                st.write(f"**Tasks in Critical Path:** {critical_path_info['task_count']}")
                st.write(f"**Duration:** {critical_path_info['adjusted_duration']:.1f} days")
                st.write("**Critical Path Tasks:**")
                for task_name in critical_path_info['tasks']:
                    st.write(f"→ {task_name}")

        # TAB 3: Monte Carlo Simulation
        with tab3:
            st.subheader("Monte Carlo Risk Simulation")

            iterations = st.slider("Number of Simulations", 100, 5000, 1000, 100)

            if st.button("🎲 Run Simulation", type="primary"):
                with st.spinner(f"Running {iterations:,} simulations..."):
                    simulator = RiskSimulator(project, iterations=iterations)
                    result = simulator.run_simulation()

                    # Store in session state
                    st.session_state.simulation_result = result
                    st.session_state.simulator = simulator

                st.success("✅ Simulation complete!")

            if 'simulation_result' in st.session_state:
                result = st.session_state.simulation_result
                simulator = st.session_state.simulator
                scenarios = result.get_scenarios()

                # Display scenarios
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Best Case (P10)",
                              f"${scenarios['best_case']['cost']:,.0f}",
                              f"{scenarios['best_case']['timeline']:.1f} days")

                with col2:
                    st.metric("Expected (Mean)",
                              f"${scenarios['expected']['cost']:,.0f}",
                              f"{scenarios['expected']['timeline']:.1f} days")

                with col3:
                    st.metric("P75",
                              f"${scenarios['p75']['cost']:,.0f}",
                              f"{scenarios['p75']['timeline']:.1f} days")

                with col4:
                    st.metric("Worst Case (P90)",
                              f"${scenarios['worst_case']['cost']:,.0f}",
                              f"{scenarios['worst_case']['timeline']:.1f} days")

                # Risk Analysis
                st.subheader("Risk Analysis")
                risk_analysis = simulator.analyze_risk_drivers(result)

                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Cost Variability:** {risk_analysis['cost_variability']:.1%}")
                    st.write(f"**Timeline Variability:** {risk_analysis['timeline_variability']:.1%}")

                with col2:
                    st.write("**Primary Risk Drivers:**")
                    for driver in risk_analysis['primary_drivers']:
                        st.write(f"• {driver}")

                # Distribution histograms
                st.subheader("Distribution Analysis")
                col1, col2 = st.columns(2)

                with col1:
                    import plotly.graph_objects as go
                    fig = go.Figure(data=[go.Histogram(x=result.costs, nbinsx=50)])
                    fig.update_layout(
                        title="Cost Distribution",
                        xaxis_title="Cost ($)",
                        yaxis_title="Frequency",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    fig = go.Figure(data=[go.Histogram(x=result.timelines, nbinsx=50)])
                    fig.update_layout(
                        title="Timeline Distribution",
                        xaxis_title="Days",
                        yaxis_title="Frequency",
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # TAB 4: Charts & Reports
                with tab4:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("📊 Visualization Charts")

                        if st.button("Generate All Charts", type="primary", key="gen_charts"):
                            with st.spinner("Generating charts..."):
                                visualizer = ProjectVisualizer(project)

                                simulation_result = st.session_state.get('simulation_result', None)
                                charts = visualizer.generate_all_charts(simulation_result)

                                st.session_state.charts = charts

                            st.success("✅ Charts generated!")

                        if 'charts' in st.session_state:
                            charts = st.session_state.charts

                            # Display charts
                            if 'cost_breakdown' in charts and os.path.exists(charts['cost_breakdown']):
                                st.image(charts['cost_breakdown'], caption="Cost Breakdown by Task")

                            if 'timeline_comparison' in charts and os.path.exists(charts['timeline_comparison']):
                                st.image(charts['timeline_comparison'], caption="Timeline Comparison")

                            if 'critical_path' in charts and charts['critical_path'] and os.path.exists(
                                    charts['critical_path']):
                                st.image(charts['critical_path'], caption="Critical Path")

                            if 'risk_distribution' in charts and os.path.exists(charts['risk_distribution']):
                                st.image(charts['risk_distribution'], caption="Risk Distribution")

                            if 'scenario_comparison' in charts and os.path.exists(charts['scenario_comparison']):
                                st.image(charts['scenario_comparison'], caption="Scenario Comparison")

                    with col2:
                        st.subheader("📅 Gantt Chart")

                        if st.button("Generate Gantt Chart", type="primary", key="gen_gantt"):
                            with st.spinner("Creating Gantt chart..."):
                                gantt_gen = GanttChartGenerator(project)
                                gantt_fig = gantt_gen.generate_gantt_chart()

                                st.session_state.gantt_fig = gantt_fig

                            st.success("✅ Gantt chart created!")

                        if 'gantt_fig' in st.session_state:
                            st.plotly_chart(st.session_state.gantt_fig, use_container_width=True)

                    # PDF Report section
                    st.markdown("---")
                    st.subheader("📄 PDF Report")

                    if st.button("📥 Generate PDF Report", type="primary", key="gen_pdf"):
                        with st.spinner("Generating PDF report..."):
                            pdf_gen = PDFReportGenerator(project)

                            simulation_result = st.session_state.get('simulation_result', None)
                            simulator = st.session_state.get('simulator', None)
                            charts = st.session_state.get('charts', None)

                            pdf_path = pdf_gen.generate_full_report(
                                simulation_result=simulation_result,
                                simulator=simulator,
                                chart_paths=charts
                            )

                            st.session_state.pdf_path = pdf_path

                        st.success(f"✅ PDF report generated!")

                    if 'pdf_path' in st.session_state:
                        with open(st.session_state.pdf_path, 'rb') as pdf_file:
                            st.download_button(
                                label="📥 Download PDF Report",
                                data=pdf_file,
                                file_name=os.path.basename(st.session_state.pdf_path),
                                mime='application/pdf',
                                type="primary"
                            )

    except Exception as e:
        st.error(f"Error: {e}")
        import traceback
        st.code(traceback.format_exc())


if __name__ == "__main__":
    main()