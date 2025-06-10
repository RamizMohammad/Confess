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
  
  resetCard.style.display = 'none';
  invalidTokenCard.style.display = 'block';
  
  // Update page title
  document.title = 'Invalid Reset Link';
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
      // Check if it's a token-related error
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
document.addEventListener('DOMContentLoaded', () => {
  const token = getTokenFromURL();
  
  // Check if token exists
  if (!token) {
    showInvalidTokenPage();
    return;
  }
  
  // Setup password toggle functionality
  const togglePasswordBtn = document.getElementById('togglePassword');
  if (togglePasswordBtn) {
    togglePasswordBtn.addEventListener('click', togglePasswordVisibility);
  }
  
  // Handle form submission
  const form = document.getElementById('resetForm');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const newPassword = document.getElementById('newPassword').value;
    
    // Basic validation
    if (newPassword.length < 6) {
      showMessage('Password must be at least 6 characters long.', 'error');
      return;
    }
    
    await resetPassword(token, newPassword);
  });
  
  // Clear messages when user starts typing
  document.getElementById('newPassword').addEventListener('input', () => {
    const messageEl = document.getElementById('message');
    if (messageEl.classList.contains('error')) {
      messageEl.style.display = 'none';
    }
  });
  
  // Add keyboard support for password toggle
  document.getElementById('togglePassword').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      togglePasswordVisibility();
    }
  });
});