let currentTemplate = 'runner';

document.addEventListener('DOMContentLoaded', () => {
    refreshTrends();
    log("Dashboard Ready.", "system");
});

function selectTemplate(template, element) {
    currentTemplate = template;

    // UI 업데이트
    document.querySelectorAll('.template-card').forEach(el => el.classList.remove('selected'));
    element.classList.add('selected');

    log(`Template selected: ${template}`, "system");
}

async function refreshTrends() {
    const container = document.getElementById('trend-cloud');
    container.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const response = await fetch('/api/trends');
        const data = await response.json();

        container.innerHTML = '';
        data.keywords.forEach(kw => {
            const tag = document.createElement('div');
            tag.className = 'trend-tag';
            tag.textContent = `#${kw.text}`;
            tag.style.fontSize = `${0.8 + (kw.value / 100)}rem`; // 점수에 따른 크기 조절
            tag.onclick = () => {
                document.getElementById('gameConcept').value += ` #${kw.text}`;
                log(`Added keyword #${kw.text} to concept`, "system");
            };
            container.appendChild(tag);
        });

        log("Trend data refreshed.", "success");
    } catch (error) {
        log("Failed to fetch trends.", "error");
        container.innerHTML = 'Error loading trends.';
    }
}

async function startManufacture() {
    const name = document.getElementById('gameName').value.trim();
    const concept = document.getElementById('gameConcept').value.trim();

    if (!name) {
        alert("Please enter a Project Name!");
        return;
    }

    log(`Initializing production sequence for: ${name}...`, "system");

    const btn = document.querySelector('.action-btn.primary');
    const originalText = btn.innerText;
    btn.innerText = "MANUFACTURING...";
    btn.disabled = true;

    try {
        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                game_name: name,
                template: currentTemplate,
                concept: concept
            })
        });

        const result = await response.json();

        if (response.ok) {
            log(`SUCCESS: Game created at ${result.details.gdd_path}`, "success");
            log(`Command: python cli.py new ${name} --template ${currentTemplate}`, "system");
        } else {
            log(`ERROR: ${result.detail}`, "error");
        }
    } catch (error) {
        log(`CRITICAL FAIL: ${error.message}`, "error");
    } finally {
        setTimeout(() => {
            btn.innerText = originalText;
            btn.disabled = false;
        }, 1000);
    }
}

function log(message, type = "system") {
    const consoleEl = document.getElementById('log-console');
    const line = document.createElement('div');
    line.className = `log-line ${type}`;

    const time = new Date().toLocaleTimeString();
    line.innerText = `[${time}] ${message}`;

    consoleEl.insertBefore(line, consoleEl.firstChild);
}
