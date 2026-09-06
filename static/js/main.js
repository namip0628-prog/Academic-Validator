/**
 * Academic Document Authenticity Validator - Frontend Controller (Version 2.0)
 * Integrates OCR extraction, OpenCV enhancement, and Ethereum smart contract verification.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (window.lucide) {
        window.lucide.createIcons();
    }

    // ==========================================
    // State Variables
    // ==========================================
    let activeTab = 'register'; // 'register', 'verify', 'history'

    // Registration Flow State
    let registerFile = null;
    let originalImageUrl = null;
    let processedImageUrl = null;
    let extractedRawText = '';
    let currentExtractedData = null;
    let currentHash = null;

    // Verification Flow State
    let verifyFile = null;
    let lastVerificationRecordId = null;

    // ==========================================
    // DOM Elements: Navigation & Header
    // ==========================================
    const tabBtnRegister = document.getElementById('tabBtnRegister');
    const tabBtnVerify = document.getElementById('tabBtnVerify');
    const tabBtnHistory = document.getElementById('tabBtnHistory');
    const viewRegister = document.getElementById('viewRegister');
    const viewVerify = document.getElementById('viewVerify');
    const viewHistory = document.getElementById('viewHistory');

    const ocrStatusBadge = document.getElementById('ocrStatusBadge');
    const ocrStatusText = document.getElementById('ocrStatusText');
    const blockchainStatusBadge = document.getElementById('blockchainStatusBadge');
    const blockchainStatusText = document.getElementById('blockchainStatusText');
    const tesseractWarningBanner = document.getElementById('tesseractWarningBanner');

    // Registration DOM Elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const filePreviewContainer = document.getElementById('filePreviewContainer');
    const filePreviewThumb = document.getElementById('filePreviewThumb');
    const previewFileName = document.getElementById('previewFileName');
    const previewFileSize = document.getElementById('previewFileSize');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const validateBtn = document.getElementById('validateBtn');
    const sampleBtn = document.getElementById('sampleBtn');

    const processingStepper = document.getElementById('processingStepper');
    const stepperStatusMsg = document.getElementById('stepperStatusMsg');
    const stepUpload = document.getElementById('stepUpload');
    const stepHash = document.getElementById('stepHash');
    const stepPreprocess = document.getElementById('stepPreprocess');
    const stepOCR = document.getElementById('stepOCR');
    const stepExtract = document.getElementById('stepExtract');

    const resultsSection = document.getElementById('resultsSection');
    const sha256Value = document.getElementById('sha256Value');
    const copyHashBtn = document.getElementById('copyHashBtn');
    const btnRegisterOnChain = document.getElementById('btnRegisterOnChain');
    const txSuccessBanner = document.getElementById('txSuccessBanner');
    const txHashValue = document.getElementById('txHashValue');
    const txBlockValue = document.getElementById('txBlockValue');
    const txContractValue = document.getElementById('txContractValue');
    const txTimestamp = document.getElementById('txTimestamp');

    const ocrConfidenceBadge = document.getElementById('ocrConfidenceBadge');
    const completenessBadge = document.getElementById('completenessBadge');
    const displayImage = document.getElementById('displayImage');
    const toggleOriginal = document.getElementById('toggleOriginal');
    const toggleProcessed = document.getElementById('toggleProcessed');
    const pipelineChips = document.getElementById('pipelineChips');
    const rawTextContent = document.getElementById('rawTextContent');
    const textMetaPill = document.getElementById('textMetaPill');
    const copyRawTextBtn = document.getElementById('copyRawTextBtn');

    // Verification DOM Elements
    const verifyDropZone = document.getElementById('verifyDropZone');
    const verifyFileInput = document.getElementById('verifyFileInput');
    const verifyBrowseBtn = document.getElementById('verifyBrowseBtn');
    const verifyFilePreviewContainer = document.getElementById('verifyFilePreviewContainer');
    const verifyFilePreviewThumb = document.getElementById('verifyFilePreviewThumb');
    const verifyPreviewFileName = document.getElementById('verifyPreviewFileName');
    const verifyPreviewFileSize = document.getElementById('verifyPreviewFileSize');
    const verifyRemoveFileBtn = document.getElementById('verifyRemoveFileBtn');
    const btnRunVerification = document.getElementById('btnRunVerification');
    const btnVerifySample = document.getElementById('btnVerifySample');

    const verificationResultSection = document.getElementById('verificationResultSection');
    const bannerAuthentic = document.getElementById('bannerAuthentic');
    const bannerTampered = document.getElementById('bannerTampered');
    const btnDownloadReport = document.getElementById('btnDownloadReport');
    const verifySha256Value = document.getElementById('verifySha256Value');
    const auditTimestamp = document.getElementById('auditTimestamp');
    const auditBlockNumber = document.getElementById('auditBlockNumber');
    const auditTxHash = document.getElementById('auditTxHash');
    const auditStudentName = document.getElementById('auditStudentName');
    const auditStudentId = document.getElementById('auditStudentId');
    const auditInstitution = document.getElementById('auditInstitution');
    const auditCourse = document.getElementById('auditCourse');
    const auditMarks = document.getElementById('auditMarks');
    const auditIssuer = document.getElementById('auditIssuer');

    // History DOM Elements
    const historyTableBody = document.getElementById('historyTableBody');
    const btnRefreshHistory = document.getElementById('btnRefreshHistory');

    // Initialize System Status on Load
    checkSystemStatus();

    // ==========================================
    // Tab Navigation Logic
    // ==========================================
    function switchTab(target) {
        activeTab = target;
        [tabBtnRegister, tabBtnVerify, tabBtnHistory].forEach(btn => btn.classList.remove('active'));
        [viewRegister, viewVerify, viewHistory].forEach(v => v.classList.add('hidden'));

        if (target === 'register') {
            tabBtnRegister.classList.add('active');
            viewRegister.classList.remove('hidden');
        } else if (target === 'verify') {
            tabBtnVerify.classList.add('active');
            viewVerify.classList.remove('hidden');
        } else if (target === 'history') {
            tabBtnHistory.classList.add('active');
            viewHistory.classList.remove('hidden');
            loadHistoryTable();
        }

        if (window.lucide) window.lucide.createIcons();
    }

    tabBtnRegister.addEventListener('click', () => switchTab('register'));
    tabBtnVerify.addEventListener('click', () => switchTab('verify'));
    tabBtnHistory.addEventListener('click', () => switchTab('history'));
    btnRefreshHistory.addEventListener('click', loadHistoryTable);

    // ==========================================
    // System Status Check
    // ==========================================
    async function checkSystemStatus() {
        try {
            const resp = await fetch('/api/system-status');
            const data = await resp.json();

            // OCR Status
            if (data.ocr_available) {
                ocrStatusBadge.className = 'status-badge online';
                ocrStatusText.textContent = 'OCR Engine Online';
                tesseractWarningBanner.classList.add('hidden');
            } else {
                ocrStatusBadge.className = 'status-badge warning';
                ocrStatusText.textContent = 'Tesseract Not Detected';
                tesseractWarningBanner.classList.remove('hidden');
            }

            // Blockchain Status
            const bc = data.blockchain;
            if (bc.connected) {
                blockchainStatusBadge.className = 'status-badge online';
                blockchainStatusText.textContent = `Hardhat Connected (Block #${bc.block_number})`;
            } else {
                blockchainStatusBadge.className = 'status-badge blockchain-badge';
                blockchainStatusText.textContent = `${bc.mode}`;
            }
        } catch (err) {
            console.warn('System status check failed:', err);
            ocrStatusBadge.className = 'status-badge warning';
            ocrStatusText.textContent = 'Server Offline';
        }
    }

    // ==========================================
    // Tab 1: Registration Drag & Drop + File Upload
    // ==========================================
    browseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        fileInput.click();
    });

    dropZone.addEventListener('click', () => {
        if (!registerFile) fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleRegisterFile(e.target.files[0]);
        }
    });

    setupDragDrop(dropZone, handleRegisterFile);

    removeFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        registerFile = null;
        fileInput.value = '';
        filePreviewContainer.classList.add('hidden');
        dropZone.querySelector('.drop-zone-content').classList.remove('hidden');
        validateBtn.setAttribute('disabled', 'true');
    });

    function handleRegisterFile(file) {
        if (!validateImageFile(file)) return;
        registerFile = file;

        previewFileName.textContent = file.name;
        previewFileSize.textContent = formatBytes(file.size);

        const reader = new FileReader();
        reader.onload = (e) => {
            filePreviewThumb.src = e.target.result;
            filePreviewContainer.classList.remove('hidden');
            dropZone.querySelector('.drop-zone-content').classList.add('hidden');
            validateBtn.removeAttribute('disabled');
        };
        reader.readAsDataURL(file);
    }

    // ==========================================
    // Tab 1: OCR Extraction & Stepper
    // ==========================================
    validateBtn.addEventListener('click', () => {
        if (!registerFile) return;
        submitRegistrationExtraction();
    });

    sampleBtn.addEventListener('click', () => {
        submitSampleExtraction();
    });

    async function submitRegistrationExtraction() {
        startStepper();
        const formData = new FormData();
        formData.append('document', registerFile);

        try {
            animateStepperStages();
            const response = await fetch('/api/validate', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            finishStepperAndRender(data);
        } catch (err) {
            console.error('Validation error:', err);
            showToast('Document processing failed: ' + err.message, 'error');
            processingStepper.classList.add('hidden');
            validateBtn.removeAttribute('disabled');
            sampleBtn.removeAttribute('disabled');
        }
    }

    async function submitSampleExtraction() {
        startStepper();
        try {
            animateStepperStages();
            const response = await fetch('/api/validate-sample', {
                method: 'POST',
            });
            const data = await response.json();
            finishStepperAndRender(data);
        } catch (err) {
            console.error('Sample processing error:', err);
            showToast('Sample processing failed: ' + err.message, 'error');
            processingStepper.classList.add('hidden');
            validateBtn.removeAttribute('disabled');
            sampleBtn.removeAttribute('disabled');
        }
    }

    function animateStepperStages() {
        setTimeout(() => {
            setStepCompleted(stepUpload, 0);
            setStepActive(stepHash, 'Calculating SHA-256 cryptographic digest...');
        }, 300);

        setTimeout(() => {
            setStepCompleted(stepHash, 1);
            setStepActive(stepPreprocess, 'Applying OpenCV grayscale, denoising & Otsu binarization...');
        }, 700);

        setTimeout(() => {
            setStepCompleted(stepPreprocess, 2);
            setStepActive(stepOCR, 'Running Tesseract OCR text extraction...');
        }, 1100);
    }

    function finishStepperAndRender(data) {
        setStepCompleted(stepOCR, 3);
        setStepActive(stepExtract, 'Parsing academic entities & verifying authenticity...');

        setTimeout(() => {
            setStepCompleted(stepExtract, 4);
            stepperStatusMsg.textContent = 'Document successfully processed!';
            renderRegistrationResults(data);
        }, 400);
    }

    function renderRegistrationResults(data) {
        if (!data.success) {
            showToast(data.error || 'Failed to process document.', 'error');
            return;
        }

        validateBtn.removeAttribute('disabled');
        sampleBtn.removeAttribute('disabled');
        resultsSection.classList.remove('hidden');

        currentHash = data.sha256_hash;
        currentExtractedData = data.academic_data;

        // Render SHA-256 Hash
        sha256Value.textContent = currentHash;

        // Render Academic Fields
        const fields = data.academic_data.fields;
        for (const [key, field] of Object.entries(fields)) {
            const valEl = document.getElementById(`field_${key}`);
            const confEl = document.getElementById(`conf_${key}`);
            if (valEl && confEl) {
                if (field.value) {
                    valEl.textContent = field.value;
                    confEl.textContent = field.confidence;
                    confEl.className = `confidence-tag ${field.confidence}`;
                } else {
                    valEl.textContent = 'Not Detected';
                    valEl.style.color = 'var(--text-muted)';
                    confEl.textContent = 'None';
                    confEl.className = 'confidence-tag none';
                }
            }
        }

        // Completeness & Confidence Badges
        const summary = data.academic_data.summary;
        completenessBadge.textContent = `${summary.detected_fields} / ${summary.total_fields} Fields (${summary.completeness_score}%)`;

        if (data.ocr && data.ocr.confidence > 0) {
            ocrConfidenceBadge.textContent = `OCR Conf: ${data.ocr.confidence}%`;
            ocrConfidenceBadge.classList.remove('hidden');
        } else {
            ocrConfidenceBadge.textContent = 'OCR Engine Tested';
        }

        // Visual Inspection Images
        originalImageUrl = data.original_image_url;
        processedImageUrl = data.processed_image_url;
        displayImage.src = processedImageUrl || originalImageUrl;
        toggleProcessed.classList.add('active');
        toggleOriginal.classList.remove('active');

        // Pipeline Chips
        pipelineChips.innerHTML = '';
        if (data.preprocessing && data.preprocessing.steps_applied) {
            data.preprocessing.steps_applied.forEach(step => {
                const chip = document.createElement('span');
                chip.className = 'chip';
                chip.innerHTML = `<i data-lucide="check"></i> ${step}`;
                pipelineChips.appendChild(chip);
            });
        }
        if (data.preprocessing && data.preprocessing.processed_dimensions) {
            const dimChip = document.createElement('span');
            dimChip.className = 'chip';
            dimChip.innerHTML = `<i data-lucide="maximize-2"></i> ${data.preprocessing.processed_dimensions}`;
            pipelineChips.appendChild(dimChip);
        }

        // Raw OCR Text
        extractedRawText = data.ocr.raw_text || '';
        if (extractedRawText) {
            rawTextContent.textContent = extractedRawText;
            textMetaPill.textContent = `${data.ocr.char_count} chars • ${data.ocr.word_count} words`;
        } else if (data.ocr.error) {
            rawTextContent.textContent = `${data.ocr.error}\n\n${data.ocr.install_guide || ''}`;
            textMetaPill.textContent = 'OCR Notice';
        } else {
            rawTextContent.textContent = 'No text detected in document.';
            textMetaPill.textContent = '0 chars • 0 words';
        }

        // Reset or Show Blockchain Registration State
        if (data.already_on_chain) {
            txSuccessBanner.classList.remove('hidden');
            const rec = data.on_chain_record;
            txHashValue.textContent = rec.transaction_hash;
            txBlockValue.textContent = `#${rec.block_number}`;
            txContractValue.textContent = rec.contract_address;
            txTimestamp.textContent = rec.formatted_date;
            btnRegisterOnChain.setAttribute('disabled', 'true');
            btnRegisterOnChain.innerHTML = `<i data-lucide="check"></i> Already Anchored on Chain`;
        } else {
            txSuccessBanner.classList.add('hidden');
            btnRegisterOnChain.removeAttribute('disabled');
            btnRegisterOnChain.innerHTML = `<i data-lucide="link"></i> Register on Blockchain`;
        }

        if (window.lucide) window.lucide.createIcons();
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        showToast('Document analyzed & SHA-256 fingerprint generated!', 'success');
    }

    // ==========================================
    // Tab 1: Smart Contract Registration Action
    // ==========================================
    btnRegisterOnChain.addEventListener('click', async () => {
        if (!currentHash) return;

        btnRegisterOnChain.setAttribute('disabled', 'true');
        btnRegisterOnChain.innerHTML = `<span class="status-dot"></span> Anchoring to Ethereum...`;

        try {
            const fields = currentExtractedData ? currentExtractedData.fields : {};
            const payload = {
                document_hash: currentHash,
                student_name: fields.student_name?.value || "Aarav Sharma",
                student_id: fields.student_id?.value || "1NT20CS045",
                institution: fields.institution?.value || "National Institute of Technology",
                course: fields.course?.value || "Bachelor of Technology in Computer Science",
                marks: fields.marks?.value || "CGPA: 8.85 / 10.0",
                document_name: registerFile ? registerFile.name : "sample_degree_certificate.png",
            };

            const response = await fetch('/api/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const res = await response.json();

            if (res.success) {
                txSuccessBanner.classList.remove('hidden');
                txHashValue.textContent = res.transaction_hash;
                txBlockValue.textContent = `#${res.block_number}`;
                txContractValue.textContent = res.contract_address;
                txTimestamp.textContent = res.formatted_date;

                btnRegisterOnChain.innerHTML = `<i data-lucide="check-check"></i> Anchored on Blockchain!`;
                showToast('Credential hash successfully registered onto the blockchain!', 'success');
                checkSystemStatus();
            } else {
                showToast(res.error || 'Registration failed.', 'error');
                btnRegisterOnChain.removeAttribute('disabled');
                btnRegisterOnChain.innerHTML = `<i data-lucide="link"></i> Register on Blockchain`;
            }
        } catch (err) {
            console.error('Registration error:', err);
            showToast('Blockchain transaction failed: ' + err.message, 'error');
            btnRegisterOnChain.removeAttribute('disabled');
            btnRegisterOnChain.innerHTML = `<i data-lucide="link"></i> Register on Blockchain`;
        }

        if (window.lucide) window.lucide.createIcons();
    });

    // ==========================================
    // Tab 2: Public Verification Portal (Phase 3)
    // ==========================================
    verifyBrowseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        verifyFileInput.click();
    });

    verifyDropZone.addEventListener('click', () => {
        if (!verifyFile) verifyFileInput.click();
    });

    verifyFileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleVerifyFile(e.target.files[0]);
        }
    });

    setupDragDrop(verifyDropZone, handleVerifyFile);

    verifyRemoveFileBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        verifyFile = null;
        verifyFileInput.value = '';
        verifyFilePreviewContainer.classList.add('hidden');
        verifyDropZone.querySelector('.drop-zone-content').classList.remove('hidden');
        btnRunVerification.setAttribute('disabled', 'true');
    });

    function handleVerifyFile(file) {
        if (!validateImageFile(file)) return;
        verifyFile = file;

        verifyPreviewFileName.textContent = file.name;
        verifyPreviewFileSize.textContent = formatBytes(file.size);

        const reader = new FileReader();
        reader.onload = (e) => {
            verifyFilePreviewThumb.src = e.target.result;
            verifyFilePreviewContainer.classList.remove('hidden');
            verifyDropZone.querySelector('.drop-zone-content').classList.add('hidden');
            btnRunVerification.removeAttribute('disabled');
        };
        reader.readAsDataURL(file);
    }

    btnRunVerification.addEventListener('click', () => {
        if (!verifyFile) return;
        runVerificationProcess();
    });

    btnVerifySample.addEventListener('click', () => {
        runSampleVerificationProcess();
    });

    async function runVerificationProcess() {
        btnRunVerification.setAttribute('disabled', 'true');
        btnRunVerification.innerHTML = `<span class="status-dot"></span> Checking Blockchain...`;

        const formData = new FormData();
        formData.append('document', verifyFile);

        try {
            const response = await fetch('/api/verify', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            renderVerificationVerdict(data.verification);
        } catch (err) {
            console.error('Verification error:', err);
            showToast('Verification query failed: ' + err.message, 'error');
        } finally {
            btnRunVerification.removeAttribute('disabled');
            btnRunVerification.innerHTML = `<i data-lucide="shield-check"></i> Verify Authenticity`;
            if (window.lucide) window.lucide.createIcons();
        }
    }

    async function runSampleVerificationProcess() {
        btnVerifySample.setAttribute('disabled', 'true');
        btnVerifySample.innerHTML = `<span class="status-dot"></span> Checking Blockchain...`;

        try {
            const response = await fetch('/api/verify-sample', {
                method: 'POST',
            });
            const data = await response.json();
            renderVerificationVerdict(data.verification);
        } catch (err) {
            console.error('Sample verification error:', err);
            showToast('Sample verification failed: ' + err.message, 'error');
        } finally {
            btnVerifySample.removeAttribute('disabled');
            btnVerifySample.innerHTML = `<i data-lucide="sparkles"></i> Verify Sample Certificate`;
            if (window.lucide) window.lucide.createIcons();
        }
    }

    function renderVerificationVerdict(res) {
        verificationResultSection.classList.remove('hidden');
        lastVerificationRecordId = res.record_id;

        verifySha256Value.textContent = res.document_hash;

        if (res.is_authentic) {
            bannerAuthentic.classList.remove('hidden');
            bannerTampered.classList.add('hidden');

            auditTimestamp.textContent = res.formatted_date || "-";
            auditBlockNumber.textContent = `#${res.block_number || "-"}`;
            auditTxHash.textContent = res.transaction_hash || "-";
            auditStudentName.textContent = res.student_name || "-";
            auditStudentId.textContent = res.student_id || "-";
            auditInstitution.textContent = res.institution || "-";
            auditCourse.textContent = res.course || "-";
            auditMarks.textContent = res.marks || "-";
            auditIssuer.textContent = res.issuer || "-";

            showToast('✓ Authentic! Document verified against blockchain record.', 'success');
        } else {
            bannerAuthentic.classList.add('hidden');
            bannerTampered.classList.remove('hidden');

            auditTimestamp.textContent = "Not Found";
            auditBlockNumber.textContent = "Unregistered";
            auditTxHash.textContent = "No On-Chain Transaction Found";
            auditStudentName.textContent = "Unauthenticated";
            auditStudentId.textContent = "N/A";
            auditInstitution.textContent = "N/A";
            auditCourse.textContent = "N/A";
            auditMarks.textContent = "N/A";
            auditIssuer.textContent = "N/A";

            showToast('✗ Invalid or modified! No matching hash found on blockchain.', 'error');
        }

        if (window.lucide) window.lucide.createIcons();
        verificationResultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // PDF Download Handler
    btnDownloadReport.addEventListener('click', () => {
        if (!lastVerificationRecordId) {
            showToast('No active verification record to export.', 'error');
            return;
        }
        window.open(`/api/download-report/${lastVerificationRecordId}`, '_blank');
        showToast('Generating official Verification Certificate (PDF)...', 'success');
    });

    // ==========================================
    // Tab 3: Audit Ledger & History
    // ==========================================
    async function loadHistoryTable() {
        historyTableBody.innerHTML = `<tr><td colspan="8" class="empty-table-msg">Fetching blockchain audit records...</td></tr>`;

        try {
            const resp = await fetch('/api/history');
            const data = await resp.json();

            if (!data.history || data.history.length === 0) {
                historyTableBody.innerHTML = `<tr><td colspan="8" class="empty-table-msg">No credentials have been registered or verified yet.</td></tr>`;
                return;
            }

            historyTableBody.innerHTML = '';
            data.history.forEach(item => {
                const tr = document.createElement('tr');

                let badgeClass = 'registered';
                let verdictLabel = item.verdict;
                if (item.verdict === 'AUTHENTIC') {
                    badgeClass = 'authentic';
                    verdictLabel = '✓ Authentic';
                } else if (item.verdict === 'INVALID_OR_MODIFIED') {
                    badgeClass = 'invalid';
                    verdictLabel = '✗ Invalid';
                }

                const shortHash = item.document_hash.substring(0, 10) + '...' + item.document_hash.substring(56);
                const shortTx = item.tx_hash && item.tx_hash !== '-' ? item.tx_hash.substring(0, 10) + '...' : '-';

                tr.innerHTML = `
                    <td style="color: var(--text-muted); font-size: 0.775rem;">${item.formatted_date}</td>
                    <td><span class="badge badge-outline">${item.event_type}</span></td>
                    <td style="font-weight: 600;">${item.document_name}</td>
                    <td>${item.student_name || '-'}</td>
                    <td><code class="monospace-val" style="font-size: 0.75rem;">${shortHash}</code></td>
                    <td><span class="table-verdict-badge ${badgeClass}">${verdictLabel}</span></td>
                    <td><code style="font-family: var(--font-mono); font-size: 0.75rem; color: #a78bfa;">${shortTx}</code></td>
                    <td>
                        <button type="button" class="btn btn-sm btn-outline" onclick="window.open('/api/download-report/${item.id}', '_blank')">
                            <i data-lucide="download"></i> PDF
                        </button>
                    </td>
                `;
                historyTableBody.appendChild(tr);
            });

            if (window.lucide) window.lucide.createIcons();
        } catch (err) {
            console.error('History load error:', err);
            historyTableBody.innerHTML = `<tr><td colspan="8" class="empty-table-msg" style="color: var(--danger);">Failed to load history: ${err.message}</td></tr>`;
        }
    }

    // ==========================================
    // UI Helpers & Utilities
    // ==========================================
    copyHashBtn.addEventListener('click', () => {
        const hashText = sha256Value.textContent.trim();
        if (hashText && !hashText.startsWith('---')) {
            navigator.clipboard.writeText(hashText);
            showToast('SHA-256 Hash copied to clipboard!', 'success');
        }
    });

    copyRawTextBtn.addEventListener('click', () => {
        if (extractedRawText) {
            navigator.clipboard.writeText(extractedRawText);
            showToast('Extracted OCR text copied to clipboard!', 'success');
        }
    });

    toggleOriginal.addEventListener('click', () => {
        toggleOriginal.classList.add('active');
        toggleProcessed.classList.remove('active');
        if (originalImageUrl) displayImage.src = originalImageUrl;
    });

    toggleProcessed.addEventListener('click', () => {
        toggleProcessed.classList.add('active');
        toggleOriginal.classList.remove('active');
        if (processedImageUrl) displayImage.src = processedImageUrl;
    });

    function setupDragDrop(el, callback) {
        ['dragenter', 'dragover'].forEach(eventName => {
            el.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                el.classList.add('dragover');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            el.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                el.classList.remove('dragover');
            });
        });

        el.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            if (dt && dt.files && dt.files[0]) {
                callback(dt.files[0]);
            }
        });
    }

    function validateImageFile(file) {
        const validExtensions = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/tiff', 'image/bmp'];
        if (!validExtensions.includes(file.type) && !file.name.match(/\.(png|jpe?g|webp|tiff|bmp)$/i)) {
            showToast('Invalid file format. Please upload an image (PNG, JPG, WEBP).', 'error');
            return false;
        }
        if (file.size > 16 * 1024 * 1024) {
            showToast('File size exceeds the 16MB maximum limit.', 'error');
            return false;
        }
        return true;
    }

    function formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function startStepper() {
        processingStepper.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        validateBtn.setAttribute('disabled', 'true');
        sampleBtn.setAttribute('disabled', 'true');

        [stepUpload, stepHash, stepPreprocess, stepOCR, stepExtract].forEach(step => {
            step.className = 'step-item';
        });
        document.querySelectorAll('.step-connector').forEach(conn => conn.classList.remove('completed'));
        setStepActive(stepUpload, 'Uploading document to secure validator...');
    }

    function setStepActive(stepEl, msg) {
        stepEl.classList.add('active');
        stepperStatusMsg.textContent = msg;
    }

    function setStepCompleted(stepEl, connectorIdx) {
        stepEl.classList.remove('active');
        stepEl.classList.add('completed');
        const connectors = document.querySelectorAll('.step-connector');
        if (connectors[connectorIdx]) {
            connectors[connectorIdx].classList.add('completed');
        }
    }

    function showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const iconName = type === 'success' ? 'check-circle-2' : type === 'error' ? 'alert-circle' : 'info';
        toast.innerHTML = `<i data-lucide="${iconName}"></i><span>${message}</span>`;
        container.appendChild(toast);

        if (window.lucide) window.lucide.createIcons();

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            toast.style.transition = 'all 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
});
