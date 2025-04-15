document.addEventListener('DOMContentLoaded', () => {
    // Get DOM elements
    const toggleSwitch = document.getElementById('toggle-switch');
    const toggleStatus = document.getElementById('toggle-status');
    const modelSelect = document.getElementById('model-select');
    const searchInput = document.getElementById('search-input');
    const voiceSearchButton = document.getElementById('voice-search');
    const searchResults = document.getElementById('search-results');

    // AI Assignment Helper elements
    const aiHelperLink = document.getElementById('ai-assignment-helper-link');
    const aiHelperSection = document.getElementById('ai-assignment-helper');
    const uploadImageInput = document.getElementById('upload-image');
    const pasteTextArea = document.getElementById('paste-text');
    const submitButton = document.getElementById('submit-assignment');
    const clearButton = document.getElementById('clear-assignment');
    const resultSection = document.getElementById('assignment-result');
    const answerElem = document.getElementById('assignment-answer');
    const summaryElem = document.getElementById('assignment-summary');
    const explanationElem = document.getElementById('assignment-explanation');

    // Toggle Switch Functionality
    if (toggleSwitch && toggleStatus) {
        toggleSwitch.addEventListener('change', function() {
            const isChecked = this.checked;
            toggleStatus.textContent = isChecked ? 'Web Search is ON' : 'Web Search is OFF';
            toggleStatus.className = isChecked ? 'text-primary-500 font-medium' : 'text-gray-700 font-medium';
            
            searchInput.disabled = !isChecked;
            voiceSearchButton.disabled = !isChecked;
            
            if (!isChecked) {
                searchInput.value = '';
                searchResults.innerHTML = '';
                searchResults.classList.add('hidden');
            } else {
                searchInput.focus();
            }
        });
    }

    // AI Assignment Helper Functionality
    if (aiHelperLink) {
        aiHelperLink.addEventListener('click', (e) => {
            e.preventDefault();
            if (aiHelperSection.classList.contains('hidden')) {
                aiHelperSection.classList.remove('hidden');
                aiHelperSection.scrollIntoView({ behavior: 'smooth' });
            } else {
                aiHelperSection.classList.add('hidden');
            }
        });
    }

    if (clearButton) {
        clearButton.addEventListener('click', () => {
            uploadImageInput.value = '';
            pasteTextArea.value = '';
            resultSection.classList.add('hidden');
            answerElem.textContent = '';
            summaryElem.textContent = '';
            explanationElem.textContent = '';
        });
    }

    if (submitButton) {
        submitButton.addEventListener('click', async () => {
            const imageFile = uploadImageInput.files[0];
            const pastedText = pasteTextArea.value.trim();

            if (!imageFile && !pastedText) {
                alert('Please upload an image or paste text to submit.');
                return;
            }

            // Show loading state
            submitButton.disabled = true;
            answerElem.textContent = 'Processing...';
            summaryElem.textContent = 'Please wait...';
            explanationElem.textContent = 'Analyzing your input...';
            resultSection.classList.remove('hidden');

            try {
                const formData = new FormData();
                if (imageFile) {
                    formData.append('image', imageFile);
                }
                if (pastedText) {
                    formData.append('text', pastedText);
                }

                const response = await fetch('/submit-assignment', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    throw new Error('Failed to process submission');
                }

                const result = await response.json();
                
                answerElem.textContent = result.answer;
                summaryElem.textContent = result.summary;
                explanationElem.textContent = result.explanation;

            } catch (error) {
                answerElem.textContent = 'Error: ' + error.message;
                summaryElem.textContent = 'Failed to process your submission';
                explanationElem.textContent = 'Please try again later';
            } finally {
                submitButton.disabled = false;
            }
        });
    }

    // Voice Search Functionality
    if (voiceSearchButton) {
        voiceSearchButton.addEventListener('click', function() {
            if ('webkitSpeechRecognition' in window) {
                const recognition = new webkitSpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = false;

                recognition.onstart = function() {
                    voiceSearchButton.innerHTML = '<i class="fas fa-circle text-red-500 animate-pulse text-2xl"></i>';
                };

                recognition.onresult = function(event) {
                    const transcript = event.results[0][0].transcript;
                    searchInput.value = transcript;
                    performSearch();
                };

                recognition.onend = function() {
                    voiceSearchButton.innerHTML = '<i class="fas fa-microphone text-2xl"></i>';
                };

                recognition.start();
            }
        });
    }

    // Search Functionality
    if (searchInput && searchResults) {
        searchInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !searchInput.disabled) {
                e.preventDefault();
                if (!modelSelect.value) {
                    modelSelect.style.borderColor = '#ef4444';
                    modelSelect.style.boxShadow = '0 0 0 3px rgba(239, 68, 68, 0.2)';
                    setTimeout(() => {
                        modelSelect.style.borderColor = '';
                        modelSelect.style.boxShadow = '';
                    }, 2000);
                    return;
                }
                performSearch();
            }
        });
    }

    // Model Selection
    if (modelSelect) {
        modelSelect.addEventListener('change', function() {
            if (this.value) {
                this.style.borderColor = '#06b6d4';
                if (searchInput.value.trim() && !searchInput.disabled) {
                    performSearch();
                }
            } else {
                this.style.borderColor = '';
            }
        });
    }

    function performSearch() {
        const query = searchInput.value.trim();
        if (!query || searchInput.disabled || !modelSelect.value) return;

        searchResults.classList.remove('hidden');
        searchResults.innerHTML = `
            <div class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-primary-500"></div>
            </div>
        `;

        setTimeout(() => {
            const results = [
                {
                    title: 'Understanding ' + query,
                    description: 'Comprehensive analysis and insights about ' + query + ' using advanced AI processing.',
                    confidence: '98%',
                    tags: ['Research', 'Analysis']
                },
                {
                    title: 'Latest Developments in ' + query,
                    description: 'Recent updates and breakthroughs related to ' + query + ' in the field.',
                    confidence: '95%',
                    tags: ['Updates', 'News']
                },
                {
                    title: query + ' Applications',
                    description: 'Practical applications and real-world implementations of ' + query + '.',
                    confidence: '92%',
                    tags: ['Implementation', 'Practice']
                }
            ];

            searchResults.innerHTML = results.map((result, index) => `
                <div class="search-result bg-white rounded-xl p-6 shadow-sm border-l-4 border-primary-500 hover:shadow-md transition-all duration-300"
                     style="animation: slideIn 0.3s ease-out ${index * 0.1}s forwards; opacity: 0; transform: translateY(20px)">
                    <div class="flex justify-between items-start mb-3">
                        <h3 class="text-xl font-semibold text-primary-600 hover:text-primary-700">
                            ${result.title}
                        </h3>
                        <span class="text-sm font-medium text-primary-500 bg-primary-50 px-3 py-1 rounded-full">
                            ${result.confidence}
                        </span>
                    </div>
                    <p class="mt-2 text-gray-600">${result.description}</p>
                    <div class="mt-3 flex items-center justify-between">
                        <div class="flex gap-2">
                            ${result.tags.map(tag => `
                                <span class="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                                    ${tag}
                                </span>
                            `).join('')}
                        </div>
                        <div class="flex items-center space-x-3">
                            <button class="text-sm text-primary-600 hover:text-primary-700 flex items-center space-x-1">
                                <i class="fas fa-share-alt"></i>
                                <span>Share</span>
                            </button>
                            <button class="text-sm text-primary-600 hover:text-primary-700 flex items-center space-x-1">
                                <i class="fas fa-bookmark"></i>
                                <span>Save</span>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        }, 1500);
    }
});
