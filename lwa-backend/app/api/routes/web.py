from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["web"])

NAV = """
<nav style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px">
  <a href="/dashboard">Dashboard</a>
  <a href="/upload">Upload</a>
  <a href="/generate">Generate</a>
  <a href="/history">History</a>
  <a href="/batches">Batches</a>
  <a href="/campaigns">Campaigns</a>
  <a href="/wallet">Wallet</a>
  <a href="/settings">Settings</a>
</nav>
"""


def shell(title: str, body: str, script: str = "") -> HTMLResponse:
    return HTMLResponse(
        f"""
        <html>
          <head>
            <title>{title}</title>
            <style>
              body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #07090f; color: #f6f8ff; margin: 0; padding: 32px; }}
              a {{ color: #56d9d3; text-decoration: none; }}
              input, textarea, button, select {{ width: 100%; padding: 12px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.12); background: rgba(255,255,255,0.06); color: white; margin-top: 8px; }}
              button {{ cursor: pointer; background: linear-gradient(135deg,#2ad2ff,#8f87ff); color: #071018; font-weight: 700; }}
              .card {{ max-width: 880px; margin: 0 auto; background: rgba(255,255,255,0.05); padding: 24px; border-radius: 24px; }}
              pre {{ white-space: pre-wrap; background: rgba(255,255,255,0.05); padding: 16px; border-radius: 16px; }}
              .row {{ display:grid; gap:16px; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); }}
            </style>
          </head>
          <body>
            <div class="card">
              {NAV}
              <h1>{title}</h1>
              {body}
            </div>
            <script>
              const token = localStorage.getItem("lwa.access_token") || "";
              async function api(path, options={{}}) {{
                const headers = options.headers || {{}};
                if (token) headers["Authorization"] = `Bearer ${{token}}`;
                const response = await fetch(path, {{...options, headers}});
                const text = await response.text();
                try {{ return JSON.parse(text); }} catch {{ return text; }}
              }}
              {script}
            </script>
          </body>
        </html>
        """
    )


@router.get("/login")
async def login_page() -> HTMLResponse:
    return shell(
        "Login",
        """
        <label>Email<input id="email" type="email"></label>
        <label>Password<input id="password" type="password"></label>
        <button onclick="login()">Login</button>
        <pre id="out"></pre>
        """,
        """
        async function login() {
          const payload = { email: email.value, password: password.value };
          const result = await api("/v1/auth/login", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(payload) });
          if (result.access_token) { localStorage.setItem("lwa.access_token", result.access_token); location.href="/dashboard"; return; }
          out.textContent = JSON.stringify(result, null, 2);
        }
        """,
    )


@router.get("/signup")
async def signup_page() -> HTMLResponse:
    return shell(
        "Signup",
        """
        <label>Email<input id="email" type="email"></label>
        <label>Password<input id="password" type="password"></label>
        <button onclick="signup()">Create Account</button>
        <pre id="out"></pre>
        """,
        """
        async function signup() {
          const payload = { email: email.value, password: password.value };
          const result = await api("/v1/auth/signup", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(payload) });
          if (result.access_token) { localStorage.setItem("lwa.access_token", result.access_token); location.href="/dashboard"; return; }
          out.textContent = JSON.stringify(result, null, 2);
        }
        """,
    )


@router.get("/dashboard")
async def dashboard_page() -> HTMLResponse:
    return shell("Dashboard", "<pre id='out'>Loading...</pre>", "api('/v1/auth/me').then(r => out.textContent = JSON.stringify(r, null, 2));")


@router.get("/upload")
async def upload_page() -> HTMLResponse:
    return shell(
        "Upload",
        """
        <input id="file" type="file" accept=".mp4,.mov,.m4v,.webm">
        <button onclick="sendUpload()">Upload Video</button>
        <pre id="out"></pre>
        """,
        """
        async function sendUpload() {
          const form = new FormData();
          form.append("file", file.files[0]);
          const headers = token ? { Authorization: `Bearer ${token}` } : {};
          const response = await fetch("/v1/uploads", { method:"POST", headers, body: form });
          out.textContent = JSON.stringify(await response.json(), null, 2);
        }
        """,
    )


@router.get("/generate")
async def generate_page() -> HTMLResponse:
    return shell(
        "Generate",
        """
        <label>Video URL<input id="video_url" placeholder="https://..."></label>
        <label>Upload ID<input id="upload_id" placeholder="upload_..."></label>
        <label>Target Platform
          <select id="target_platform">
            <option>TikTok</option><option>Instagram</option><option>YouTube</option><option>Facebook</option>
          </select>
        </label>
        <button onclick="generate()">Generate Clip Pack</button>
        <pre id="out"></pre>
        """,
        """
        async function generate() {
          const payload = {
            video_url: video_url.value || null,
            upload_file_id: upload_id.value || null,
            target_platform: target_platform.value
          };
          const result = await api("/generate", { method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(payload) });
          out.textContent = JSON.stringify(result, null, 2);
        }
        """,
    )


@router.get("/batches")
async def batches_page() -> HTMLResponse:
    return shell("Batches", "<pre id='out'>Loading...</pre>", "api('/v1/batches').then(r => out.textContent = JSON.stringify(r, null, 2));")


@router.get("/campaigns")
async def campaigns_page() -> HTMLResponse:
    return shell("Campaigns", "<pre id='out'>Loading...</pre>", "api('/v1/campaigns').then(r => out.textContent = JSON.stringify(r, null, 2));")


@router.get("/wallet")
async def wallet_page() -> HTMLResponse:
    return shell("Wallet", "<pre id='out'>Loading...</pre>", "api('/v1/wallet').then(r => out.textContent = JSON.stringify(r, null, 2));")


@router.get("/settings")
async def settings_page() -> HTMLResponse:
    return shell("Settings", "<pre id='out'>Use the browser devtools or app settings to manage tokens and endpoints for now.</pre>")


@router.get("/history")
async def history_page() -> HTMLResponse:
    return shell("History", "<pre id='out'>Loading...</pre>", "api('/v1/me/clip-packs').then(r => out.textContent = JSON.stringify(r, null, 2));")
