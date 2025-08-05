class VideoDownloader {
    constructor() {
        this.form = document.getElementById('downloadForm');
        this.statusContainer = document.getElementById('status');
        this.statusMessage = document.getElementById('statusMessage');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.init();
    }

    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.loadDownloads();
        
        // Load saved repo info
        this.loadSavedRepoInfo();
    }

    loadSavedRepoInfo() {
        const savedOwner = localStorage.getItem('repoOwner');
        const savedRepo = localStorage.getItem('repoName');
        
        if (savedOwner) document.getElementById('repoOwner').value = savedOwner;
        if (savedRepo) document.getElementById('repoName').value = savedRepo;
    }

    saveRepoInfo(owner, repo) {
        localStorage.setItem('repoOwner', owner);
        localStorage.setItem('repoName', repo);
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const formData = this.getFormData();
        if (!this.validateForm(formData)) return;

        this.saveRepoInfo(formData.repoOwner, formData.repoName);
        this.setLoading(true);
        this.showStatus('Triggering download workflow...', 'info');

        try {
            const result = await this.triggerWorkflow(formData);
            if (result.success) {
                this.showStatus(
                    `Workflow triggered successfully! Run ID: ${result.runId}`, 
                    'success'
                );
                this.showWorkflowLink(formData.repoOwner, formData.repoName, result.runId);
                this.pollWorkflowStatus(formData, result.runId);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            this.showStatus(`Error: ${error.message}`, 'error');
        } finally {
            this.setLoading(false);
        }
    }

    getFormData() {
        return {
            videoUrl: document.getElementById('videoUrl').value,
            githubToken: document.getElementById('githubToken').value,
            downloadType: document.getElementById('downloadType').value,
            repoOwner: document.getElementById('repoOwner').value,
            repoName: document.getElementById('repoName').value
        };
    }

    validateForm(data) {
        if (!data.videoUrl || !data.githubToken || !data.repoOwner || !data.repoName) {
            this.showStatus('Please fill in all required fields', 'error');
            return false;
        }

        if (!this.isValidUrl(data.videoUrl)) {
            this.showStatus('Please enter a valid YouTube or TikTok URL', 'error');
            return false;
        }

        return true;
    }

    isValidUrl(url) {
        const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
        const tiktokRegex = /^(https?:\/\/)?(www\.)?tiktok\.com\/.+/;
        return youtubeRegex.test(url) || tiktokRegex.test(url);
    }

    async triggerWorkflow(data) {
        const workflowType = this.getWorkflowType(data.videoUrl);
        const apiUrl = `https://api.github.com/repos/${data.repoOwner}/${data.repoName}/dispatches`;

        const payload = {
            event_type: workflowType,
            client_payload: {
                video_url: data.videoUrl,
                download_type: data.downloadType,
                timestamp: new Date().toISOString()
            }
        };

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Authorization': `token ${data.githubToken}`,
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
        }

        // Since repository_dispatch doesn't return run ID directly,
        // we'll need to fetch recent workflow runs
        const runId = await this.getLatestWorkflowRun(data, workflowType);
        
        return { success: true, runId };
    }

    async getLatestWorkflowRun(data, workflowType) {
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait a bit for workflow to start
        
        const apiUrl = `https://api.github.com/repos/${data.repoOwner}/${data.repoName}/actions/runs`;
        
        const response = await fetch(apiUrl, {
            headers: {
                'Authorization': `token ${data.githubToken}`,
                'Accept': 'application/vnd.github.v3+json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            const latestRun = data.workflow_runs[0];
            return latestRun ? latestRun.id : null;
        }
        
        return null;
    }

    getWorkflowType(url) {
        if (url.includes('youtube.com') || url.includes('youtu.be')) {
            return 'download-youtube';
        } else if (url.includes('tiktok.com')) {
            return 'download-tiktok';
        }
        return 'download-video';
    }

    async pollWorkflowStatus(formData, runId) {
        if (!runId) return;

        const maxAttempts = 30; // 5 minutes max
        let attempts = 0;

        const poll = async () => {
            attempts++;
            
            try {
                const status = await this.checkWorkflowStatus(formData, runId);
                
                if (status.conclusion === 'success') {
                    this.showStatus('Download completed successfully!', 'success');
                    this.loadDownloads();
                    return;
                } else if (status.conclusion === 'failure') {
                    this.showStatus('Download failed. Check the workflow logs for details.', 'error');
                    return;
                } else if (status.status === 'in_progress' && attempts < maxAttempts) {
                    this.showStatus(`Download in progress... (${attempts}/${maxAttempts})`, 'info');
                    setTimeout(poll, 10000); // Poll every 10 seconds
                } else if (attempts >= maxAttempts) {
                    this.showStatus('Polling timeout. Please check workflow manually.', 'warning');
                }
            } catch (error) {
                console.error('Error polling workflow status:', error);
            }
        };

        poll();
    }

    async checkWorkflowStatus(formData, runId) {
        const apiUrl = `https://api.github.com/repos/${formData.repoOwner}/${formData.repoName}/actions/runs/${runId}`;
        
        const response = await fetch(apiUrl, {
            headers: {
                'Authorization': `token ${formData.githubToken}`,
                'Accept': 'application/vnd.github.v3+json'
            }
        });

        if (response.ok) {
            return await response.json();
        }
        
        throw new Error('Failed to check workflow status');
    }

    showWorkflowLink(owner, repo, runId) {
        const workflowLink = document.getElementById('workflowLink');
        const url = `https://github.com/${owner}/${repo}/actions/runs/${runId}`;
        workflowLink.innerHTML = `<a href="${url}" target="_blank">View Workflow Progress</a>`;
        workflowLink.style.display = 'block';
    }

    setLoading(loading) {
        const btnText = this.downloadBtn.querySelector('.btn-text');
        const loadingSpinner = this.downloadBtn.querySelector('.loading');
        
        if (loading) {
            btnText.style.display = 'none';
            loadingSpinner.style.display = 'inline';
            this.downloadBtn.disabled = true;
        } else {
            btnText.style.display = 'inline';
            loadingSpinner.style.display = 'none';
            this.downloadBtn.disabled = false;
        }
    }

    showStatus(message, type) {
        this.statusMessage.textContent = message;
        this.statusMessage.className = `status-message ${type}`;
        this.statusContainer.style.display = 'block';
    }

    async loadDownloads() {
        const downloadsList = document.getElementById('downloadsList');
        
        try {
            // This would need to be implemented to check the downloads folder
            // For now, just show a placeholder
            downloadsList.innerHTML = '<p class="no-downloads">Check your repository\'s downloads folder for completed files</p>';
        } catch (error) {
            console.error('Error loading downloads:', error);
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new VideoDownloader();
});
