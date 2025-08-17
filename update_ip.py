import requests
import re
import subprocess
from pathlib import Path
import os

# === CONFIGURATION ===
GITHUB_USERNAME = "afinemax"
GITHUB_REPO = "mc_server_website"  # replace with your repo name
GITHUB_BRANCH = "main"             # replace with your branch name
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # store safely in env var
HTML_FILE = Path("index.html")
README_FILE = Path("README.md")

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

    pattern = r'(<strong>Server IP:</strong>\s*<code>)([\d\.]+:\d+)(</code><br>)'
    match = re.search(pattern, html_content)
    if not match:
        print("No IP line found in HTML.")
        return False

    old_ip_port = match.group(2)
    port = old_ip_port.split(":")[1]  # preserve port
    new_ip_port = f"{ip}:{port}"

    if old_ip_port == new_ip_port:
        print("IP has not changed in HTML.")
        return False

    def repl(m):
        return f"{m.group(1)}{new_ip_port}{m.group(3)}"

    new_html_content = re.sub(pattern, repl, html_content)
    HTML_FILE.write_text(new_html_content)

    print(f"Updated HTML IP from {old_ip_port} to {new_ip_port}")
    return True

# === UPDATE README IF IP CHANGED ===
def update_readme(ip):
    if not README_FILE.exists():
        print(f"{README_FILE} not found!")
        return False

    readme_content = README_FILE.read_text()

    pattern = r'(\*\*IP:\*\*\s*`)([\d\.]+:\d+)(`)'
    match = re.search(pattern, readme_content)
    if not match:
        print("No IP line found in README.")
        return False

    old_ip_port = match.group(2)
    port = old_ip_port.split(":")[1]  # preserve port
    new_ip_port = f"{ip}:{port}"

    if old_ip_port == new_ip_port:
        print("IP has not changed in README.")
        return False

    def repl(m):
        return f"{m.group(1)}{new_ip_port}{m.group(3)}"

    new_readme_content = re.sub(pattern, repl, readme_content)
    README_FILE.write_text(new_readme_content)

    print(f"Updated README IP from {old_ip_port} to {new_ip_port}")
    return True

# === GIT OPERATIONS ===
def git_push(files_changed):
    try:
        subprocess.run(["git", "add"] + files_changed, check=True)
        subprocess.run(["git", "commit", "-m", "Update server IP"], check=True)
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

    changed_files = []
    if update_html(ip):
        changed_files.append(str(HTML_FILE))
    if update_readme(ip):
        changed_files.append(str(README_FILE))

    if changed_files:
        git_push(changed_files)

if __name__ == "__main__":
    main()

