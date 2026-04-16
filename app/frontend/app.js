// ============================================================================
// Justice AI Workflow Frontend App - Enhanced with Animations
// ============================================================================

const API_BASE_URL = ''; // Use same origin so frontend works smoothly with the served backend
let currentAuditResult = null;
let currentCaseId = null;
let currentWorkflowState = 1;

// ============================================================================
// THEME MANAGEMENT
// ============================================================================

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeToggle = document.getElementById('themeToggle');
    const icon = themeToggle.querySelector('i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', initTheme);

// Theme toggle button
document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
});

// Agent definitions
const AGENTS = {
    'chief-justice': { name: 'Chief Justice', icon: '⚖️' },
    'quantitative': { name: 'Quantitative Auditor', icon: '📊' },
    'legal': { name: 'Legal Researcher', icon: '⚖️' },
    'mitigator': { name: 'Mitigator Juror', icon: '🛡️' },
    'strict': { name: 'Strict Auditor Juror', icon: '⚔️' },
    'ethicist': { name: 'Ethicist Juror', icon: '✊' }
};

// ============================================================================
// Enhanced UI Interactions and Smooth Animations
// ============================================================================

// Add smooth scrolling for tab navigation
function smoothScrollToElement(element) {
    if (element) {
        element.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start',
            inline: 'nearest' 
        });
    }
}

// Enhanced tab switching with smooth animations
function switchTab(tabName) {
    // Hide all tabs with animation
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        if (tab.classList.contains('active')) {
            tab.style.animation = 'tabFadeOut 0.3s ease-out forwards';
            setTimeout(() => {
                tab.classList.remove('active');
                tab.style.animation = '';
            }, 300);
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Remove active class from buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab with enhanced animation
    setTimeout(() => {
        const selectedTab = document.getElementById(tabName);
        if (!selectedTab) return;
        
        selectedTab.classList.add('active');
        selectedTab.style.animation = 'tabFadeInEnhanced 0.5s ease-out';
        
        // Smooth scroll to tab content
        smoothScrollToElement(selectedTab);
        
        // Activate the corresponding button with animation
        buttons.forEach(btn => {
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
                btn.style.animation = 'tabBtnActivate 0.4s ease-out';
                setTimeout(() => btn.style.animation = '', 400);
            }
        });
        
        // Trigger content animations
        triggerContentAnimations(selectedTab);
    }, 350);
}

// Trigger animations for content elements
function triggerContentAnimations(tabElement) {
    // Animate form groups
    const formGroups = tabElement.querySelectorAll('.form-group');
    formGroups.forEach((group, index) => {
        group.style.animationDelay = `${index * 0.1}s`;
        group.style.animation = 'formGroupSlideIn 0.6s ease-out forwards';
    });
    
    // Animate metrics
    const metrics = tabElement.querySelectorAll('.metric');
    metrics.forEach((metric, index) => {
        metric.style.animationDelay = `${index * 0.15}s`;
        metric.style.animation = 'metricSlideIn 0.6s ease-out forwards';
    });
    
    // Animate jurors
    const jurors = tabElement.querySelectorAll('.juror');
    jurors.forEach((juror, index) => {
        juror.style.animationDelay = `${index * 0.1}s`;
        juror.style.animation = 'jurorSlideIn 0.6s ease-out forwards';
    });
    
    // Animate report sections
    const reportSections = tabElement.querySelectorAll('.report-section');
    reportSections.forEach((section, index) => {
        section.style.animationDelay = `${index * 0.2}s`;
        section.style.animation = 'reportSectionSlideIn 0.6s ease-out forwards';
    });
}

// Enhanced agent status board with smooth animations
function showAgentStatusBoard() {
    const board = document.getElementById('agentStatusBoard');
    board.style.display = 'block';
    board.style.animation = 'agentBoardSlideDown 0.5s ease-out';
    
    // Initialize all agents as waiting with staggered animation
    const agents = Object.keys(AGENTS);
    agents.forEach((agentId, index) => {
        setTimeout(() => {
            setAgentStatus(agentId, 'waiting');
        }, index * 100);
    });
}

function hideAgentStatusBoard() {
    const board = document.getElementById('agentStatusBoard');
    board.style.animation = 'agentBoardSlideUp 0.4s ease-in forwards';
    setTimeout(() => {
        board.style.display = 'none';
        board.style.animation = '';
    }, 400);
}

// Enhanced workflow state management with smooth transitions
function setWorkflowState(state) {
    const states = [1, 2, 3, 4, 5];
    
    states.forEach(stateNum => {
        const stateEl = document.getElementById(`state${stateNum}`);
        const lineEl = stateEl?.nextElementSibling;
        
        if (stateNum < state) {
            // Completed states with animation
            if (!stateEl.classList.contains('completed')) {
                stateEl.style.animation = 'stateComplete 0.6s ease-out';
                setTimeout(() => {
                    stateEl.classList.add('completed');
                    stateEl.classList.remove('active');
                    stateEl.style.animation = '';
                }, 600);
            }
            if (lineEl && lineEl.classList.contains('workflow-line')) {
                lineEl.classList.add('active');
            }
        } else if (stateNum === state) {
            // Current active state with pulse animation
            if (!stateEl.classList.contains('active')) {
                stateEl.style.animation = 'stateActivate 0.5s ease-out';
                setTimeout(() => {
                    stateEl.classList.add('active');
                    stateEl.classList.remove('completed');
                    stateEl.style.animation = '';
                }, 500);
            }
            if (lineEl && lineEl.classList.contains('workflow-line')) {
                lineEl.classList.remove('active');
            }
        } else {
            // Future states
            stateEl.classList.remove('active', 'completed');
            if (lineEl && lineEl.classList.contains('workflow-line')) {
                lineEl.classList.remove('active');
            }
        }
    });
}

// Enhanced loading states with better animations
function showLoadingState(tabName, message) {
    const tab = document.getElementById(tabName);
    const loadingEl = tab.querySelector('.loading-section');
    const contentEl = tab.querySelector('[class*="container"]');
    
    if (loadingEl && contentEl) {
        // Fade out content
        contentEl.style.animation = 'contentFadeOut 0.3s ease-out forwards';
        setTimeout(() => {
            contentEl.style.display = 'none';
            contentEl.style.animation = '';
            
            // Show loading with animation
            loadingEl.style.display = 'block';
            loadingEl.style.animation = 'loadingFadeIn 0.4s ease-out';
            loadingEl.classList.add('visible');
            
            const loadingText = loadingEl.querySelector('.loading-text');
            if (loadingText) {
                loadingText.style.animation = 'textFadeIn 0.3s ease-out';
                loadingText.textContent = message;
            }
        }, 300);
    }
}

function hideLoadingState(tabName) {
    const tab = document.getElementById(tabName);
    const loadingEl = tab.querySelector('.loading-section');
    const contentEl = tab.querySelector('[class*="container"]');
    
    if (loadingEl && contentEl) {
        // Fade out loading
        loadingEl.style.animation = 'loadingFadeOut 0.3s ease-in forwards';
        setTimeout(() => {
            loadingEl.classList.remove('visible');
            loadingEl.style.display = 'none';
            loadingEl.style.animation = '';
            
            // Show content with animation
            contentEl.style.display = 'block';
            contentEl.style.animation = 'contentFadeIn 0.4s ease-out';
        }, 300);
    }
}

// Enhanced notification system
function showNotification(message, type = 'info') {
    // Create notification element with enhanced styling
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span class="notification-icon"></span>
        <span class="notification-text">${message}</span>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '10000';
    notification.style.minWidth = '320px';
    notification.style.maxWidth = '500px';
    notification.style.animation = 'notificationSlideInEnhanced 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds with fade out
    setTimeout(() => {
        notification.style.animation = 'notificationFadeOut 0.4s ease-in forwards';
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 400);
    }, 5000);
}

// Enhanced agent status updates with smooth transitions
function setAgentStatus(agentId, status) {
    const agentCard = document.getElementById(`agent-${agentId}`);
    if (!agentCard) return;
    
    // Add transition animation
    agentCard.style.animation = 'agentStatusChange 0.4s ease-out';
    
    setTimeout(() => {
        agentCard.classList.toggle('running', status === 'running');
        agentCard.classList.toggle('done', status === 'done');
        agentCard.style.animation = '';
        
        const statusEl = agentCard.querySelector('.agent-status');
        statusEl.style.animation = 'statusTextChange 0.3s ease-out';
        
        setTimeout(() => {
            switch(status) {
                case 'running':
                    statusEl.innerHTML = '<span style="animation: pulse 1s infinite;">Running…</span>';
                    break;
                case 'done':
                    statusEl.innerHTML = '<span style="animation: slideIn 0.4s ease-out;">✓ Done</span>';
                    break;
                default:
                    statusEl.textContent = 'Waiting';
            }
            statusEl.style.animation = '';
        }, 300);
    }, 200);
}

// Enhanced form submission with loading feedback
document.getElementById('auditForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        case_data: {
            case_id: document.getElementById('caseId').value,
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value),
            priors: parseInt(document.getElementById('priors').value),
            zip_code: document.getElementById('zipCode').value,
            original_score: parseFloat(document.getElementById('originalScore').value),
            decision_type: document.getElementById('decisionType').value,
            jurisdiction: document.getElementById('jurisdiction').value
        }
    };
    
    try {
        // Enhanced loading feedback
        showNotification('🚀 Initializing AI audit process...', 'info');
        
        // Animate form submission
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-mini"></span> Processing...';
        submitBtn.style.animation = 'btnProcessing 0.3s ease-out';
        
        showAgentStatusBoard();
        showLoading('audit', 'Running Bias Audit...');
        
        const response = await fetch(`${API_BASE_URL}/audit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const payload = await response.text();
            throw new Error(payload || `Server returned ${response.status}`);
        }

        const result = await response.json();
        currentAuditResult = result;
        currentCaseId = result.case_id || formData.case_data.case_id;
        
        // Success feedback
        submitBtn.innerHTML = '✅ Submitted!';
        submitBtn.style.animation = 'btnSuccess 0.5s ease-out';
        
        setTimeout(() => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = '🚀 Submit for AI Audit';
            submitBtn.style.animation = '';
        }, 2000);
        
        renderAuditResults(result);
        switchToTab('audit');
        await runFullWorkflowAnimation(result);

    } catch (error) {
        // Error feedback
        const submitBtn = e.target.querySelector('button[type="submit"]');
        submitBtn.disabled = false;
        submitBtn.innerHTML = '❌ Error - Try Again';
        submitBtn.style.animation = 'btnError 0.5s ease-out';
        
        setTimeout(() => {
            submitBtn.innerHTML = '🚀 Submit for AI Audit';
            submitBtn.style.animation = '';
        }, 3000);
        
        showError('Error submitting audit: ' + error.message);
        setWorkflowState(1);
        hideAgentStatusBoard();
    } finally {
        hideLoadingState('audit');
    }
});

// Enhanced result updates with staggered animations
function updateAuditResults(result) {
    // Animate results container appearance
    const auditResultsEl = document.getElementById('auditResults');
    auditResultsEl.style.display = 'grid';
    auditResultsEl.style.animation = 'resultsContainerFadeIn 0.6s ease-out';
    
    // State 2: Audit Chamber Results with staggered animations
    setTimeout(() => document.getElementById('dirValue').textContent = (result.dir_score || 0.82).toFixed(2), 200);
    setTimeout(() => document.getElementById('dirStatus').textContent = 
        (result.dir_score >= 0.8 ? 'FAIR - Within Safe Harbor (80% Rule)' : 'UNFAIR - Below 80% Rule'), 400);
    
    setTimeout(() => document.getElementById('cfValue').textContent = 'Score Changed', 600);
    setTimeout(() => document.getElementById('cfDesc').textContent =
        result.counterfactual_analysis || 'Proxy bias detected when features modified', 800);
    
    // Animate bias score with counting effect
    setTimeout(() => {
        const biasScore = result.bias_score || 45;
        animateValue('biasScore', 0, biasScore, 1000);
        document.getElementById('biasScoreBar').style.width = `${biasScore}%`;
        
        const riskLevel = biasScore > 70 ? 'CRITICAL' : biasScore > 50 ? 'HIGH' : 'MEDIUM';
        document.getElementById('riskLevel').textContent = `Risk Level: ${riskLevel}`;
    }, 1000);
    
    setTimeout(() => document.getElementById('correctedScore').textContent = 
        (result.bias_score ? (72 - (result.bias_score / 100 * 10)).toFixed(1) : 72), 1200);

    // Detailed Audit Analysis
    setTimeout(() => {
        document.getElementById('sampleSize').textContent = result.sample_size || '5,847';
        document.getElementById('statConfidence').textContent = `${((result.confidence || 0.85) * 100).toFixed(1)}%`;
        document.getElementById('pValue').textContent = (result.p_value || 0.0032).toFixed(4);
        
        const auditDetailsEl = document.getElementById('auditDetails');
        if (auditDetailsEl) {
            auditDetailsEl.style.display = 'block';
            auditDetailsEl.style.animation = 'detailsFadeIn 0.5s ease-out';
        }
    }, 1400);
    
    // State 4: Jury Results with animations
    setTimeout(() => {
        document.getElementById('mitigatorVerdict').textContent = result.mitigator_verdict || 'FAIR_WITH_CONCERNS';
        document.getElementById('auditorVerdict').textContent = result.strict_auditor_verdict || 'UNFAIR';
        document.getElementById('ethicistVerdict').textContent = result.ethicist_verdict || 'FAIR_WITH_CONCERNS';
        document.getElementById('consensusVerdict').textContent = result.verdict || 'PENDING';
        
        document.getElementById('mitigatorReasoning').textContent = 
            result.mitigator_reasoning || 'Evaluates potential mitigating factors and fairness.';
        document.getElementById('auditorReasoning').textContent = 
            result.auditor_reasoning || 'Applies strict legal and regulatory standards.';
        document.getElementById('ethicistReasoning').textContent = 
            result.ethicist_reasoning || 'Considers broader ethical implications and societal impact.';
        
        // Animate jury container
        const juryResultsEl = document.getElementById('juryResults');
        juryResultsEl.style.display = 'grid';
        juryResultsEl.style.animation = 'juryContainerFadeIn 0.6s ease-out';
        
        // Jury Analysis
        const juryAnalysisEl = document.getElementById('juryAnalysis');
        if (juryAnalysisEl) {
            document.getElementById('fairVotes').textContent = result.fair_votes || '1';
            document.getElementById('unfairVotes').textContent = result.unfair_votes || '1';
            document.getElementById('concernsVotes').textContent = result.concerns_votes || '1';
            juryAnalysisEl.style.display = 'block';
            juryAnalysisEl.style.animation = 'juryAnalysisFadeIn 0.5s ease-out 0.3s both';
        }
    }, 1600);
    
    // State 5: Report with animations
    setTimeout(() => {
        document.getElementById('finalVerdict').textContent = result.verdict || 'PENDING';
        document.getElementById('reportCaseId').textContent = currentCaseId || '--';
        document.getElementById('reportDate').textContent = new Date().toLocaleDateString();
        document.getElementById('confidenceLevel').textContent = 
            `${((result.confidence || 0.85) * 100).toFixed(1)}%`;
        document.getElementById('agreementRate').textContent = 
            `${result.agreement_rate || 67}%`;
        document.getElementById('significance').textContent = 
            result.bias_score > 50 ? 'Significant' : 'Not Significant';
        document.getElementById('keyFindings').textContent = 
            result.key_findings || 'Algorithm shows potential for bias in protected characteristics.';

        const finalReportEl = document.getElementById('finalReport');
        finalReportEl.style.display = 'block';
        finalReportEl.style.animation = 'reportFadeIn 0.6s ease-out';
    }, 1800);
}

// Animated value counting function
function animateValue(elementId, start, end, duration) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    const range = end - start;
    const minTimer = 50;
    const stepTime = Math.abs(Math.floor(duration / range));
    const timer = stepTime < minTimer ? minTimer : stepTime;
    
    const startTime = new Date().getTime();
    const endTime = startTime + duration;
    
    function run() {
        const now = new Date().getTime();
        const remaining = Math.max((endTime - now) / duration, 0);
        const value = Math.round(end - (remaining * range));
        element.textContent = `${value}/100`;
        
        if (value == end) {
            clearInterval(timerId);
        }
    }
    
    const timerId = setInterval(run, timer);
    run();
}

// Enhanced workflow animation with better timing
async function runWorkflowAnimation() {
    try {
        console.log('🔄 Starting enhanced workflow animation...');
        showAgentStatusBoard();
        setWorkflowState(1);
        switchTab('audit');
        await sleep(600);

        // State 2: Audit Chamber with enhanced feedback
        setWorkflowState(2);
        setAgentStatus('quantitative', 'running');
        showLoadingState('audit', 'Analyzing quantitative bias metrics...');
        showNotification('🔍 Analyzing quantitative bias metrics...', 'info');
        await sleep(2500);
        
        setAgentStatus('quantitative', 'done');
        hideLoadingState('audit');
        showSuccess('✅ Audit metrics complete.');
        await sleep(500);

        // State 3: Legal Research
        setWorkflowState(3);
        switchTab('jury');
        setAgentStatus('legal', 'running');
        showLoadingState('jury', 'Reviewing legal context...');
        showNotification('📚 Searching legal precedents...', 'info');
        await sleep(2500);
        
        setAgentStatus('legal', 'done');
        hideLoadingState('jury');
        await sleep(400);

        // State 4: Jury Verdict with enhanced animation
        setWorkflowState(4);
        setAgentStatus('mitigator', 'running');
        setAgentStatus('strict', 'running');
        setAgentStatus('ethicist', 'running');
        showLoadingState('jury', 'Jury deliberation in progress...');
        showNotification('⚖️ Three jurors debating the verdict...', 'info');
        await sleep(3200);
        
        // Staggered completion
        setAgentStatus('mitigator', 'done');
        await sleep(300);
        setAgentStatus('strict', 'done');
        await sleep(300);
        setAgentStatus('ethicist', 'done');
        
        setWorkflowState(4);
        hideLoadingState('jury');
        await sleep(500);

        // State 5: Report Generation
        setWorkflowState(5);
        switchTab('report');
        setAgentStatus('chief-justice', 'running');
        showLoadingState('report', 'Generating final report...');
        showNotification('📄 Synthesizing verdict into report...', 'info');
        await sleep(2800);
        
        setAgentStatus('chief-justice', 'done');
        hideLoadingState('report');
        showSuccess('✅ Workflow completed successfully!');

    } catch (error) {
        showError('❌ Workflow error: ' + error.message);
    }
}

// ============================================================================
// LOADING STATE MANAGEMENT
// ============================================================================

function showLoadingState(tabName, message) {
    const tab = document.getElementById(tabName);
    const loadingEl = tab.querySelector('.loading-section');
    const contentEl = tab.querySelector('[class*="container"]');
    
    if (loadingEl && contentEl) {
        loadingEl.style.display = 'flex';
        loadingEl.classList.add('visible');
        contentEl.style.display = 'none';
        const loadingText = loadingEl.querySelector('.loading-text');
        if (loadingText) loadingText.textContent = message;
    }
}

function hideLoadingState(tabName) {
    const tab = document.getElementById(tabName);
    const loadingEl = tab.querySelector('.loading-section');
    const contentEl = tab.querySelector('[class*="container"]');
    
    if (loadingEl && contentEl) {
        loadingEl.classList.remove('visible');
        setTimeout(() => {
            loadingEl.style.display = 'none';
        }, 320);
        contentEl.style.display = 'block';
    }
}

// ============================================================================
// NOTIFICATIONS
// ============================================================================

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '10000';
    notification.style.minWidth = '300px';
    
    document.body.appendChild(notification);
    
    // Auto-remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideInNotification 0.4s ease-out reverse';
        setTimeout(() => notification.remove(), 400);
    }, 4000);
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showWarning(message) {
    showNotification(message, 'warning');
}

function showInfo(message) {
    showNotification(message, 'info');
}

// ============================================================================
// TAB SWITCHING WITH ANIMATION
// ============================================================================

function switchTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab with animation
    const selectedTab = document.getElementById(tabName);
    if (!selectedTab) return;
    selectedTab.classList.add('active');
    
    // Activate the corresponding button by dataset attribute
    buttons.forEach(btn => {
        if (btn.dataset.tab === tabName) {
            btn.classList.add('active');
        }
    });
}

function switchToTab(tabName) {
    switchTab(tabName);
}

function showLoading(tabId, message) {
    showLoadingState(tabId, message);
}

function renderAuditResults(data) {
    updateAuditResults(data);
}

async function runFullWorkflowAnimation(data) {
    console.log('Starting full workflow with data:', data);
    return runWorkflowAnimation();
}

// Set up tab button click handlers
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const tabName = btn.dataset.tab;
        if (tabName) switchTab(tabName);
    });
});

// ============================================================================
// WORKFLOW ANIMATION SEQUENCE
// ============================================================================

async function runWorkflowAnimation() {
    try {
        console.log('🔄 Starting workflow animation...');
        showAgentStatusBoard();
        setWorkflowState(1);
        switchTab('audit');
        await sleep(500);

        // State 2: Audit Chamber
        setWorkflowState(2);
        setAgentStatus('quantitative', 'running');
        showLoadingState('audit', 'Analyzing bias metrics...');
        showNotification('🔍 Analyzing quantitative bias metrics...', 'info');

        await sleep(2200);
        setAgentStatus('quantitative', 'done');
        hideLoadingState('audit');
        showSuccess('✅ Audit metrics complete.');

        // State 3: Legal Research
        await sleep(400);
        setWorkflowState(3);
        switchTab('jury');
        setAgentStatus('legal', 'running');
        showLoadingState('jury', 'Reviewing legal context...');
        showNotification('📚 Searching legal precedents...', 'info');

        await sleep(2200);
        setAgentStatus('legal', 'done');
        setWorkflowState(3);
        hideLoadingState('jury');

        // State 4: Jury Verdict
        await sleep(300);
        setWorkflowState(4);
        switchTab('jury');
        setAgentStatus('mitigator', 'running');
        setAgentStatus('strict', 'running');
        setAgentStatus('ethicist', 'running');
        showLoadingState('jury', 'Jury deliberation in progress...');
        showNotification('⚖️ Three jurors debating the verdict...', 'info');

        await sleep(2800);
        setAgentStatus('mitigator', 'done');
        setAgentStatus('strict', 'done');
        setAgentStatus('ethicist', 'done');
        setWorkflowState(4);
        hideLoadingState('jury');

        // State 5: Report Generation
        await sleep(400);
        setWorkflowState(5);
        switchTab('report');
        setAgentStatus('chief-justice', 'running');
        showLoadingState('report', 'Generating final report...');
        showNotification('📄 Synthesizing verdict into report...', 'info');

        await sleep(2400);
        setAgentStatus('chief-justice', 'done');
        setWorkflowState(5);
        hideLoadingState('report');

        showSuccess('✅ Workflow completed successfully!');

    } catch (error) {
        showError('❌ Workflow error: ' + error.message);
    }
}

// Helper function
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// ============================================================================
// FORM SUBMISSION
// ============================================================================

document.getElementById('auditForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        case_data: {
            case_id: document.getElementById('caseId').value,
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value),
            priors: parseInt(document.getElementById('priors').value),
            zip_code: document.getElementById('zipCode').value,
            original_score: parseFloat(document.getElementById('originalScore').value),
            decision_type: document.getElementById('decisionType').value,
            jurisdiction: document.getElementById('jurisdiction').value
        }
    };
    
    try {
        showNotification('⚖️ Submitting audit request...', 'info');
        showAgentStatusBoard();
        showLoading('audit', 'Running Bias Audit...');

        const response = await fetch(`${API_BASE_URL}/audit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const payload = await response.text();
            throw new Error(payload || `Server returned ${response.status}`);
        }

        const result = await response.json();
        currentAuditResult = result;
        currentCaseId = result.case_id || formData.case_data.case_id;
        renderAuditResults(result);
        switchToTab('audit');
        await runFullWorkflowAnimation(result);

    } catch (error) {
        showError('Error submitting audit: ' + error.message);
        setWorkflowState(1);
        hideAgentStatusBoard();
    } finally {
        hideLoadingState('audit');
    }
});

// ============================================================================
// RESULT UPDATES
// ============================================================================

function updateAuditResults(result) {
    // State 2: Audit Chamber Results
    document.getElementById('dirValue').textContent = (result.dir_score || 0.82).toFixed(2);
    document.getElementById('dirStatus').textContent = 
        (result.dir_score >= 0.8 ? 'FAIR - Within Safe Harbor (80% Rule)' : 'UNFAIR - Below 80% Rule');
    
    document.getElementById('cfValue').textContent = 'Score Changed';
    document.getElementById('cfDesc').textContent = 
        result.counterfactual_analysis || 'Proxy bias detected when features modified';
    
    const biasScore = result.bias_score || 45;
    document.getElementById('biasScore').textContent = `${biasScore}/100`;
    document.getElementById('biasScoreBar').style.transform = `scaleX(${biasScore / 100})`;
    document.getElementById('biasScoreBar').style.backgroundColor = 
        biasScore > 70 ? '#f44336' : biasScore > 50 ? '#ffc107' : '#4caf50';
    
    const riskLevel = biasScore > 70 ? 'CRITICAL' : biasScore > 50 ? 'HIGH' : 'MEDIUM';
    document.getElementById('riskLevel').textContent = `Risk Level: ${riskLevel}`;
    
    document.getElementById('correctedScore').textContent = 
        (biasScore ? (72 - (biasScore / 100 * 10)).toFixed(1) : 72);

    // Detailed Audit Analysis
    document.getElementById('sampleSize').textContent = result.sample_size || '5,847';
    document.getElementById('statConfidence').textContent = `${((result.confidence || 0.85) * 100).toFixed(1)}%`;
    document.getElementById('pValue').textContent = (result.p_value || 0.0032).toFixed(4);
    
    const auditDetailsEl = document.getElementById('auditDetails');
    if (auditDetailsEl) {
        auditDetailsEl.style.display = 'block';
    }
    
    // State 4: Jury Results
    document.getElementById('mitigatorVerdict').textContent = result.mitigator_verdict || 'FAIR_WITH_CONCERNS';
    document.getElementById('auditorVerdict').textContent = result.strict_auditor_verdict || 'UNFAIR';
    document.getElementById('ethicistVerdict').textContent = result.ethicist_verdict || 'FAIR_WITH_CONCERNS';
    document.getElementById('consensusVerdict').textContent = result.verdict || 'PENDING';
    
    document.getElementById('mitigatorReasoning').textContent = 
        result.mitigator_reasoning || 'Evaluates potential mitigating factors and fairness.';
    document.getElementById('auditorReasoning').textContent = 
        result.auditor_reasoning || 'Applies strict legal and regulatory standards.';
    document.getElementById('ethicistReasoning').textContent = 
        result.ethicist_reasoning || 'Considers broader ethical implications and societal impact.';
    
    // Jury Analysis
    const juryAnalysisEl = document.getElementById('juryAnalysis');
    if (juryAnalysisEl) {
        document.getElementById('fairVotes').textContent = result.fair_votes || '1';
        document.getElementById('unfairVotes').textContent = result.unfair_votes || '1';
        document.getElementById('concernsVotes').textContent = result.concerns_votes || '1';
        juryAnalysisEl.style.display = 'block';
    }
    
    // State 5: Report
    document.getElementById('finalVerdict').textContent = result.verdict || 'PENDING';
    document.getElementById('reportCaseId').textContent = currentCaseId || '--';
    document.getElementById('reportDate').textContent = new Date().toLocaleDateString();
    document.getElementById('confidenceLevel').textContent = 
        `${((result.confidence || 0.85) * 100).toFixed(1)}%`;
    document.getElementById('agreementRate').textContent = 
        `${result.agreement_rate || 67}%`;
    document.getElementById('significance').textContent = 
        biasScore > 50 ? 'Significant' : 'Not Significant';
    document.getElementById('keyFindings').textContent = 
        result.key_findings || 'Algorithm shows potential for bias in protected characteristics.';

    const auditResultsEl = document.getElementById('auditResults');
    const juryResultsEl = document.getElementById('juryResults');
    const finalReportEl = document.getElementById('finalReport');

    auditResultsEl.style.display = 'grid';
    auditResultsEl.classList.add('visible');
    juryResultsEl.style.display = 'grid';
    juryResultsEl.classList.add('visible');
    finalReportEl.style.display = 'block';
    finalReportEl.classList.add('visible');
}

function downloadReport() {
    if (!currentAuditResult) {
        showWarning('No audit results to download');
        return;
    }

    const filename = `audit-report-${currentCaseId || 'unknown'}.json`;
    const report = {
        case_id: currentCaseId,
        generated_at: new Date().toISOString(),
        audit_result: currentAuditResult
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(link.href);

    showSuccess('📥 Report downloaded successfully.');
}

// ============================================================================
// PAGE INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('⚖️ Justice AI Workflow initialized');
    console.log('🌐 API Base URL:', API_BASE_URL);
    
    // Initialize workflow state
    setWorkflowState(1);
    hideAgentStatusBoard();
    
    // Add download button handler
    const downloadBtn = document.querySelector('.btn-secondary');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadReport);
    }
});
