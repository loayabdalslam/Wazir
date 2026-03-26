class SwarmCountry {
  constructor() {
    this.ws = null;
    this.state = {
      country: '',
      goal: '',
      running: false,
      dashboard: null,
      agents: [],
      scenarios: [],
      projections: null,
      wildcards: [],
      feasibility: 0,
    };
    this.init();
  }

  init() {
    this.countryInput = document.getElementById('country');
    this.goalInput = document.getElementById('goal');
    this.btnSimulate = document.getElementById('btn-simulate');
    this.progressBar = document.getElementById('progress-fill');
    this.progressContainer = document.getElementById('progress-bar');
    this.statusLine = document.getElementById('status-line');
    this.dashboard = document.getElementById('dashboard');
    this.agentList = document.getElementById('agent-briefs');
    this.scenarioList = document.getElementById('scenario-cards');
    this.projectionGrid = document.getElementById('projection-grid');
    this.wildcardList = document.getElementById('wildcard-list');
    this.feasibilitySection = document.getElementById('feasibility-section');
    this.dashboardHeader = document.getElementById('dashboard-header');
    this.domainGrid = document.getElementById('domain-grid');

    this.btnSimulate.addEventListener('click', () => this.startSimulation());
    this.countryInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') this.startSimulation();
    });
  }

  startSimulation() {
    const country = this.countryInput.value.trim();
    if (!country) return;

    this.state.country = country;
    this.state.goal = this.goalInput.value.trim();
    this.state.running = true;
    this.state.agents = [];
    this.state.scenarios = [];
    this.state.wildcards = [];

    this.resetUI();
    this.showProgress();
    this.btnSimulate.disabled = true;
    this.btnSimulate.textContent = 'SIMULATING...';

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/simulate`);

    this.ws.onopen = () => {
      this.ws.send(JSON.stringify({
        country: this.state.country,
        goal: this.state.goal
      }));
    };

    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      this.handleMessage(msg);
    };

    this.ws.onclose = () => {
      this.state.running = false;
      this.btnSimulate.disabled = false;
      this.btnSimulate.textContent = 'SIMULATE';
    };

    this.ws.onerror = () => {
      this.state.running = false;
      this.btnSimulate.disabled = false;
      this.btnSimulate.textContent = 'SIMULATE';
      this.setStatus('Connection error — retry');
    };
  }

  handleMessage(msg) {
    switch (msg.type) {
      case 'status':
        this.setStatus(msg.message);
        this.setProgress(msg.progress);
        break;

      case 'country_data':
        this.setStatus(`Data loaded for ${msg.data.country || this.state.country}`);
        break;

      case 'dashboard':
        this.state.dashboard = msg.data;
        this.renderDashboard(msg.data);
        this.setProgress(msg.progress);
        break;

      case 'agent_brief':
        this.state.agents.push(msg);
        this.renderAgentBrief(msg);
        this.setProgress(msg.progress);
        break;

      case 'scenarios':
        this.state.scenarios = msg.data;
        this.renderScenarios(msg.data);
        this.setProgress(msg.progress);
        break;

      case 'projections':
        this.state.projections = msg.data;
        this.renderProjections(msg.data);
        this.setProgress(msg.progress);
        break;

      case 'wildcards':
        this.state.wildcards = msg.data;
        this.renderWildcards(msg.data);
        this.setProgress(msg.progress);
        break;

      case 'feasibility':
        this.state.feasibility = msg.score;
        this.renderFeasibility(msg.score);
        this.setProgress(msg.progress);
        break;

      case 'complete':
        this.setStatus('Simulation complete');
        this.state.running = false;
        this.btnSimulate.disabled = false;
        this.btnSimulate.textContent = 'SIMULATE';
        setTimeout(() => this.hideProgress(), 2000);
        break;

      case 'scenario_detail':
        this.renderScenarioDetail(msg);
        break;
    }
  }

  setStatus(text) {
    this.statusLine.textContent = `> ${text}`;
  }

  setProgress(pct) {
    this.progressBar.style.width = `${pct}%`;
  }

  showProgress() {
    this.progressContainer.classList.add('active');
    this.statusLine.classList.add('active');
  }

  hideProgress() {
    this.progressContainer.classList.remove('active');
    this.statusLine.classList.remove('active');
  }

  resetUI() {
    this.agentList.innerHTML = '';
    this.scenarioList.innerHTML = '';
    this.projectionGrid.innerHTML = '';
    this.wildcardList.innerHTML = '';
    this.feasibilitySection.innerHTML = '';
    this.domainGrid.innerHTML = '';
    this.dashboardHeader.innerHTML = '';
    this.dashboard.classList.remove('visible');
    this.progressBar.style.width = '0%';
  }

  renderDashboard(data) {
    this.dashboard.classList.add('visible');

    this.dashboardHeader.innerHTML = `
      <h2>${data.country || this.state.country}</h2>
      <span class="goal-badge">${data.goal || 'General Assessment'}</span>
    `;

    const domains = data.domains || [];
    this.domainGrid.innerHTML = domains.map(d => {
      const riskClass = `risk-${d.risk.toLowerCase()}`;
      return `
        <div class="domain-card">
          <div class="domain-header">
            <span class="domain-name">${d.icon} ${d.name}</span>
            <span class="domain-risk ${riskClass}">${d.risk}</span>
          </div>
          <div class="domain-meta">
            <span>${d.status}</span>
            <span>${d.trend}</span>
          </div>
        </div>
      `;
    }).join('');

    const metrics = data.metrics || [];
    const indSection = document.getElementById('indicators-section');
    const indGrid = document.getElementById('indicator-grid');
    
    if (metrics.length > 0) {
      indSection.style.display = 'block';
      indGrid.innerHTML = metrics.map(m => `
        <div class="indicator-card">
          <div class="ind-icon">${m.icon}</div>
          <div class="ind-info">
            <div class="ind-label">${m.label}</div>
            <div class="ind-value">${m.value}</div>
          </div>
        </div>
      `).join('');
    } else {
      indSection.style.display = 'none';
    }
  }

  renderAgentBrief(msg) {
    const div = document.createElement('div');
    div.className = 'agent-brief';
    div.innerHTML = `
      <div class="agent-header">
        <span class="agent-icon">${msg.icon}</span>
        <span class="agent-name">${msg.agent}</span>
        <span class="agent-domain">${msg.domain}</span>
      </div>
      <div class="agent-text">${msg.brief}</div>
    `;
    this.agentList.appendChild(div);
  }

  renderScenarios(scenarios) {
    this.scenarioList.innerHTML = scenarios.map((s, i) => `
      <div class="scenario-card" data-index="${i}" onclick="app.selectScenario(${i})">
        <div class="scenario-num">Path ${i + 1}</div>
        <h3>${s.icon} ${s.name}</h3>
        <div class="scenario-desc">${s.summary}</div>
        <div class="timeline">
          <h4>Short-term (0-12 months)</h4>
          <p>${s.short_term}</p>
        </div>
        <div class="timeline">
          <h4>Long-term (1-5 years)</h4>
          <p>${s.long_term}</p>
        </div>
        <div class="risks">
          ${(s.risks || []).map(r => `<span class="risk-tag">${r}</span>`).join('')}
        </div>
        <div class="agent-votes">
          <span class="vote-for">✓ ${s.agents_for.join(', ')}</span>
          <span class="vote-against">✗ ${s.agents_against.join(', ')}</span>
        </div>
      </div>
    `).join('');
  }

  selectScenario(idx) {
    document.querySelectorAll('.scenario-card').forEach(c => c.classList.remove('selected'));
    document.querySelector(`.scenario-card[data-index="${idx}"]`)?.classList.add('selected');

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'scenario_select', scenario: idx }));
    }
  }

  renderScenarioDetail(msg) {
    const s = msg.scenario;
    const followUp = msg.follow_up || [];
    const proj = msg.projections || {};

    const existing = document.getElementById('scenario-detail');
    if (existing) existing.remove();

    const div = document.createElement('div');
    div.id = 'scenario-detail';
    div.className = 'agent-brief';
    div.style.borderColor = 'var(--accent)';
    div.innerHTML = `
      <div class="agent-header">
        <span class="agent-icon">${s.icon}</span>
        <span class="agent-name">${s.name} — Action Plan</span>
      </div>
      <div class="agent-text">
        <strong>Critical Path:</strong>
        <ol style="margin: 12px 0 16px 20px; color: var(--text-dim);">
          ${followUp.map(f => `<li style="margin-bottom: 4px;">${f}</li>`).join('')}
        </ol>
        <strong>Projected Impact:</strong>
        <div style="display: flex; gap: 24px; margin-top: 8px;">
          ${Object.entries(proj).map(([k, v]) => `
            <div>
              <div style="font-size: 10px; color: var(--text-muted); text-transform: uppercase;">${k.replace(/_/g, ' ')}</div>
              <div style="font-family: var(--mono); color: var(--accent);">${v.min}–${v.max} <span style="color: var(--text-muted);">(base: ${v.base})</span></div>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    this.scenarioList.after(div);
  }

  renderProjections(data) {
    this.projectionGrid.innerHTML = Object.entries(data).map(([key, val]) => {
      const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      const range = `${val.min}–${val.max}${val.unit}`;
      const base = `${val.base}${val.unit}`;

      const minV = parseFloat(val.min);
      const maxV = parseFloat(val.max);
      const baseV = parseFloat(val.base);
      const pctBase = maxV > minV ? ((baseV - minV) / (maxV - minV)) * 100 : 50;
      const pctMin = maxV > minV ? ((minV) / (maxV)) * 20 : 0;
      const pctWidth = maxV > minV ? 80 : 40;

      return `
        <div class="projection-card">
          <div class="proj-label">${label}</div>
          <div class="proj-base">${base}</div>
          <div class="proj-range">${range}</div>
          <div class="projection-bar">
            <div class="bar-fill" style="left: ${pctMin}%; width: ${pctWidth}%;"></div>
            <div class="bar-base" style="left: ${pctBase}%;"></div>
          </div>
        </div>
      `;
    }).join('');
  }

  renderWildcards(data) {
    this.wildcardList.innerHTML = data.map(w => `
      <div class="wildcard">
        <div class="wc-header">
          <span class="wc-source">${w.agent}</span>
          <span class="wc-prob">${w.probability}% probability · ${w.impact} impact</span>
        </div>
        <div class="wc-event">${w.event}</div>
      </div>
    `).join('');
  }

  renderFeasibility(score) {
    if (!score) return;
    this.feasibilitySection.innerHTML = `
      <div class="feasibility">
        <div class="score">${score}</div>
        <div class="score-label">Goal Feasibility Score</div>
      </div>
    `;
  }
}

const app = new SwarmCountry();
