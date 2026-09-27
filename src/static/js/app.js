document.addEventListener('DOMContentLoaded', () => {

  /* ===== STATE ===== */
  const state = {
    currentView: 'repository',
    assignments: [],
    pyqPapers: [],
    notebooks: [],
    curriculum: [],
    chatHistory: [],
    flashcards: [],
    quizQuestions: [],
    quizIndex: 0,
    quizScore: 0,
    theme: document.documentElement.getAttribute('data-theme') || 'dark',
  };

  /* ===== DOM REFS ===== */
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => document.querySelectorAll(sel);

  /* ===== THEME ===== */
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    state.theme = theme;
  }
  applyTheme(state.theme);

  /* ===== NAVIGATION ===== */
const viewTitles = {
    repository: 'Assignment Repository',
    pyq: 'Previous Year Papers',
    notebook: 'Notebook OCR & Notes',
    'question-bank': 'Topic Question Bank',
    curriculum: 'Curriculum Browser',
    generator: 'Assignment Generator',
    help: 'Socratic Helper & Grader',
    notes: 'Note Maker & Flashcards',
    quiz: 'AI Quiz & Weakness Radar',
    chat: 'RAG Academic Chat',
    recommendations: 'Smart Recommendations',
  };

  function switchView(viewName) {
    state.currentView = viewName;
    $$('.view-panel').forEach(p => p.classList.remove('active'));
    const panel = document.getElementById('view-' + viewName);
    if (panel) panel.classList.add('active');
    $$('.nav-item').forEach(n => n.classList.remove('active'));
    const navItem = document.querySelector(`.nav-item[data-view="${viewName}"]`);
    if (navItem) navItem.classList.add('active');
    const title = $('#current-view-title');
    if (title) title.textContent = viewTitles[viewName] || viewName;
    loadViewData(viewName);
  }

  function loadViewData(viewName) {
    switch(viewName) {
      case 'repository': renderAssignments(); break;
      case 'pyq': renderPYQ(); break;
      case 'notebook': renderNotebooks(); break;
      case 'curriculum': renderCurriculum(); break;
      case 'notes': refreshNotesView(); break;
      case 'question-bank': renderQuestionBank(); break;
      case 'recommendations': loadRecommendations(); break;
    }
  }

  $$('.nav-item[data-view]').forEach(item => {
    item.addEventListener('click', () => switchView(item.getAttribute('data-view')));
  });

  /* ===== API HELPERS ===== */
  async function api(url, opts = {}) {
    try {
      const res = await fetch(url, opts);
      return await res.json();
    } catch (e) { console.error(url, e); return null; }
  }

  /* ===== BADGES ===== */
  async function refreshBadges() {
    const a = await api('/api/assignments?limit=1');
    const p = await api('/api/pyq/papers?limit=1');
    const n = await api('/api/notebooks?limit=1');
    const ab = $('#nav-badge-assignments');
    const pb = $('#nav-badge-pyq');
    const nb = $('#nav-badge-notebooks');
    if (ab) ab.textContent = a && a.total !== undefined ? a.total : (Array.isArray(a) ? a.length : 0);
    if (pb) pb.textContent = p && p.total !== undefined ? p.total : (Array.isArray(p) ? p.length : 0);
    if (nb) nb.textContent = n && n.total !== undefined ? n.total : (Array.isArray(n) ? n.length : 0);
  }

  /* ===== SYSTEM STATUS ===== */
  async function loadStatus() {
    const s = await api('/api/system/status');
    if (!s) return;
    const el = $('#c-core-status');
    if (el) el.textContent = s.c_core_accelerated ? 'Native DLL' : 'JS Fallback';
    const rag = $('#rag-status-text');
    if (rag) rag.textContent = (s.indexed_rag_chunks || 0) + ' chunks';
  }

  async function renderPYQ() {
    const subject = $('#pyq-search-subject')?.value || '';
    const college = $('#pyq-search-college')?.value || '';
    if (!subject) return;
    const data = await api('/api/pyq/search?subject=' + encodeURIComponent(subject) + '&college=' + encodeURIComponent(college));
    if (!data) return;
    state.pyqPapers = Array.isArray(data) ? data : [];
    const grid = $('#pyq-results-grid');
    if (!grid) return;
    if (state.pyqPapers.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-dim);padding:2rem;">No papers found.</p>';
      return;
    }
    grid.innerHTML = state.pyqPapers.map(p => `
      <div class="pyq-card">
        <div style="font-weight:700;margin-bottom:0.25rem;">${escapeHtml(p.title||'Untitled')}</div>
        <div style="font-size:0.8rem;color:var(--text-dim);">${escapeHtml(p.college||'')} &middot; Sem ${p.semester||'?'} &middot; ${p.academic_year||''}</div>
        ${p.source_url ? `<a href="${escapeHtml(p.source_url)}" target="_blank" class="btn btn-sm btn-secondary">Source</a>` : ''}
      </div>`).join('');
  }

  /* ===== ASSIGNMENTS ===== */
  async function renderAssignments() {
    const college = $('#filter-college')?.value || '';
    const subject = $('#filter-subject')?.value || '';
    const semester = $('#filter-semester')?.value || '';
    const status = $('#filter-status')?.value || '';
    const difficulty = $('#filter-difficulty')?.value || '';
    const search = $('#global-search-input')?.value || '';

    const params = new URLSearchParams({ limit: '100', offset: '0' });
    if (college) params.set('college', college);
    if (subject) params.set('subject', subject);
    if (semester) params.set('semester', semester);
    if (status) params.set('status', status);
    if (difficulty) params.set('difficulty', difficulty);
    if (search) params.set('search', search);

    const data = await api('/api/assignments?' + params.toString());
    if (!data) return;
    state.assignments = Array.isArray(data) ? data : [];
    const grid = $('#assignments-grid');
    if (!grid) return;

    if (state.assignments.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-dim);padding:2rem;">No assignments found.</p>';
      return;
    }

    grid.innerHTML = state.assignments.map(a => `
      <div class="assignment-card" data-id="${a.id}" onclick="openAssignmentDetail('${a.id}')">
        <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:0.5rem;">
          <span class="ac-subject">${escapeHtml(a.title || 'Untitled')}</span>
          <span class="badge badge-${diffBadge(a.difficulty)}">${a.difficulty || 'Intermediate'}</span>
        </div>
        <div class="ac-meta">
          <i class="fa-solid fa-building" style="margin-right:4px;"></i>${escapeHtml(a.college||'')} &middot;
          <i class="fa-solid fa-book" style="margin-right:4px;"></i>${escapeHtml(a.subject||'')} &middot;
          Sem ${a.semester||'?'} &middot; ${a.academic_year||''}
        </div>
        <div class="ac-meta">
          <i class="fa-solid fa-circle-check" style="margin-right:4px;color:var(--success);"></i>${a.status||'Pending'}
        </div>
        ${a.topic_tags && a.topic_tags.length ? `<div class="ac-tags">${a.topic_tags.slice(0,4).map(t=>'<span class="badge badge-info">'+escapeHtml(t)+'</span>').join('')}</div>` : ''}
        ${(a.questions && a.questions.length) ? `<div style="margin-top:0.5rem;font-size:0.75rem;color:var(--text-dim);">${a.questions.length} questions</div>` : ''}
      </div>
    `).join('');
  }

  function diffBadge(d) {
    if (d === 'Advanced') return 'danger';
    if (d === 'Introductory') return 'success';
    return 'primary';
  }

  /* Filter handlers */
  $('#filter-college')?.addEventListener('change', renderAssignments);
  $('#filter-subject')?.addEventListener('change', renderAssignments);
  $('#filter-semester')?.addEventListener('change', renderAssignments);
  $('#filter-status')?.addEventListener('change', renderAssignments);
  $('#filter-difficulty')?.addEventListener('change', renderAssignments);
  $('#global-search-input')?.addEventListener('input', debounce(renderAssignments, 350));
  $('#sort-assignments-by')?.addEventListener('change', renderAssignments);

  /* ===== PYQ ===== */
  $('#btn-search-pyq')?.addEventListener('click', async () => {
    const subject = $('#pyq-search-subject')?.value || '';
    const college = $('#pyq-search-college')?.value || '';
    if (!subject) return;
    const data = await api('/api/pyq/search?subject=' + encodeURIComponent(subject) + '&college=' + encodeURIComponent(college));
    if (!data) return;
    state.pyqPapers = Array.isArray(data) ? data : [];
    const grid = $('#pyq-results-grid');
    if (!grid) return;
    if (state.pyqPapers.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-dim);padding:2rem;">No papers found for this subject.</p>';
      return;
    }
    grid.innerHTML = state.pyqPapers.map(p => `
      <div class="pyq-card">
        <div style="font-weight:700;margin-bottom:0.25rem;">${escapeHtml(p.title||'Untitled')}</div>
        <div style="font-size:0.8rem;color:var(--text-dim);">
          ${escapeHtml(p.college||'')} &middot; Sem ${p.semester||'?'} &middot; ${p.academic_year||''} &middot; ${escapeHtml(p.exam_type||'End-Sem')}
        </div>
        ${p.source_url ? `<div style="margin-top:0.4rem;"><a href="${escapeHtml(p.source_url)}" target="_blank" class="btn btn-sm btn-secondary"><i class="fa-solid fa-arrow-up-right-from-square"></i> Source</a></div>` : ''}
      </div>
    `).join('');
  });

  /* ===== NOTEBOOKS ===== */
  function setupDropzone() {
    const dz = $('#notebook-dropzone');
    const inp = $('#notebook-file-input');
    if (!dz || !inp) return;

    dz.addEventListener('click', () => inp.click());
    dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('dragover'); });
    dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
    dz.addEventListener('drop', e => { e.preventDefault(); dz.classList.remove('dragover'); if (e.dataTransfer.files.length) uploadNotebook(e.dataTransfer.files[0]); });
    inp.addEventListener('change', () => { if (inp.files.length) uploadNotebook(inp.files[0]); inp.value = ''; });
  }

  async function uploadNotebook(file) {
    const college = $('#upload-college-input')?.value || 'University';
    const subject = $('#upload-subject-input')?.value || 'General';
    const semester = $('#upload-semester-input')?.value || '1';

    const form = new FormData();
    form.append('file', file);
    form.append('college', college);
    form.append('subject', subject);
    form.append('semester', semester);

    try {
      const res = await fetch('/api/notebooks/upload', { method: 'POST', body: form });
      const json = await res.json();
      showToast('Notebook uploaded & parsed: ' + (json.original_name || file.name), 'success');
      renderNotebooks();
      refreshNotesSelects();
    } catch (e) { showToast('Upload failed', 'error'); }
  }

  async function renderNotebooks() {
    const data = await api('/api/notebooks');
    if (!data) return;
    state.notebooks = Array.isArray(data) ? data : [];
    const grid = $('#notebooks-list-grid');
    if (!grid) return;
    if (state.notebooks.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-dim);padding:1rem;">No notebooks uploaded yet.</p>';
      return;
    }
    grid.innerHTML = state.notebooks.map(n => `
      <div class="notebook-card">
        <div style="font-weight:700;font-size:0.9rem;">${escapeHtml(n.original_name)}</div>
        <div style="font-size:0.78rem;color:var(--text-dim);margin-top:0.2rem;">
          ${n.file_type} &middot; ${(n.file_size/1024).toFixed(1)}KB &middot; ${escapeHtml(n.subject||'')} Sem ${n.semester||'?'}
        </div>
        ${n.summary ? `<div style="font-size:0.78rem;color:var(--text-secondary);margin-top:0.4rem;">${escapeHtml(n.summary.substring(0,120))}...</div>` : ''}
        ${n.extracted_topics && n.extracted_topics.length ? `<div style="margin-top:0.4rem;display:flex;gap:0.3rem;flex-wrap:wrap;">${n.extracted_topics.slice(0,6).map(t=>'<span class="badge badge-info">'+escapeHtml(t)+'</span>').join('')}</div>` : ''}
      </div>
    `).join('');
  }

  /* ===== CURRICULUM ===== */
  async function renderCurriculum() {
    const sem = $('#curriculum-sem-filter')?.value || '';
    const url = sem ? '/api/curriculum?semester=' + sem : '/api/curriculum';
    const data = await api(url);
    if (!data) return;
    state.curriculum = Array.isArray(data) ? data : [];
    const grid = $('#curriculum-grid');
    if (!grid) return;
    const stats = $('#curriculum-stats');
    if (stats) stats.textContent = state.curriculum.length + ' courses';

    if (state.curriculum.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-dim);padding:1rem;">No curriculum entries found.</p>';
      return;
    }
    grid.innerHTML = state.curriculum.map(c => `
      <div class="curriculum-card">
        <div style="display:flex;justify-content:space-between;align-items:start;">
          <div>
            <div style="font-weight:700;font-size:0.9rem;">${escapeHtml(c.code)} — ${escapeHtml(c.name)}</div>
            <div style="font-size:0.75rem;color:var(--text-dim);margin-top:0.15rem;">Sem ${c.semester} &middot; ${c.credits||3} credits &middot; ${escapeHtml(c.category||'')}</div>
          </div>
          <span class="badge badge-${c.type==='Elective'?'warning':'primary'}">${c.type||'Core'}</span>
        </div>
        ${c.modules && c.modules.length ? `<div style="margin-top:0.5rem;font-size:0.78rem;color:var(--text-secondary);">${c.modules.map(m=>'<div style="margin-bottom:0.2rem;"><strong>'+escapeHtml(m.title)+'</strong>: '+(m.topics||[]).join(', ')+'</div>').join('')}</div>` : ''}
        <div style="margin-top:0.75rem;display:flex;gap:0.5rem;flex-wrap:wrap;">
          <button class="btn btn-info btn-sm" onclick="studyTopic('${escapeHtml(c.code)}','${escapeHtml(c.name)}','${c.modules?c.modules.map(m=>m.title).join('|'):''}')"><i class="fa-solid fa-book-open"></i> Study Now</button>
          <button class="btn btn-secondary btn-sm" onclick="generateAssignmentForCourse('${escapeHtml(c.code)}','${escapeHtml(c.name)}')"><i class="fa-solid fa-file-pen"></i> Generate Assignment</button>
          <button class="btn btn-secondary btn-sm" onclick="startQuizForCourse('${escapeHtml(c.code)}','${escapeHtml(c.name)}')"><i class="fa-solid fa-gamepad"></i> Quiz</button>
        </div>
      </div>
    `).join('');
  }

  $('#curriculum-sem-filter')?.addEventListener('change', renderCurriculum);

  /* ===== COURSE ACTIONS (Study Now, Generate Assignment, Quiz) ===== */
  window.studyTopic = async function(courseCode, courseName, moduleTopics) {
    // Direct navigation — no landing redirect, no delay
    showToast('Opening ' + courseName, 'info');
    const panel = document.getElementById('view-curriculum');
    const navItem = document.querySelector('.nav-item[data-view="curriculum"]');
    if (panel) {
      document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
      panel.classList.add('active');
      // Load questions directly in the panel
      const display = document.getElementById('question-bank-display');
      if (display) {
        display.innerHTML = '<p style="color:var(--text-dim);padding:1rem;">Loading questions for ' + courseName + '...</p>';
        try {
          const res = await api('/api/questions/topic/' + encodeURIComponent(courseName) + '/' + encodeURIComponent('Topic 1'));
          const res2 = await api('/api/questions/topic/' + encodeURIComponent(courseName) + '/' + encodeURIComponent('Topic 2'));
          const res3 = await api('/api/questions/topic/' + encodeURIComponent(courseName) + '/' + encodeURIComponent('Topic 3'));
          let combined = { questions: [], total: 0, subject: courseName, topic: 'Topics 1-3' };
          const seen = new Set();
          for (const r of [res, res2, res3]) {
            if (r && r.questions) { r.questions.forEach(q => { if (!seen.has(q.id)) { seen.add(q.id); combined.questions.push(q); } }); combined.total += r.total || r.questions.length; }
          }
          if (combined.questions.length > 0) {
            renderQuestionBankView({ ...combined, questions: combined.questions.slice(0, 15) });
          } else {
            display.innerHTML = '<p style="color:var(--text-dim);padding:1rem;">No questions yet for ' + courseName + '. Generate some below.</p>';
          }
        } catch (e) {
          display.innerHTML = '<p style="color:var(--danger);padding:1rem;">Failed to load questions.</p>';
        }
      }
    }
    if (navItem) navItem.classList.add('active');
    document.getElementById('current-view-title').textContent = 'Study — ' + courseName;
  };

  window.generateAssignmentForCourse = async function(courseCode, courseName) {
    showToast('Generating assignment for ' + courseCode, 'info');
    switchView('generator');
    setTimeout(() => {
      const subj = $('#gen-subject');
      const exam = $('#gen-target-exam');
      if (subj) subj.value = courseCode;
      if (exam) exam.value = 'University End-Sem';
    }, 300);
  };

  window.startQuizForCourse = async function(courseCode, courseName) {
    showToast('Starting quiz for ' + courseCode, 'info');
    switchView('quiz');
    setTimeout(() => {
      const topicInp = $('#quiz-topic-input');
      if (topicInp) topicInp.value = courseCode;
    }, 300);
  };

  /* ===== QUESTION BANK ===== */
  async function renderQuestionBank() {
    const display = $('#question-bank-display');
    if (!display) return;
    display.innerHTML = '<p style="color:var(--text-dim);padding:1rem;">Enter a subject and topic to load the question bank.</p>';
    
    // Load button
    $('#btn-load-bank')?.addEventListener('click', () => {
      const subject = $('#qb-subject')?.value?.trim() || '';
      const topic = $('#qb-topic')?.value?.trim() || '';
      if (!subject || !topic) { showToast('Enter subject and topic', 'error'); return; }
      loadQuestionBank(subject, topic);
    });
    
    // Generate buttons
    $('#btn-gen-5')?.addEventListener('click', () => {
      const subject = $('#qb-subject')?.value?.trim() || '';
      const topic = $('#qb-topic')?.value?.trim() || '';
      if (!subject || !topic) { showToast('Enter subject and topic', 'error'); return; }
      generateTopicQuestions(subject, topic, 5);
    });
    
    $('#btn-gen-10')?.addEventListener('click', () => {
      const subject = $('#qb-subject')?.value?.trim() || '';
      const topic = $('#qb-topic')?.value?.trim() || '';
      if (!subject || !topic) { showToast('Enter subject and topic', 'error'); return; }
      generateTopicQuestions(subject, topic, 10);
    });
    
    $('#btn-gen-15')?.addEventListener('click', () => {
      const subject = $('#qb-subject')?.value?.trim() || '';
      const topic = $('#qb-topic')?.value?.trim() || '';
      if (!subject || !topic) { showToast('Enter subject and topic', 'error'); return; }
      generateTopicQuestions(subject, topic, 15);
    });
  }

  async function loadQuestionBank(subject, topic) {
    const display = $('#question-bank-display');
    if (!display) return;
    display.innerHTML = '<p style="color:var(--text-dim);padding:1rem;">Loading...</p>';
    
    const data = await api('/api/questions/topic/' + encodeURIComponent(subject) + '/' + encodeURIComponent(topic));
    if (!data) {
      display.innerHTML = '<p style="color:var(--danger);padding:1rem;">Failed to load question bank.</p>';
      return;
    }
    renderQuestionBankView(data);
  }

  function renderQuestionBankView(data) {
    const display = $('#question-bank-display');
    if (!display) return;
    
    const subject = data.subject || '';
    const topic = data.topic || '';
    const total = data.total || 0;
    const target = data.target || 20;
    const diffBreakdown = data.difficulty_breakdown || {};
    const typeBreakdown = data.type_breakdown || {};
    const questions = data.questions || [];
    
    const diffOrder = ['Easy', 'Medium', 'Hard', 'Advanced'];
    const diffBadges = {'Easy': 'success', 'Medium': 'primary', 'Hard': 'warning', 'Advanced': 'danger'};
    
    display.innerHTML = `
      <div class="card" style="margin-bottom:1rem;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
          <div>
            <div style="font-weight:700;font-size:1rem;">${escapeHtml(topic)}</div>
            <div style="font-size:0.8rem;color:var(--text-dim);">${escapeHtml(subject)} Question Bank</div>
          </div>
          <div style="display:flex;gap:0.5rem;align-items:center;">
            <span class="badge badge-primary">${total} / ${target} Questions</span>
            <span class="badge badge-${total >= target ? 'success' : 'info'}">${Math.round(total / target * 100)}% Complete</span>
          </div>
        </div>
        <div style="display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1rem;">
          ${diffOrder.map(d => `<span class="badge badge-${diffBadges[d] || 'info'}">${d}: ${diffBreakdown[d] || 0}</span>`).join('')}
        </div>
        <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1rem;">
          ${Object.entries(typeBreakdown).map(([k,v]) => `<span class="badge badge-info">${k}: ${v}</span>`).join('')}
        </div>
        <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
          <button class="btn btn-secondary btn-sm" onclick="generateTopicQuestions('${escapeHtml(subject)}','${escapeHtml(topic)}',5)"><i class="fa-solid fa-wand-magic-sparkles"></i> Generate 5</button>
          <button class="btn btn-secondary btn-sm" onclick="generateTopicQuestions('${escapeHtml(subject)}','${escapeHtml(topic)}',10)"><i class="fa-solid fa-wand-magic-sparkles"></i> Generate 10</button>
          <button class="btn btn-secondary btn-sm" onclick="generateTopicQuestions('${escapeHtml(subject)}','${escapeHtml(topic)}',15)"><i class="fa-solid fa-wand-magic-sparkles"></i> Generate 15</button>
          <button class="btn btn-secondary btn-sm" onclick="generateTopicQuestions('${escapeHtml(subject)}','${escapeHtml(topic)}',20)"><i class="fa-solid fa-wand-magic-sparkles"></i> Fill to 20</button>
        </div>
      </div>
      <div style="display:flex;flex-direction:column;gap:0.5rem;">
        ${questions.map((q, i) => `
          <div class="question-item" style="border:1px solid var(--border-color);border-radius:var(--radius-sm);padding:0.75rem;">
            <div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:0.25rem;">
              <strong style="font-size:0.85rem;">Q${i+1}: ${escapeHtml(q.question_text?.substring(0,100))}...</strong>
              <div style="display:flex;gap:0.3rem;flex-wrap:wrap;">
                <span class="badge badge-${diffBadges[q.difficulty] || 'info'}">${q.difficulty || 'Medium'}</span>
                <span class="badge badge-info">${q.question_type || 'Exam'}</span>
                <span class="badge badge-primary">${q.marks || 5} marks</span>
                <span class="badge badge-${q.source_type === 'AI_Generated' ? 'purple' : 'info'}">${q.source_type || 'Unknown'}</span>
                ${q.course_code ? `<a href="http://127.0.0.1:8000/api/curriculum?semester=${q.year ? (q.year <= 2 ? 1 : q.year <= 4 ? 3 : q.year <= 6 ? 5 : 7) : 1}" class="badge badge-info" style="text-decoration:none;font-size:0.7rem;">${q.course_code || ''}${q.year ? ' · Y'+q.year : ''}</a>` : ''}
              </div>
            </div>
            <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:0.5rem;">${escapeHtml(q.question_text || '')}</div>
            <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
              <button class="btn btn-secondary btn-sm" onclick="viewQuestionDetail('${q.id || ''}')"><i class="fa-solid fa-eye"></i> View</button>
              <button class="btn btn-secondary btn-sm" onclick="generateSimilarSingle('${q.id || ''}')"><i class="fa-solid fa-wand-magic-sparkles"></i> Generate Similar</button>
            </div>
          </div>
        `).join('') || '<p style="color:var(--text-dim);padding:1rem;">No questions yet.</p>'}
      </div>
    `;
  }

  window.generateTopicQuestions = async function(subject, topic, count) {
    const btn = event.target.closest('button');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...'; }
    
    const res = await api('/api/questions/generate/topic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subject, topic, target_count: count })
    });
    
    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Generate ' + count; }
    
    if (!res) { showToast('Generation failed', 'error'); return; }
    
    showToast('Generated ' + (res.generated?.length || 0) + ' questions', 'success');
    
    if (res.generated && res.generated.length) {
      // Show review modal
      showReviewModal(res.generated, subject, topic);
    } else {
      loadQuestionBank(subject, topic);
    }
  };

  window.generateSimilarSingle = async function(questionId) {
    if (!questionId) return;
    
    const res = await api('/api/questions/generate/similar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ source_question_id: questionId, count: 5 })
    });
    
    if (!res) { showToast('Generation failed', 'error'); return; }
    
    if (res.generated && res.generated.length) {
      showReviewModal(res.generated, '', '');
    } else {
      showToast('No new questions generated (too similar)', 'info');
    }
  };

  function showReviewModal(questions, subject, topic) {
    // Remove existing modal
    const existing = document.getElementById('review-modal');
    if (existing) existing.remove();
    
    const modal = document.createElement('div');
    modal.id = 'review-modal';
    modal.className = 'modal-backdrop';
    modal.innerHTML = `
      <div class="modal-content" style="max-width:800px;">
        <div class="modal-header">
          <h3 class="card-title"><i class="fa-solid fa-clipboard-check" style="color:var(--primary);"></i> Review Generated Questions</h3>
          <button class="btn btn-secondary btn-icon" onclick="this.closest('.modal-backdrop').classList.remove('open')"><i class="fa-solid fa-times"></i></button>
        </div>
        <div class="modal-body" style="max-height:70vh;overflow-y:auto;">
          ${questions.map((q, i) => `
            <div class="card" style="margin-bottom:1rem;padding:1rem;">
              <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">
                <strong style="font-size:0.85rem;">Q${i+1}: ${escapeHtml(q.question_text?.substring(0,80))}...</strong>
                <div style="display:flex;gap:0.3rem;">
                  <span class="badge badge-${diffBadge(q.difficulty || 'Medium')}">${q.difficulty || 'Medium'}</span>
                  <span class="badge badge-info">${q.question_type || 'Exam'}</span>
                  <span class="badge badge-primary">${q.marks || 5} marks</span>
                </div>
              </div>
              <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:0.5rem;">${escapeHtml(q.question_text || '')}</div>
              <div style="display:flex;gap:0.5rem;">
                <label style="display:flex;align-items:center;gap:0.3rem;font-size:0.8rem;cursor:pointer;"><input type="checkbox" class="review-checkbox" checked data-q='${escapeHtml(JSON.stringify(q))}'> Keep</label>
              </div>
            </div>
          `).join('')}
          <div style="display:flex;gap:0.5rem;justify-content:flex-end;margin-top:1rem;">
            <button class="btn btn-secondary" onclick="document.getElementById('review-modal').classList.remove('open')">Cancel</button>
            <button class="btn btn-primary" onclick="saveReviewedQuestions()"><i class="fa-solid fa-save"></i> Save Selected</button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
    // Force reflow then open
    requestAnimationFrame(() => modal.classList.add('open'));
  }

  window.saveReviewedQuestions = async function() {
    const checkboxes = document.querySelectorAll('.review-checkbox:checked');
    const selected = Array.from(checkboxes).map(cb => JSON.parse(cb.dataset.q));
    
    if (!selected.length) {
      showToast('No questions selected', 'error');
      return;
    }
    
    // Get subject/topic from first question or use modal context
    const firstQ = selected[0];
    const subject = firstQ.subject || '';
    const topic = firstQ.topic || '';
    
    if (!subject || !topic) {
      showToast('Subject/topic missing', 'error');
      return;
    }
    
    const res = await api('/api/questions/save-generated', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ questions: selected, subject, topic })
    });
    
    if (res && res.success) {
      showToast('Saved ' + res.count + ' questions to bank', 'success');
      document.getElementById('review-modal')?.classList.remove('open');
      if (subject && topic) loadQuestionBank(subject, topic);
    } else {
      showToast('Save failed', 'error');
    }
  };

  /* ===== ASSIGNMENT GENERATOR ===== */
  $('#btn-trigger-generate')?.addEventListener('click', async () => {
    const notebook = $('#gen-source-notebook')?.value || '';
    const subject = $('#gen-subject')?.value || '';
    const exam = $('#gen-target-exam')?.value || 'University End-Sem';
    const difficulty = $('#gen-difficulty')?.value || 'Intermediate';
    const numQ = parseInt($('#gen-num-q')?.value || '30');

    const btn = $('#btn-trigger-generate');
    if (btn) { btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...'; }

    const res = await api('/api/generator/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notebook_id: notebook, subject, semester: '1', difficulty, target_exam: exam, num_questions: numQ })
    });

    if (btn) { btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-bolt"></i> Generate Assignment'; }

    if (!res) { showToast('Generation failed', 'error'); return; }
    showToast('Generated: ' + res.title, 'success');
    renderGeneratedAssignment(res);
  });

  function renderGeneratedAssignment(ga) {
    const out = $('#generated-assignment-output');
    if (!out) return;
    out.style.display = 'block';
    out.innerHTML = `
      <div class="card">
        <div class="card-header"><h3 class="card-title"><i class="fa-solid fa-file-lines"></i> ${escapeHtml(ga.title||'Generated Assignment')}</h3>
        <span class="badge badge-primary">${ga.total_marks||0} marks &middot; ${ga.time_limit_mins||180}min</span></div>
        <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:1rem;">
          ${(ga.rubric||[]).map(r=>'<span class="badge badge-info">'+escapeHtml(r.criteria)+' ('+r.weight_pct+'%)</span>').join('')}
        </div>
        ${(ga.questions||[]).map(q=>`
          <div style="border:1px solid var(--border-color);border-radius:var(--radius-sm);padding:0.75rem;margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.25rem;">
              <strong style="font-size:0.85rem;">Q${q.num}: ${escapeHtml(q.topic||'')} <span class="badge badge-${diffBadge(q.bloom_level)}">${q.bloom_level||''}</span></strong>
              <span class="badge badge-primary">${q.marks||5} marks</span>
            </div>
            <div style="font-size:0.82rem;color:var(--text-secondary);">${escapeHtml(q.text||'')}</div>
            ${q.model_answer_summary ? `<div style="margin-top:0.35rem;font-size:0.75rem;color:var(--text-dim);"><strong>Model:</strong> ${escapeHtml(q.model_answer_summary.substring(0,200))}</div>` : ''}
          </div>
        `).join('')}
      </div>
    `;
  }

  /* ===== HELPER & GRADER ===== */
  $('#btn-hint-1')?.addEventListener('click', () => getHint(1));
  $('#btn-hint-2')?.addEventListener('click', () => getHint(2));
  $('#btn-hint-3')?.addEventListener('click', () => getHint(3));

  async function getHint(level) {
    const q = $('#help-question-input')?.value || '';
    if (!q) return;
    const res = await api('/api/help/hint', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_text: q, level })
    });
    if (!res) return;
    const box = $('#hint-display-box');
    if (box) box.style.display = 'block';
    const hdr = $('#hint-level-header');
    if (hdr) hdr.textContent = 'Hint Level ' + level;
    const body = $('#hint-body-text');
    if (body) body.innerHTML = res.hint_text || '';
  }

  $('#btn-grade-answer')?.addEventListener('click', async () => {
    const q = $('#help-question-input')?.value || '';
    const ans = $('#student-answer-input')?.value || '';
    if (!ans) return;
    const res = await api('/api/help/evaluate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question_text: q, student_answer: ans, total_marks: 10 })
    });
    if (!res) return;
    const box = $('#evaluation-results-box');
    if (!box) return;
    box.style.display = 'flex';
    box.innerHTML = `
      <div class="card" style="border-color:var(--primary);">
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:0.75rem;">
          <span style="font-size:1.5rem;font-weight:800;color:var(--primary);">${res.marks_awarded||0}</span>
          <span style="color:var(--text-muted);">/ ${res.total_marks||10} marks</span>
        </div>
        <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:0.75rem;">${escapeHtml(res.feedback_text||'')}</div>
        ${res.rubric_breakdown ? Object.entries(res.rubric_breakdown).map(([k,v])=>`<div style="display:flex;justify-content:space-between;font-size:0.78rem;padding:0.2rem 0;"><span>${k}</span><span style="color:var(--accent);">${v}</span></div>`).join('') : ''}
        ${(res.missing_points||[]).length ? `<div style="margin-top:0.5rem;font-size:0.78rem;color:var(--warning);">Missing: ${res.missing_points.join(', ')}</div>` : ''}
      </div>
    `;
  });

  /* ===== NOTES & FLASHCARDS ===== */
  async function refreshNotesSelects() {
    const data = await api('/api/notebooks');
    if (!data) return;
    const selects = ['#notes-notebook-select', '#quiz-notebook-select'];
    selects.forEach(sel => {
      const el = $(sel);
      if (!el) return;
      const cur = el.value;
      el.innerHTML = '<option value="">Select an uploaded notebook...</option>' +
        data.map(n => `<option value="${n.id}">${escapeHtml(n.original_name)}</option>`).join('');
      el.value = cur;
    });
  }

  async function refreshNotesView() {
    const data = await api('/api/notes');
    if (!data) return;
    const container = $('#study-notes-content');
    if (!container) return;
    if (!data.length) { container.innerHTML = '<p style="color:var(--text-dim);">No study notes yet. Generate from a notebook.</p>'; return; }
    container.innerHTML = data.map(n => `
      <div class="card">
        <div style="font-weight:700;margin-bottom:0.25rem;">${escapeHtml(n.subject)} — ${escapeHtml(n.topic)}</div>
        ${n.summary ? `<div style="font-size:0.82rem;color:var(--text-secondary);margin-bottom:0.4rem;">${escapeHtml(n.summary.substring(0,200))}</div>` : ''}
        ${n.flashcards && n.flashcards.length ? `<div style="font-size:0.78rem;color:var(--text-dim);">${n.flashcards.length} flashcards</div>` : ''}
      </div>
    `).join('');
  }

  $('#btn-generate-notes')?.addEventListener('click', async () => {
    const notebook = $('#notes-notebook-select')?.value || '';
    const topic = $('#notes-topic-input')?.value || '';
    if (!notebook) return;
    const res = await api('/api/notes/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notebook_id: notebook, topic, subject: 'General' })
    });
    if (!res) return;
    showToast('Study notes generated', 'success');
    refreshNotesView();
  });

  /* ===== FLASHCARDS ===== */
  $('#btn-fc-prev')?.addEventListener('click', () => flipFC(-1));
  $('#btn-fc-next')?.addEventListener('click', () => flipFC(1));

  function flipFC(dir) {
    const el = $('#flashcard-element');
    if (!el) return;
    el.classList.toggle('flipped');
    const total = state.flashcards.length || 1;
    const idx = (state.flashcards.findIndex(f => f.flipped) + dir + total) % total;
    updateFlashcard(idx);
  }

  function updateFlashcard(idx) {
    const fc = state.flashcards[idx];
    if (!fc) return;
    const front = $('#fc-front-text');
    const back = $('#fc-back-text');
    const hint = $('#fc-hint-text');
    const cat = $('#fc-category');
    if (front) front.textContent = fc.question || '';
    if (back) back.textContent = fc.answer || '';
    if (hint) hint.textContent = fc.hint || '';
    if (cat) cat.textContent = fc.category || 'Flashcard';
    const counter = $('#fc-counter');
    if (counter) counter.textContent = `Card ${idx+1} of ${state.flashcards.length || 1}`;
  }

  /* ===== QUIZ ===== */
  $('#btn-start-quiz')?.addEventListener('click', async () => {
    const notebook = $('#quiz-notebook-select')?.value || '';
    const topic = $('#quiz-topic-input')?.value || '';
    if (!notebook && !topic) return;
    const res = await api('/api/quiz/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notebook_id: notebook, topic, subject: 'General', num_questions: 5 })
    });
    if (!res) return;
    state.quizQuestions = res.questions || [];
    state.quizIndex = 0;
    state.quizScore = 0;
    renderQuizQuestion();
  });

  function renderQuizQuestion() {
    const box = $('#active-quiz-box');
    if (!box) return;
    const q = state.quizQuestions[state.quizIndex];
    if (!q) { renderQuizResults(); return; }
    box.style.display = 'block';
    box.innerHTML = `
      <div class="card">
        <div style="font-size:0.8rem;color:var(--text-dim);margin-bottom:0.3rem;">Question ${state.quizIndex+1} of ${state.quizQuestions.length} &middot; ${q.type||''} &middot; ${q.marks||5} marks</div>
        <div style="font-weight:700;margin-bottom:0.75rem;">${escapeHtml(q.text||'')}</div>
        ${(q.options||[]).map((opt,i)=>`
          <div class="quiz-option" onclick="selectQuizOption(${i})">
            <span class="opt-indicator">${String.fromCharCode(65+i)}</span>
            <span>${escapeHtml(opt)}</span>
          </div>
        `).join('')}
      </div>
    `;
  }

  window.selectQuizOption = function(idx) {
    const q = state.quizQuestions[state.quizIndex];
    if (!q) return;
    const correct = (q.correct_answer || '').toLowerCase();
    const selected = (q.options || [])[idx]?.toLowerCase() || '';
    const isCorrect = correct === selected;
    if (isCorrect) state.quizScore += (q.marks || 5);

    $$('.quiz-option').forEach((el, i) => {
      if ((q.options||[])[i]?.toLowerCase() === correct) el.classList.add('correct');
      else if (i === idx && !isCorrect) el.classList.add('wrong');
      el.style.pointerEvents = 'none';
    });

    setTimeout(() => {
      state.quizIndex++;
      renderQuizQuestion();
    }, 1200);
  };

  function renderQuizResults() {
    const box = $('#active-quiz-box');
    const resBox = $('#quiz-results-box');
    if (box) box.style.display = 'none';
    if (!resBox) return;
    resBox.style.display = 'flex';
    const total = state.quizQuestions.reduce((s,q) => s + (q.marks||5), 0);
    const pct = total > 0 ? Math.round((state.quizScore / total) * 100) : 0;
    resBox.innerHTML = `
      <div class="card" style="text-align:center;padding:var(--space-6);">
        <div style="font-size:2.5rem;font-weight:800;color:var(--primary);">${pct}%</div>
        <div style="color:var(--text-muted);margin-top:0.25rem;">${state.quizScore} / ${total} marks</div>
        <div class="progress-bar" style="margin-top:1rem;"><div class="progress-bar-fill" style="width:${pct}%;"></div></div>
      </div>
    `;
    state.quizQuestions = [];
  }

  /* ===== CHAT ===== */
  async function sendChatMessage() {
    const input = $('#chat-input-field');
    const msg = input?.value?.trim();
    if (!msg) return;
    const container = $('#chat-messages-container');
    if (!container) return;

    container.innerHTML += `<div class="chat-bubble user">${escapeHtml(msg)}</div>`;
    if (input) input.value = '';
    container.scrollTop = container.scrollHeight;

    const res = await api('/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg })
    });

    if (res && res.response) {
      container.innerHTML += `<div class="chat-bubble assistant"><div style="font-weight:700;color:var(--accent);margin-bottom:0.25rem;"><i class="fa-solid fa-graduation-cap"></i> Antigravity Academic AI</div><div>${escapeHtml(res.response)}</div>${(res.citations||[]).map(c=>`<div class="citation-chip"><i class="fa-solid fa-book"></i> ${escapeHtml(c.doc_name||'')} (${escapeHtml(c.page_or_sec||'')})</div>`).join('')}</div>`;
    } else {
      container.innerHTML += `<div class="chat-bubble assistant"><div style="font-weight:700;color:var(--accent);margin-bottom:0.25rem;"><i class="fa-solid fa-graduation-cap"></i> Antigravity Academic AI</div><div>Sorry, I couldn't process your question right now.</div></div>`;
    }
    container.scrollTop = container.scrollHeight;
  }

  $('#btn-send-chat')?.addEventListener('click', sendChatMessage);
  $('#chat-input-field')?.addEventListener('keydown', e => { if (e.key === 'Enter') sendChatMessage(); });

  /* ===== MODAL ===== */
  $('#header-action-btn')?.addEventListener('click', () => {
    $('#new-assignment-modal')?.classList.add('open');
  });
  $('#btn-close-modal')?.addEventListener('click', () => {
    $('#new-assignment-modal')?.classList.remove('open');
  });
  $('#btn-modal-cancel')?.addEventListener('click', () => {
    $('#new-assignment-modal')?.classList.remove('open');
  });
  $('#new-assignment-modal')?.addEventListener('click', (e) => {
    if (e.target === $('#new-assignment-modal')) $('#new-assignment-modal')?.classList.remove('open');
  });

  $('#btn-modal-save')?.addEventListener('click', async () => {
    const title = $('#modal-title')?.value || '';
    const college = $('#modal-college')?.value || 'University';
    const subject = $('#modal-subject')?.value || 'General';
    const semester = $('#modal-semester')?.value || '1';
    const year = $('#modal-year')?.value || new Date().getFullYear();
    const difficulty = $('#modal-difficulty')?.value || 'Intermediate';
    const tags = $('#modal-tags')?.value || '';
    const content = $('#modal-content')?.value || '';

    if (!title) { showToast('Title is required', 'error'); return; }

    const res = await api('/api/assignments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title, college, department: '', subject, course_code: '', semester, academic_year: year, topic_tags: tags.split(',').map(t=>t.trim()).filter(Boolean), difficulty, due_date: '', status: 'Pending', content_text: content, questions: [], attachments: [], is_pyq: 0, source_url: '' })
    });
    if (res) {
      $('#new-assignment-modal')?.classList.remove('open');
      showToast('Assignment saved', 'success');
      renderAssignments();
      refreshBadges();
    }
  });

  /* ===== EXPORT ===== */
  $('#btn-export-repository').addEventListener('click', () => {
    // Use existing POST endpoint with correct payload, download markdown
    fetch('/api/assignments/batch-export', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ format: 'markdown', assignment_ids: [] })
    }).then(r => r.blob()).then(blob => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href = url; a.download = 'assignments.md'; a.click();
      showToast('Export downloaded', 'success');
    }).catch(() => showToast('Export failed', 'error'));
  });
  $('#btn-export-notes')?.addEventListener('click', async () => {
    const data = await api('/api/notes');
    if (!data) return;
    const md = data.map(n => `## ${n.subject} — ${n.topic}\n${n.summary}\n`).join('\n---\n');
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a'); a.href = url; a.download = 'study-notes.md'; a.click();
  });

  /* ===== THEME TOGGLE ===== */
  $('#theme-toggle-btn')?.addEventListener('click', () => {
    const next = state.theme === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    const icon = $('#theme-toggle-btn i');
    if (icon) icon.className = next === 'dark' ? 'fa-solid fa-moon' : 'fa-solid fa-sun';
  });

  /* ===== UTILS ===== */
  function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function debounce(fn, ms) {
    let t; return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  }

  function showToast(msg, type = 'info') {
    let container = $('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3500);
  }

  async function loadRecommendations() {
    const data = await api('/api/recommendations');
    if (!data) return;
    const container = $('#recommendations-content');
    if (!container) return;
    
    let html = '';
    if (data.weak_topics_to_review && data.weak_topics_to_review.length) {
      html += `<div style="padding:0.75rem;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:var(--radius-sm);"><strong style="color:var(--danger);">Weak Topics to Review:</strong>`;
      html += data.weak_topics_to_review.map(t => `<div style="font-size:0.85rem;margin-top:0.25rem;"><strong>${escapeHtml(t.topic)}</strong> — Avg Score: ${t.avg_score || 0}% (${t.attempts || 0} attempts)</div>`).join('');
      html += `</div>`;
    }
    if (data.next_to_study && data.next_to_study.length) {
      html += `<div style="padding:0.75rem;background:rgba(8,145,178,0.1);border:1px solid rgba(8,145,178,0.3);border-radius:var(--radius-sm);margin-top:0.75rem;"><strong style="color:var(--accent);">Next to Study:</strong>`;
      html += data.next_to_study.map(t => `<div style="font-size:0.85rem;margin-top:0.25rem;"><strong>${escapeHtml(t.topic_name)}</strong> (${escapeHtml(t.course_code)})</div>`).join('');
      html += `</div>`;
    }
    if (data.suggested_review && data.suggested_review.length) {
      html += `<div style="padding:0.75rem;background:rgba(5,150,105,0.1);border:1px solid rgba(5,150,105,0.3);border-radius:var(--radius-sm);margin-top:0.75rem;"><strong style="color:var(--success);">Suggested Review:</strong>`;
      html += data.suggested_review.map(t => `<div style="font-size:0.85rem;margin-top:0.25rem;"><strong>${escapeHtml(t.topic)}</strong> (${escapeHtml(t.subject || '')}) — Completed</div>`).join('');
      html += `</div>`;
    }
    container.innerHTML = html || '<p style="color:var(--text-dim);">No recommendations yet. Take a quiz to get personalized study suggestions.</p>';
  }

  window.openAssignmentDetail = async function(id) {
    const a = state.assignments.find(x => x.id === id);
    if (!a) {
      // Fetch from API if not in current view
      const res = await api('/api/assignments/' + id);
      if (!res) return;
      openAssignmentDetailFromData(res);
      return;
    }
    openAssignmentDetailFromData(a);
  };

  function openAssignmentDetailFromData(a) {
    const modal = document.getElementById('assignment-detail-modal');
    if (!modal) {
      // Create modal if missing
      const div = document.createElement('div');
      div.className = 'modal-backdrop';
      div.id = 'assignment-detail-modal';
      div.innerHTML = `
        <div class="modal-content" style="max-width:720px;">
          <div class="modal-header">
            <h3 class="card-title" id="ad-title"></h3>
            <button class="btn btn-secondary btn-icon" onclick="document.getElementById('assignment-detail-modal').classList.remove('open')"><i class="fa-solid fa-times"></i></button>
          </div>
          <div class="modal-body" id="ad-body"></div>
        </div>`;
      document.body.appendChild(div);
    }
    const m = document.getElementById('assignment-detail-modal');
    m.classList.add('open');
    document.getElementById('ad-title').textContent = a.title || 'Assignment Details';
    const questions = (a.questions || []).map(q => `
      <div style="border:1px solid var(--border-color);border-radius:var(--radius-sm);padding:0.75rem;margin-bottom:0.5rem;">
        <strong style="font-size:0.85rem;">Q${q.num || ''}: ${escapeHtml(q.topic || '')}</strong> <span class="badge badge-primary">${q.marks || 5} marks</span>
        <div style="font-size:0.82rem;color:var(--text-secondary);margin-top:0.25rem;">${escapeHtml(q.text || '')}</div>
        ${q.model_answer_summary ? `<div style="font-size:0.75rem;color:var(--text-dim);margin-top:0.25rem;"><strong>Model Answer:</strong> ${escapeHtml(q.model_answer_summary.substring(0,200))}</div>` : ''}
      </div>`).join('');
    document.getElementById('ad-body').innerHTML = `
      <div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.75rem;">
        <span class="badge badge-primary">${escapeHtml(a.college||'')}</span>
        <span class="badge badge-info">${escapeHtml(a.subject||'')}</span>
        <span class="badge badge-success">Sem ${a.semester||''}</span>
        <span class="badge badge-warning">${a.academic_year||''}</span>
        <span class="badge badge-danger">${escapeHtml(a.difficulty||'Intermediate')}</span>
      </div>
      <div style="font-size:0.85rem;color:var(--text-secondary);margin-bottom:0.5rem;"><strong>Status:</strong> ${a.status||'Pending'} | <strong>Tags:</strong> ${(a.topic_tags||[]).join(', ')}</div>
      <h4 style="margin-bottom:0.5rem;color:var(--text-main);">Questions (${(a.questions||[]).length})</h4>
      ${questions || '<p style="color:var(--text-dim);">No questions shown.</p>'}
      <div style="margin-top:1rem;display:flex;gap:0.5rem;">
        <button class="btn btn-info btn-sm" onclick="showToast('AI assistance coming for this assignment', 'info')"><i class="fa-solid fa-robot"></i> AI Help</button>
        <button class="btn btn-secondary btn-sm" onclick="window.open('/api/assignments/batch-export?format=markdown','_blank')"><i class="fa-solid fa-download"></i> Export PDF</button>
      </div>`;
  }

  /* ===== INIT ===== */
  async function init() {
    await refreshBadges();
    await loadStatus();
    refreshNotesSelects();
    setupDropzone();
    loadViewData('repository');
  }

  init();
});