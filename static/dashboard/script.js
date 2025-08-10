
document.addEventListener("DOMContentLoaded", async () => {
    const token = localStorage.getItem("token");
    if (!token) {
        // Not logged in
        window.location.href = "/login.html";
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
            window.location.href = "/login.html";
            return;
        }

        const data = await res.json();
        document.getElementById("welcome").textContent = `Welcome, ${data.username}`;
    } catch (err) {
        console.error(err);
        window.location.href = "/login.html";
    }
});
