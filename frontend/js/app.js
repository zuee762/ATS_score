/**
 * Main Application Controller for ATS Resume Analyzer.
 */
const App = {
  state: {
    roles: [],
    samples: {},
    selectedRoleId: 'fullstack_dev',
    customJd: '',
    selectedFile: null,
    resumeRawText: '',
    parsedResume: null,
    analysisResult: null,
    tailoredResult: null,
    settings: {
      provider: 'local',
      apiKey: ''
    }
  },

  async init() {
    this.loadSettings();
    this.bindEvents();
    await this.loadRoles();
    await this.loadSamples();
    lucide.createIcons();
  },

  loadSettings() {
    const saved = localStorage.getItem('ats_settings');
    if (saved) {
      try {
        this.state.settings = JSON.parse(saved);
        document.getElementById('selectLlmProvider').value = this.state.settings.provider || 'local';
        document.getElementById('inputApiKey').value = this.state.settings.apiKey || '';
        this.toggleApiKeyVisibility();
      } catch (e) {
        console.error('Failed to load settings:', e);
      }
    }
  },

  saveSettings() {
    const provider = document.getElementById('selectLlmProvider').value;
    const apiKey = document.getElementById('inputApiKey').value.trim();
    this.state.settings = { provider, apiKey };
    localStorage.setItem('ats_settings', JSON.stringify(this.state.settings));
    document.getElementById('settingsModal').style.display = 'none';
    UI.showToast('Settings saved successfully!', 'success');
  },

  toggleApiKeyVisibility() {
    const provider = document.getElementById('selectLlmProvider').value;
    const group = document.getElementById('apiKeyGroup');
    group.style.display = provider === 'local' ? 'none' : 'block';
  },

  async loadRoles() {
    const select = document.getElementById('selectJobRole');
    try {
      const roles = await API.getRoles();
      this.state.roles = roles;

      if (roles.length > 0) {
        select.innerHTML = roles.map(r => `
          <option value="${r.id}" ${r.id === 'fullstack_dev' ? 'selected' : ''}>
            ${r.title} (${r.category})
          </option>
        `).join('');

        this.onRoleSelected(roles[0].id);
      }
    } catch (e) {
      console.error('Error loading roles:', e);
    }
  },

  async loadSamples() {
    try {
      const samples = await API.getSamples();
      this.state.samples = samples;
    } catch (e) {
      console.error('Error loading samples:', e);
    }
  },

  bindEvents() {
    // Role selection change
    const selectRole = document.getElementById('selectJobRole');
    selectRole.addEventListener('change', (e) => {
      this.onRoleSelected(e.target.value);
    });

    // Role Tabs (Curated vs Custom JD)
    document.getElementById('tabCuratedRoles').addEventListener('click', () => {
      document.getElementById('tabCuratedRoles').classList.add('active');
      document.getElementById('tabCustomJd').classList.remove('active');
      document.getElementById('viewCuratedRoles').classList.add('active');
      document.getElementById('viewCustomJd').classList.remove('active');
    });

    document.getElementById('tabCustomJd').addEventListener('click', () => {
      document.getElementById('tabCustomJd').classList.add('active');
      document.getElementById('tabCuratedRoles').classList.remove('active');
      document.getElementById('viewCustomJd').classList.add('active');
      document.getElementById('viewCuratedRoles').classList.remove('active');
    });

    // File Drag & Drop
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('resumeFileInput');

    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('drag-over');
      if (e.dataTransfer.files.length > 0) {
        this.handleFileSelected(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        this.handleFileSelected(e.target.files[0]);
      }
    });

    // Remove File button
    document.getElementById('btnRemoveFile').addEventListener('click', () => {
      this.clearSelectedFile();
    });

    // Sample pills
    document.querySelectorAll('.sample-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        const sampleKey = btn.getAttribute('data-sample');
        this.loadSampleResume(sampleKey);
      });
    });

    // Scan & Analyze Button
    document.getElementById('btnAnalyze').addEventListener('click', () => {
      this.runAnalysis();
    });

    // Proceed to Tailor button (from Step 2 to Step 3)
    document.getElementById('btnProceedToTailor').addEventListener('click', () => {
      this.proceedToTailor();
    });

    // Editor Tab switching
    document.querySelectorAll('.editor-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const target = tab.getAttribute('data-tab');
        document.querySelectorAll('.editor-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.editor-tab-content').forEach(c => c.classList.remove('active'));
        
        tab.classList.add('active');
        const capTarget = target.charAt(0).toUpperCase() + target.slice(1);
        const contentEl = document.getElementById(`tabContent${capTarget}`);
        if (contentEl) contentEl.classList.add('active');

        // Sync changes with paper preview if full view is opened
        if (target === 'fullview') {
          UI.renderPaperPreview(this.state.tailoredResult.tailored_data);
        }
      });
    });

    // Live Edit Summary
    const editSummary = document.getElementById('editTailoredSummary');
    editSummary.addEventListener('input', (e) => {
      if (this.state.tailoredResult?.tailored_data) {
        this.state.tailoredResult.tailored_data.summary = e.target.value;
      }
    });

    // Add Skill Input
    document.getElementById('btnAddSkill').addEventListener('click', () => this.addSkillFromInput());
    document.getElementById('inputAddSkill').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.addSkillFromInput();
      }
    });

    // Export Buttons
    document.getElementById('btnExportPdf').addEventListener('click', () => this.exportPdf());
    document.getElementById('btnExportDocx').addEventListener('click', () => this.exportDocx());
    document.getElementById('btnCopyText').addEventListener('click', () => this.copyText());

    // Navigation Buttons
    document.getElementById('btnBackToAudit').addEventListener('click', () => {
      document.getElementById('stepTailor').style.display = 'none';
      document.getElementById('stepResults').style.display = 'block';
      document.getElementById('stepResults').scrollIntoView({ behavior: 'smooth' });
    });

    document.getElementById('btnStartNew').addEventListener('click', () => {
      document.getElementById('stepTailor').style.display = 'none';
      document.getElementById('stepResults').style.display = 'none';
      document.getElementById('stepInput').style.display = 'block';
      document.getElementById('stepInput').scrollIntoView({ behavior: 'smooth' });
    });

    // Settings Modal
    document.getElementById('btnOpenSettings').addEventListener('click', () => {
      document.getElementById('settingsModal').style.display = 'flex';
    });
    document.getElementById('btnCloseSettings').addEventListener('click', () => {
      document.getElementById('settingsModal').style.display = 'none';
    });
    document.getElementById('selectLlmProvider').addEventListener('change', () => {
      this.toggleApiKeyVisibility();
    });
    document.getElementById('btnSaveSettings').addEventListener('click', () => {
      this.saveSettings();
    });
  },

  onRoleSelected(roleId) {
    this.state.selectedRoleId = roleId;
    const role = this.state.roles.find(r => r.id === roleId);
    if (!role) return;

    document.getElementById('previewRoleCategory').innerText = role.category || 'General';
    document.getElementById('previewRoleSkillsCount').innerText = `${role.mandatory_skills.length} Core Skills`;
    document.getElementById('previewRoleDesc').innerText = role.description;
    
    const chipsContainer = document.getElementById('previewRoleSkills');
    chipsContainer.innerHTML = role.mandatory_skills.slice(0, 6).map(s => 
      `<span class="chip-mini">${s}</span>`
    ).join('');
  },

  handleFileSelected(file) {
    this.state.selectedFile = file;
    this.state.resumeRawText = '';

    document.getElementById('dropZone').style.display = 'none';
    const preview = document.getElementById('filePreviewCard');
    preview.style.display = 'flex';
    document.getElementById('fileName').innerText = file.name;
    document.getElementById('fileSize').innerText = `${Math.round(file.size / 1024)} KB`;

    document.getElementById('btnAnalyze').disabled = false;
    UI.showToast(`Loaded ${file.name}`, 'info');
  },

  clearSelectedFile() {
    this.state.selectedFile = null;
    this.state.resumeRawText = '';
    document.getElementById('resumeFileInput').value = '';
    document.getElementById('filePreviewCard').style.display = 'none';
    document.getElementById('dropZone').style.display = 'block';
    document.getElementById('btnAnalyze').disabled = true;
  },

  loadSampleResume(sampleKey) {
    const sample = this.state.samples[sampleKey] || (window.FALLBACK_SAMPLES && window.FALLBACK_SAMPLES[sampleKey]);
    if (!sample) return;

    this.state.selectedFile = null;
    this.state.resumeRawText = sample.content || sample.text;

    // Switch role selector
    const targetRole = sample.target_role || sample.role_id;
    if (targetRole) {
      document.getElementById('selectJobRole').value = targetRole;
      this.onRoleSelected(targetRole);
    }

    document.getElementById('dropZone').style.display = 'none';
    const preview = document.getElementById('filePreviewCard');
    preview.style.display = 'flex';
    document.getElementById('fileName').innerText = sample.filename || 'Sample_Resume.txt';
    document.getElementById('fileSize').innerText = 'Sample Resume (Ready)';

    document.getElementById('btnAnalyze').disabled = false;
    UI.showToast(`Loaded sample: ${sample.title || sampleKey}`, 'success');
  },

  async runAnalysis() {
    const isCustom = document.getElementById('tabCustomJd').classList.contains('active');
    const roleId = isCustom ? document.getElementById('customJobTitle').value.trim() : this.state.selectedRoleId;
    const customJd = isCustom ? document.getElementById('customJdText').value.trim() : '';

    if (isCustom && (!roleId || !customJd)) {
      UI.showToast('Please provide both target job title and job description.', 'error');
      return;
    }

    const stopScanner = UI.showScanner(
      'Analyzing ATS Compatibility',
      `Evaluating resume against ${roleId || 'target profile'}...`
    );

    try {
      const resp = await API.analyzeResume({
        file: this.state.selectedFile,
        rawText: this.state.resumeRawText,
        roleId: roleId || 'fullstack_dev',
        customJd: customJd
      });

      stopScanner();
      UI.hideScanner();

      this.state.parsedResume = resp.parsed;
      this.state.analysisResult = resp.analysis;
      this.state.tailoredResult = resp.tailored;

      UI.renderScorecard(resp.analysis, resp.parsed);
      UI.showToast('Analysis complete! Check your ATS Scorecard below.', 'success');

    } catch (err) {
      stopScanner();
      UI.hideScanner();
      document.getElementById('stepInput').style.display = 'block';
      UI.showToast(err.message || 'Analysis failed. Please check your resume file.', 'error');
    }
  },

  proceedToTailor() {
    if (!this.state.tailoredResult) {
      UI.showToast('Tailored version not generated yet.', 'error');
      return;
    }
    UI.renderTailorView(this.state.tailoredResult, this.state.parsedResume);
  },

  onBulletChange(textareaEl) {
    const roleIdx = parseInt(textareaEl.getAttribute('data-role-idx'), 10);
    const bulletIdx = parseInt(textareaEl.getAttribute('data-bullet-idx'), 10);
    const newVal = textareaEl.value;

    if (this.state.tailoredResult?.tailored_data?.experience) {
      const exp = this.state.tailoredResult.tailored_data.experience[roleIdx];
      if (exp && exp.bullets) {
        exp.bullets[bulletIdx] = newVal;
      }
    }
  },

  addSkillFromInput() {
    const input = document.getElementById('inputAddSkill');
    const val = input.value.trim();
    if (!val) return;

    if (!this.state.tailoredResult?.tailored_data?.skills) {
      this.state.tailoredResult.tailored_data.skills = [];
    }

    const skills = this.state.tailoredResult.tailored_data.skills;
    if (!skills.some(s => s.toLowerCase() === val.toLowerCase())) {
      skills.push(val);
      input.value = '';
      UI.renderTailoredSkillsChips(skills, [val]);
      UI.showToast(`Added skill: ${val}`, 'info');
    }
  },

  removeSkill(skillName) {
    if (!this.state.tailoredResult?.tailored_data?.skills) return;
    const skills = this.state.tailoredResult.tailored_data.skills;
    this.state.tailoredResult.tailored_data.skills = skills.filter(
      s => s.toLowerCase() !== skillName.toLowerCase()
    );
    UI.renderTailoredSkillsChips(this.state.tailoredResult.tailored_data.skills, []);
  },

  async exportPdf() {
    try {
      UI.showToast('Generating ATS-compliant PDF...', 'info');
      await API.exportPdf(this.state.tailoredResult.tailored_data);
      UI.showToast('PDF downloaded successfully!', 'success');
    } catch (err) {
      UI.showToast(err.message || 'Failed to download PDF', 'error');
    }
  },

  async exportDocx() {
    try {
      UI.showToast('Generating Word DOCX...', 'info');
      await API.exportDocx(this.state.tailoredResult.tailored_data);
      UI.showToast('Word (.docx) downloaded successfully!', 'success');
    } catch (err) {
      UI.showToast(err.message || 'Failed to download DOCX', 'error');
    }
  },

  copyText() {
    const data = this.state.tailoredResult?.tailored_data;
    if (!data) return;

    let text = `${(data.contact?.name || 'CANDIDATE').toUpperCase()}\n`;
    text += `${data.contact?.email || ''} | ${data.contact?.phone || ''} | ${data.contact?.linkedin || ''}\n\n`;
    text += `PROFESSIONAL SUMMARY\n${data.summary}\n\n`;
    text += `TECHNICAL SKILLS\n${(data.skills || []).join(', ')}\n\n`;
    text += `WORK EXPERIENCE\n`;
    (data.experience || []).forEach(exp => {
      text += `\n${exp.role} | ${exp.company} (${exp.dates})\n`;
      (exp.bullets || []).forEach(b => {
        text += `• ${b}\n`;
      });
    });

    navigator.clipboard.writeText(text).then(() => {
      UI.showToast('Resume plain text copied to clipboard!', 'success');
    });
  }
};

document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
