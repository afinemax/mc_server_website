import requests
import re
import subprocess
from pathlib import Path
import os

# === CONFIGURATION ===
GITHUB_USERNAME = "afinemax"
GITHUB_REPO = "mc_server_website"  # replace with your repo name
GITHUB_BRANCH = "main"          # replace with your branch name
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # store safely in env var
HTML_FILE = Path("index.html")

# === GET CURRENT PUBLIC IP ===
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org")
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching IP: {e}")
        return None

# === UPDATE HTML IF IP CHANGED ===
def update_html(ip):
    if not HTML_FILE.exists():
        print(f"{HTML_FILE} not found!")
        return False

    html_content = HTML_FILE.read_text()

    # Match exactly the IP:port inside the <code> tags
    pattern = r'(<strong>Server IP:</strong>\s*<code>)([\d\.]+:\d+)(</code><br>)'
    match = re.search(pattern, html_content)

    if not match:
        print("No IP line found in HTML.")
        return False

    old_ip_port = match.group(2)
    port = old_ip_port.split(":")[1]  # keep the same port
    new_ip_port = f"{ip}:{port}"

    if old_ip_port == new_ip_port:
        print("IP has not changed.")
        return False

    # Use a function to safely rebuild the replacement
    def repl(m):
        return f"{m.group(1)}{new_ip_port}{m.group(3)}"

    new_html_content = re.sub(pattern, repl, html_content)
    HTML_FILE.write_text(new_html_content)

    print(f"Updated IP from {old_ip_port} to {new_ip_port}")
    return True


# === GIT OPERATIONS ===
def git_push():
    try:
        subprocess.run(["git", "add", str(HTML_FILE)], check=True)
        subprocess.run(["git", "commit", "-m", "Update server IP"], check=True)
        # Push using token in HTTPS URL
        repo_url = f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO}.git"
        subprocess.run(["git", "push", repo_url, GITHUB_BRANCH], check=True)
        print("Changes pushed to GitHub.")
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e}")

# === MAIN SCRIPT ===
def main():
    ip = get_public_ip()
    if not ip:
        return
    
    if update_html(ip):
        git_push()

if __name__ == "__main__":
    main()
