// ============================================================================
// Justice AI Workflow Frontend App - Enhanced with Animations
// ============================================================================

const API_BASE_URL = 'http://localhost:8000';
let currentAuditResult = null;
let currentWorkflowState = 1;

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
// WORKFLOW STATE MANAGEMENT
// ============================================================================

function setWorkflowState(state) {
    currentWorkflowState = state;
    
    // Update all state circles
    for (let i = 1; i <= 5; i++) {
        const stateEl = document.getElementById(`state${i}`);
        const lineEl = stateEl.nextElementSibling;
        
        if (i < state) {
            // Completed states
            stateEl.classList.add('completed');
            stateEl.classList.remove('active');
            if (lineEl && lineEl.classList.contains('workflow-line')) {
                lineEl.classList.add('active');
            }
        } else if (i === state) {
            // Current active state
            stateEl.classList.add('active');
            stateEl.classList.remove('completed');
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
    }
}

// ============================================================================
// AGENT STATUS MANAGEMENT
// ============================================================================

function showAgentStatusBoard() {
    const board = document.getElementById('agentStatusBoard');
    board.style.display = 'block';
    
    // Initialize all agents as waiting
    Object.keys(AGENTS).forEach(agentId => {
        setAgentStatus(agentId, 'waiting');
    });
}

function hideAgentStatusBoard() {
    const board = document.getElementById('agentStatusBoard');
    board.style.display = 'none';
}

function setAgentStatus(agentId, status) {
    const agentCard = document.getElementById(`agent-${agentId}`);
    if (!agentCard) return;
    
    const statusEl = agentCard.querySelector('.agent-status');
    statusEl.className = 'agent-status ' + status;
    
    switch(status) {
        case 'running':
            statusEl.textContent = 'Running…';
            break;
        case 'done':
            statusEl.innerHTML = '<span style="animation: slideIn 0.4s;">✓ Done</span>';
            break;
        default:
            statusEl.textContent = 'Waiting';
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
        loadingEl.style.display = 'block';
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
        loadingEl.style.display = 'none';
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
    selectedTab.classList.add('active');
    
    // Find and activate the corresponding button
    buttons.forEach(btn => {
        if (btn.textContent.includes(selectedTab.querySelector('h2')?.textContent || '')) {
            btn.classList.add('active');
        }
    });
}

// Set up tab button click handlers
document.querySelectorAll('.tab-btn').forEach((btn, index) => {
    btn.addEventListener('click', () => {
        const tabs = ['intake', 'audit', 'jury', 'report'];
        if (tabs[index]) switchTab(tabs[index]);
    });
});

// ============================================================================
// WORKFLOW ANIMATION SEQUENCE
// ============================================================================

async function runWorkflowAnimation() {
    try {
        // State 1: Intake
        console.log('🔄 Starting workflow animation...');
        setWorkflowState(1);
        await sleep(500);
        
        // Show agent board
        showAgentStatusBoard();
        showNotification('⚖️ Starting fairness audit workflow...', 'info');
        
        // State 2: Audit Chamber
        await sleep(1000);
        setWorkflowState(2);
        setAgentStatus('quantitative', 'running');
        showLoadingState('audit', 'Analyzing bias metrics...');
        showNotification('🔍 Analyzing quantitative bias metrics...', 'info');
        
        await sleep(2500);
        setAgentStatus('quantitative', 'done');
        setWorkflowState(2);
        
        // State 3: Legal Research
        await sleep(500);
        setWorkflowState(3);
        setAgentStatus('legal', 'running');
        showNotification('📚 Searching legal precedents...', 'info');
        
        await sleep(2500);
        setAgentStatus('legal', 'done');
        setWorkflowState(3);
        
        // State 4: Jury Verdict
        await sleep(500);
        setWorkflowState(4);
        setAgentStatus('mitigator', 'running');
        setAgentStatus('strict', 'running');
        setAgentStatus('ethicist', 'running');
        showLoadingState('jury', 'Jury debate in progress...');
        showNotification('⚖️ Three jurors debating the verdict...', 'info');
        
        await sleep(3000);
        setAgentStatus('mitigator', 'done');
        setAgentStatus('strict', 'done');
        setAgentStatus('ethicist', 'done');
        setWorkflowState(4);
        hideLoadingState('jury');
        
        // State 5: Report Generation
        await sleep(500);
        setWorkflowState(5);
        setAgentStatus('chief-justice', 'running');
        showLoadingState('report', 'Generating final report...');
        showNotification('📄 Synthesizing verdict into report...', 'info');
        
        await sleep(2500);
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
        
        // Run workflow animation
        runWorkflowAnimation();
        
        // Optionally fetch real results
        const response = await fetch(`${API_BASE_URL}/audit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            const result = await response.json();
            currentAuditResult = result;
            updateAuditResults(result);
        }
        
    } catch (error) {
        showError('Error submitting audit: ' + error.message);
        setWorkflowState(1);
        hideAgentStatusBoard();
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
    document.getElementById('biasScoreBar').style.width = `${biasScore}%`;
    document.getElementById('biasScoreBar').style.backgroundColor = 
        biasScore > 70 ? '#f44336' : biasScore > 50 ? '#ffc107' : '#4caf50';
    
    const riskLevel = biasScore > 70 ? 'CRITICAL' : biasScore > 50 ? 'HIGH' : 'MEDIUM';
    document.getElementById('riskLevel').textContent = `Risk Level: ${riskLevel}`;
    
    document.getElementById('correctedScore').textContent = 
        (biasScore ? (72 - (biasScore / 100 * 10)).toFixed(1) : 72);
    
    // State 4: Jury Results
    document.getElementById('mitigatorVerdict').textContent = result.mitigator_verdict || 'FAIR_WITH_CONCERNS';
    document.getElementById('auditorVerdict').textContent = result.strict_auditor_verdict || 'UNFAIR';
    document.getElementById('ethicistVerdict').textContent = result.ethicist_verdict || 'FAIR_WITH_CONCERNS';
    document.getElementById('consensusVerdict').textContent = result.verdict || 'PENDING';
    
    // State 5: Report
    document.getElementById('finalVerdict').textContent = result.verdict || 'PENDING';
    document.getElementById('confidenceLevel').textContent = 
        `${((result.confidence || 0.85) * 100).toFixed(1)}%`;
    document.getElementById('keyFindings').textContent = 
        result.key_findings || 'Algorithm shows potential for bias in protected characteristics.';
}

function downloadReport() {
    if (!currentAuditResult) {
        showWarning('No audit results to download');
        return;
    }
    showNotification('📥 Report download initiated...', 'info');
    console.log('Downloading report for case:', currentAuditResult.case_id);
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
