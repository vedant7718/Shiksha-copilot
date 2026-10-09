from flask import Flask, render_template, request, redirect, url_for, session, flash
import json, os, random
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SHIKSHA_SECRET_KEY", "change-this-local-demo-key")
DATA_FILE = os.path.join(os.path.dirname(__file__), "learner_data.json")

SAMPLE_QUESTIONS = [
    {"topic":"Variables", "question":"What is a variable in Python?", "options":["A named place to store a value","A loop that repeats code","A type of database","A function that prints text"], "answer":0,
     "explanation":"A variable is a name that refers to a value, such as age = 19."},
    {"topic":"Conditions", "question":"Which keyword runs code only when a condition is true?", "options":["repeat","if","loop","define"], "answer":1,
     "explanation":"The if statement checks a condition and runs its block when the condition is true."},
    {"topic":"Loops", "question":"How many times does this loop run: for i in range(3)?", "options":["2 times","3 times","4 times","It never runs"], "answer":1,
     "explanation":"range(3) produces 0, 1, and 2, so the loop runs three times."},
    {"topic":"Loops", "question":"Why are loops useful?", "options":["They store files","They repeat steps without rewriting them","They always make code faster","They replace every variable"], "answer":1,
     "explanation":"Loops repeat a block of code, which reduces repeated writing."},
    {"topic":"Functions", "question":"What is the main purpose of a function?", "options":["To group reusable instructions","To shut down Python","To make a variable private automatically","To store images only"], "answer":0,
     "explanation":"A function groups instructions that can be called when needed."},
    {"topic":"Logic", "question":"If x = 4, what is printed by if x > 2: print('Yes')?", "options":["No","Yes","4","Nothing, because x is not a string"], "answer":1,
     "explanation":"4 is greater than 2, so the condition is true and Yes is printed."}
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def current_user():
    name = session.get("student_name")
    data = load_data()
    if name:
        data.setdefault(name, {"attempts": [], "mastery": {}, "modules": {}, "reason": "", "goal": "Understand concepts", "created": datetime.now().isoformat()})
        save_data(data)
        return name, data[name], data
    return None, None, data

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        reason = request.form.get("reason", "Understand concepts")
        goal = request.form.get("goal", "Understand concepts")
        if not name:
            flash("Please enter your name to start.", "error")
            return redirect(url_for("home"))
        data = load_data()
        data.setdefault(name, {"attempts": [], "mastery": {}, "modules": {}, "reason": reason, "goal": goal, "created": datetime.now().isoformat()})
        data[name]["reason"] = reason
        data[name]["goal"] = goal
        save_data(data)
        session["student_name"] = name
        return redirect(url_for("dashboard"))
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    name, profile, data = current_user()
    if not name:
        return redirect(url_for("home"))
    attempts = profile["attempts"]
    latest = attempts[-1] if attempts else None
    topics = sorted(set(q["topic"] for q in SAMPLE_QUESTIONS))
    topic_stats = []
    for topic in topics:
        vals = [a for a in attempts if a.get("topic_scores", {}).get(topic) is not None]
        score = round(sum(a["topic_scores"][topic] for a in vals) / len(vals)) if vals else profile["mastery"].get(topic, 0)
        topic_stats.append({"topic":topic, "score":score})
    weak = sorted(topic_stats, key=lambda x: x["score"])[:2]
    return render_template("dashboard.html", name=name, profile=profile, latest=latest, topic_stats=topic_stats, weak=weak, module_count=len(profile["modules"]))

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    name, profile, data = current_user()
    if not name:
        return redirect(url_for("home"))
    if request.method == "POST":
        questions = session.get("active_questions", [])
        correct = 0
        topic_total, topic_correct = {}, {}
        answers = []
        for i, q in enumerate(questions):
            selected = request.form.get(f"q{i}")
            selected_idx = int(selected) if selected is not None else -1
            is_correct = selected_idx == q["answer"]
            correct += int(is_correct)
            topic_total[q["topic"]] = topic_total.get(q["topic"], 0) + 1
            topic_correct[q["topic"]] = topic_correct.get(q["topic"], 0) + int(is_correct)
            answers.append({"question":q["question"], "topic":q["topic"], "selected":selected_idx, "correct":q["answer"], "is_correct":is_correct, "explanation":q["explanation"]})
        topic_scores = {t: round(100 * topic_correct.get(t,0) / n) for t,n in topic_total.items()}
        attempt = {"date":datetime.now().strftime("%Y-%m-%d %H:%M"), "score":correct, "total":len(questions), "topic_scores":topic_scores, "answers":answers}
        profile["attempts"].append(attempt)
        for t, score in topic_scores.items():
            old = profile["mastery"].get(t, score)
            profile["mastery"][t] = round(old * 0.4 + score * 0.6)
        data[name] = profile
        save_data(data)
        session["last_result"] = attempt
        session.pop("active_questions", None)
        return redirect(url_for("results"))
    mode = request.args.get("mode", "assessment")
    questions = random.sample(SAMPLE_QUESTIONS, k=min(5, len(SAMPLE_QUESTIONS)))
    session["active_questions"] = questions
    return render_template("quiz.html", questions=questions, mode=mode)

@app.route("/results")
def results():
    name, profile, data = current_user()
    if not name:
        return redirect(url_for("home"))
    result = session.get("last_result")
    if not result:
        return redirect(url_for("dashboard"))
    return render_template("results.html", result=result)

@app.route("/learning")
def learning():
    name, profile, data = current_user()
    if not name:
        return redirect(url_for("home"))
    weak = sorted(profile["mastery"].items(), key=lambda x: x[1])[:3]
    if not weak:
        weak = [("Loops", 0), ("Logic", 0)]
    return render_template("learning.html", weak=weak, profile=profile)

@app.route("/complete-module", methods=["POST"])
def complete_module():
    name, profile, data = current_user()
    if not name:
        return redirect(url_for("home"))
    topic = request.form.get("topic", "Loops")
    explanation = request.form.get("explanation", "").strip()
    if len(explanation) < 20:
        flash("Please explain the concept in at least 20 characters before marking it complete.", "error")
        return redirect(url_for("learning"))
    profile["modules"][topic] = {"status":"Teach-back submitted", "explanation":explanation, "date":datetime.now().strftime("%Y-%m-%d %H:%M")}
    data[name] = profile
    save_data(data)
    flash("Your explanation has been saved. In this demo, it is submitted for review; it is not automatically verified by AI.", "success")
    return redirect(url_for("learning"))

@app.route("/daily-quiz")
def daily_quiz():
    return redirect(url_for("quiz", mode="daily"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
