from core.telegram_bot import send_message, send_approval_request
from core.ai_brain import diagnose_bug
from agents.builder_agent import auto_deploy_fix

pending_fixes = {}

def analyze_and_fix(error: str, context: str = "") -> str:
    send_message(f"🔍 *Fix Agent activated*\nAnalyzing: `{error}`")
    fix = diagnose_bug(error, context)
    return fix

def propose_fix(error: str, fix: str, file_path: str = "index.html"):
    fix_id = str(len(pending_fixes) + 1)
    pending_fixes[fix_id] = {
        "error": error,
        "fix": fix,
        "file_path": file_path
    }

    message = f"""🔧 *AI Fix Proposal #{fix_id}*

*Error:*
`{error}`

*Proposed fix:*
*Auto-deploy this fix?*"""

    send_approval_request(
        message=message,
        approve_data=f"approve_{fix_id}",
        reject_data=f"reject_{fix_id}"
    )
    return fix_id

def apply_fix(fix_id: str) -> bool:
    if fix_id not in pending_fixes:
        send_message(f"❌ Fix #{fix_id} not found")
        return False

    fix_data = pending_fixes[fix_id]
    send_message(f"✅ *Fix #{fix_id} approved! Auto-deploying...*")

    success = auto_deploy_fix(
        file_path=fix_data["file_path"],
        error=fix_data["error"],
        fix=fix_data["fix"]
    )

    try:
        with open("logs/fixes.log", "a") as f:
            f.write(f"\nFix #{fix_id}\n")
            f.write(f"Error: {fix_data['error']}\n")
            f.write(f"Fix: {fix_data['fix']}\n")
            f.write(f"Deployed: {success}\n")
            f.write("---\n")
    except:
        pass

    del pending_fixes[fix_id]
    return success

def reject_fix(fix_id: str):
    if fix_id in pending_fixes:
        del pending_fixes[fix_id]
    send_message(f"❌ Fix #{fix_id} rejected. Monitoring continues...")

def handle_callback(callback_data: str):
    if callback_data.startswith("approve_"):
        fix_id = callback_data.replace("approve_", "")
        apply_fix(fix_id)
    elif callback_data.startswith("reject_"):
        fix_id = callback_data.replace("reject_", "")
        reject_fix(fix_id)