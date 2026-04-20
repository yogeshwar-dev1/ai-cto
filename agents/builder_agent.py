import os
import requests
from core.telegram_bot import send_message
from core.ai_brain import generate_code
from config.settings import GITHUB_TOKEN, GITHUB_USERNAME, GITHUB_REPO_NAME

def get_file_content(file_path: str) -> str:
    try:
        with open(file_path, "r") as f:
            return f.read()
    except:
        return ""

def write_file(file_path: str, content: str) -> bool:
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        return True
    except Exception as e:
        send_message(f"❌ Failed to write file: {e}")
        return False

def apply_fix_to_file(file_path: str, error: str, fix: str) -> bool:
    send_message(f"🔧 Applying fix to `{file_path}`...")
    
    current_content = get_file_content(file_path)
    
    if not current_content:
        send_message(f"⚠️ File `{file_path}` not found — creating new file with fix")
        return write_file(file_path, fix)
    
    prompt = f"""Current file content:
{current_content}

Error that occurred:
{error}

Fix to apply:
{fix}

Return the COMPLETE updated file content with the fix applied. Return ONLY the code, nothing else."""
    
    updated_content = generate_code(prompt)
    success = write_file(file_path, updated_content)
    
    if success:
        send_message(f"✅ Fix applied to `{file_path}`")
    return success

def build_feature(description: str, file_path: str) -> bool:
    send_message(f"🏗️ *Builder Agent activated*\nBuilding: {description}")
    
    current_content = get_file_content(file_path)
    
    prompt = f"""{"Current file content:" + current_content if current_content else "Create a new file."}
    
New feature to add:
{description}

Return the COMPLETE updated file content. Return ONLY the code, nothing else."""
    
    new_content = generate_code(prompt)
    success = write_file(file_path, new_content)
    
    if success:
        send_message(f"✅ Feature built in `{file_path}`\nReady to deploy!")
    return success

def auto_deploy_fix(file_path: str, error: str, fix: str) -> bool:
    # Apply fix to file
    success = apply_fix_to_file(file_path, error, fix)
    if not success:
        return False
    
    # Push to GitHub
    try:
        import git
        repo = git.Repo(os.getcwd())
        repo.git.add(A=True)
        if repo.is_dirty(untracked_files=True):
            repo.index.commit(f"Auto-fix: {error[:50]}")
            origin = repo.remote(name="origin")
            origin.push(refspec="HEAD:main")
            send_message("🚀 Fix pushed to GitHub! Render will auto-redeploy in ~1 minute.")
            return True
        else:
            send_message("ℹ️ No changes detected after fix")
            return False
    except Exception as e:
        send_message(f"❌ Failed to push fix: {e}")
        return False