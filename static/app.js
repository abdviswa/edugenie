const task = document.getElementById('task');
const inputText = document.getElementById('inputText');
const inputLabel = document.getElementById('inputLabel');
const submitBtn = document.getElementById('submitBtn');
const result = document.getElementById('result');
const resultTitle = document.getElementById('resultTitle');
const copyBtn = document.getElementById('copyBtn');
const levelRow = document.getElementById('levelRow');
const level = document.getElementById('level');
const statusPill = document.getElementById('statusPill');

const config = {
  qa: { label: 'Your question', placeholder: 'Example: Which is the largest ocean?', button: 'Ask EduGenie', title: 'Answer' },
  explain: { label: 'Topic to explain', placeholder: 'Example: Explain the Pythagoras theorem', button: 'Explain Topic', title: 'Explanation' },
  quiz: { label: 'Passage or topic', placeholder: 'Paste a study passage or describe a topic for the quiz.', button: 'Generate Quiz', title: 'Practice Quiz' },
  summarize: { label: 'Text to summarize', placeholder: 'Paste a long educational passage here.', button: 'Summarize', title: 'Quick Revision' },
  learn: { label: 'Topic to learn', placeholder: 'Example: SQL', button: 'Build Learning Path', title: 'Learning Path' }
};

function refreshForm() {
  const c = config[task.value];
  inputLabel.textContent = c.label;
  inputText.placeholder = c.placeholder;
  submitBtn.textContent = c.button;
  levelRow.hidden = task.value !== 'learn';
}

task.addEventListener('change', refreshForm);
refreshForm();

async function checkHealth() {
  try {
    const r = await fetch('/health');
    const data = await r.json();
    statusPill.textContent = data.gemini_configured ? `AI ready · ${data.model}` : 'API key required';
  } catch { statusPill.textContent = 'Backend offline'; }
}
checkHealth();

function showText(text) {
  result.className = 'result-body';
  result.textContent = text;
  copyBtn.hidden = false;
}

function showQuiz(data) {
  result.className = 'result-body';
  result.innerHTML = data.questions.map((q, i) => `
    <div class="quiz-q">
      <h3>${i + 1}. ${escapeHtml(q.question)}</h3>
      ${q.options.map(o => `<div class="option ${o === q.correct_answer ? 'correct' : ''}">${escapeHtml(o)}</div>`).join('')}
      <div class="explanation"><strong>Answer:</strong> ${escapeHtml(q.correct_answer)}<br>${escapeHtml(q.explanation)}</div>
    </div>`).join('');
  copyBtn.hidden = true;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
}

submitBtn.addEventListener('click', async () => {
  const value = inputText.value.trim();
  if (!value) { inputText.focus(); return; }

  const current = task.value;
  const endpoint = current === 'learn' ? '/learn/recommendations' : `/${current}`;
  const body = current === 'learn' ? { topic: value, level: level.value } : { text: value };

  submitBtn.disabled = true;
  submitBtn.textContent = 'Thinking…';
  resultTitle.textContent = config[current].title;
  result.className = 'result-body empty';
  result.textContent = 'EduGenie is preparing your response…';
  copyBtn.hidden = true;

  try {
    const response = await fetch(endpoint, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Request failed');
    if (current === 'quiz') showQuiz(data);
    else showText(data.answer || data.explanation || data.summary || data.recommendations || 'No response received.');
  } catch (error) {
    showText(`Error: ${error.message}`);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = config[current].button;
  }
});

copyBtn.addEventListener('click', async () => {
  await navigator.clipboard.writeText(result.innerText);
  copyBtn.textContent = 'Copied';
  setTimeout(() => copyBtn.textContent = 'Copy', 1200);
});
