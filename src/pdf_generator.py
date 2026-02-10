"""
PDF report generator for project analysis.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
import os

from src.project import Project
from src.calculator import ProjectCalculator
from src.risk_simulator import SimulationResult, RiskSimulator


class PDFReportGenerator:
    """
    Generates professional PDF reports for project analysis.
    """

    def __init__(self, project: Project, output_dir: str = "output/reports"):
        """
        Initialize PDF generator.

        Args:
            project: The project to generate report for
            output_dir: Directory to save PDF
        """
        self.project = project
        self.output_dir = output_dir
        self.calculator = ProjectCalculator(project)

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))

        # Subsection
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#7F8C8D'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))

    def generate_full_report(
            self,
            simulation_result: SimulationResult = None,
            simulator: RiskSimulator = None,
            chart_paths: dict = None
    ) -> str:
        """
        Generate complete PDF report.

        Args:
            simulation_result: Optional Monte Carlo results
            simulator: Optional simulator instance
            chart_paths: Optional dict of chart file paths

        Returns:
            Path to generated PDF
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_slug = self.project.name.lower().replace(" ", "_")[:30]
        filename = f"{project_slug}_report_{timestamp}.pdf"
        filepath = os.path.join(self.output_dir, filename)

        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Build content
        story = []

        # Title page
        story.extend(self._build_title_page())
        story.append(PageBreak())

        # Executive summary
        story.extend(self._build_executive_summary())
        story.append(Spacer(1, 0.2 * inch))

        # Cost analysis
        story.extend(self._build_cost_section())
        story.append(Spacer(1, 0.2 * inch))

        # Timeline analysis
        story.extend(self._build_timeline_section())
        story.append(Spacer(1, 0.2 * inch))

        # Critical path
        story.extend(self._build_critical_path_section())
        story.append(PageBreak())

        # Task breakdown
        story.extend(self._build_task_breakdown())
        story.append(PageBreak())

        # Monte Carlo results (if available)
        if simulation_result and simulator:
            story.extend(self._build_simulation_section(simulation_result, simulator))
            story.append(PageBreak())

        # Charts (if available)
        if chart_paths:
            story.extend(self._build_charts_section(chart_paths))

        # Build PDF
        doc.build(story)

        return filepath

    def _build_title_page(self):
        """Build title page elements."""
        elements = []

        elements.append(Spacer(1, 2 * inch))

        title = Paragraph(
            f"<b>{self.project.name}</b>",
            self.styles['CustomTitle']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))

        subtitle = Paragraph(
            "Project Cost & Risk Analysis Report",
            self.styles['Heading2']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.5 * inch))

        # Project info table
        info_data = [
            ['Project Name:', self.project.name],
            ['Team Size:', str(self.project.team_size)],
            ['Risk Level:', self.project.risk_level.capitalize()],
            ['Total Tasks:', str(self.project.task_count)],
            ['Report Generated:', datetime.now().strftime("%B %d, %Y at %I:%M %p")]
        ]

        info_table = Table(info_data, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#34495E')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(info_table)

        return elements

    def _build_executive_summary(self):
        """Build executive summary section."""
        elements = []

        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))

        cost_breakdown = self.calculator.calculate_cost_breakdown()
        timeline_breakdown = self.calculator.calculate_timeline_breakdown()

        summary_data = [
            ['Metric', 'Value'],
            ['Base Cost', f"${cost_breakdown['base_cost']:,.2f}"],
            ['Total Estimated Cost', f"${cost_breakdown['total_cost']:,.2f}"],
            ['Cost per Team Member', f"${cost_breakdown['cost_per_resource']:,.2f}"],
            ['Realistic Timeline', f"{timeline_breakdown['parallel_realistic']:.1f} days"],
            ['Sequential Timeline', f"{timeline_breakdown['sequential']:.1f} days"],
        ]

        summary_table = Table(summary_data, colWidths=[3 * inch, 3 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 1), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ECF0F1')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))

        elements.append(summary_table)

        return elements

    def _build_cost_section(self):
        """Build cost analysis section."""
        elements = []

        elements.append(Paragraph("Cost Analysis", self.styles['SectionHeader']))

        cost_breakdown = self.calculator.calculate_cost_breakdown()

        cost_text = f"""
        The project has a base cost of <b>${cost_breakdown['base_cost']:,.2f}</b>. 
        With a {self.project.risk_level} risk level, we apply a risk overhead of 
        <b>${cost_breakdown['risk_overhead']:,.2f}</b>, bringing the total estimated 
        cost to <b>${cost_breakdown['total_cost']:,.2f}</b>. 
        This translates to approximately <b>${cost_breakdown['cost_per_resource']:,.2f}</b> 
        per team member.
        """

        elements.append(Paragraph(cost_text, self.styles['Normal']))

        return elements

    def _build_timeline_section(self):
        """Build timeline analysis section."""
        elements = []

        elements.append(Paragraph("Timeline Analysis", self.styles['SectionHeader']))

        timeline_breakdown = self.calculator.calculate_timeline_breakdown()

        timeline_text = f"""
        <b>Realistic Estimate:</b> {timeline_breakdown['parallel_realistic']:.1f} days<br/>
        This accounts for task dependencies, resource constraints, and risk factors.<br/><br/>
        <b>Optimistic (Critical Path):</b> {timeline_breakdown['parallel_optimistic']:.1f} days<br/>
        Best-case scenario with unlimited resources and no delays.<br/><br/>
        <b>Sequential (Worst Case):</b> {timeline_breakdown['sequential']:.1f} days<br/>
        If all tasks must run one after another.
        """

        elements.append(Paragraph(timeline_text, self.styles['Normal']))

        return elements

    def _build_critical_path_section(self):
        """Build critical path section."""
        elements = []

        elements.append(Paragraph("Critical Path Analysis", self.styles['SectionHeader']))

        critical_path_info = self.calculator.get_critical_path_analysis()

        if critical_path_info['exists']:
            cp_text = f"""
            The critical path contains <b>{critical_path_info['task_count']}</b> tasks 
            with a total duration of <b>{critical_path_info['duration']:.1f} days</b> 
            (adjusted: <b>{critical_path_info['adjusted_duration']:.1f} days</b>).
            These tasks directly impact the project timeline and should be monitored closely.
            """
            elements.append(Paragraph(cp_text, self.styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))

            elements.append(Paragraph("Critical Path Tasks:", self.styles['SubSection']))

            for task_name in critical_path_info['tasks']:
                elements.append(Paragraph(f"• {task_name}", self.styles['Normal']))
        else:
            elements.append(Paragraph("No critical path identified.", self.styles['Normal']))

        return elements

    def _build_task_breakdown(self):
        """Build task breakdown table."""
        elements = []

        elements.append(Paragraph("Task Breakdown", self.styles['SectionHeader']))

        task_costs = self.calculator.calculate_task_costs()

        # Table data
        data = [['Task Name', 'Days', '$/Day', 'Base Cost', 'Adjusted Cost']]

        for tc in task_costs:
            data.append([
                tc['task_name'],
                f"{tc['days']:.1f}",
                f"${tc['cost_per_day']:,.0f}",
                f"${tc['base_cost']:,.2f}",
                f"${tc['adjusted_cost']:,.2f}"
            ])

        # Create table
        task_table = Table(data, colWidths=[2.2 * inch, 0.8 * inch, 0.8 * inch, 1.1 * inch, 1.1 * inch])
        task_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ECC71')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#E8F8F5')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(task_table)

        return elements

    def _build_simulation_section(self, result: SimulationResult, simulator: RiskSimulator):
        """Build Monte Carlo simulation section."""
        elements = []

        elements.append(Paragraph("Monte Carlo Risk Simulation", self.styles['SectionHeader']))

        scenarios = result.get_scenarios()
        risk_analysis = simulator.analyze_risk_drivers(result)

        # Scenarios table
        scenario_data = [
            ['Scenario', 'Cost', 'Timeline', 'Probability'],
            [
                'Best Case (P10)',
                f"${scenarios['best_case']['cost']:,.0f}",
                f"{scenarios['best_case']['timeline']:.1f} days",
                '10% or better'
            ],
            [
                'Expected (Mean)',
                f"${scenarios['expected']['cost']:,.0f}",
                f"{scenarios['expected']['timeline']:.1f} days",
                'Most likely'
            ],
            [
                'P75',
                f"${scenarios['p75']['cost']:,.0f}",
                f"{scenarios['p75']['timeline']:.1f} days",
                '25% worse'
            ],
            [
                'Worst Case (P90)',
                f"${scenarios['worst_case']['cost']:,.0f}",
                f"{scenarios['worst_case']['timeline']:.1f} days",
                '10% or worse'
            ]
        ]

        scenario_table = Table(scenario_data, colWidths=[1.5 * inch, 1.5 * inch, 1.5 * inch, 1.5 * inch])
        scenario_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E74C3C')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FADBD8')]),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))

        elements.append(scenario_table)
        elements.append(Spacer(1, 0.2 * inch))

        # Risk drivers
        elements.append(Paragraph("Primary Risk Drivers:", self.styles['SubSection']))
        for driver in risk_analysis['primary_drivers']:
            elements.append(Paragraph(f"• {driver}", self.styles['Normal']))

        return elements

    def _build_charts_section(self, chart_paths: dict):
        """Add charts to PDF."""
        elements = []

        elements.append(Paragraph("Visualizations", self.styles['SectionHeader']))

        # Add each chart if it exists
        for chart_name, chart_path in chart_paths.items():
            if chart_path and os.path.exists(chart_path):
                try:
                    img = Image(chart_path, width=6 * inch, height=4 * inch)
                    elements.append(img)
                    elements.append(Spacer(1, 0.3 * inch))
                except Exception as e:
                    print(f"Could not add chart {chart_name}: {e}")

        return elements