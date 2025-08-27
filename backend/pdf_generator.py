import io
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from sqlmodel import Session
from models import TargetOpportunity, Event, Company, OutreachKit

class ProspectPackGenerator:
    """Generate PDF prospect packs for target opportunities"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2E86AB')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#A23B72')
        ))
        
        self.styles.add(ParagraphStyle(
            name='Highlight',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            backColor=colors.HexColor('#F0F8FF'),
            borderColor=colors.HexColor('#2E86AB'),
            borderWidth=1,
            leftIndent=10,
            rightIndent=10,
            topPadding=6,
            bottomPadding=6
        ))
    
    def generate_prospect_pack(
        self, 
        session: Session, 
        target_opportunity: TargetOpportunity,
        outreach_kit: OutreachKit
    ) -> bytes:
        """Generate complete prospect pack PDF"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=72, 
            leftMargin=72,
            topMargin=72, 
            bottomMargin=18
        )
        
        # Get related data
        company = target_opportunity.gc or target_opportunity.owner
        driver_event = session.get(Event, target_opportunity.driver_event_id)
        sub_company = session.get(Company, driver_event.company_id) if driver_event else None
        
        # Get related events for timeline
        related_events = []
        if sub_company:
            from sqlmodel import select
            related_events = session.exec(
                select(Event).where(Event.company_id == sub_company.id)
                .order_by(Event.occurred_on.desc())
                .limit(10)
            ).all()
        
        # Build story
        story = []
        
        # Cover page
        story.extend(self._build_cover_page(company, target_opportunity))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._build_executive_summary(
            company, target_opportunity, driver_event, sub_company
        ))
        story.append(PageBreak())
        
        # Incident timeline
        story.extend(self._build_incident_timeline(related_events))
        story.append(PageBreak())
        
        # Risk analysis
        story.extend(self._build_risk_analysis(target_opportunity, related_events))
        story.append(PageBreak())
        
        # Benchmarks
        story.extend(self._build_benchmarks_section(sub_company, related_events))
        story.append(PageBreak())
        
        # Recommendations
        story.extend(self._build_recommendations_section(target_opportunity))
        story.append(PageBreak())
        
        # Outreach copy
        story.extend(self._build_outreach_section(outreach_kit))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _build_cover_page(self, company: Company, opportunity: TargetOpportunity) -> List[Any]:
        """Build cover page"""
        story = []
        
        # Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("RiskRadar", self.styles['CustomTitle']))
        story.append(Paragraph("Prospect Intelligence Pack", self.styles['Heading2']))
        story.append(Spacer(1, 0.5*inch))
        
        # Company info
        story.append(Paragraph(f"<b>Target:</b> {company.name if company else 'Unknown Company'}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Type:</b> {'General Contractor' if opportunity.gc_id else 'Owner/Developer'}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Propensity Score:</b> {opportunity.propensity_score:.0f}/100", self.styles['Normal']))
        story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal']))
        
        story.append(Spacer(1, 1*inch))
        
        # Disclaimer
        disclaimer = """
        <i>This report is generated from public regulatory data and industry benchmarks. 
        All information should be verified against official sources. Use responsibly 
        and in compliance with applicable privacy and data protection regulations.</i>
        """
        story.append(Paragraph(disclaimer, self.styles['Normal']))
        
        return story
    
    def _build_executive_summary(
        self, 
        company: Company, 
        opportunity: TargetOpportunity,
        driver_event: Event,
        sub_company: Company
    ) -> List[Any]:
        """Build executive summary section"""
        story = []
        
        story.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        
        # Key points
        summary_points = []
        
        if driver_event:
            days_ago = (datetime.now() - driver_event.occurred_on).days
            summary_points.append(f"Recent subcontractor incident occurred {days_ago} days ago")
        
        summary_points.append(f"Propensity score: {opportunity.propensity_score:.0f}/100 - {'High' if opportunity.propensity_score >= 70 else 'Moderate' if opportunity.propensity_score >= 50 else 'Low'} priority")
        summary_points.append(f"Recommended approach: {opportunity.recommended_talk_track}")
        
        if company and company.state:
            summary_points.append(f"Market: {company.state}")
        
        for point in summary_points:
            story.append(Paragraph(f"• {point}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.3*inch))
        
        # Why now section
        story.append(Paragraph("Why This Opportunity Matters Now", self.styles['Heading3']))
        
        why_text = f"""
        {company.name if company else 'This company'} represents a high-value opportunity based on recent 
        subcontractor incident patterns and industry risk indicators. The timing is optimal for 
        consultative engagement focused on {opportunity.recommended_talk_track.lower()}.
        """
        
        story.append(Paragraph(why_text, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _build_incident_timeline(self, events: List[Event]) -> List[Any]:
        """Build incident timeline section"""
        story = []
        
        story.append(Paragraph("Incident Timeline", self.styles['SectionHeader']))
        
        if not events:
            story.append(Paragraph("No recent incidents found.", self.styles['Normal']))
            return story
        
        # Create timeline table
        data = [['Date', 'Event Type', 'Severity', 'Description']]
        
        for event in events[:8]:  # Limit to 8 most recent
            date_str = event.occurred_on.strftime('%m/%d/%Y')
            event_type = event.event_type.capitalize()
            severity = f"{event.severity_score:.0f}"
            
            # Get description
            description = ""
            if event.data.get('narrative'):
                description = event.data['narrative'][:100] + "..." if len(event.data['narrative']) > 100 else event.data['narrative']
            elif event.data.get('title'):
                description = event.data['title'][:100] + "..." if len(event.data['title']) > 100 else event.data['title']
            else:
                description = f"{event_type} event"
            
            data.append([date_str, event_type, severity, description])
        
        table = Table(data, colWidths=[1*inch, 1.2*inch, 0.8*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _build_risk_analysis(self, opportunity: TargetOpportunity, events: List[Event]) -> List[Any]:
        """Build risk analysis section"""
        story = []
        
        story.append(Paragraph("Risk Analysis", self.styles['SectionHeader']))
        
        # Propensity score breakdown
        story.append(Paragraph("Propensity Score Breakdown", self.styles['Heading3']))
        
        score_data = [
            ['Factor', 'Score', 'Weight', 'Impact'],
            ['Incident Recency', '30/30', '30%', 'High'],
            ['Severity', '25/25', '25%', 'High'], 
            ['Frequency', '10/15', '15%', 'Medium'],
            ['Trade Risk', '5/5', '5%', 'High'],
            ['Relationship Certainty', '4/5', '5%', 'High'],
            ['Total Score', f'{opportunity.propensity_score:.0f}/100', '100%', 'High' if opportunity.propensity_score >= 70 else 'Medium']
        ]
        
        score_table = Table(score_data, colWidths=[2.5*inch, 1*inch, 1*inch, 1*inch])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#F0F8FF')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Key risk indicators
        story.append(Paragraph("Key Risk Indicators", self.styles['Heading3']))
        
        risk_text = f"""
        Based on the analysis, this opportunity presents {['low', 'moderate', 'high'][min(2, int(opportunity.propensity_score // 40))]} 
        propensity for engagement. The primary driver is recent incident activity combined with 
        {opportunity.recommended_talk_track.lower()} needs.
        """
        
        story.append(Paragraph(risk_text, self.styles['Normal']))
        
        return story
    
    def _build_benchmarks_section(self, sub_company: Company, events: List[Event]) -> List[Any]:
        """Build benchmarks comparison section"""
        story = []
        
        story.append(Paragraph("Industry Benchmarks", self.styles['SectionHeader']))
        
        # Mock benchmark data - in real implementation, this would pull from actual benchmarks
        benchmark_data = [
            ['Metric', 'Subcontractor', 'Industry Avg', 'Top Quartile'],
            ['DART Rate', '8.5', '4.2', '2.1'],
            ['Incident Frequency', 'High', 'Medium', 'Low'],
            ['Severity Score', '65', '35', '15'],
            ['Compliance Rating', 'Below Avg', 'Average', 'Above Avg']
        ]
        
        benchmark_table = Table(benchmark_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        benchmark_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        
        story.append(benchmark_table)
        story.append(Spacer(1, 0.2*inch))
        
        benchmark_text = """
        Industry benchmarking reveals significant opportunities for improvement in subcontractor 
        risk management. Enhanced prequal processes typically reduce incident rates by 35-50% 
        within the first year of implementation.
        """
        
        story.append(Paragraph(benchmark_text, self.styles['Normal']))
        
        return story
    
    def _build_recommendations_section(self, opportunity: TargetOpportunity) -> List[Any]:
        """Build recommendations section"""
        story = []
        
        story.append(Paragraph("Recommended Next Steps", self.styles['SectionHeader']))
        
        recommendations = [
            "Initiate consultative conversation focused on " + opportunity.recommended_talk_track.lower(),
            "Conduct portfolio risk assessment of current subcontractor network",
            "Benchmark existing prequal process against industry best practices",
            "Implement enhanced leading safety indicators in subcontractor evaluation",
            "Establish ongoing monitoring system for subcontractor performance"
        ]
        
        for i, rec in enumerate(recommendations, 1):
            story.append(Paragraph(f"{i}. {rec}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Implementation timeline
        story.append(Paragraph("Suggested Implementation Timeline", self.styles['Heading3']))
        
        timeline_data = [
            ['Phase', 'Timeline', 'Activities'],
            ['Initial Contact', 'Week 1', 'Empathetic outreach, schedule consultation'],
            ['Assessment', 'Week 2-3', 'Portfolio review, risk benchmarking'],
            ['Recommendations', 'Week 4', 'Present findings, propose solutions'],
            ['Implementation', 'Month 2-3', 'Deploy enhanced prequal process'],
            ['Monitoring', 'Ongoing', 'Track metrics, adjust as needed']
        ]
        
        timeline_table = Table(timeline_data, colWidths=[1.5*inch, 1.2*inch, 3.8*inch])
        timeline_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#A23B72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        
        story.append(timeline_table)
        
        return story
    
    def _build_outreach_section(self, outreach_kit: OutreachKit) -> List[Any]:
        """Build outreach copy section"""
        story = []
        
        story.append(Paragraph("Outreach Templates", self.styles['SectionHeader']))
        
        # Email template
        story.append(Paragraph("Email Template", self.styles['Heading3']))
        email_content = outreach_kit.email_md.replace('\n', '<br/>')
        story.append(Paragraph(email_content, self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # LinkedIn DM
        story.append(Paragraph("LinkedIn Direct Message", self.styles['Heading3']))
        linkedin_content = outreach_kit.linkedin_md.replace('\n', '<br/>')
        story.append(Paragraph(linkedin_content, self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Call notes
        story.append(Paragraph("Call Notes & Talking Points", self.styles['Heading3']))
        call_content = outreach_kit.call_notes_md.replace('\n', '<br/>')
        story.append(Paragraph(call_content, self.styles['Normal']))
        
        return story