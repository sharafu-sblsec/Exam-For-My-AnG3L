from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
import json, random, string
import re, random, redis
SAMPLE_SIZE = 125
SECRET_KEY = "CreateAndPlaceABasicComplexAppSecretKey"
PREMIUM_TOKEN = "PremiumTokenFormyLoveOnlyHAHAHAHAHAHJustForGiveherACetificate!!"
PREMIUM_NAME = "AnyPremiumNameNoUseJustprahasanam"

app = Flask(__name__)

app.secret_key = SECRET_KEY

def is_malicious_input(value):
    if not value:
        return False

    pattern = re.compile(r'^[a-zA-Z0-9 ]+$')
    return not bool(pattern.match(value))

def load_questions():
    with open("QuestionSample.json", encoding="utf-8") as f:
        return json.load(f)

redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route('/generate-token')
def generate_token():
    name = request.args.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Missing name'}), 400

    if is_malicious_input(name):
        return jsonify({'error': 'Malicious input detected'}), 400

    token = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    redis_client.set(token, name, ex=11700)
    return jsonify({'token': token})


@app.route('/verify')
def verify():
    token = request.args.get('token')
    return render_template('submitToken.html', token=token or "")


@app.route('/submit-token', methods=['POST'])
def submit_token():
    token = request.form.get('token', '').strip()

    if is_malicious_input(token):
        return render_template('submitToken.html', show_payload_alert=True, token=token)

    if token == PREMIUM_TOKEN:
        session['token'] = token
        return redirect(url_for('exam'))

    name = redis_client.get(token)
    if name:
        session['token'] = token
        return redirect(url_for('exam'))

    return "Invalid or expired token", 403


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/pingme')
def pingme():
    return render_template('pingme.html')

@app.route('/start', methods=['GET', 'POST'])
def start():
    token = session.get('token')
    if token and token != PREMIUM_TOKEN:
        redis_client.delete(token)
        session.clear()

    if request.method == 'POST':
        name = request.form.get('name', '')
        if is_malicious_input(name):
            return render_template('start.html', show_payload_alert=True)
        return render_template('start.html', show_payload_alert=False, name=name)

    return render_template('start.html', show_payload_alert=False)

@app.route('/exam')
def exam():
    token = session.get('token')

    if not token:
        session.clear()
        return "Unauthorized access", 403

    if token == PREMIUM_TOKEN:
        name = PREMIUM_NAME
    else:
        name = redis_client.get(token)
        if not name:
            session.clear()
            return "Unauthorized or expired token", 403

    all_questions = load_questions()
    shown_all = session.get('shown_qids', {})
    shown_qids = shown_all.get(token, [])
    active_exams = session.get('active_exams', {})

    if token not in active_exams:
        remaining_questions = [q for q in all_questions if q['id'] not in shown_qids]
        if not remaining_questions:
            shown_all.pop(token, None)
            session['shown_qids'] = shown_all
            return "All questions completed! Thank you for taking the exam."

        k = min(SAMPLE_SIZE, len(remaining_questions))
        selected_questions = random.sample(remaining_questions, k)
        selected_ids = [q['id'] for q in selected_questions]

        active_exams[token] = selected_ids
        shown_all[token] = shown_qids + selected_ids
        session['active_exams'] = active_exams
        session['shown_qids'] = shown_all
    else:
        selected_ids = active_exams[token]
        selected_questions = [q for q in all_questions if q['id'] in selected_ids]

    questions_to_render = []
    for q in selected_questions:
        qcopy = dict(q)
        qcopy.pop('answer', None)
        questions_to_render.append(qcopy)

    random.shuffle(questions_to_render)

    return render_template(
        "buildexam.html",
        username=name,
        token=token,
        questions=questions_to_render
    )

@app.route('/submit', methods=['POST'])
def submit():
    token = session.get('token')
    active_exams = session.get('active_exams', {})

    if not token:
        return jsonify({"success": False, "error": "Unauthorized access"}), 403

    if token != PREMIUM_TOKEN:
        name = redis_client.get(token)
        if not name:
            session.clear()
            return jsonify({"success": False, "error": "Token expired"}), 403

    if token not in active_exams:
        return jsonify({"success": False, "error": "No active exam"}), 400

    selected_ids = active_exams[token]
    submitted = request.json.get("answers", {})

    all_questions = load_questions()
    question_map = {q["id"]: q for q in all_questions}

    score = 0
    for qid in selected_ids:
        q = question_map.get(qid)
        if q:
            answer_given = submitted.get(str(qid))
            if answer_given is not None and int(answer_given) == q["answer"]:
                score += 1

    session['score'] = score
    session['total'] = len(selected_ids)

    active_exams.pop(token, None)
    session['active_exams'] = active_exams

    return jsonify({"success": True})

@app.route("/result")
def result():
    score = session.get("score")
    total = session.get("total")
    token = session.get("token")

    if score is None or total is None or token is None:
        return "Unauthorized result access", 403

    if token != PREMIUM_TOKEN:
        name = redis_client.get(token)
        if not name:
            session.clear()
            return "Token expired", 403

    passed = score >= int(0.7 * total)
    is_premium = token == PREMIUM_TOKEN

    if not is_premium:
        redis_client.delete(token)
        session.clear()

    return render_template(
        "buildresult.html",
        score=score,
        total=total,
        passed=passed,
        is_premium=is_premium
    )

@app.route("/downloadcert")
def download_certificate():
    token = session.get("token")
    score = session.get("score")
    total = session.get("total")

    if token != PREMIUM_TOKEN or score is None or total is None:
        return "Access denied", 403

    passed = score >= int(0.7 * total)
    if not passed:
        return "Only passed premium users can download", 403

    session.clear()

    return send_file("private/samplesuccess.pdf", as_attachment=True)

@app.route("/downloadfailcert")
def download_failed_certificate():
    token = session.get("token")
    score = session.get("score")
    total = session.get("total")

    if token != PREMIUM_TOKEN or score is None or total is None:
        return "Access denied", 403

    passed = score >= int(0.7 * total)
    if passed:
        return "Only failed premium users can download this", 403

    session.clear()

    return send_file("private/samplefailed", as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

