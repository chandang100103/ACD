import os
import json
import random
from flask_session import Session
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session
)

# ==========================================================
# APP CONFIG
# ==========================================================

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False

Session(app)

# ==========================================================
# CONSTANTS
# ==========================================================

TOTAL_QUESTIONS = 40

PASS_PERCENTAGE = 65

DATA_FOLDER = "data"


# ==========================================================
# PDF LOADER
# ==========================================================

def get_pdfs(folder):

    folder_path = os.path.join(
        app.static_folder,
        "pdfs",
        folder
    )

    if not os.path.exists(folder_path):

        return []

    pdfs = []

    for file in os.listdir(folder_path):

        if file.lower().endswith(".pdf"):

            pdfs.append(

                {

                    "name": os.path.splitext(file)[0],

                    "file": file

                }

            )

    pdfs.sort(key=lambda x: x["name"])

    return pdfs

# ==========================================================
# QUESTION LOADER
# ==========================================================

def load_questions(course):

    path = os.path.join(

        DATA_FOLDER,

        f"{course}_questions.json"

    )

    if not os.path.exists(path):

        return []

    with open(

        path,

        "r",

        encoding="utf-8"

    ) as f:

        return json.load(f)

# ==========================================================
# EXAM HELPERS
# ==========================================================
def initialize_exam(course, mode="final"):

    questions = load_questions(course)

    if mode == "quick":

        questions = [
            q for q in questions
            if q.get("difficulty") in [
                "easy",
                "medium"
            ]
        ]

        total = min(40, len(questions))

    elif mode == "foundation":

        questions = [
            q for q in questions
            if q.get("difficulty") in [
                "medium",
                "hard"
            ]
        ]

        total = min(40, len(questions))

    else:

        questions = [
            q for q in questions
            if q.get("difficulty") in [
                "easy",
                "medium",
                "hard"
            ]
        ]

        total = min(60, len(questions))

    selected_questions = random.sample(
        questions,
        total
    )

    session["course"] = course
    session["exam_mode"] = mode

    session["mock_questions"] = selected_questions
    session["mock_answers"] = {}
    session["review_questions"] = []
    session["current_question"] = 0

    session.modified = True

# ==========================================================
# START EXAM
# ==========================================================
@app.route("/start_exam")
def start_exam():

    initialize_exam("itil")

    return redirect(url_for("mock_exam", course="itil"))

@app.route("/start_quick_mock")
def start_quick_mock():

    initialize_exam(
        "itil",
        "quick"
    )

    return redirect(url_for("mock_exam", course="itil"))

@app.route("/start_foundation_mock")
def start_foundation_mock():

    initialize_exam(
        "itil",
        "foundation"
    )

    return redirect(url_for("mock_exam", course="itil"))

@app.route("/start_final_mock")
def start_final_mock():


    initialize_exam(
        "itil",
        "final"
    )

    return redirect(url_for("mock_exam", course="itil"))

@app.route("/basis_start_quick_mock")
def basis_start_quick_mock():



    initialize_exam(
        "basis",
        "quick"
    )

    return redirect(url_for("mock_exam", course="basis"))

@app.route("/basis_start_foundation_mock")
def basis_start_foundation_mock():


    initialize_exam(
        "basis",
        "foundation"
    )

    return redirect(url_for("mock_exam", course="basis"))

@app.route("/basis_start_final_mock")
def basis_start_final_mock():

    initialize_exam(
        "basis",
        "final"
    )

    return redirect(url_for("mock_exam", course="basis"))

@app.route("/az900_start_quick_mock")
def az900_start_quick_mock():



    initialize_exam(
        "az900",
        "quick"
    )

    return redirect(url_for("mock_exam", course="az900"))

@app.route("/az900_start_foundation_mock")
def az900_start_foundation_mock():

    initialize_exam(
        "az900",
        "foundation"
    )

    return redirect(url_for("mock_exam", course="az900"))

@app.route("/az900_start_final_mock")
def az900_start_final_mock():


    initialize_exam(
        "az900",
        "final"
    )

    return redirect(url_for("mock_exam", course="az900"))

@app.route("/az104_start_quick_mock")
def az104_start_quick_mock():



    initialize_exam(
        "az104",
        "quick"
    )

    return redirect(url_for("mock_exam", course="az104"))

@app.route("/az104_start_foundation_mock")
def az104_start_foundation_mock():


    initialize_exam(
        "az104",
        "foundation"
    )

    return redirect(url_for("mock_exam", course="az104"))

@app.route("/az104_start_final_mock")
def az104_start_final_mock():


    initialize_exam(
        "az104",
        "final"
    )

    return redirect(url_for("mock_exam", course="az104"))

def current_question():

    questions = session["mock_questions"]

    index = session["current_question"]

    return questions[index]


def save_answer(question):

    key = str(question["id"])

    if question["type"] == "single":

        answer = request.form.get("answer")

        if answer:

            session["mock_answers"][key] = [answer]

        else:

            session["mock_answers"][key] = []

    else:

        session["mock_answers"][key] = request.form.getlist("answer")

    session.modified = True
def validate_answer(question):
    selected = request.form.getlist("answer")

    if question["type"] == "single":
        if len(selected) != 1:
            return False, "Please select an answer before continuing."

    elif question["type"] == "multiple":
        required = int(question["select"])

        if len(selected) != required:
            return False, f"Please select exactly {required} answers."

    return True, ""
def navigate_exam(action, total_questions):

    current = session["current_question"]

    if action == "next":

        if current < total_questions - 1:

            session["current_question"] += 1

    elif action == "previous":

        if current > 0:

            session["current_question"] -= 1

    elif action == "jump":

        jump = request.form.get("jump")

        if jump:

            jump = int(jump) - 1

            if 0 <= jump < total_questions:

                session["current_question"] = jump

    session.modified = True

def calculate_score():

    score = 0

    questions = session["mock_questions"]

    answers = session["mock_answers"]

    for question in questions:

        correct = sorted(

            question["correct"]

        )

        selected = sorted(

            answers.get(

                str(question["id"]),

                []

            )

        )

        if correct == selected:

            score += 1

    return score


def calculate_percentage():

    total = len(

        session["mock_questions"]

    )

    if total == 0:

        return 0

    return round(

        calculate_score() * 100 / total,

        2

    )


def exam_result():

    score = calculate_score()

    total = len(session["mock_questions"])

    percentage = round((score / total) * 100, 2) if total else 0

    return {

        "score": score,

        "total": total,

        "percentage": percentage,

        "passed": percentage >= PASS_PERCENTAGE

    }

# ==========================================================
# ROUTES
# ==========================================================
# -------------------------------------------------
# ROUTES
# -------------------------------------------------
# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():

    return redirect(url_for("dashboard"))





# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html")

    courses = [

        {
            "title": "ITIL 4",
            "icon": "📘",
            "description": "Study Material & Mock Tests",
            "url": "/itil"
        },

        {
            "title": "AZ-900",
            "icon": "☁️",
            "description": "Azure Fundamentals",
            "url": "/az900"
        },

        {
            "title": "AZ-104",
            "icon": "⚙️",
            "description": "Azure Administrator",
            "url": "/az104"
        },
        {
            "title": "SAP BASIS",
            "description": "SAP BASIS Administration",
            "icon": "🖥️",
            "url": "/basis"
        }

    ]

    return render_template(

        "dashboard.html",

        username="Welcome",

        courses=courses

    )


# ==========================================================
# ITIL PAGE
# ==========================================================

@app.route("/itil")
def itil():


    notes = get_pdfs("itil/notes")

    question_banks = get_pdfs("itil/question_banks")

    return render_template(

        "itil.html",

        username="Welcome",

        notes=notes,

        question_banks=question_banks

    )
# ==========================================================
# BASIS PAGE
# ==========================================================

@app.route("/basis")
def basis():


    notes = get_pdfs("basis/notes")

    question_banks = get_pdfs("basis/question_banks")

    return render_template(
        "basis.html",
        username="Welcome",
        notes=notes,
        question_banks=question_banks
    )
# ==========================================================
# AZ-900 PAGE
# ==========================================================

@app.route("/az900")
def az900():


    notes = get_pdfs("az900/notes")

    question_banks = get_pdfs("az900/question_banks")

    return render_template(

        "az900.html",

        username="Welcome",

        notes=notes,

        question_banks=question_banks

    )


# ==========================================================
# AZ-104 PAGE
# ==========================================================

@app.route("/az104")
def az104():

    notes = get_pdfs("az104/notes")

    question_banks = get_pdfs("az104/question_banks")

    return render_template(

        "az104.html",

        username="Welcome",

        notes=notes,

        question_banks=question_banks

    )


# ==========================================================

# ==========================================================
# ITIL MOCK EXAM
# ==========================================================

@app.route("/<course>/mock", methods=["GET", "POST"])
def mock_exam(course):
    
    if course not in ["itil", "basis", "az900", "az104"]:
        return redirect(url_for("dashboard"))
    
    if "mock_questions" not in session:
            return redirect(url_for("itil"))
    # ------------------------------------------------------
    # START EXAM
    # ------------------------------------------------------


    questions = session["mock_questions"]

    current = session["current_question"]

    question = questions[current]

    answers = session["mock_answers"]

    review = session["review_questions"]
    course_names = {
        "itil": "ITIL",
        "basis": "SAP BASIS",
        "az900": "AZ-900",
        "az104": "AZ-104"
    }

    # ------------------------------------------------------
    # SAVE CURRENT ANSWER
    # ------------------------------------------------------

    if request.method == "POST":

        action = request.form.get("action")
        selected_from_form = request.form.getlist("answer")

        # --------------------------------------------------
        # VALIDATE ANSWER BEFORE NEXT / SUBMIT
        # --------------------------------------------------

        if action in ["next", "submit"]:

            # Single-answer question
            if question["type"] == "single":

                if len(selected_from_form) != 1:
                    error = "Please select an answer before continuing."

                    return render_template(
                        "mock_test.html",
                        username="Welcome",
                        question=question,
                        current=current + 1,
                        total=len(questions),
                        selected=selected_from_form,
                        course=course,
                        course_name=course_names.get(
                            course,
                            course.upper()
                        ),
                        error=error,
                        palette=[]
                    )

            # Multiple-answer question
            elif question["type"] == "multiple":

                required = int(question["select"])

                if len(selected_from_form) != required:
                    error = f"Please select exactly {required} answers."

                    return render_template(
                        "mock_test.html",
                        username="Welcome",
                        question=question,
                        current=current + 1,
                        total=len(questions),
                        selected=selected_from_form,
                        course=course,
                        course_name=course_names.get(
                            course,
                            course.upper()
                        ),
                        error=error,
                        palette=[]
                    )

        # --------------------------------------------------
        # SAVE ANSWER
        # --------------------------------------------------

        save_answer(question)

        # --------------------------------------------------
        # NEXT
        # --------------------------------------------------

        if action == "next":

            if current < len(questions) - 1:
                session["current_question"] += 1

            session.modified = True

            return redirect(
                url_for("mock_exam", course=course)
            )

        # --------------------------------------------------
        # PREVIOUS
        # --------------------------------------------------

        elif action == "previous":

            if current > 0:
                session["current_question"] -= 1

            session.modified = True

            return redirect(
                url_for("mock_exam", course=course)
            )

        # --------------------------------------------------
        # MARK FOR REVIEW
        # --------------------------------------------------

        elif action == "review":

            if question["id"] not in review:

                review.append(question["id"])
                session["review_questions"] = review

            if current < len(questions) - 1:
                session["current_question"] += 1

            session.modified = True

            return redirect(
                url_for("mock_exam", course=course)
            )

        # --------------------------------------------------
        # JUMP TO QUESTION
        # --------------------------------------------------

        elif action == "jump":

            jump = request.form.get("jump")

            if jump:

                jump = int(jump) - 1

                if 0 <= jump < len(questions):
                    session["current_question"] = jump

            session.modified = True

            return redirect(
                url_for("mock_exam", course=course)
            )

        # --------------------------------------------------
        # SUBMIT
        # --------------------------------------------------

        elif action == "submit":

            return redirect(
                url_for("mock_result", course=course)
            )

    # ------------------------------------------------------
    # CURRENT SELECTED ANSWERS
    # ------------------------------------------------------

    selected = answers.get(
        str(question["id"]),
        []
    )
    # ------------------------------------------------------
    # BUILD QUESTION PALETTE
    # ------------------------------------------------------

    palette = []

    for i, q in enumerate(questions):

        qid = str(q["id"])

        if q["id"] in review:

            status = "review"

        elif qid in answers and answers[qid]:

            status = "answered"

        else:

            status = "not_answered"

        palette.append({

            "number": i + 1,

            "status": status,

            "current": i == current

        })

    # ------------------------------------------------------
    # RENDER PAGE
    # ------------------------------------------------------
    course = session.get("course", "itil")

    course_names = {
    "itil": "ITIL 4 Foundation",
    "basis": "SAP BASIS",
    "az900": "AZ-900",
    "az104": "AZ-104"
    }

    return render_template(

        "mock_test.html",

        username="Welcome",

        question=question,

        current=current + 1,

        total=len(questions),

        selected=selected,

        palette=palette,
        course=course,
        course_name=course_names.get(course, course.upper())
    )

# ==========================================================
# RESULT
# ==========================================================

@app.route("/<course>/result")
def mock_result(course):


    # Calculate result BEFORE clearing session
    result = exam_result()

    questions = session.get("mock_questions", [])
    answers = session.get("mock_answers", {})

    review = []

    for q in questions:

        user_answer = answers.get(str(q["id"]), [])

        review.append({

            "question": q["question"],

            "chapter": q["chapter"],

            "difficulty": q["difficulty"],

            "options": q["options"],

            "correct": q["correct"],

            "selected": user_answer,

            "explanation": q["explanation"],

            "is_correct": sorted(user_answer) == sorted(q["correct"])

        })

    # Clear exam session so user cannot return to completed exam
    session.pop("mock_questions", None)
    session.pop("mock_answers", None)
    session.pop("current_question", None)
    session.pop("review_questions", None)

    course = session.get("course", "itil")

    course_names = {
    "itil": "ITIL 4 Foundation",
    "basis": "SAP BASIS",
    "az900": "AZ-900",
    "az104": "AZ-104"
    }
    return render_template(

        "result.html",
        username="Welcome",
        result=result,
        review=review,
        pass_percentage=PASS_PERCENTAGE,
        course=course,
        course_name=course_names.get(course, course.upper())
)

    
@app.after_request
def prevent_exam_caching(response):

    if request.path.endswith("/mock"):
        response.headers["Cache-Control"] = (
            "no-store, no-cache, must-revalidate, max-age=0"
        )
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response

# ==========================================================
# RESET MOCK
# ==========================================================

@app.route("/itil/reset")
def reset_mock():

    session.pop("mock_questions", None)

    session.pop("mock_answers", None)

    session.pop("review_questions", None)

    session.pop("current_question", None)

    return redirect(url_for("start_exam"))

# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.route("/health")
def health():

    return {
        "status": "running",
        "application": "Academy",
        "course_loaded": session.get("course", "")
    }

# ==========================================================
# ERROR HANDLERS
# ==========================================================




# ==========================================================
# CLEAR EXAM
# ==========================================================

@app.route("/clear_exam")
def clear_exam():

    keys = [

        "course",

        "mock_questions",

        "mock_answers",

        "review_questions",

        "current_question"

    ]

    for key in keys:

        session.pop(key, None)

    return redirect(url_for("dashboard"))


# ==========================================================
# RESTART EXAM
# ==========================================================

# ==========================================================
# RESTART EXAM
# ==========================================================


@app.route("/restart_exam")
def restart_exam():


    # Remember which course and exam mode the user was taking
    course = session.get("course", "itil")
    mode = session.get("exam_mode", "final")

    # Clear previous exam data
    session.pop("mock_questions", None)
    session.pop("mock_answers", None)
    session.pop("current_question", None)
    session.pop("review_questions", None)

    # Start the same course and same exam type again
    initialize_exam(course, mode)

    return redirect(url_for("mock_exam", course=course))
# ==========================================================
# APPLICATION START
# ==========================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=8080,

        debug=True

    )
