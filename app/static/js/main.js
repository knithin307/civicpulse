// CivicPulse Global JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 6000);
    });

    // 2. Upvote Issue AJAX Handler
    document.querySelectorAll('.btn-upvote').forEach(button => {
        button.addEventListener('click', async (e) => {
            e.preventDefault();
            const issueId = button.dataset.issueId;
            if (!issueId) return;

            try {
                const response = await fetch(`/api/v1/issues/${issueId}/upvote`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (response.status === 401) {
                    window.location.href = `/auth/login?next=${encodeURIComponent(window.location.pathname)}`;
                    return;
                }

                const data = await response.json();
                if (data.success) {
                    const countSpan = button.querySelector('.upvote-count');
                    const icon = button.querySelector('i');
                    if (countSpan) countSpan.textContent = data.upvotes_count;

                    if (data.has_upvoted) {
                        button.classList.add('btn-primary', 'active');
                        button.classList.remove('btn-outline-primary');
                        if (icon) icon.className = 'bi bi-hand-thumbs-up-fill me-1';
                    } else {
                        button.classList.remove('btn-primary', 'active');
                        button.classList.add('btn-outline-primary');
                        if (icon) icon.className = 'bi bi-hand-thumbs-up me-1';
                    }
                }
            } catch (err) {
                console.error('Failed to upvote:', err);
            }
        });
    });

    // 3. Quick Account Filler for Evaluators on Login Page
    window.fillCredentials = function(email, password) {
        const emailInput = document.getElementById('email');
        const passInput = document.getElementById('password');
        if (emailInput && passInput) {
            emailInput.value = email;
            passInput.value = password;
        }
    };
});
