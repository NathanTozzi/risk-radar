# RiskRadar Propensity Scoring Rubric

## Overview

The RiskRadar propensity scoring system calculates opportunity scores (0-100) to prioritize business development efforts. The system uses a weighted multi-factor approach that considers incident characteristics, timing, relationships, and industry context.

## Scoring Methodology

### Total Score Calculation
```
Total Score = Σ(Factor Score × Weight)
Maximum Score = 100
```

### Scoring Factors

#### 1. Incident Recency (Weight: 30%)
**Purpose**: Recent incidents create immediate opportunities for risk management discussions.

| Days Since Incident | Score | Reasoning |
|-------------------|-------|-----------|
| 0-30 days | 30.0 | Immediate opportunity window |
| 31-60 days | 25.0 | Still highly relevant |
| 61-90 days | 20.0 | Moderately relevant |
| 91-180 days | 5-15.0 | Declining relevance (exponential decay) |
| >180 days | 0.0 | Too distant for direct connection |

**Formula**: Exponential decay with 90-day half-life
```python
score = 30.0 * exp(-days_ago / 90) if days_ago <= 180 else 0.0
```

#### 2. Incident Severity (Weight: 25%)
**Purpose**: Higher severity incidents indicate greater need for risk management intervention.

| Severity Level | Score | Trigger Conditions |
|---------------|-------|-------------------|
| Critical | 25.0 | Fatality incidents |
| High | 20.0 | Catastrophic incidents, willful violations |
| Significant | 15.0 | Serious violations, penalties >$50k |
| Moderate | 10.0 | Multiple violations (≥5) |
| Low | 5.0 | Other-than-serious violations |

**Assessment Criteria**:
- **Fatality**: Any incident resulting in worker death
- **Catastrophe**: Multiple serious injuries, major structural failures
- **Willful**: OSHA determination of intentional safety violations
- **Serious**: Violations with substantial probability of harm
- **High Penalty**: Financial penalties indicating severity

#### 3. Incident Frequency (Weight: 15%)
**Purpose**: Pattern recognition for subcontractors with recurring issues.

| Incident Count (24 months) | Score | Risk Implication |
|---------------------------|-------|------------------|
| 5+ incidents | 15.0 | Chronic safety issues |
| 3-4 incidents | 10.0 | Concerning pattern |
| 2 incidents | 5.0 | Beginning pattern |
| 1 incident | 0.0 | Isolated incident |

**Counted Event Types**:
- OSHA inspections with violations
- OSHA citations
- Workplace accidents
- Media-reported safety incidents

#### 4. ITA Metrics vs. Benchmarks (Weight: 15%)
**Purpose**: Quantitative safety performance assessment using industry benchmarks.

| DART Rate Ratio | Score | Performance Level |
|----------------|-------|------------------|
| ≥2.0× benchmark | 15.0 | Well above benchmark |
| 1.5-2.0× benchmark | 10.0 | Significantly above |
| 1.2-1.5× benchmark | 5.0 | Moderately above |
| <1.2× benchmark | 0.0 | At or below benchmark |

**Industry DART Benchmarks** (per 200,000 hours):
- Commercial Building Construction (NAICS 236220): 3.5
- Industrial Building Construction (NAICS 236210): 4.8
- Roofing Contractors (NAICS 238160): 5.0
- Structural Steel Contractors (NAICS 238120): 4.2
- Site Preparation (NAICS 238910): 7.2

#### 5. High-Risk Trade Involvement (Weight: 5%)
**Purpose**: Identify opportunities in trades with elevated safety risks.

| Trade Category | Score | Risk Factors |
|---------------|-------|--------------|
| Critical Risk Trades | 5.0 | Steel erection, roofing, excavation, demolition |
| High Risk Trades | 3.0 | Crane operation, scaffolding, electrical high-voltage |
| Standard Trades | 0.0 | General construction, finishing work |

**High-Risk Trade List**:
- Steel erection
- Roofing
- Excavation
- Demolition
- Crane operation
- Scaffolding
- Electrical high voltage
- Confined space work
- Fall protection activities

#### 6. Relationship Certainty (Weight: 5%)
**Purpose**: Higher confidence relationships warrant increased investment.

| Relationship Evidence | Score | Confidence Level |
|----------------------|-------|------------------|
| Multiple confirmed projects | 5.0 | Very high confidence |
| Single detailed relationship | 4.0 | High confidence |
| Basic relationship data | 2.0 | Moderate confidence |
| Inferred/uncertain | 0.0 | Low confidence |

**Evidence Quality Factors**:
- Project documentation with dates and values
- Multiple project relationships
- Trade-specific contract details
- Geographic and timing alignment

#### 7. News Coverage Impact (Weight: 5%)
**Purpose**: Public incidents may increase urgency for reputation management.

| Media Coverage Type | Score | Impact Level |
|--------------------|-------|--------------|
| Negative headlines | 5.0 | High public visibility |
| Industry coverage | 3.0 | Sector-specific attention |
| Minimal coverage | 1.0 | Limited visibility |
| No coverage | 0.0 | Private incident |

**Negative Keywords**: lawsuit, violation, death, fatality, accident, injury, default, delay, penalty

## Talk Track Determination

Based on scoring component analysis, the system recommends engagement approaches:

### Post-Incident Stabilization
**Trigger**: Severity score >20 or recency score >25
**Message**: "Post-incident path to stronger prequal"
**Approach**: Empathetic support focused on immediate prevention measures

### Trend Analysis & Prevention
**Trigger**: Frequency score >10
**Message**: "Trend analysis & prevention strategies"  
**Approach**: Pattern-based discussion on systematic improvements

### Portfolio Risk Benchmarking
**Trigger**: ITA score >10 or overall score >60
**Message**: "Portfolio risk benchmarking"
**Approach**: Comparative analysis against industry standards

### Compliance Gap Assessment
**Trigger**: Default for other scenarios
**Message**: "Compliance gap assessment"
**Approach**: General risk management evaluation

## Scoring Examples

### Example 1: Recent High-Severity Incident
```
Company: MegaBuild Construction Corp
Subcontractor: ABC Construction LLC (recent OSHA fatality)
Incident: 15 days ago, fatality, willful violation, $100k penalty

Scoring Breakdown:
- Recency (15 days): 30.0 × 0.30 = 9.0
- Severity (fatality): 25.0 × 0.25 = 6.25
- Frequency (3 incidents/24mo): 10.0 × 0.15 = 1.5
- ITA (DART 8.5 vs 3.5): 15.0 × 0.15 = 2.25
- Trade Risk (roofing): 5.0 × 0.05 = 0.25
- Relationship (confirmed): 4.0 × 0.05 = 0.2
- News (headline coverage): 5.0 × 0.05 = 0.25

Total Score: 89.7/100
Talk Track: "Post-incident stabilization & future prequal"
Priority: Critical (>80)
```

### Example 2: Pattern-Based Moderate Risk
```
Company: Skyline Construction Group  
Subcontractor: QuickBuild Contractors (repeat violations)
Incident: 45 days ago, serious violation, $15k penalty

Scoring Breakdown:
- Recency (45 days): 22.0 × 0.30 = 6.6
- Severity (serious): 15.0 × 0.25 = 3.75
- Frequency (4 incidents/24mo): 10.0 × 0.15 = 1.5
- ITA (DART 6.8 vs 4.2): 10.0 × 0.15 = 1.5
- Trade Risk (steel): 5.0 × 0.05 = 0.25
- Relationship (multiple projects): 5.0 × 0.05 = 0.25
- News (no coverage): 0.0 × 0.05 = 0.0

Total Score: 63.9/100
Talk Track: "Trend analysis & prevention strategies"
Priority: High (60-80)
```

## Threshold Guidelines

### Priority Classifications
- **Critical (80-100)**: Immediate outreach within 48 hours
- **High (60-79)**: Outreach within 1 week  
- **Moderate (40-59)**: Outreach within 2-4 weeks
- **Low (20-39)**: Monitor for additional incidents
- **Minimal (<20)**: Database tracking only

### Quality Controls

#### Score Validation
- Maximum possible score: 100.0
- Minimum practical score: 0.0
- Weighted sum validation: Σ(weights) = 1.0

#### Confidence Thresholds  
- High confidence: Score ≥70 with relationship certainty ≥0.8
- Medium confidence: Score 40-69 with relationship certainty ≥0.6
- Low confidence: Score <40 or relationship certainty <0.6

#### Data Quality Requirements
- Recent incident data (within 2 years for frequency analysis)
- Valid company relationships (GC-sub or Owner-sub)
- Verified incident sources (OSHA, credible news sources)

## Configuration Management

### Benchmark Updates
Benchmarks are stored in `/backend/config/benchmarks.yaml`:
```yaml
dart_benchmarks:
  "236220": 3.5  # Commercial building construction
  "238160": 5.0  # Roofing contractors

scoring_config:
  recency_decay_half_life_days: 90
  max_recency_days: 180
```

### Weight Adjustments
Scoring weights can be modified based on business priorities:
- **Market Focus**: Increase recency weight for rapid response
- **Risk Assessment**: Increase severity weight for safety-first approach  
- **Relationship Building**: Increase relationship certainty weight

### Calibration Process
1. **Historical Analysis**: Review closed opportunities vs. scores
2. **Win Rate Correlation**: Analyze score ranges vs. success rates
3. **False Positive Review**: Identify low-converting high scores
4. **Threshold Optimization**: Adjust priority thresholds based on capacity

## Compliance and Ethics

### Data Usage Guidelines
- Use only public regulatory and news data
- No speculation beyond documented facts
- Respectful interpretation of incident data
- Focus on prevention, not blame

### Scoring Integrity
- Transparent methodology
- Consistent application across all opportunities
- Regular calibration against outcomes
- Documentation of all scoring changes

This scoring rubric provides a systematic, defensible approach to opportunity prioritization while maintaining ethical standards and business effectiveness.