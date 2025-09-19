

// Form validation and submission for signup
document.getElementById('signupForm').addEventListener('submit',async function(e) {
    e.preventDefault();
    
    const company_name = document.getElementById('companyName').value;
    // const lastName = document.getElementById('lastName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const terms = document.getElementById('terms').checked;

    // Basic validation
    if (!companyName || !email || !password) {
        alert('Please fill in all required fields.');
        return;
    }

    if (password.length < 8) {
        alert('Password must be at least 8 characters long.');
        return;
    }

    if (!terms) {
        alert('Please agree to the Terms of Service and Privacy Policy.');
        return;
    }

    console.log('Signup reached')
    const response = await fetch("http://127.0.0.1:8008/auth/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, company_name})
    });

    if (response.ok) {
        alert("User created! Now log in.");
    } else {
        const data = await response.json();
        alert("Error: " + data.detail);
    }

});

// Password strength indicator
document.getElementById('password').addEventListener('input', function(e) {
    const password = e.target.value;
    const requirements = document.querySelector('.password-requirements');
    
    if (password.length >= 8 && /[A-Za-z]/.test(password) && /[0-9]/.test(password)) {
        requirements.style.color = '#00b894';
        requirements.textContent = '✓ Password meets requirements';
    } else {
        requirements.style.color = '#666';
        requirements.textContent = 'Must be at least 8 characters with a mix of letters and numbers';
    }
});

// Social login buttons
document.querySelectorAll('.social-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        const provider = this.textContent.includes('Google') ? 'Google' : 'Facebook';
        alert(`${provider} login would be implemented here.`);
    });
});



// Smooth animations on scroll
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const header = document.querySelector('.header');
    
    if (scrolled > 50) {
        header.style.background = 'rgba(255, 255, 255, 0.98)';
        header.style.backdropFilter = 'blur(20px)';
    } else {
        header.style.background = 'rgba(255, 255, 255, 0.95)';
        header.style.backdropFilter = 'blur(10px)';
    }
});

// Display Login div
document.addEventListener('click', function (e) {
    const target = e.target;
    if (target.classList.contains('login-button')) {
        e.preventDefault();

        const action = target.dataset.action;
        const signupLoginForm = document.getElementById('signupLoginForm');
        if (action === 'login') {
            signupLoginForm.innerHTML = `
                    <h2 class="form-title">Log In</h2>
                    

                    <form id="loginForm">
                        
                        <div class="form-group full-width">
                            <label class="form-label" for="email">Email</label>
                            <input type="email" id="email" class="form-input" placeholder="you@company.com" required>
                        </div>

                        <div class="form-group full-width">
                            <label class="form-label" for="password">Password</label>
                            <input type="password" id="password" class="form-input" placeholder="Create a strong password" required>
                            <p class="password-requirements">Must be at least 8 characters with a mix of letters and numbers</p>
                        </div>



                        <button type="submit" class="submit-btn">Login</button>
                    </form>

                    <div class="divider">OR CONTINUE WITH</div>

                    <div class="social-buttons">
                        <a href="#" class="social-btn">
                            <span>🔍</span>
                            Continue with Google
                        </a>
                        <a href="#" class="social-btn">
                            <span>📘</span>
                            Continue with Facebook
                        </a>
                    </div>

                    <div class="signin-link">
                        Don't have an account? <a class="login-button" href="#" data-action="signup">Sign up</a>
                    </div>`;
        } else if (action === 'signup') {
            console.log('Switching to signup form');
            signupLoginForm.innerHTML = `<h2 class="form-title">Create Account</h2>
                <p class="form-subtitle">Start your free trial today</p>

                <form id="signupForm">
                    <div class="form-row">
                        <div class="form-group">
                            <label class="form-label" for="companyName">Company Name</label>
                            <input type="text" id="companyName" class="form-input" placeholder="John" required>
                        </div>
                    </div>

                    <div class="form-group full-width">
                        <label class="form-label" for="email">Email</label>
                        <input type="email" id="email" class="form-input" placeholder="you@company.com" required>
                    </div>

                    <div class="form-group full-width">
                        <label class="form-label" for="password">Password</label>
                        <input type="password" id="password" class="form-input" placeholder="Create a strong password" required>
                        <p class="password-requirements">Must be at least 8 characters with a mix of letters and numbers</p>
                    </div>

                    <div class="checkbox-group">
                        <input type="checkbox" id="terms" class="checkbox" required>
                        <label for="terms" class="checkbox-label">
                            I agree to the <a href="#">Terms of Service</a> and <a href="#">Privacy Policy</a>
                        </label>
                    </div>

                    <button type="submit" class="submit-btn">Start Free Trial →</button>
                </form>

                <div class="divider">OR CONTINUE WITH</div>

                <div class="social-buttons">
                    <a href="#" class="social-btn">
                        <span>🔍</span>
                        Continue with Google
                    </a>
                    <a href="#" class="social-btn">
                        <span>📘</span>
                        Continue with Facebook
                    </a>
                </div>

                <div class="signin-link">
                    Already have an account? <a class="login-button" href="#" data-action="login" href="#">Log in</a>
                </div>`;
        }}

    })

    document.addEventListener("submit", async function (e) {
        if (e.target && e.target.id === "loginForm") {
            e.preventDefault();
    
            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;
    
            const formData = new FormData();
            formData.append("username", email);
            formData.append("password", password);
            console.log("Login form submitted with data:")
            try {
                const res = await fetch("/auth/token", {
                    method: "POST",
                    body: formData
                });
    
                if (!res.ok) {
                    const error = await res.json();
                    alert(error.detail || "Login failed");
                    return;
                }
    
                const data = await res.json();
                localStorage.setItem("token", data.access_token);
                console.log("Login successful, token stored:", data.access_token);
                console.log(data);
            
                window.location.href = "/dashboard";
            } catch (err) {
                console.error(err);
                alert("Something went wrong!");
            }
        }
    });
    