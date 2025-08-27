const API_BASE = '/api';

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE}${endpoint}`;
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Companies
  async getCompanies(params?: { type?: string; q?: string }) {
    const searchParams = new URLSearchParams();
    if (params?.type) searchParams.set('type', params.type);
    if (params?.q) searchParams.set('q', params.q);
    
    const query = searchParams.toString();
    return this.request(`/companies${query ? `?${query}` : ''}`);
  }

  async getCompany(id: number) {
    return this.request(`/companies/${id}`);
  }

  // Events
  async getEvents(params?: { company_id?: number; event_type?: string; since?: string; until?: string }) {
    const searchParams = new URLSearchParams();
    if (params?.company_id) searchParams.set('company_id', params.company_id.toString());
    if (params?.event_type) searchParams.set('event_type', params.event_type);
    if (params?.since) searchParams.set('since', params.since);
    if (params?.until) searchParams.set('until', params.until);
    
    const query = searchParams.toString();
    return this.request(`/events${query ? `?${query}` : ''}`);
  }

  // Opportunities
  async getOpportunities(params?: { min_score?: number; limit?: number }) {
    const searchParams = new URLSearchParams();
    if (params?.min_score) searchParams.set('min_score', params.min_score.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    
    const query = searchParams.toString();
    return this.request(`/opportunities${query ? `?${query}` : ''}`);
  }

  async getOpportunity(id: number) {
    return this.request(`/opportunities/${id}`);
  }

  async rebuildOpportunities(params?: { since?: string; until?: string }) {
    return this.request('/opportunities/rebuild', {
      method: 'POST',
      body: JSON.stringify(params || {}),
    });
  }

  // Outreach
  async generateOutreachKit(target_id: number) {
    return this.request('/outreach/generate', {
      method: 'POST',
      body: JSON.stringify({ target_id }),
    });
  }

  async getOutreachKit(id: number) {
    return this.request(`/outreach/${id}`);
  }

  async exportProspectPack(id: number): Promise<Blob> {
    const url = `${API_BASE}/outreach/${id}/export/pdf`;
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Export failed: ${response.status} ${response.statusText}`);
    }

    return response.blob();
  }

  // Ingestion
  async runIngestion(data: { sources: string[]; since?: string; until?: string; companies?: string[] }) {
    return this.request('/ingest/run', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getIngestionStatus() {
    return this.request('/ingest/status');
  }

  // File uploads
  async uploadCSV(file: File, mapping_type: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('mapping_type', mapping_type);

    const response = await fetch(`${API_BASE}/uploads/${mapping_type}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }
}

export const api = new ApiClient();