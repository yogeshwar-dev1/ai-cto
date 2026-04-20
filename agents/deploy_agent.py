import os
import requests
from core.telegram_bot import send_message
from config.settings import (
    GITHUB_TOKEN, GITHUB_USERNAME, GITHUB_REPO_NAME,
    VERCEL_TOKEN, VERCEL_PROJECT_ID
)

def create_github_repo():
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "name": GITHUB_REPO_NAME,
        "private": False,
        "auto_init": True
    }
    res = requests.post(url, json=payload, headers=headers)
    if res.status_code == 201:
        send_message(f"✅ GitHub repo created: github.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}")
        return True
    elif res.status_code == 422:
        send_message(f"ℹ️ Repo already exists: github.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}")
        return True
    else:
        send_message(f"❌ GitHub repo creation failed: {res.json()}")
        return False

def push_to_github(commit_message: str = "Auto deploy by AI CTO") -> bool:
    try:
        import git
        repo_path = os.getcwd()
        try:
            repo = git.Repo(repo_path)
        except:
            repo = git.Repo.init(repo_path)
            remote_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}.git"
            repo.create_remote("origin", remote_url)

        repo.git.add(A=True)
        if repo.is_dirty(untracked_files=True):
            repo.index.commit(commit_message)
            origin = repo.remote(name="origin")
            origin.push(refspec="HEAD:main")
            send_message(f"✅ Code pushed to GitHub\nCommit: `{commit_message}`")
            return True
        else:
            send_message("ℹ️ No changes to push")
            return True
    except Exception as e:
        send_message(f"❌ GitHub push failed: {e}")
        return False

def deploy_to_vercel() -> bool:
    url = "https://api.vercel.com/v13/deployments"
    headers = {
        "Authorization": f"Bearer {VERCEL_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": GITHUB_REPO_NAME,
        "gitSource": {
            "type": "github",
            "repoId": f"{GITHUB_USERNAME}/{GITHUB_REPO_NAME}",
            "ref": "main"
        }
    }
    try:
        res = requests.post(url, json=payload, headers=headers)
        data = res.json()
        if "url" in data:
            site_url = f"https://{data['url']}"
            send_message(f"🚀 Deployed to Vercel!\nLive at: {site_url}")
            return True
        else:
            send_message(f"❌ Vercel deploy failed: {data}")
            return False
    except Exception as e:
        send_message(f"❌ Vercel error: {e}")
        return False

def full_deploy(commit_message: str = "Auto deploy by AI CTO") -> bool:
    send_message("🔄 Starting full deploy...")
    step1 = create_github_repo()
    if not step1:
        return False
    step2 = push_to_github(commit_message)
    if not step2:
        return False
    step3 = deploy_to_vercel()
    return step3