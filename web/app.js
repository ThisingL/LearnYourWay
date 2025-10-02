// API 配置
const API_BASE_URL = 'http://localhost:8000';

// 全局状态
let currentProfile = {
    user_id: 'demo_user',  // 使用下划线命名，匹配后端
    grade: 5,
    interests: ['足球', '科学实验', '恐龙']
};

let generatedResults = {
    quiz: null,
    mindmap: null,
    immersive: null
};

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    loadProfile();
    setupInterestInput();
    
    // 显示默认兴趣标签
    renderInterestTags();
});

// ============ 用户画像管理 ============

function setupInterestInput() {
    const input = document.getElementById('interestInput');
    input.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && this.value.trim()) {
            const interest = this.value.trim();
            if (!currentProfile.interests.includes(interest)) {
                currentProfile.interests.push(interest);
                renderInterestTags();
            }
            this.value = '';
        }
    });
}

function renderInterestTags() {
    const container = document.getElementById('interestTags');
    container.innerHTML = currentProfile.interests.map((interest, index) => `
        <span class="interest-tag">
            ${interest}
            <button onclick="removeInterest(${index})" class="ml-2 text-purple-800 hover:text-purple-900">×</button>
        </span>
    `).join('');
}

function removeInterest(index) {
    currentProfile.interests.splice(index, 1);
    renderInterestTags();
}

function loadProfile() {
    const saved = localStorage.getItem('learnyourway_profile');
    if (saved) {
        currentProfile = JSON.parse(saved);
        document.getElementById('userId').value = currentProfile.user_id;
        document.getElementById('grade').value = currentProfile.grade;
        renderInterestTags();
    }
}

async function saveProfile() {
    currentProfile.user_id = document.getElementById('userId').value;
    currentProfile.grade = parseInt(document.getElementById('grade').value);
    
    if (currentProfile.interests.length === 0) {
        alert('请至少添加一个兴趣爱好！');
        return;
    }
    
    try {
        showLoading();
        
        const response = await axios.post(`${API_BASE_URL}/profiles`, currentProfile);
        
        if (response.data.code === 0) {
            localStorage.setItem('learnyourway_profile', JSON.stringify(currentProfile));
            showProfileStatus('✅ 画像保存成功！', 'success');
        }
    } catch (error) {
        console.error('保存画像失败:', error);
        
        // 更详细的错误信息
        let errorMsg = '未知错误';
        if (error.response) {
            // 服务器返回了错误响应
            if (error.response.data?.detail) {
                errorMsg = error.response.data.detail;
            } else if (typeof error.response.data === 'string') {
                errorMsg = error.response.data;
            } else {
                errorMsg = `HTTP ${error.response.status}: ${error.response.statusText}`;
            }
        } else if (error.message) {
            errorMsg = error.message;
        }
        
        showProfileStatus('❌ 保存失败：' + errorMsg, 'error');
        
        // 同时在控制台显示完整错误
        console.log('完整错误信息:', {
            status: error.response?.status,
            data: error.response?.data,
            message: error.message
        });
    } finally {
        hideLoading();
    }
}

function showProfileStatus(message, type) {
    const status = document.getElementById('profileStatus');
    status.textContent = message;
    status.className = type === 'success' ? 'ml-4 text-sm text-green-600' : 'ml-4 text-sm text-red-600';
    setTimeout(() => {
        status.textContent = '';
    }, 3000);
}

// ============ PDF 上传 ============

async function handlePDFUpload(input) {
    const file = input.files[0];
    if (!file) return;
    
    // 显示文件名
    const fileNameDiv = document.getElementById('pdfFileName');
    fileNameDiv.textContent = `📄 ${file.name}`;
    fileNameDiv.classList.remove('hidden');
    
    // 显示上传状态
    const statusDiv = document.getElementById('pdfUploadStatus');
    statusDiv.classList.remove('hidden');
    updatePDFStatus('正在上传 PDF...', 10);
    
    try {
        // 创建 FormData
        const formData = new FormData();
        formData.append('file', file);
        
        // 上传 PDF
        const uploadResponse = await axios.post(
            `${API_BASE_URL}/ingest/pdf`,
            formData,
            {
                headers: { 'Content-Type': 'multipart/form-data' }
            }
        );
        
        if (uploadResponse.data.code === 0) {
            const taskId = uploadResponse.data.data.task_id;
            updatePDFStatus('解析中...', 30);
            
            // 轮询任务状态
            await pollPDFTask(taskId);
        } else {
            throw new Error(uploadResponse.data.message || '上传失败');
        }
        
    } catch (error) {
        console.error('PDF 上传失败:', error);
        updatePDFStatus('❌ 上传失败：' + (error.response?.data?.detail || error.message), 0);
        
        setTimeout(() => {
            statusDiv.classList.add('hidden');
        }, 3000);
    }
}

async function pollPDFTask(taskId, maxAttempts = 30) {
    const statusDiv = document.getElementById('pdfUploadStatus');
    
    for (let i = 0; i < maxAttempts; i++) {
        try {
            const response = await axios.get(`${API_BASE_URL}/ingest/tasks/${taskId}`);
            const taskData = response.data.data;
            
            // 更新进度
            updatePDFStatus(
                taskData.stage || '处理中...',
                taskData.progress || 50
            );
            
            if (taskData.status === 'success') {
                // 解析成功
                updatePDFStatus('✅ 解析完成！', 100);
                
                console.log('PDF 解析结果:', taskData.result);
                
                // 提取文本内容填入输入框
                let extractedText = '';
                
                if (taskData.result) {
                    // 方式1: 如果有 chunks 数组
                    if (taskData.result.chunks && Array.isArray(taskData.result.chunks)) {
                        extractedText = taskData.result.chunks
                            .map(chunk => chunk.text || chunk)
                            .join('\n\n');
                    }
                    // 方式2: 如果直接是 filename 和 total_pages
                    else if (taskData.result.filename) {
                        extractedText = `PDF 文件：${taskData.result.filename}\n总页数：${taskData.result.total_pages}\n\n提取的文本将显示在这里...`;
                    }
                    // 方式3: 如果是其他格式
                    else if (typeof taskData.result === 'string') {
                        extractedText = taskData.result;
                    }
                }
                
                // 填入文本框
                if (extractedText) {
                    document.getElementById('contentInput').value = extractedText;
                    console.log('已填充文本，长度:', extractedText.length);
                } else {
                    console.warn('⚠️ 无法提取文本内容，result 格式:', taskData.result);
                    document.getElementById('contentInput').value = '⚠️ PDF 已上传，但暂时无法提取文本内容。请手动输入学习内容。';
                }
                
                // 立即隐藏状态栏（不延迟）
                setTimeout(() => {
                    statusDiv.classList.add('hidden');
                }, 1500);
                
                return;
            } else if (taskData.status === 'failure') {
                throw new Error(taskData.error || '解析失败');
            }
            
            // 等待 2 秒后继续轮询
            await new Promise(resolve => setTimeout(resolve, 2000));
            
        } catch (error) {
            console.error('查询任务失败:', error);
            updatePDFStatus('❌ 解析失败：' + error.message, 0);
            
            setTimeout(() => {
                statusDiv.classList.add('hidden');
            }, 3000);
            return;
        }
    }
    
    // 超时
    updatePDFStatus('⚠️ 解析超时，请重试', 0);
    setTimeout(() => {
        statusDiv.classList.add('hidden');
    }, 3000);
}

function updatePDFStatus(text, progress) {
    document.getElementById('pdfStatusText').textContent = text;
    document.getElementById('pdfProgressBar').style.width = progress + '%';
}

// ============ 内容生成 ============

async function generateQuiz() {
    const content = document.getElementById('contentInput').value.trim();
    if (!content) {
        alert('请先输入学习内容！');
        return;
    }
    
    try {
        showLoading();
        
        const response = await axios.post(`${API_BASE_URL}/materials/quiz`, {
            chunk_id: 'web_' + Date.now(),
            profile_id: currentProfile.user_id,
            content: content,
            count: 5
        });
        
        if (response.data.code === 0) {
            generatedResults.quiz = response.data.data;
            renderQuizResults(response.data.data);
            showResults();
            switchTab('quiz');
        }
    } catch (error) {
        console.error('生成测验题失败:', error);
        alert('生成失败：' + (error.response?.data?.detail || error.message));
    } finally {
        hideLoading();
    }
}

async function generateMindmap() {
    const content = document.getElementById('contentInput').value.trim();
    if (!content) {
        alert('请先输入学习内容！');
        return;
    }
    
    try {
        showLoading();
        
        const response = await axios.post(`${API_BASE_URL}/materials/mindmap`, {
            chunk_id: 'web_' + Date.now(),
            profile_id: currentProfile.user_id,
            content: content
        });
        
        if (response.data.code === 0) {
            generatedResults.mindmap = response.data.data;
            renderMindmap(response.data.data);
            showResults();
            switchTab('mindmap');
        }
    } catch (error) {
        console.error('生成思维导图失败:', error);
        alert('生成失败：' + (error.response?.data?.detail || error.message));
    } finally {
        hideLoading();
    }
}

async function generateImmersive() {
    const content = document.getElementById('contentInput').value.trim();
    if (!content) {
        alert('请先输入学习内容！');
        return;
    }
    
    try {
        showLoading();
        
        const response = await axios.post(`${API_BASE_URL}/materials/immersive`, {
            chunk_id: 'web_' + Date.now(),
            profile_id: currentProfile.user_id,
            content: content
        });
        
        if (response.data.code === 0) {
            generatedResults.immersive = response.data.data;
            renderImmersiveText(response.data.data);
            showResults();
            switchTab('immersive');
        }
    } catch (error) {
        console.error('生成沉浸式文本失败:', error);
        alert('生成失败：' + (error.response?.data?.detail || error.message));
    } finally {
        hideLoading();
    }
}

async function generateAll() {
    const content = document.getElementById('contentInput').value.trim();
    if (!content) {
        alert('请先输入学习内容！');
        return;
    }
    
    try {
        showLoading();
        
        // 并发生成所有素材
        const [quizRes, mindmapRes, immersiveRes] = await Promise.all([
            axios.post(`${API_BASE_URL}/materials/quiz`, {
                chunk_id: 'web_' + Date.now(),
                profile_id: currentProfile.user_id,
                content: content,
                count: 5
            }),
            axios.post(`${API_BASE_URL}/materials/mindmap`, {
                chunk_id: 'web_' + Date.now(),
                profile_id: currentProfile.user_id,
                content: content
            }),
            axios.post(`${API_BASE_URL}/materials/immersive`, {
                chunk_id: 'web_' + Date.now(),
                profile_id: currentProfile.user_id,
                content: content
            })
        ]);
        
        generatedResults.quiz = quizRes.data.data;
        generatedResults.mindmap = mindmapRes.data.data;
        generatedResults.immersive = immersiveRes.data.data;
        
        renderQuizResults(quizRes.data.data);
        renderMindmap(mindmapRes.data.data);
        renderImmersiveText(immersiveRes.data.data);
        
        showResults();
        switchTab('quiz');
        
    } catch (error) {
        console.error('生成失败:', error);
        alert('生成失败：' + (error.response?.data?.detail || error.message));
    } finally {
        hideLoading();
    }
}

// ============ 结果渲染 ============

function renderQuizResults(data) {
    const container = document.getElementById('quizResults');
    
    const html = data.questions.map((q, index) => {
        const typeLabels = {
            'single': '单选题',
            'multi': '多选题',
            'tf': '判断题',
            'short': '简答题'
        };
        
        const difficultyStars = '⭐'.repeat(q.difficulty);
        
        let optionsHtml = '';
        if (q.options && q.options.length > 0) {
            optionsHtml = q.options.map(opt => `
                <div class="ml-4 py-1">${opt}</div>
            `).join('');
        }
        
        let answerDisplay = q.answer;
        if (Array.isArray(q.answer)) {
            answerDisplay = q.answer.join('、');
        } else if (typeof q.answer === 'boolean') {
            answerDisplay = q.answer ? '✓ 正确' : '✗ 错误';
        }
        
        return `
            <div class="mb-6 p-5 border border-gray-200 rounded-lg hover:border-blue-300 transition">
                <div class="flex items-center justify-between mb-3">
                    <span class="text-sm font-medium px-3 py-1 bg-blue-100 text-blue-800 rounded-full">
                        ${typeLabels[q.type]}
                    </span>
                    <span class="text-sm text-gray-500">
                        难度：${difficultyStars}
                    </span>
                </div>
                
                <h4 class="text-lg font-semibold mb-3">
                    ${index + 1}. ${q.stem}
                </h4>
                
                ${optionsHtml}
                
                <details class="mt-3">
                    <summary class="cursor-pointer text-sm text-gray-600 hover:text-blue-600">
                        查看答案和解析 👇
                    </summary>
                    <div class="mt-2 p-3 bg-green-50 rounded border-l-4 border-green-500">
                        <p class="font-medium text-green-800">答案：${answerDisplay}</p>
                        <p class="text-gray-700 mt-2">${q.explanation}</p>
                    </div>
                </details>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `
        <div class="mb-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded">
            <p class="font-medium text-blue-900">✅ 成功生成 ${data.questions.length} 道测验题</p>
        </div>
        ${html}
    `;
}

function renderMindmap(data) {
    const chartDom = document.getElementById('mindmapChart');
    
    // 如果已经有实例，先销毁
    if (window.mindmapChart && typeof window.mindmapChart.dispose === 'function') {
        window.mindmapChart.dispose();
    }
    
    const myChart = echarts.init(chartDom);
    window.mindmapChart = myChart;
    
    // 转换数据格式为 ECharts 需要的格式
    const nodes = data.nodes.map(node => ({
        name: node.label,
        id: node.id,
        symbolSize: node.type === 'root' ? 100 : node.type === 'concept' ? 70 : 50,
        itemStyle: {
            color: node.type === 'root' ? '#667eea' : node.type === 'concept' ? '#48bb78' : '#ed8936',
            borderColor: '#fff',
            borderWidth: 3,
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.3)'
        },
        label: {
            show: true,
            fontSize: node.type === 'root' ? 16 : node.type === 'concept' ? 14 : 12,
            fontWeight: node.type === 'root' ? 'bold' : 'normal',
            color: '#fff'
        }
    }));
    
    const links = data.edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        label: {
            show: true,
            formatter: edge.label,
            fontSize: 11,
            color: '#666'
        },
        lineStyle: {
            curveness: 0.2
        }
    }));
    
    const option = {
        title: {
            text: '知识结构思维导图',
            subtext: '可拖拽、缩放查看',
            left: 'center',
            top: 20,
            textStyle: {
                fontSize: 22,
                fontWeight: 'bold',
                color: '#333'
            },
            subtextStyle: {
                fontSize: 14,
                color: '#999'
            }
        },
        tooltip: {
            trigger: 'item',
            formatter: '{b}',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            textStyle: {
                color: '#fff'
            }
        },
        series: [{
            type: 'graph',
            layout: 'force',
            data: nodes,
            links: links,
            roam: true,  // 允许缩放和拖拽
            draggable: true,
            focusNodeAdjacency: true,  // 高亮相邻节点
            force: {
                repulsion: 800,      // 增大斥力，让节点分散
                gravity: 0.05,       // 降低重力
                edgeLength: 200,     // 增大边长
                layoutAnimation: true,
                friction: 0.2        // 减小摩擦力，让布局更自由
            },
            lineStyle: {
                color: '#999',
                width: 2,
                curveness: 0.3,
                opacity: 0.8
            },
            emphasis: {
                focus: 'adjacency',
                lineStyle: {
                    width: 4
                },
                itemStyle: {
                    shadowBlur: 20
                }
            }
        }]
    };
    
    myChart.setOption(option);
    
    // 窗口大小改变时自动调整
    window.addEventListener('resize', () => {
        myChart.resize();
    });
}

function renderImmersiveText(data) {
    const container = document.getElementById('immersiveResults');
    
    const html = data.sections.map((section, index) => {
        const paragraphsHtml = section.paragraphs.map(p => {
            // 检测插图占位符
            const imageMatch = p.match(/\{\{image:(.*?)\}\}/);
            if (imageMatch) {
                return `
                    <div class="my-4 p-4 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 text-center">
                        <svg class="w-16 h-16 mx-auto text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                        </svg>
                        <p class="text-gray-600 mt-2">📸 ${imageMatch[1]}</p>
                    </div>
                `;
            }
            return `<p class="mb-4 leading-relaxed">${p}</p>`;
        }).join('');
        
        return `
            <div class="mb-8">
                <h3 class="text-2xl font-bold mb-4 text-gray-800 border-l-4 border-orange-500 pl-4">
                    ${section.title}
                </h3>
                <div class="text-gray-700 text-lg leading-loose">
                    ${paragraphsHtml}
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `
        <div class="mb-4 p-4 bg-orange-50 border-l-4 border-orange-500 rounded">
            <p class="font-medium text-orange-900">✅ 成功生成 ${data.sections.length} 个章节的沉浸式文本</p>
        </div>
        <div class="prose prose-lg max-w-none">
            ${html}
        </div>
    `;
}

// ============ UI 控制 ============

function switchTab(tabName) {
    // 移除所有 active 状态
    document.querySelectorAll('[id^="tab-"]').forEach(tab => {
        tab.classList.remove('tab-active', 'text-blue-600', 'text-green-600', 'text-orange-600');
        tab.classList.add('text-gray-600');
    });
    
    // 隐藏所有内容
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.add('hidden');
    });
    
    // 激活选中的 tab
    const activeTab = document.getElementById(`tab-${tabName}`);
    activeTab.classList.add('tab-active');
    
    if (tabName === 'quiz') activeTab.classList.add('text-blue-600');
    if (tabName === 'mindmap') activeTab.classList.add('text-green-600');
    if (tabName === 'immersive') activeTab.classList.add('text-orange-600');
    
    // 显示对应内容
    document.getElementById(`content-${tabName}`).classList.remove('hidden');
}

function showResults() {
    document.getElementById('resultsContainer').classList.remove('hidden');
    // 平滑滚动到结果区域
    document.getElementById('resultsContainer').scrollIntoView({ behavior: 'smooth' });
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

// ============ 工具函数 ============

// 复制文本到剪贴板
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('已复制到剪贴板！');
    });
}

// 导出为 Markdown
function exportAsMarkdown() {
    let markdown = `# LearnYourWay 生成结果\n\n`;
    markdown += `**学习者**：${currentProfile.user_id}\n`;
    markdown += `**年级**：${currentProfile.grade} 年级\n`;
    markdown += `**兴趣**：${currentProfile.interests.join('、')}\n\n`;
    
    if (generatedResults.quiz) {
        markdown += `## 测验题\n\n`;
        generatedResults.quiz.questions.forEach((q, i) => {
            markdown += `### ${i+1}. ${q.stem}\n\n`;
            if (q.options) {
                q.options.forEach(opt => {
                    markdown += `- ${opt}\n`;
                });
            }
            markdown += `\n**答案**：${q.answer}\n\n`;
            markdown += `**解析**：${q.explanation}\n\n`;
        });
    }
    
    const blob = new Blob([markdown], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'learnyourway_result.md';
    a.click();
}
