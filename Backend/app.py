from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Try importing logic engine (safe fallback)
try:
    from logic import (
        calculate_earned_xp,
        calculate_level,
        calculate_consistency_score,
        get_consistency_category,
        get_burnout_risk,
        get_streak_multiplier,
        get_difficulty_multiplier
    )
    LOGIC_READY = True
except:
    LOGIC_READY = False


# ---------------- USER DATA ----------------
user_data = {
    "name": "Demo Warrior",
    "xp": 0,
    "level": 1,
    "streak": 0,
    "missions_completed": 0,
    "pomodoro_sessions": 0,
    "total_days": 1,
    "consistency_score": 0,
    "consistency_category": "Low",
    "selection_probability": 0,
    "burnout_risk": "High",
    "feedback": "Start building consistency. Complete daily missions."
}

# ---------------- MISSIONS ----------------
missions = [
    {
        "id": 1,
        "title": "Complete Modern History Quest",
        "subject": "History",
        "duration": 25,
        "xp": 50,
        "difficulty": "medium",
        "completed": False
    },
    {
        "id": 2,
        "title": "Polity Constitution Basics",
        "subject": "Polity",
        "duration": 25,
        "xp": 50,
        "difficulty": "easy",
        "completed": False
    },
    {
        "id": 3,
        "title": "Current Affairs Daily Challenge",
        "subject": "Current Affairs",
        "duration": 15,
        "xp": 30,
        "difficulty": "hard",
        "completed": False
    }
]

# ---------------- SQUAD ----------------
squad = [
    {"rank": 1, "name": "Riya", "xp": 220, "streak": 5},
    {"rank": 2, "name": "Aarav", "xp": 180, "streak": 4},
    {"rank": 3, "name": "Demo Warrior", "xp": 0, "streak": 0},
    {"rank": 4, "name": "Kabir", "xp": 80, "streak": 2},
    {"rank": 5, "name": "Meera", "xp": 60, "streak": 1}
]

# ---------------- LOGIC UPDATE ----------------
def update_user_progress():
    if LOGIC_READY:
        user_data["level"] = calculate_level(user_data["xp"])

        cs = calculate_consistency_score(
            user_data["missions_completed"],
            user_data["pomodoro_sessions"],
            user_data["streak"],
            user_data["total_days"]
        )

        user_data["consistency_score"] = round(cs, 2)
        user_data["consistency_category"] = get_consistency_category(cs)

        user_data["burnout_risk"] = get_burnout_risk(
            user_data["streak"],
            user_data["missions_completed"]
        )

        # Selection probability (simple scaling)
        user_data["selection_probability"] = min(round(cs * 20, 2), 95)

        # Feedback
        if user_data["selection_probability"] >= 75:
            user_data["feedback"] = "Excellent consistency. Strong selection probability."
        elif user_data["selection_probability"] >= 40:
            user_data["feedback"] = "Good progress. Maintain your streak."
        else:
            user_data["feedback"] = "Build consistency by completing daily missions."


# ---------------- ROUTES ----------------
@app.route('/')
def home():
    return "SuccessOS Backend Running 🚀"

@app.route('/get-user', methods=['GET'])
def get_user():
    return jsonify(user_data)

@app.route('/get-missions', methods=['GET'])
def get_missions():
    return jsonify(missions)

@app.route('/get-squad', methods=['GET'])
def get_squad():
    squad[2]["xp"] = user_data["xp"]
    squad[2]["streak"] = user_data["streak"]

    sorted_squad = sorted(squad, key=lambda x: x["xp"], reverse=True)

    for i, member in enumerate(sorted_squad):
        member["rank"] = i + 1

    return jsonify(sorted_squad)

@app.route('/start-mission', methods=['POST'])
def start_mission():
    data = request.get_json()
    mission_id = data.get("mission_id")

    for mission in missions:
        if mission["id"] == mission_id:
            return jsonify({
                "message": "Mission started",
                "mission": mission,
                "timer_minutes": mission["duration"]
            })

    return jsonify({"error": "Mission not found"}), 404

@app.route('/complete-mission', methods=['POST'])
def complete_mission():
    data = request.get_json()
    mission_id = data.get("mission_id")

    selected_mission = None

    for mission in missions:
        if mission["id"] == mission_id:
            selected_mission = mission
            break

    if selected_mission is None:
        return jsonify({"error": "Mission not found"}), 404

    if selected_mission["completed"]:
        return jsonify({"error": "Mission already completed"}), 400

    selected_mission["completed"] = True

    base_xp = selected_mission["xp"]
    difficulty = selected_mission.get("difficulty", "medium")

    if LOGIC_READY:
        earned_xp = calculate_earned_xp(base_xp, user_data["streak"], difficulty)
    else:
        earned_xp = base_xp

    user_data["xp"] += int(earned_xp)
    user_data["missions_completed"] += 1
    user_data["streak"] += 1
    user_data["pomodoro_sessions"] += 1

    update_user_progress()

    return jsonify({
        "message": "Mission completed",
        "earned_xp": int(earned_xp),
        "user": user_data
    })

@app.route('/reset-demo', methods=['POST'])
def reset_demo():
    user_data.update({
        "xp": 0,
        "level": 1,
        "streak": 0,
        "missions_completed": 0,
        "pomodoro_sessions": 0,
        "total_days": 1,
        "consistency_score": 0,
        "consistency_category": "Low",
        "selection_probability": 0,
        "burnout_risk": "High",
        "feedback": "Start building consistency. Complete daily missions."
    })

    for mission in missions:
        mission["completed"] = False

    return jsonify({
        "message": "Demo reset successful",
        "user": user_data
    })

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
