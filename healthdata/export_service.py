# healthdata/export_service.py
"""
PDF Export Service for Health Reports.
Generates downloadable health summaries for doctor visits.
"""

from datetime import datetime, timedelta
from io import BytesIO

from django.utils import timezone
from django.db.models import Avg, Sum, Count

# PDF generation (install: pip install reportlab)
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT


class HealthReportGenerator:
    """
    Generates PDF health reports for users.
    """

    def __init__(self, user, days=30):
        self.user = user
        self.days = days
        self.start_date = timezone.localdate() - timedelta(days=days)
        self.end_date = timezone.localdate()

    def generate_pdf(self):
        """
        Generate complete PDF report.

        Returns:
            BytesIO: PDF file buffer
        """
        buffer = BytesIO()

        # Create PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Build content
        story = []
        styles = getSampleStyleSheet()

        # Add custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#007AFF'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1C1C1E'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Title
        story.append(Paragraph(
            "CareU Health Report",
            styles['CustomTitle']
        ))

        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles['Normal']
        ))

        story.append(Paragraph(
            f"Report Period: {self.start_date.strftime('%B %d, %Y')} - {self.end_date.strftime('%B %d, %Y')}",
            styles['Normal']
        ))

        story.append(Spacer(1, 0.5 * inch))

        # Patient Info
        story.extend(self._add_patient_info(styles))
        story.append(Spacer(1, 0.3 * inch))

        # Nutrition Summary
        story.extend(self._add_nutrition_summary(styles))
        story.append(Spacer(1, 0.3 * inch))

        # Health Metrics
        story.extend(self._add_health_metrics(styles))
        story.append(Spacer(1, 0.3 * inch))

        # AI-Flagged Concerns
        story.extend(self._add_ai_concerns(styles))
        story.append(Spacer(1, 0.3 * inch))

        # Active Goals
        story.extend(self._add_goals(styles))

        # Footer
        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph(
            "⚠️ This report is for informational purposes only and should be discussed with your healthcare provider.",
            styles['Normal']
        ))

        # Build PDF
        doc.build(story)
        buffer.seek(0)

        return buffer

    def _add_patient_info(self, styles):
        """Add patient information section."""
        content = []

        content.append(Paragraph("Patient Information", styles['SectionHeader']))

        # Handle missing profile gracefully
        profile = getattr(self.user, "profile", None)

        name = self.user.get_full_name() or self.user.username
        if profile:
            age = f"{profile.age} years" if getattr(profile, "age", None) else "Not provided"
            height = f"{profile.height_cm} cm" if getattr(profile, "height_cm", None) else "Not provided"
            weight = f"{profile.weight_kg} kg" if getattr(profile, "weight_kg", None) else "Not provided"
        else:
            age = "Not provided"
            height = "Not provided"
            weight = "Not provided"

        data = [
            ['Name:', name],
            ['Age:', age],
            ['Height:', height],
            ['Weight:', weight],
        ]

        bmi = getattr(profile, "bmi", None) if profile else None
        if bmi is not None:
            data.append(['BMI:', f"{bmi}"])

        table = Table(data, colWidths=[2 * inch, 4 * inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        content.append(table)

        return content

    def _add_nutrition_summary(self, styles):
        """Add nutrition data summary."""
        from healthdata.models import NutritionEntry

        content = []
        content.append(Paragraph("Nutrition Summary", styles['SectionHeader']))

        entries = NutritionEntry.objects.filter(
            user=self.user,
            logged_at__gte=self.start_date,
            logged_at__lte=self.end_date
        )

        if not entries.exists():
            content.append(Paragraph("No nutrition data available for this period.", styles['Normal']))
            return content

        # Calculate averages
        agg = entries.aggregate(
            avg_calories=Avg('calories'),
            avg_protein=Avg('protein_g'),
            avg_carbs=Avg('carbs_g'),
            avg_fat=Avg('fat_g'),
            total_entries=Count('id')
        )

        days_logged = entries.values('logged_at').distinct().count()

        data = [
            ['Metric', 'Average', 'Details'],
            ['Calories', f"{agg['avg_calories']:.0f} kcal/day", f"{agg['total_entries']} meals logged"],
            ['Protein', f"{float(agg['avg_protein'] or 0):.1f} g/day", ''],
            ['Carbohydrates', f"{float(agg['avg_carbs'] or 0):.1f} g/day", ''],
            ['Fat', f"{float(agg['avg_fat'] or 0):.1f} g/day", ''],
            ['Logging Consistency', f"{(days_logged / self.days) * 100:.1f}%", f"{days_logged} of {self.days} days"],
        ]

        table = Table(data, colWidths=[2 * inch, 1.5 * inch, 2.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#007AFF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        content.append(table)

        return content

    def _add_health_metrics(self, styles):
        """Add health metrics (glucose, activity, sleep)."""
        from healthdata.models import GlucoseEntry, ActivityData
        # SleepData may or may not exist in the project – make it optional
        try:
            from healthdata.models import SleepData
        except ImportError:
            SleepData = None

        content = []
        content.append(Paragraph("Health Metrics", styles['SectionHeader']))

        data = [['Metric', 'Average/Total', 'Observations']]

        # Glucose
        glucose_entries = GlucoseEntry.objects.filter(
            user=self.user,
            created_at__gte=self.start_date
        )

        if glucose_entries.exists():
            avg_glucose = glucose_entries.aggregate(avg=Avg('glucose_mg_dl'))['avg']
            if avg_glucose is not None:
                data.append([
                    'Blood Glucose',
                    f"{avg_glucose:.1f} mg/dL",
                    f"{glucose_entries.count()} readings"
                ])

        # Activity
        activity = ActivityData.objects.filter(
            user=self.user,
            date__gte=self.start_date
        )

        if activity.exists():
            avg_steps = activity.aggregate(avg=Avg('steps'))['avg']
            if avg_steps is not None:
                data.append([
                    'Daily Steps',
                    f"{avg_steps:.0f} steps/day",
                    f"{activity.count()} days tracked"
                ])

        # Sleep (only if model exists)
        if SleepData is not None:
            sleep = SleepData.objects.filter(
                user=self.user,
                date__gte=self.start_date
            )

            if sleep.exists():
                avg_sleep = sleep.aggregate(avg=Avg('total_sleep_minutes'))['avg']
                if avg_sleep is not None:
                    hours = avg_sleep / 60
                    data.append([
                        'Sleep Duration',
                        f"{hours:.1f} hours/night",
                        f"{sleep.count()} nights tracked"
                    ])

        if len(data) > 1:
            table = Table(data, colWidths=[2 * inch, 1.5 * inch, 2.5 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34C759')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            content.append(table)
        else:
            content.append(Paragraph("No health metrics data available.", styles['Normal']))

        return content

    def _add_ai_concerns(self, styles):
        """Add AI-flagged health concerns."""
        from healthdata.models import HealthReminder

        content = []
        content.append(Paragraph("AI-Flagged Concerns", styles['SectionHeader']))

        # Get active high-priority reminders
        concerns = HealthReminder.objects.filter(
            user=self.user,
            priority='high',
            dismissed_at__isnull=True
        ).order_by('-created_at')[:5]

        if not concerns.exists():
            content.append(Paragraph(
                "✅ No significant concerns detected. Keep up the good work!",
                styles['Normal']
            ))
            return content

        for concern in concerns:
            bullet_text = f"• <b>{concern.title}:</b> {concern.message}"
            content.append(Paragraph(bullet_text, styles['Normal']))
            content.append(Spacer(1, 0.1 * inch))

        return content

    def _add_goals(self, styles):
        """Add active health goals."""
        from healthdata.models import Goal

        content = []
        content.append(Paragraph("Active Health Goals", styles['SectionHeader']))

        goals = Goal.objects.filter(
            user=self.user,
            status='active'
        ).order_by('-created_at')[:5]

        if not goals.exists():
            content.append(Paragraph("No active goals set.", styles['Normal']))
            return content

        data = [['Goal', 'Progress', 'Target']]

        for goal in goals:
            data.append([
                goal.title,
                f"{goal.progress:.0f}%",
                f"{goal.target_value} {goal.get_goal_type_display()}"
            ])

        table = Table(data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF9500')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        content.append(table)

        return content
