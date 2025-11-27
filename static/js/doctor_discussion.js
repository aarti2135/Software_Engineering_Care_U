/**
 * Doctor Discussion Topics - Frontend Handler
 * Epic 7 Story 2: Integrates with existing AI agent
 */

class DoctorDiscussionHandler {
    constructor() {
        this.modal = null;
        this.currentTopics = null;
        this.init();
    }

    init() {
        // Initialize modal
        const modalElement = document.getElementById('doctorDiscussionModal');
        if (modalElement) {
            this.modal = new bootstrap.Modal(modalElement);
        }

        // Attach event listeners
        this.attachEventListeners();
    }

    attachEventListeners() {
        // Button to trigger discussion generation
        const triggerBtn = document.getElementById('generateDiscussionBtn');
        if (triggerBtn) {
            triggerBtn.addEventListener('click', () => this.generateTopics());
        }

        // Export button
        const exportBtn = document.getElementById('exportDiscussionBtn');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportTopics());
        }

        // Reset modal on close
        const modalElement = document.getElementById('doctorDiscussionModal');
        if (modalElement) {
            modalElement.addEventListener('hidden.bs.modal', () => this.resetModal());
        }
    }

    getCsrfToken() {
        // Try multiple methods to get CSRF token
        let token = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!token) {
            // Try getting from cookies
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const [name, value] = cookie.trim().split('=');
                if (name === 'csrftoken') {
                    token = value;
                    break;
                }
            }
        }

        return token;
    }

    async generateTopics() {
        // Show modal
        this.modal.show();

        // Show loading state
        this.showLoading();

        try {
            // Get CSRF token
            const csrfToken = this.getCsrfToken();

            if (!csrfToken) {
                console.error('CSRF token not found');
                this.showError('Security token missing. Please refresh the page and try again.');
                return;
            }

            // ✅ FIXED: Correct URL path
            const url = '/dashboard/doctor-discussion/';
            console.log('Making request to:', url);

            // Make POST request to backend
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'same-origin',
                body: JSON.stringify({})
            });

            console.log('Response status:', response.status);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server error:', errorText);
                throw new Error(`Server returned ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            console.log('Response data:', data);

            if (data.success) {
                this.currentTopics = data.topics;
                this.displayTopics(data.topics);
            } else {
                this.showError(data.error || 'Failed to generate discussion topics');
            }

        } catch (error) {
            console.error('Error fetching discussion topics:', error);
            this.showError('Error: ' + error.message);
        }
    }

    showLoading() {
        document.getElementById('discussionLoading').classList.remove('d-none');
        document.getElementById('discussionError').classList.add('d-none');
        document.getElementById('discussionContent').classList.add('d-none');
        document.getElementById('exportDiscussionBtn').disabled = true;
    }

    showError(message) {
        document.getElementById('discussionLoading').classList.add('d-none');
        document.getElementById('discussionError').classList.remove('d-none');
        document.getElementById('discussionContent').classList.add('d-none');
        document.getElementById('discussionErrorMessage').textContent = message;
        document.getElementById('exportDiscussionBtn').disabled = true;
    }

    displayTopics(topics) {
        // Hide loading, show content
        document.getElementById('discussionLoading').classList.add('d-none');
        document.getElementById('discussionError').classList.add('d-none');
        document.getElementById('discussionContent').classList.remove('d-none');
        document.getElementById('exportDiscussionBtn').disabled = false;

        // Populate disclaimer
        document.getElementById('discussionDisclaimer').textContent =
            topics.disclaimer || 'These are observations from your data, not medical advice.';

        // Populate observations
        this.populateList('discussionObservations', topics.observations || [], 'observation');

        // Populate questions
        this.populateList('discussionQuestions', topics.questions || [], 'question');

        // Populate context
        this.populateList('discussionContext', topics.context || [], 'context');
    }

    populateList(elementId, items, type) {
        const listElement = document.getElementById(elementId);
        listElement.innerHTML = '';

        if (!items || items.length === 0) {
            listElement.innerHTML = '<li class="list-group-item text-muted">No items available</li>';
            return;
        }

        items.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'list-group-item';

            // Add emoji based on type
            let emoji = '';
            if (type === 'observation') {
                emoji = '✓';
            } else if (type === 'question') {
                emoji = '?';
            } else if (type === 'context') {
                emoji = '•';
            }

            li.innerHTML = `<strong style="margin-right: 0.5rem;">${emoji}</strong><span>${this.escapeHtml(item)}</span>`;
            listElement.appendChild(li);
        });
    }

    exportTopics() {
        if (!this.currentTopics) return;

        // Create text content
        let textContent = '=== Doctor Discussion Topics ===\n\n';
        textContent += `Generated: ${new Date().toLocaleString()}\n\n`;

        textContent += `DISCLAIMER:\n${this.currentTopics.disclaimer}\n\n`;

        textContent += '--- OBSERVATIONS FROM YOUR DATA ---\n';
        (this.currentTopics.observations || []).forEach((obs, i) => {
            textContent += `${i + 1}. ${obs}\n`;
        });
        textContent += '\n';

        textContent += '--- QUESTIONS TO ASK YOUR DOCTOR ---\n';
        (this.currentTopics.questions || []).forEach((q, i) => {
            textContent += `${i + 1}. ${q}\n`;
        });
        textContent += '\n';

        textContent += '--- ADDITIONAL CONTEXT ---\n';
        (this.currentTopics.context || []).forEach((c, i) => {
            textContent += `${i + 1}. ${c}\n`;
        });

        // Create downloadable file
        const blob = new Blob([textContent], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Doctor_Discussion_Topics_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }

    resetModal() {
        this.currentTopics = null;
        this.showLoading();
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.doctorDiscussionHandler = new DoctorDiscussionHandler();
});