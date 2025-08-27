export interface Company {
  id: number;
  name: string;
  type: 'GC' | 'Owner' | 'Sub' | 'Unknown';
  naics?: string;
  state?: string;
  website?: string;
  normalized_name: string;
  created_at: string;
}

export interface Event {
  id: number;
  source: string;
  event_type: 'inspection' | 'citation' | 'accident' | 'news' | 'ita';
  company_id: number;
  project_id?: number;
  occurred_on: string;
  severity_score: number;
  data: Record<string, any>;
  link?: string;
  created_at: string;
  company?: Company;
}

export interface TargetOpportunity {
  id: number;
  gc_id?: number;
  owner_id?: number;
  driver_event_id: number;
  propensity_score: number;
  confidence: number;
  recommended_talk_track: string;
  created_at: string;
  gc?: Company;
  owner?: Company;
  driver_event?: Event;
}

export interface OutreachKit {
  id: number;
  target_id: number;
  email_md: string;
  linkedin_md: string;
  call_notes_md: string;
  attachments: Record<string, any>;
  created_at: string;
}

export interface DashboardStats {
  new_incidents_30_days: number;
  top_opportunities_count: number;
  high_risk_subs_count: number;
  total_companies: number;
}

export interface MetricsITA {
  id: number;
  sub_id: number;
  year: number;
  recordables?: number;
  darts?: number;
  hours_worked?: number;
  dart_rate?: number;
  source_link?: string;
}