/**
 * API Client for interacting with the FastAPI backend.
 */
const API = {
  baseUrl: window.location.origin,

  async getRoles() {
    try {
      const res = await fetch(`${this.baseUrl}/api/roles`);
      if (!res.ok) throw new Error('Failed to fetch roles');
      const data = await res.json();
      return data.roles || [];
    } catch (err) {
      console.warn('Backend roles unavailable, using fallback:', err);
      return [];
    }
  },

  async getSamples() {
    try {
      const res = await fetch(`${this.baseUrl}/api/samples`);
      if (!res.ok) throw new Error('Failed to fetch samples');
      const data = await res.json();
      return data.samples || {};
    } catch (err) {
      console.warn('Backend samples unavailable, using fallback:', err);
      return window.FALLBACK_SAMPLES || {};
    }
  },

  async analyzeResume({ file, rawText, roleId, customJd }) {
    const formData = new FormData();
    if (file) {
      formData.append('file', file);
    } else if (rawText) {
      formData.append('raw_text', rawText);
    } else {
      throw new Error('No resume provided');
    }

    formData.append('role_id', roleId || 'fullstack_dev');
    if (customJd) {
      formData.append('custom_jd', customJd);
    }

    const res = await fetch(`${this.baseUrl}/api/analyze`, {
      method: 'POST',
      body: formData
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || `Server returned error status ${res.status}`);
    }

    return await res.json();
  },

  async tailorResume({ parsedResume, targetRoleId, customJd, apiKey, llmProvider }) {
    const payload = {
      parsed_resume: parsedResume,
      target_role_id: targetRoleId,
      custom_jd: customJd || '',
      api_key: apiKey || null,
      llm_provider: llmProvider || 'local'
    };

    const res = await fetch(`${this.baseUrl}/api/tailor`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      throw new Error(errData.detail || 'Tailoring failed');
    }

    return await res.json();
  },

  async exportPdf(tailoredData) {
    const res = await fetch(`${this.baseUrl}/api/export/pdf`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tailored_data: tailoredData, format: 'pdf' })
    });

    if (!res.ok) throw new Error('PDF export failed');
    const blob = await res.blob();
    this.downloadBlob(blob, 'ATS_Optimized_Resume.pdf');
  },

  async exportDocx(tailoredData) {
    const res = await fetch(`${this.baseUrl}/api/export/docx`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ tailored_data: tailoredData, format: 'docx' })
    });

    if (!res.ok) throw new Error('Word DOCX export failed');
    const blob = await res.blob();
    this.downloadBlob(blob, 'ATS_Optimized_Resume.docx');
  },

  downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  }
};
