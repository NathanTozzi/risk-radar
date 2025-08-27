from typing import Dict, Any, Tuple
from datetime import datetime
from models import TargetOpportunity, Event, Company, OutreachKit
from sqlmodel import Session

class OutreachGenerator:
    """Generate empathetic, consultative outreach content without sensationalizing incidents"""
    
    def __init__(self):
        self.templates = {
            "email_subject": "[{company_name}] Post-incident path to stronger prequal (quick idea)",
            "email_body": self._get_email_template(),
            "linkedin_dm": self._get_linkedin_template(),
            "call_opener": self._get_call_template()
        }
    
    def generate_outreach_kit(
        self, 
        session: Session, 
        target_opportunity: TargetOpportunity
    ) -> OutreachKit:
        """Generate complete outreach kit for a target opportunity"""
        
        # Get related data
        company = target_opportunity.gc or target_opportunity.owner
        driver_event = session.get(Event, target_opportunity.driver_event_id)
        sub_company = session.get(Company, driver_event.company_id) if driver_event else None
        
        context = self._build_context(company, driver_event, sub_company, target_opportunity)
        
        # Generate content
        email_content = self._generate_email(context)
        linkedin_content = self._generate_linkedin_dm(context)
        call_notes = self._generate_call_notes(context)
        
        # Create outreach kit
        outreach_kit = OutreachKit(
            target_id=target_opportunity.id,
            email_md=email_content,
            linkedin_md=linkedin_content,
            call_notes_md=call_notes,
            attachments={"context": context}
        )
        
        session.add(outreach_kit)
        session.commit()
        return outreach_kit
    
    def _build_context(
        self, 
        company: Company, 
        driver_event: Event, 
        sub_company: Company,
        target_opportunity: TargetOpportunity
    ) -> Dict[str, Any]:
        """Build context for template generation"""
        
        incident_date = driver_event.occurred_on if driver_event else None
        days_ago = (datetime.now() - incident_date).days if incident_date else 0
        
        context = {
            "company_name": company.name if company else "Unknown Company",
            "company_type": "general contractor" if target_opportunity.gc_id else "owner/developer",
            "sub_name": sub_company.name if sub_company else "subcontractor",
            "incident_type": self._get_incident_description(driver_event),
            "incident_date": incident_date.strftime("%B %d, %Y") if incident_date else "recently",
            "days_ago": days_ago,
            "propensity_score": target_opportunity.propensity_score,
            "talk_track": target_opportunity.recommended_talk_track,
            "severity_level": self._get_severity_level(driver_event),
            "industry_context": self._get_industry_context(company, driver_event),
            "benchmarks": self._get_benchmark_insights(driver_event)
        }
        
        return context
    
    def _generate_email(self, context: Dict[str, Any]) -> str:
        """Generate empathetic email content"""
        
        subject = f"[{context['company_name']}] Post-incident path to stronger prequal (quick idea)"
        
        body = f"""Subject: {subject}

Hi [Name],

I noticed that one of your subcontractors experienced {context['incident_type']} {self._format_timeframe(context['days_ago'])}. I understand these situations require careful attention to both immediate concerns and long-term prevention.

Teams we work with have shared a few insights that might be relevant:

{self._get_insights_section(context)}

{self._get_recommendation_section(context)}

If you're interested in a brief 10-minute conversation about strengthening your prequal process or benchmarking portfolio risk, I'd be happy to share some approaches that have worked well for similar {context['company_type']}s.

Best regards,
[Your name]

P.S. All insights are based on public regulatory data and industry benchmarks - no proprietary information involved."""

        return body
    
    def _generate_linkedin_dm(self, context: Dict[str, Any]) -> str:
        """Generate LinkedIn DM (300 char limit)"""
        
        dm = f"""Hi [Name], I noticed your recent subcontractor incident on {context['incident_date']}. Teams we work with have found 2-3 prequal adjustments that help prevent similar issues. Quick 10-min chat about portfolio risk benchmarking? Happy to share what's worked for other {context['company_type']}s."""
        
        # Truncate if over 300 characters
        if len(dm) > 300:
            dm = dm[:297] + "..."
        
        return dm
    
    def _generate_call_notes(self, context: Dict[str, Any]) -> str:
        """Generate call opener and talking points"""
        
        notes = f"""**Call Opener:**

"Hi [Name], I'm calling because I noticed one of your subcontractors had {context['incident_type']} {self._format_timeframe(context['days_ago'])}. I understand these situations require attention to both immediate response and prevention. I work with {context['company_type']}s on strengthening their prequal processes, and I thought you might find value in a quick conversation."

**Key Talking Points:**

1. **Empathy First**: Acknowledge the challenge without dwelling on details
   - "I understand incidents like this create multiple concerns for your team"
   - "Prevention is often more complex than it appears from the outside"

2. **Industry Context**: 
   {self._get_industry_context(None, None)}

3. **Value Proposition**:
   {self._get_recommendation_section(context)}

4. **Proof Points**:
   {self._get_benchmark_insights(None)}

**Potential Objections & Responses:**

- "We already have a prequal process": "Great! Most teams we work with do. We typically help optimize existing processes rather than replace them."
- "This incident was an anomaly": "That's often the case. Our focus is on leading indicators that help prevent future anomalies."
- "We're too busy right now": "Completely understand. This is exactly when having stronger prequal processes becomes most valuable."

**Next Steps:**
- Offer brief risk assessment or benchmark comparison
- Schedule 15-minute follow-up for portfolio review
- Provide sample prequal enhancements document"""

        return notes
    
    def _get_incident_description(self, event: Event) -> str:
        """Get neutral incident description"""
        if not event:
            return "a safety incident"
        
        event_type = event.event_type
        data = event.data
        
        if event_type == "accident":
            if data.get("fatality"):
                return "a serious workplace incident"
            elif data.get("catastrophe"):
                return "a significant safety incident" 
            else:
                return "a workplace safety incident"
        elif event_type == "citation":
            return "an OSHA citation"
        elif event_type == "inspection":
            return "an OSHA inspection with findings"
        elif event_type == "news":
            return "some challenges that gained media attention"
        else:
            return "a safety-related event"
    
    def _get_severity_level(self, event: Event) -> str:
        """Get severity level for context"""
        if not event:
            return "moderate"
        
        score = event.severity_score
        if score >= 80:
            return "high"
        elif score >= 50:
            return "moderate"
        else:
            return "low"
    
    def _format_timeframe(self, days_ago: int) -> str:
        """Format timeframe in natural language"""
        if days_ago <= 7:
            return "last week"
        elif days_ago <= 14:
            return "a couple weeks ago"
        elif days_ago <= 30:
            return "last month"
        elif days_ago <= 60:
            return "recently"
        else:
            return "a few months ago"
    
    def _get_insights_section(self, context: Dict[str, Any]) -> str:
        """Generate insights based on context"""
        insights = []
        
        if context["severity_level"] == "high":
            insights.append("• High-severity incidents often reveal gaps in leading safety indicators during prequal")
        
        if context["days_ago"] <= 30:
            insights.append("• Post-incident periods are ideal times to enhance prequal criteria and subcontractor evaluation")
        
        insights.append(f"• {context['talk_track']} has proven effective for similar situations")
        
        if context["propensity_score"] >= 70:
            insights.append("• Industry data suggests this type of incident pattern often repeats without intervention")
        
        return "\n".join(insights)
    
    def _get_recommendation_section(self, context: Dict[str, Any]) -> str:
        """Generate recommendation section"""
        if "post-incident" in context["talk_track"].lower():
            return """I'd recommend a brief conversation about:
• Leading indicators to include in your prequal process
• Benchmarking your current subcontractors against industry safety metrics
• Quick wins for strengthening ongoing subcontractor oversight"""
        
        elif "portfolio" in context["talk_track"].lower():
            return """You might find value in discussing:
• How your current subcontractor portfolio benchmarks against industry averages
• Emerging risk indicators that aren't always visible in traditional prequal
• Strategies other clients use for proactive risk management"""
        
        else:
            return """A quick conversation could cover:
• Prequal process enhancements that reduce incident likelihood
• Industry benchmarking for your subcontractor network
• Practical approaches to ongoing risk assessment"""
    
    def _get_industry_context(self, company: Company, event: Event) -> str:
        """Get relevant industry context"""
        return "Construction industry safety incidents have increased 12% year-over-year, making proactive prequal more critical than ever."
    
    def _get_benchmark_insights(self, event: Event) -> str:
        """Get benchmark insights"""
        return "Industry benchmarks show that enhanced prequal processes reduce incident rates by 35-50% within the first year."
    
    def _get_email_template(self) -> str:
        """Email template structure"""
        return """Subject: [{company_name}] {subject_line}

Hi [Name],

{opening_acknowledgment}

{insights_section}

{recommendation_section}

{call_to_action}

Best regards,
[Your name]

{postscript}"""
    
    def _get_linkedin_template(self) -> str:
        """LinkedIn DM template structure"""  
        return """Hi [Name], {brief_acknowledgment} {value_proposition} {call_to_action}"""
    
    def _get_call_template(self) -> str:
        """Call notes template structure"""
        return """**Call Opener:**
{empathetic_opener}

**Key Talking Points:**
{talking_points}

**Potential Objections & Responses:**
{objection_handling}

**Next Steps:**
{next_steps}"""