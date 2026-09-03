# Placeholder for helper functions (e.g., payment verification, trial checks)
def check_trial_status(user_id):
    from database import get_user
    user = get_user(user_id)
    if not user:
        return False
    from datetime import datetime
    trial_until = datetime.fromisoformat(user[4])
    return datetime.now() < trial_until
