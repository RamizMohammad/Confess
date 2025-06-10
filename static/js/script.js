// Extract token from URL path
function getTokenFromURL() {
  const pathSegments = window.location.pathname.split('/');
  // Expected URL: /reset-password/{token}
  return pathSegments[pathSegments.length - 1];
}

// Display messages
function showMessage(text, type = 'info') {
  const messageEl = document.getElementById('message');
  messageEl.textContent = text;
  messageEl.className = `message ${type}`;
  messageEl.style.display = 'block';

  if (type === 'success') {
    setTimeout(() => {
      messageEl.style.display = 'none';
    }, 5000);
  }
}

// Set loading state
function setLoading(isLoading) {
  const submitBtn = document.getElementById('submitBtn');
  const btnText = submitBtn.querySelector('.btn-text');
  const btnLoader = submitBtn.querySelector('.btn-loader');

  submitBtn.disabled = isLoading;
  btnText.style.display = isLoading ? 'none' : 'inline';
  btnLoader.style.display = isLoading ? 'inline' : 'none';
}

// Validate token via backend
async function validateToken(token) {
  try {
    const response = await fetch(`https://confess-ysj8.onrender.com/validate-token/${token}`);
    const result = await response.json();

    if (!result.valid) {
      showMessage(result.message || 'Invalid or expired token.', 'error');
      document.getElementById('resetForm').style.display = 'none';
    }
  } catch (error) {
    console.error("Token validation error:", error);
    showMessage("Token validation failed. Try again later.", 'error');
    document.getElementById('resetForm').style.display = 'none';
  }
}

// Submit new password
async function resetPassword(token, newPassword) {
  try {
    setLoading(true);
    const response = await fetch('https://confess-ysj8.onrender.com/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, newPassword })
    });

    const data = await response.json();

    if (response.ok) {
      showMessage('Password reset successfully! You can now log in.', 'success');
      document.getElementById('resetForm').reset();
    } else {
      showMessage(data.message || 'Failed to reset password.', 'error');
    }
  } catch (err) {
    console.error("Reset error:", err);
    showMessage('Network error. Try again later.', 'error');
  } finally {
    setLoading(false);
  }
}

// Initialize the form logic
document.addEventListener('DOMContentLoaded', () => {
  const token = getTokenFromURL();

  if (!token || token === 'reset-password') {
    showMessage('Missing or invalid reset token.', 'error');
    document.getElementById('resetForm').style.display = 'none';
    return;
  }

  validateToken(token);

  const form = document.getElementById('resetForm');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const newPassword = document.getElementById('newPassword').value;

    if (newPassword.length < 6) {
      showMessage('Password must be at least 6 characters.', 'error');
      return;
    }

    await resetPassword(token, newPassword);
  });

  document.getElementById('newPassword').addEventListener('input', () => {
    const msg = document.getElementById('message');
    if (msg.classList.contains('error')) msg.style.display = 'none';
  });
});
