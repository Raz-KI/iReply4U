
document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");
    if (!token) {
        return;
    }
    
    try {
        const res = await fetch("/dashboard-data", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });

        if (!res.ok) {
            // Token invalid or expired
            localStorage.removeItem("token");
            // window.location.href = "/login.html";
            return;
        }

        const data = await res.json();
        console.log(data)
        document.getElementById("companyName").textContent = `${data.company_name}`;
        document.getElementById("search-count").textContent = `${data.search_count}`;
        document.getElementById("reply-count").textContent = `${data.reply_count}`;
    } catch (err) {
        console.error(err);
        // window.location.href = "/login.html";
    }
// });
// document.addEventListener('DOMContentLoaded', async function () {
    // const token = localStorage.getItem("token");
    //=========== GLOBAL ELEMENT SELECTORS & STATE ===========//
    const newSearchModal = document.getElementById('newSearchModal');
    const viewEditModal = document.getElementById('viewEditModal');
    const newSearchBtn = document.getElementById('newSearchBtn');
    const newSearchForm = document.getElementById('newSearchForm');
    const queriesTbody = document.getElementById('queries-tbody');
    const repliesTbody = document.getElementById('replies-tbody');
    
    const approveReplyBtn = document.getElementById('approveReplyBtn');
    const postReplyBtn = document.getElementById('postReplyBtn');
    
    let currentlyEditingRow = null; // Variable to store the table row being edited
    
    //=========== HELPER FUNCTIONS ===========//
    const truncateText = (text, maxLength) => {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength) + '...';
    };
    
    //=========== MODAL INTERACTIVITY ===========//
    function openModal(modal) {
        if (modal) modal.classList.add('active');
    }
    
    function closeModal(modal) {
        if (modal) {
            modal.classList.remove('active');
            if (modal === viewEditModal) {
                currentlyEditingRow = null; // Reset the editing state when modal closes
            }
        }
    }
    // Retrieve existing queries from the server
    try {
        const res = await fetch("/api/get_queries", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (!res.ok) {
            const errText = await res.text();
            alert("Error fetching queries: " + errText);
            return;
        }
        else {
            const data = await res.json();
            if (data && data.queries) {
                data.queries.forEach(query => {
                    const platformInfo = {
                        reddit: { icon: 'bxl-reddit', name: 'Reddit' },
                        linkedin: { icon: 'bxl-linkedin-square', name: 'LinkedIn' },
                        twitter: { icon: 'bxl-twitter', name: 'X/Twitter' },
                        facebook: { icon: 'bxl-facebook-square', name: 'Facebook' },
                    };
                    const newRow = document.createElement('tr');
                    newRow.innerHTML = `
                        <td><i class='bx ${platformInfo[query.platform].icon}'></i> ${platformInfo[query.platform].name}</td>
                        <td>${query.id}</td>
                        <td><span class="status-badge ${query.is_active ? 'status-active' : 'status-paused'}">${query.is_active ? 'Active' : 'Paused'}</span></td>
                        <td>${query.product_name}</td>
                        <td>${query.product_desc}</td>
                        <td>${query.product_link}</td>
                        <td>
                            <button class="btn btn-secondary btn-pause-resume">${query.is_active ? 'Pause' : 'Resume'}</button>
                            <button class="btn btn-danger btn-delete">Delete</button>
                        </td>
                    `;
                    queriesTbody.appendChild(newRow);
                });
            }
        }
    } catch (err) {
        console.error("Error fetching queries:", err);
        alert("Could not connect to server.");
    }
    
    if(newSearchBtn) newSearchBtn.addEventListener('click', () => openModal(newSearchModal));
    
    document.querySelectorAll('.modal-overlay, .close-modal-btn').forEach(el => {
        el.addEventListener('click', (event) => {
            if (event.target === el || event.target.closest('.close-modal-btn')) {
                closeModal(newSearchModal);
                closeModal(viewEditModal);
            }
        });
    });
    
    //=========== ACTIVE SEARCH QUERIES LOGIC ===========//
    if (newSearchForm) {
        newSearchForm.addEventListener('submit',async function(event) {
            event.preventDefault(); 
            const platformSelect = document.getElementById('platform');
            const keywordsInput = document.getElementById('keywords');
            const activeToggle = document.getElementById('active-toggle');
            const productNameInput = document.getElementById('productName');
            const linkInput = document.getElementById('websiteLink');
            const platform = platformSelect.value;
            const productName = productNameInput.value;
            const link = linkInput.value;
            const keywords = keywordsInput.value;
            const isActive = activeToggle.checked;
    
            if (!keywords.trim()) {
                alert('Please enter keywords.');
                return;
            }
            const platformInfo = {
                reddit: { icon: 'bxl-reddit', name: 'Reddit' },
                linkedin: { icon: 'bxl-linkedin-square', name: 'LinkedIn' },
                twitter: { icon: 'bxl-twitter', name: 'X/Twitter' },
                facebook: { icon: 'bxl-facebook-square', name: 'Facebook' },
            };
            try {
                const res = await fetch("/api/new_query", {
                    method: "POST",
                    headers: {
                        // Whenever authenticated route is accessed, we need to send the token
                        "Authorization": `Bearer ${token}`,
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        platform: platform,
                        product_name: productName,
                        keywords: keywords,
                        link: link,
                        is_active: isActive,
                    })
                    
                    
                });
                const data = await res.json();
    
                if (!res.ok) {
                    const errText = await res.text();
                    alert("Error: " + errText);
                    return;
                }
    
                
    
                //  Update UI only after backend confirms
                const platformInfo = {
                    reddit: { icon: 'bxl-reddit', name: 'Reddit' },
                    linkedin: { icon: 'bxl-linkedin-square', name: 'LinkedIn' },
                    twitter: { icon: 'bxl-twitter', name: 'X/Twitter' },
                    facebook: { icon: 'bxl-facebook-square', name: 'Facebook' },
                };
    
                const newRow = document.createElement('tr');
                newRow.innerHTML = `
                    <td><i class='bx ${platformInfo[platform].icon}'></i> ${platformInfo[platform].name}</td>
                    <td>${data.query_id}</td>
                    <td><span class="status-badge ${isActive ? 'status-active' : 'status-paused'}">${isActive ? 'Active' : 'Paused'}</span></td>
                    <td>${productName}</td>
                    <td>${keywords}</td>
                    <td>${link}</td>
                    <td>
                        <button class="btn btn-secondary btn-pause-resume">${isActive ? 'Pause' : 'Resume'}</button>
                        <button class="btn btn-danger btn-delete">Delete</button>
                    </td>
                `;
                queriesTbody.prepend(newRow);
                newSearchForm.reset();
                closeModal(newSearchModal);
    
            } catch (err) {
                console.error("Network error:", err);
                alert("Could not connect to server.");
            }
        });
    }
    
    if (queriesTbody) {
        queriesTbody.addEventListener('click', function(event) {
            const target = event.target;
            const row = target.closest('tr'); 
            if (target.classList.contains('btn-pause-resume')) {
                const statusBadge = row.querySelector('.status-badge');
                if (target.textContent === 'Pause') {
                    target.textContent = 'Resume';
                    statusBadge.textContent = 'Paused';
                    statusBadge.classList.replace('status-active', 'status-paused');
                } else {
                    target.textContent = 'Pause';
                    statusBadge.textContent = 'Active';
                    statusBadge.classList.replace('status-paused', 'status-active');
                }
            }
            if (target.classList.contains('btn-delete')) {
                if (confirm('Are you sure you want to delete this query?')) {
                    row.remove();
                }
            }
        });
    }
    
    try {
        const res = await fetch("/api/get_replies", {
            method: "GET",
            headers: {
                "Authorization": `Bearer ${token}`
            }
        });
        if (!res.ok) throw new Error("Failed to fetch replies");
        const data = await res.json();

        const tbody = document.getElementById("replies-tbody");
        tbody.innerHTML = ""; 

        data.replies.forEach(reply => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td><i class='bx bxl-${reply.platform.toLowerCase()}'></i> ${reply.platform}</td>
                <td class="post-preview" data-full-text="${reply.post_preview}">
                    ${truncateText(reply.post_preview, 50)}
                </td>
                <td class="reply-preview" data-full-text="${reply.reply_preview}">
                    ${truncateText(reply.reply_preview, 50)}
                </td>
                <td><span class="status-badge status-${reply.status.toLowerCase()}">${reply.status}</span></td>
                <td>${reply.date}</td>
                <td><button class="btn btn-secondary btn-view-edit">View</button></td>
            `;
            tbody.appendChild(row);
        });
    } catch (err) {
        console.error("Error loading replies:", err);
    }
    if (repliesTbody) {
        repliesTbody.addEventListener('click', function(event) {
            const target = event.target;
            if (target.classList.contains('btn-view-edit')) {
                const row = target.closest('tr');
                currentlyEditingRow = row; // **IMPORTANT: Store the row we are editing**
    
                const postCell = row.querySelector('.post-preview');
                const replyCell = row.querySelector('.reply-preview');
                
                // Use data-attribute for full text, fallback to textContent
                const fullPostText = postCell.dataset.fullText || postCell.textContent;
                const fullReplyText = replyCell.dataset.fullText || replyCell.textContent;
                
                document.getElementById('view-post-text').value = fullPostText;
                document.getElementById('view-reply-text').value = fullReplyText;

                document.getElementById('view-post-text').readOnly = true;
                document.getElementById('view-reply-text').readOnly = true;
                
                openModal(viewEditModal);
            }
        });
    }
    
    // Function to handle updating the reply (Approve or Post)
    function handleReplyUpdate(action) {
        if (!currentlyEditingRow) return;
    
        const newReplyText = document.getElementById('view-reply-text').value;
        const replyPreviewCell = currentlyEditingRow.querySelector('.reply-preview');
        const statusBadge = currentlyEditingRow.querySelector('.status-badge');
    
        // Update the table cell with new (truncated) text
        replyPreviewCell.textContent = truncateText(newReplyText, 35);
        // Store the full text in the data-attribute
        replyPreviewCell.dataset.fullText = newReplyText;
        
        // Update the status badge based on the action
        statusBadge.className = 'status-badge'; // Reset classes
        if (action === 'approve') {
            statusBadge.classList.add('status-approved');
            statusBadge.textContent = 'Approved';
        } else if (action === 'post') {
            statusBadge.classList.add('status-posted');
            statusBadge.textContent = 'Posted';
        }
    
        closeModal(viewEditModal);
    }
    
    // Add listeners to the modal's action buttons
    if(approveReplyBtn) approveReplyBtn.addEventListener('click', () => handleReplyUpdate('approve'));
    if(postReplyBtn) postReplyBtn.addEventListener('click', () => handleReplyUpdate('post'));
    
    
    //=========== ENGAGEMENT CHART (Chart.js) ===========//
    const ctx = document.getElementById('engagementChart');
    if (ctx) {
        const chartCanvas = ctx.getContext('2d');
        const gradient = chartCanvas.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(125, 65, 232, 0.5)');
        gradient.addColorStop(1, 'rgba(125, 65, 232, 0)');
    
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'],
                datasets: [{
                    label: 'Engagement Rate',
                    data: [11.5, 12, 11.8, 13, 12.8, 13.5, 13.2, 12.5],
                    borderColor: '#7D41E8',
                    borderWidth: 3,
                    pointBackgroundColor: '#FFFFFF',
                    pointBorderColor: '#7D41E8',
                    pointHoverRadius: 7,
                    pointHoverBorderWidth: 3,
                    pointRadius: 5,
                    tension: 0.4,
                    fill: true,
                    backgroundColor: gradient
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        grid: { color: '#322F46' },
                        ticks: {
                            color: '#A09FB1',
                            callback: value => value + '%'
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#A09FB1' }
                    }
                }
            }
        });
    }
    });