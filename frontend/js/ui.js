/**
 * UI Rendering and Animation Controller.
 */
const UI = {
  
  showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconName = 'info';
    if (type === 'success') iconName = 'check-circle';
    if (type === 'error') iconName = 'alert-circle';

    toast.innerHTML = `<i data-lucide="${iconName}"></i><span>${message}</span>`;
    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(40px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  },

  showScanner(title = 'Running Deep ATS Analysis', subtitle = 'Evaluating resume against role requirements...') {
    const scanner = document.getElementById('scannerSection');
    const inputStep = document.getElementById('stepInput');
    const resultsStep = document.getElementById('stepResults');
    const tailorStep = document.getElementById('stepTailor');

    document.getElementById('scannerStatusTitle').innerText = title;
    document.getElementById('scannerStatusSubtitle').innerText = subtitle;

    inputStep.style.display = 'none';
    resultsStep.style.display = 'none';
    tailorStep.style.display = 'none';
    scanner.style.display = 'block';

    const bar = document.getElementById('scannerProgressBar');
    bar.style.width = '10%';
    let progress = 10;
    const interval = setInterval(() => {
      progress += 18;
      if (progress > 90) clearInterval(interval);
      bar.style.width = `${Math.min(92, progress)}%`;
    }, 200);

    return () => {
      clearInterval(interval);
      bar.style.width = '100%';
    };
  },

  hideScanner() {
    const scanner = document.getElementById('scannerSection');
    scanner.style.display = 'none';
  },

  renderScorecard(analysis, parsed) {
    const resultsStep = document.getElementById('stepResults');
    resultsStep.style.display = 'block';
    resultsStep.scrollIntoView({ behavior: 'smooth' });

    const totalScore = analysis.overall_score || 50;

    // Animate radial gauge
    this.animateScoreGauge(totalScore, analysis.status_color);

    // Meta details
    document.getElementById('scoreGradeBadge').innerText = `Grade ${analysis.grade} • ${analysis.badge_label}`;
    document.getElementById('scoreGradeBadge').className = `grade-badge badge-${analysis.status_color}`;
    document.getElementById('scoreVerdictTitle').innerText = totalScore >= 75 ? 'Strong ATS Alignment' : (totalScore >= 55 ? 'Moderate ATS Match — Needs Tuning' : 'High ATS Rejection Risk');
    document.getElementById('scoreTargetRoleName').innerText = analysis.target_role.title;

    // Contact info pills
    document.getElementById('statWordCount').innerText = `${parsed.word_count || 0} Words`;
    document.getElementById('statContactName').innerText = parsed.contact?.name || 'Candidate';
    document.getElementById('statEmail').innerText = parsed.contact?.email || 'No email found';

    // 4 Category Metric Cards
    const breakdown = analysis.score_breakdown || {};
    
    // Skills
    const sScore = breakdown.skills?.score || 0;
    document.getElementById('metricSkillsScore').innerText = `${sScore}%`;
    document.getElementById('metricSkillsSummary').innerText = breakdown.skills?.summary || 'Skills Match';
    document.getElementById('barSkills').style.width = `${sScore}%`;

    // Experience
    const eScore = breakdown.experience?.score || 0;
    document.getElementById('metricExpScore').innerText = `${eScore}%`;
    document.getElementById('metricExpSummary').innerText = breakdown.experience?.summary || 'Experience Impact';
    document.getElementById('barExp').style.width = `${eScore}%`;

    // Formatting
    const fScore = breakdown.formatting?.score || 0;
    document.getElementById('metricFormatScore').innerText = `${fScore}%`;
    document.getElementById('metricFormatSummary').innerText = breakdown.formatting?.summary || 'ATS Formatting';
    document.getElementById('barFormat').style.width = `${fScore}%`;

    // Education
    const edScore = breakdown.education?.score || 0;
    document.getElementById('metricEduScore').innerText = `${edScore}%`;
    document.getElementById('metricEduSummary').innerText = breakdown.education?.summary || 'Education Relevance';
    document.getElementById('barEdu').style.width = `${edScore}%`;

    // Diagnostics (Strengths & Weaknesses)
    this.renderDiagnostics(analysis.strengths || [], analysis.weaknesses || []);

    // Keywords Analysis
    this.renderKeywordChips(analysis.keywords_analysis || {});

    // Section by section audit
    this.renderSectionAudit(analysis.section_audit || []);

    // Step 3 CTA score updates
    document.getElementById('ctaCurrentScore').innerText = `${totalScore}%`;
    document.getElementById('ctaProjectedScore').innerText = `~95%`;

    lucide.createIcons();

    // Trigger celebratory confetti if score is high
    if (totalScore >= 80 && window.confetti) {
      confetti({ particleCount: 80, spread: 60, origin: { y: 0.6 } });
    }
  },

  animateScoreGauge(score, colorName) {
    const circle = document.getElementById('scoreProgressCircle');
    const scoreNumEl = document.getElementById('overallScoreNum');
    
    // Radius = 70 => Circumference ≈ 440
    const circumference = 2 * Math.PI * 70; // 439.82
    const offset = circumference - (score / 100) * circumference;

    let strokeColor = '#6366f1';
    if (score >= 80) strokeColor = '#10b981';
    else if (score >= 60) strokeColor = '#3b82f6';
    else if (score >= 45) strokeColor = '#f59e0b';
    else strokeColor = '#f43f5e';

    circle.style.stroke = strokeColor;
    circle.style.strokeDasharray = `${circumference}`;
    circle.style.strokeDashoffset = `${offset}`;

    // Number ticker animation
    let current = 0;
    const stepTime = 1200 / (score || 1);
    const counter = setInterval(() => {
      current++;
      scoreNumEl.innerText = current;
      if (current >= score) {
        clearInterval(counter);
        scoreNumEl.innerText = score;
      }
    }, Math.max(10, stepTime));
  },

  renderDiagnostics(strengths, weaknesses) {
    const listStr = document.getElementById('listStrengths');
    const listWeak = document.getElementById('listWeaknesses');
    
    listStr.innerHTML = strengths.length 
      ? strengths.map(s => `<li>${s}</li>`).join('') 
      : '<li>No major strengths detected. Consider adding more details to your resume.</li>';

    listWeak.innerHTML = weaknesses.length 
      ? weaknesses.map(w => `<li>${w}</li>`).join('') 
      : '<li>No critical ATS flaws detected! Resume is well formatted.</li>';
  },

  renderKeywordChips(kAnalysis) {
    const boxMissingMand = document.getElementById('chipsMissingMandatory');
    const boxMatched = document.getElementById('chipsMatchedMandatory');
    const boxSecondary = document.getElementById('chipsSecondary');

    const missingMand = kAnalysis.missing_mandatory || [];
    const matchedMand = kAnalysis.matched_mandatory || [];
    const matchedSec = (kAnalysis.matched_secondary || []).concat(kAnalysis.domain_keywords_matched || []);
    const missingSec = (kAnalysis.missing_secondary || []).concat(kAnalysis.domain_keywords_missing || []);

    boxMissingMand.innerHTML = missingMand.length 
      ? missingMand.map(k => `<span class="chip-keyword missing-critical">+ ${k}</span>`).join('') 
      : '<span class="chip-mini text-emerald">All core skills matched!</span>';

    boxMatched.innerHTML = matchedMand.length 
      ? matchedMand.map(k => `<span class="chip-keyword matched"><i data-lucide="check" style="width:12px;height:12px;display:inline-block;"></i> ${k}</span>`).join('') 
      : '<span class="chip-mini text-rose">No mandatory role skills detected</span>';

    const combinedSecondary = missingSec.slice(0, 8);
    boxSecondary.innerHTML = combinedSecondary.length 
      ? combinedSecondary.map(k => `<span class="chip-keyword secondary">${k}</span>`).join('') 
      : '<span class="chip-mini text-muted">No additional keywords recommended</span>';
  },

  renderSectionAudit(auditItems) {
    const container = document.getElementById('sectionAuditContainer');
    container.innerHTML = auditItems.map((item, idx) => {
      const isPass = item.status === 'pass';
      const isWarn = item.status === 'warning';
      const badgeClass = isPass ? 'badge-emerald' : (isWarn ? 'badge-amber' : 'badge-rose');
      const icon = isPass ? 'check-circle-2' : (isWarn ? 'alert-circle' : 'x-circle');
      
      return `
        <div class="audit-item">
          <div class="audit-header" onclick="UI.toggleAccordion(this)">
            <div class="audit-title-wrap">
              <i data-lucide="${icon}" class="${isPass ? 'text-emerald' : (isWarn ? 'text-amber' : 'text-rose')}"></i>
              <span class="audit-title">${item.section}</span>
            </div>
            <div style="display:flex; align-items:center; gap:0.6rem;">
              <span class="audit-score-pill ${badgeClass}">${item.score}/100</span>
              <i data-lucide="chevron-down" style="width:16px;height:16px;"></i>
            </div>
          </div>
          <div class="audit-body" style="display: ${idx === 0 || !isPass ? 'block' : 'none'};">
            <p>${item.feedback}</p>
            ${item.tips ? `<div class="audit-tip"><strong>Recommendation:</strong> ${item.tips}</div>` : ''}
          </div>
        </div>
      `;
    }).join('');
  },

  toggleAccordion(headerEl) {
    const bodyEl = headerEl.nextElementSibling;
    if (bodyEl.style.display === 'none' || !bodyEl.style.display) {
      bodyEl.style.display = 'block';
    } else {
      bodyEl.style.display = 'none';
    }
  },

  renderTailorView(tailoredResponse, originalParsed) {
    const resultsStep = document.getElementById('stepResults');
    const tailorStep = document.getElementById('stepTailor');

    resultsStep.style.display = 'none';
    tailorStep.style.display = 'block';
    tailorStep.scrollIntoView({ behavior: 'smooth' });

    const tailored = tailoredResponse.tailored || tailoredResponse;
    const tailoredData = tailored.tailored_data || {};
    const diff = tailored.diff || {};

    // Header info
    document.getElementById('tailorRoleTitle').innerText = tailored.target_role || 'Target Role';
    document.getElementById('tailorProjectedScore').innerText = `${tailored.projected_score || 96}%`;
    document.getElementById('tailorScoreBoost').innerText = tailored.score_boost || '+32% Boost';

    // Summary Diff
    document.getElementById('diffOriginalSummary').innerText = diff.summary?.original || '(No summary in original resume)';
    document.getElementById('editTailoredSummary').value = tailoredData.summary || '';

    // Skills Diff
    const origSkillsContainer = document.getElementById('diffOriginalSkills');
    const origSkills = originalParsed.sections?.skills || [];
    origSkillsContainer.innerHTML = origSkills.length 
      ? `<div class="chips-container">${origSkills.map(s => `<span class="chip-mini">${s}</span>`).join('')}</div>` 
      : '<p class="original-text">No technical skills detected.</p>';

    this.renderTailoredSkillsChips(tailoredData.skills || [], diff.skills?.added_keywords || []);

    // Experience Diff
    this.renderExperienceDiff(tailoredData.experience || [], diff.experience || []);

    // Full Paper Preview
    this.renderPaperPreview(tailoredData);

    lucide.createIcons();

    // Confetti celebration
    if (window.confetti) {
      confetti({ particleCount: 120, spread: 80, origin: { y: 0.5 } });
    }
  },

  renderTailoredSkillsChips(skills, addedKeywords) {
    const container = document.getElementById('diffTailoredSkills');
    const addedSet = new Set((addedKeywords || []).map(k => k.toLowerCase()));

    container.innerHTML = `
      <div class="chips-container" id="tailoredSkillsChips">
        ${skills.map(s => {
          const isAdded = addedSet.has(s.toLowerCase());
          return `
            <span class="chip-keyword ${isAdded ? 'matched' : 'secondary'}" style="display:inline-flex;align-items:center;gap:0.35rem;">
              ${s}
              <i data-lucide="x" style="width:12px;height:12px;cursor:pointer;" onclick="App.removeSkill('${s.replace(/'/g, "\\'")}')"></i>
            </span>
          `;
        }).join('')}
      </div>
    `;
    lucide.createIcons();
  },

  renderExperienceDiff(tailoredExp, diffRecords) {
    const container = document.getElementById('diffExperienceContainer');
    
    if (!tailoredExp.length) {
      container.innerHTML = '<p class="original-text">No experience items available.</p>';
      return;
    }

    container.innerHTML = tailoredExp.map((exp, roleIdx) => {
      const bullets = exp.bullets || [];
      const diffItem = diffRecords[roleIdx] || {};
      const bulletDiffs = diffItem.bullet_diffs || [];

      return `
        <div class="exp-diff-card">
          <div class="exp-diff-meta">
            <span class="exp-role-title">${exp.role} ${exp.company ? `| ${exp.company}` : ''}</span>
            <span class="exp-dates">${exp.dates || ''}</span>
          </div>
          <div class="bullet-diffs-list">
            ${bullets.map((b, bIdx) => {
              const origB = bulletDiffs[bIdx]?.original || '(Added / Expanded)';
              return `
                <div class="bullet-comparison-row">
                  <div class="bullet-orig">
                    <span style="font-size:0.7rem;text-transform:uppercase;color:var(--text-dim);display:block;margin-bottom:0.25rem;">Original:</span>
                    ${origB}
                  </div>
                  <div>
                    <span style="font-size:0.7rem;text-transform:uppercase;color:var(--accent-emerald);display:block;margin-bottom:0.25rem;">STAR Optimized (Editable):</span>
                    <textarea class="bullet-tailored-input" data-role-idx="${roleIdx}" data-bullet-idx="${bIdx}" rows="2" onchange="App.onBulletChange(this)">${b}</textarea>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    }).join('');
  },

  renderPaperPreview(tailoredData) {
    const contact = tailoredData.contact || {};
    document.getElementById('paperName').innerText = (contact.name || 'CANDIDATE NAME').toUpperCase();
    
    const contactParts = [];
    if (contact.email) contactParts.push(contact.email);
    if (contact.phone) contactParts.push(contact.phone);
    if (contact.linkedin) contactParts.push(contact.linkedin);
    if (contact.github) contactParts.push(contact.github);
    document.getElementById('paperContact').innerText = contactParts.join(' • ');

    document.getElementById('paperSummary').innerText = tailoredData.summary || '';
    document.getElementById('paperSkills').innerHTML = `<strong>Proficiencies:</strong> ${(tailoredData.skills || []).join(' • ')}`;

    // Experience
    const expContainer = document.getElementById('paperExperience');
    expContainer.innerHTML = (tailoredData.experience || []).map(exp => `
      <div class="paper-experience-item">
        <div class="paper-role-header">
          <span>${exp.role} ${exp.company ? `| ${exp.company}` : ''}</span>
          <span style="color:#64748b;font-weight:normal;">${exp.dates || ''}</span>
        </div>
        <ul class="paper-bullets">
          ${(exp.bullets || []).map(b => `<li>${b}</li>`).join('')}
        </ul>
      </div>
    `).join('');

    // Education & Certs
    const eduContainer = document.getElementById('paperEducation');
    const eduList = (tailoredData.education || []).map(e => `<li>${e.details || e}</li>`).join('');
    const certList = (tailoredData.certifications || []).map(c => `<li><strong>Certified:</strong> ${c}</li>`).join('');
    eduContainer.innerHTML = `<ul class="paper-bullets">${eduList}${certList}</ul>`;
  }
};
