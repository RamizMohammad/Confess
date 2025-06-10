// Get token from URL parameters
function getTokenFromURL() {
  const urlParams = new URLSearchParams(window.location.search);
  return urlParams.get('token');
}

// Show message to user
function showMessage(text, type = 'info') {
  const messageEl = document.getElementById('message');
  messageEl.textContent = text;
  messageEl.className = `message ${type}`;
  messageEl.style.display = 'block';

  // Auto-hide success messages after 5 seconds
  if (type === 'success') {
    setTimeout(() => {
      messageEl.style.display = 'none';
    }, 5000);
  }
}

// Show loading state
function setLoading(isLoading) {
  const submitBtn = document.getElementById('submitBtn');
  const btnText = submitBtn.querySelector('.btn-text');
  const btnLoader = submitBtn.querySelector('.btn-loader');

  if (isLoading) {
    submitBtn.disabled = true;
    btnText.style.display = 'none';
    btnLoader.style.display = 'inline';
  } else {
    submitBtn.disabled = false;
    btnText.style.display = 'inline';
    btnLoader.style.display = 'none';
  }
}

// Toggle password visibility
function togglePasswordVisibility() {
  const passwordInput = document.getElementById('newPassword');
  const eyeIcon = document.querySelector('.eye-icon');
  const eyeOffIcon = document.querySelector('.eye-off-icon');

  if (passwordInput.type === 'password') {
    passwordInput.type = 'text';
    eyeIcon.style.display = 'none';
    eyeOffIcon.style.display = 'block';
  } else {
    passwordInput.type = 'password';
    eyeIcon.style.display = 'block';
    eyeOffIcon.style.display = 'none';
  }
}

// Show invalid token page
function showInvalidTokenPage() {
  const resetCard = document.getElementById('resetCard');
  const invalidTokenCard = document.getElementById('invalidTokenCard');

  if (resetCard) resetCard.style.display = 'none';
  if (invalidTokenCard) invalidTokenCard.style.display = 'block';
  document.title = 'Invalid Reset Link';
}

// Show valid form
function showResetForm() {
  const resetCard = document.getElementById('resetCard');
  const invalidTokenCard = document.getElementById('invalidTokenCard');

  if (invalidTokenCard) invalidTokenCard.style.display = 'none';
  if (resetCard) resetCard.style.display = 'block';
  document.title = 'Reset Your Password';
}

// Validate token with backend
async function validateToken(token) {
  try {
    const response = await fetch(`https://confess-ysj8.onrender.com/validate-token/${token}`);
    const data = await response.json();
    return data.valid;
  } catch (err) {
    return false;
  }
}

// Reset password function
async function resetPassword(token, newPassword) {
  try {
    setLoading(true);

    const response = await fetch('https://confess-ysj8.onrender.com/reset-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: token,
        newPassword: newPassword
      })
    });

    const data = await response.json();

    if (response.ok) {
      showMessage('Password reset successfully! You can now log in with your new password.', 'success');
      document.getElementById('resetForm').reset();
    } else {
      if (response.status === 400 || response.status === 401 || 
          (data.message && (data.message.toLowerCase().includes('token') ||
                            data.message.toLowerCase().includes('expired') ||
                            data.message.toLowerCase().includes('invalid')))) {
        showInvalidTokenPage();
      } else {
        showMessage(data.message || 'Failed to reset password. Please try again.', 'error');
      }
    }
  } catch (error) {
    console.error('Error:', error);
    showMessage('Network error. Please check your connection and try again.', 'error');
  } finally {
    setLoading(false);
  }
}

// Initialize the page
document.addEventListener('DOMContentLoaded', async () => {
  const token = getTokenFromURL();

  if (!token) {
    showInvalidTokenPage();
    return;
  }

  // Validate token from server
  const isValid = await validateToken(token);
  if (!isValid) {
    showInvalidTokenPage();
    return;
  }

  // Token is valid, show the form
  showResetForm();

  // Setup password toggle
  const togglePasswordBtn = document.getElementById('togglePassword');
  if (togglePasswordBtn) {
    togglePasswordBtn.addEventListener('click', togglePasswordVisibility);
    togglePasswordBtn.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        togglePasswordVisibility();
      }
    });
  }

  // Handle form submission
  const form = document.getElementById('resetForm');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const newPassword = document.getElementById('newPassword').value;

      if (newPassword.length < 6) {
        showMessage('Password must be at least 6 characters long.', 'error');
        return;
      }

      await resetPassword(token, newPassword);
    });
  }

  // Hide error when user types
  document.getElementById('newPassword').addEventListener('input', () => {
    const messageEl = document.getElementById('message');
    if (messageEl.classList.contains('error')) {
      messageEl.style.display = 'none';
    }
  });
});
