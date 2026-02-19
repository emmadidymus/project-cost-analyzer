"""
Gantt chart generator for project timeline visualization.
"""

import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict
import os

from src.project import Project
from src.calculator import ProjectCalculator


class GanttChartGenerator:
    """Generates interactive Gantt charts for project timelines."""

    def __init__(self, project: Project):
        """Initialize Gantt chart generator."""
        self.project = project
        self.calculator = ProjectCalculator(project)

    def generate_gantt_chart(self, start_date: datetime = None, save_path: str = None) -> go.Figure:
        """Generate an interactive Gantt chart."""
        if start_date is None:
            start_date = datetime.now()

        schedule = self._calculate_schedule(start_date)
        critical_path = self.project.get_critical_path()
        critical_task_ids = [t.task_id for t in critical_path]

        fig = go.Figure()

        # Add bars for each task
        for task in self.project.tasks:
            task_info = schedule[task.task_id]
            is_critical = task.task_id in critical_task_ids
            color = '#E74C3C' if is_critical else '#3498DB'

            fig.add_trace(go.Bar(
                name=task.name,
                x=[task_info['end_date']],
                y=[task.name],
                base=task_info['start_date'],
                orientation='h',
                marker=dict(color=color, line=dict(color='rgba(0,0,0,0.5)', width=2)),
                hovertemplate=(
                    f'<b>{task.name}</b><br>' +
                    f'Start: {task_info["start_date"].strftime("%b %d, %Y")}<br>' +
                    f'End: {task_info["end_date"].strftime("%b %d, %Y")}<br>' +
                    f'Duration: {task.estimated_days:.1f} days<br>' +
                    f'Cost: ${task.base_cost:,.2f}<br>' +
                    ('<b>⚠ CRITICAL PATH</b><br>' if is_critical else '') +
                    '<extra></extra>'
                ),
                showlegend=False,
                width=0.7
            ))

        # Update layout with better visibility
        fig.update_layout(
            title=dict(
                text=f'<b>Project Timeline: {self.project.name}</b>',
                x=0.5,
                xanchor='center',
                font=dict(size=24, color='#000000', family='Arial Black')
            ),
            xaxis=dict(
                title=dict(text='<b>Date</b>', font=dict(size=16, color='#000000')),
                gridcolor='#D0D0D0',
                showgrid=True,
                linecolor='#000000',
                linewidth=2,
                tickfont=dict(size=12, color='#000000')
            ),
            yaxis=dict(
                title=dict(text='<b>Tasks</b>', font=dict(size=16, color='#000000')),
                gridcolor='#D0D0D0',
                showgrid=True,
                linecolor='#000000',
                linewidth=2,
                tickfont=dict(size=14, color='#000000', family='Arial')
            ),
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#F5F5F5',
            height=max(500, len(self.project.tasks) * 80),
            hovermode='closest',
            margin=dict(l=250, r=120, t=120, b=100),
            bargap=0.2
        )

        # Add legend with better styling
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(size=18, color='#E74C3C', symbol='square', line=dict(color='#000', width=2)),
            showlegend=True, name='Critical Path Tasks'
        ))

        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode='markers',
            marker=dict(size=18, color='#3498DB', symbol='square', line=dict(color='#000', width=2)),
            showlegend=True, name='Regular Tasks'
        ))

        fig.update_layout(
            legend=dict(
                x=1.02, y=1, xanchor='left', yanchor='top',
                bgcolor='white',
                bordercolor='#000000', borderwidth=2,
                font=dict(size=13, color='#000000')
            )
        )

        # Add today marker
        today = datetime.now()
        if schedule:
            all_starts = [info['start_date'] for info in schedule.values()]
            all_ends = [info['end_date'] for info in schedule.values()]

            if min(all_starts) <= today <= max(all_ends):
                fig.add_shape(
                    type="line", x0=today, x1=today, y0=0, y1=1, yref="paper",
                    line=dict(color="#27AE60", width=3, dash="dash")
                )
                fig.add_annotation(
                    x=today, y=1.06, yref="paper", text="<b>Today</b>", showarrow=False,
                    font=dict(color="#27AE60", size=14, family='Arial Black'),
                    bgcolor='white', bordercolor='#27AE60', borderwidth=2, borderpad=6
                )

        if save_path:
            os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else '.', exist_ok=True)
            fig.write_html(save_path)

        return fig

    def _calculate_schedule(self, start_date: datetime) -> Dict:
        """Calculate start and end dates for all tasks."""
        schedule = {}
        earliest_start_days = {}

        for task in self.project.tasks:
            earliest_start = 0.0

            for dep_id in task.dependencies:
                if dep_id in earliest_start_days:
                    dep_task = self.project.get_task_by_id(dep_id)
                    dep_end = earliest_start_days[dep_id] + dep_task.estimated_days
                    earliest_start = max(earliest_start, dep_end)

            earliest_start_days[task.task_id] = earliest_start
            task_start_date = start_date + timedelta(days=earliest_start)
            task_end_date = task_start_date + timedelta(days=task.estimated_days)

            schedule[task.task_id] = {
                'start_date': task_start_date,
                'end_date': task_end_date,
                'start_day': earliest_start,
                'duration': task.estimated_days
            }

        return schedule

    def save_as_image(self, fig: go.Figure, filepath: str):
        """Save Gantt chart as static image."""
        try:
            fig.write_image(filepath, width=1400, height=max(600, len(self.project.tasks) * 60))
            print(f"Gantt chart saved to {filepath}")
        except Exception as e:
            print(f"Could not save image: {e}")
            html_path = filepath.replace('.png', '.html')
            fig.write_html(html_path)
            print(f"HTML chart saved to {html_path}")