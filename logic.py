# logic.py

def validate_session(timer_started, mission_completed, session_duration):
    return timer_started and mission_completed and session_duration >= 20


def get_streak_multiplier(streak):
    if 1 <= streak <= 3:
        return 1.0
    elif 4 <= streak <= 7:
        return 1.1
    elif 8 <= streak <= 14:
        return 1.25
    elif streak >= 15:
        return 1.5
    return 1.0


def get_difficulty_multiplier(difficulty):
    difficulty = difficulty.lower()

    if difficulty == "easy":
        return 1.0
    elif difficulty == "medium":
        return 1.2
    elif difficulty == "hard":
        return 1.5
    return 1.0


def calculate_earned_xp(base_xp, streak, difficulty):
    streak_multiplier = get_streak_multiplier(streak)
    difficulty_multiplier = get_difficulty_multiplier(difficulty)

    earned_xp = base_xp * streak_multiplier * difficulty_multiplier
    return max(int(earned_xp), 0)


def calculate_level(total_xp):
    if total_xp >= 3500:
        return 5
    elif total_xp >= 2000:
        return 4
    elif total_xp >= 1200:
        return 3
    elif total_xp >= 500:
        return 2
    return 1


def calculate_consistency_score(missions_completed, pomodoro_sessions, streak, days_since_start):
    if days_since_start <= 0:
        return 0

    streak_multiplier = get_streak_multiplier(streak)
    score = ((missions_completed + pomodoro_sessions) * streak_multiplier) / days_since_start

    return round(score, 2)


def get_consistency_category(score):
    if score < 1:
        return "Low"
    elif score < 2:
        return "Average"
    elif score < 3:
        return "Good"
    return "Excellent"


def get_burnout_risk(streak, missions_completed):
    if streak >= 15 and missions_completed > 100:
        return "Low"
    elif streak >= 7 and missions_completed > 40:
        return "Medium"
    return "High"