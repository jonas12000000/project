import os
import re

# importing required functions
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


# importing functions form helper
from helper import login_required, apology, admin_required, teacher_required, cash_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# main route displaying index page
@app.route("/", methods=["GET", "POST"])
def index():
    # if method is post display the student details else display index page
    if request.method == "POST":
        if not request.form.get("sid"):
            return render_template("index.html")

        sid = request.form.get("sid")

        row = db.execute("SELECT * FROM student WHERE student_id = :sid", {"sid": sid}).fetchone()

        if row is None:
            emsg = "Sorry the student with provided ID doesn't exist!"
            return render_template("show_student.html", emsg=emsg)

        return render_template("show_student.html", row=row)
    else:
        return render_template("index.html")


# adding teacher for sign in
@app.route("/add_teacher", methods=["GET", "POST"])
@admin_required
def add_teacher():
    if request.method == "POST":
        if not request.form.get("role") or request.form.get("role") is None:
            rmsg = "Please select a role"
            return render_template("amain.html", rmsg=rmsg)
        elif not request.form.get("username"):
            umsg = "Please type a username"
            return render_template("amain.html", umsg=umsg)
        elif not request.form.get("password"):
            pmsg = "Please type a password"
            return render_template("amain.html", pmsg=pmsg)
        elif not request.form.get("repass"):
            remsg = "Please type the same password again!"
            return render_template("amain.html", remsg=remsg)

        role = request.form.get("role")
        username = request.form.get("username")

        row = db.execute("SELECT * FROM teacher WHERE username = :username", {"username": username}).fetchall()

        # checking for username if already exist
        if row is None:
            umsg="Username already exist!"
            return render_template("amain.html", umsg=umsg)

        password =request.form.get("password")

        # checking for validity of password
        if len(password) < 6:
            pmsg = "Length of password must be more than 6 characters!"
            return render_template("amain.html", pmsg=pmsg)
        elif not re.search("[a-zA-Z]", password):
            pmsg = "Password should contain number, letters and a  not less than 6 characters"
            return render_template("amain.html", pmsg=pmsg)
        elif not re.search("[0-9]", password):
            pmsg = "Password should contain number, letters and a  not less than 6 characters"
            return render_template("amain.html", pmsg=pmsg)
        elif not re.search(r"[.^$*+?{}[\]\\|()_@#]", password):
            pmsg = "Password should contain number, letters and a  not less than 6 characters"
            return render_template("amain.html", pmsg=pmsg)

        repass = request.form.get("repass")

        # if retyped password match password
        if repass != password:
            remsg = "Please type the same password again"
            return render_template("amain.html", remsg=remsg)

        password = generate_password_hash(password)

        # adding to table
        try:
            db.execute("INSERT INTO teacher(username, password, role) VALUES (:username, :password, :role)",
                       {"username":username, "password":password, "role":role})
            db.commit()
        except (ValueError, InternalServerError):
            return apology("Something went Wrong!!!")

        row = db.execute("SELECT teacher_id FROM teacher WHERE username = :username", {"username": username}).fetchone()
        session["user_id"] = row.teacher_id

        success = "User added successfully!"

        return render_template("amain.html", success=success)

    else:
        return render_template("amain.html")


# signing as a teacher page
@app.route("/teacher", methods=["GET", "POST"])
def teacher():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            umsg = "Please type your username!"
            return render_template("teacher.html", umsg=umsg)
        elif not request.form.get("password"):
            pmsg = "Please type your password!"
            return render_template("teacher.html", pmsg=pmsg)

        username = request.form.get("username")
        password = request.form.get("password")

        row = db.execute("SELECT * FROM teacher WHERE username = :username", {"username": username}).fetchone()

        # checking if the teacher is in the table or password is correct and redirecting to their page
        if row is None:
            umsg = "Username didn't exist!"
            return render_template("teacher.html", umsg=umsg)
        elif row.role == "admin":
            if password != row.password:
                pmsg = "Please type correct password"
                return render_template("teacher.html", pmsg=pmsg)
            else:
                session["user_id"] = row.teacher_id
                session["admin_id"] = row.teacher_id
                return redirect("/add_teacher")
        else:
            if not check_password_hash(row.password, password):
                pmsg= "Please type correct password!"
                return render_template("teacher.html", pmsg=pmsg)
            elif row.role == "cashier":
                session["user_id"] = row.teacher_id
                session["cash_id"] = row.teacher_id
                return redirect("/fee")
            elif row.role == "teacher":
                session["user_id"] = row.teacher_id
                session["teacher_id"] = row.teacher_id
                return redirect("/add_result")

        session["user_id"] = row.teacher_id

        return redirect("/add_student")
    else:
        return render_template("teacher.html")


# adding student page after logging as a teacher
@app.route("/add_student", methods=["GET", "POST"])
@login_required
def add_student():
    if request.method == "POST":
        if not request.form.get("name"):
            nmsg = "Please type the name!"
            return render_template("student.html", nmsg=nmsg)
        elif not request.form.get("fname"):
            fmsg = "Please type father name"
            return render_template("student.html", fmsg=fmsg)
        elif not request.form.get("gname"):
            gmsg = "Please type Grandfather name"
            return render_template("student.html", gmsg=gmsg)
        elif not request.form.get("state") or request.form.get("state") is None:
            smsg = "Please select a state"
            return render_template("student.html", smsg=smsg)
        elif not request.form.get("city"):
            cmsg = "Please select a city"
            return render_template("student.html", cmsg=cmsg)

        name = request.form.get("name")
        fname = request.form.get("fname")
        gname = request.form.get("gname")
        state = request.form.get("state")
        city = request.form.get("city")

        # adding student to the table
        try:
            s_id = db.execute("INSERT INTO student(name, father_name, grandfather_name, state, city) VALUES (:name, :fname, :gname, :state, :city) RETURNING student_id",
                       {"name": name, "fname": fname, "gname": gname, "state": state, "city": city}).fetchone()
            db.execute("INSERT INTO fees(student_id) VALUES (:sid)", {"sid": s_id.student_id})
            db.commit()
            # here come the last insert and insert in to fees table
        except (ValueError, InternalServerError):
            return apology("Something went wrong!")

        success = "Student added successfully!"

        return render_template("student.html", success=success)
    else:
        return render_template("student.html")


# adding student result after logging as a teacher
@app.route("/add_result", methods=["GET", "POST"])
@login_required
@teacher_required
def add_result():
    if request.method == "POST":
        if not request.form.get("subject") or request.form.get("subject") is None:
            smsg = "Please select a subject"
            return render_template("addres.html", smsg=smsg)
        elif not request.form.get("exam_id"):
            emsg = "Please write the exam id!"
            return render_template("addres.html", emsg=emsg)
        elif not request.form.get("student_id"):
            stmsg = "Please write the student id!"
            return render_template("addres.html", stmsg=stmsg)
        elif not request.form.get("mark"):
            mmsg = "Please write the mark!"
            return render_template("addres.html", mmsg=mmsg)

        subject = request.form.get("subject")
        exam_id = request.form.get("exam_id")
        if not re.match(r"^\d{5}$", exam_id):
            emsg = "Please write the correct exam code!"
            return render_template("addres.html", emsg=emsg)

        student_id = request.form.get("student_id")
        row = db.execute("SELECT student_id FROM student WHERE student_id = :student_id", {"student_id": student_id}).fetchall()
        if row is None:
            stmsg = "Please enter the correct student id!"
            return render_template("addres.html", stmsg=stmsg)

        # validating the marks entered
        mark = float(request.form.get("mark"))
        if mark > 100 or mark < 0:
            mmsg = "Please write the correct mark!"
            return render_template("addres.html", mmsg=mmsg)

        row = db.execute("SELECT * FROM exam WHERE student_id = :sid AND subject = :subject AND exam_code = :exam_code",
                         {"sid": student_id, "subject": subject, "exam_code": exam_id}).fetchone()

        if row is None:
            # insert the mark and the rest to exam table
            try:
                db.execute(
                    "INSERT INTO exam(subject, exam_code, student_id, mark) VALUES (:subject, :examc, :sid, :mark)",
                    {"subject": subject, "examc": exam_id, "sid": student_id, "mark": mark})
                db.commit()
            except (InternalServerError, ValueError):
                return apology("Something went wrong!")
        else:
            stmsg = "You have already registered this student!"
            return render_template("addres.html", stmsg=stmsg)

        success = "Added Successfully!"

        return render_template("addres.html", success=success)
    else:
        return render_template("addres.html")


# fee page to see and add the student fees after logging as cashier
@app.route("/fee", methods=["GET", "POST"])
@login_required
@cash_required
def fee():
    if request.method == "POST":
        if not request.form.get("student_id"):
            smsg = "Please provide the student id!"
            return render_template("fees.html", smsg=smsg)
        elif not request.form.get("month") or request.form.get("month") is None:
            mmsg = "Please select a month!"
            return render_template("fees.html", mmsg=mmsg)

        student_id = request.form.get("student_id")
        row = db.execute("SELECT student_id FROM student WHERE student_id = :student_id", {"student_id": student_id}).fetchall()
        if row is None:
            smsg = "Please type the correct student ID"
            return render_template("fees.html", smsg=smsg)

        month = request.form.get("month")

        paid = True
        # update the month in fees table according to the month selected
        if month == "jan":
            db.execute("UPDATE fees SET jan = :paid WHERE student_id = :student_id", {"paid": paid, "student_id": student_id})
            db.commit()
        elif month == "feb":
            db.execute("UPDATE fees SET feb = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()
        elif month == "mar":
            db.execute("UPDATE fees SET mar = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()
        elif month == "apr":
            db.execute("UPDATE fees SET apr = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()
        elif month == "may":
            db.execute("UPDATE fees SET may = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()
        elif month == "jun":
            db.execute("UPDATE fees SET jun = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()
        elif month == "jul":
            db.execute("UPDATE fees SET jul = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()
        elif month == "aug":
            db.execute("UPDATE fees SET aug = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()
        elif month == "sep":
            db.execute("UPDATE fees SET sep = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()
        elif month == "oct":
            db.execute("UPDATE fees SET oct = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()
        elif month == "nov":
            db.execute("UPDATE fees SET nov = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()
        elif month == "dec":
            db.execute("UPDATE fees SET dec = :paid WHERE student_id = :sid", {"paid": paid, "sid": student_id})
            db.commit()

        success = "Paid Successfully!"

        return render_template("fees.html", success=success)

    else:
        return render_template("fees.html")


# rendering the about us page
@app.route("/about_us", methods=["GET"])
def about_us():
    return render_template("about_us.html")


# rendering activities page
@app.route("/activities", methods=["GET"])
def activities():
    return render_template("activities.html")


# rendering the annoucement page
@app.route("/annoucement", methods=["GET"])
def annoucement():
    return render_template("annoucement.html")


# rendering the programs page
@app.route("/programs", methods=["GET"])
def programs():
    return render_template("programs.html")


# rendering the result page
@app.route("/result", methods=["GET"])
def result():
    return render_template("result.html")


# students view their result
@app.route("/view_result", methods=["POST"])
def view_result():
    student_id = request.form.get("student_id")
    if student_id is None:
        return jsonify({"success": False})

    subject = request.form.get("subject")
    if subject is None:
        return jsonify({"success": False})

    exam_code = request.form.get("exam_code")
    if exam_code is None:
        return jsonify({"success": False})

    row = db.execute("SELECT name, father_name, subject, mark FROM exam INNER JOIN student ON exam.student_id = student.student_id  WHERE exam.student_id = :sid AND exam.subject = :subject AND exam.exam_code = :exam_code",
                     {"sid": student_id, "subject": subject, "exam_code": exam_code}).fetchone()

    if row is None:
        return jsonify({"success": False})

    return jsonify({"success": True, "name": row.name, "father": row.father_name, "subject": row.subject, "mark": row.mark})


# route to handle the fees view
@app.route("/view_fee", methods=["POST"])
def view_fee():
    student_id = request.form.get("student_id")
    if student_id is None:
        return jsonify({"success": False})

    row1 = db.execute("SELECT student_id FROM fees WHERE student_id = :sid", {"sid": student_id}).fetchone()
    if row1 is None:
        return jsonify({"success": False})

    row = db.execute("SELECT name, father_name, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec FROM fees INNER JOIN student ON fees.student_id = student.student_id WHERE fees.student_id = :sid",
                         {"sid": student_id}).fetchone()

    if row is None:
        return jsonify({"success": False})

    return jsonify({"success": True, "name": row.name, "father": row.father_name, "jan": row.jan, "feb": row.feb,
                    "mar": row.mar, "apr": row.apr, "may": row.may, "jun": row.jun, "jul": row.jul, "aug": row.aug,
                    "sep": row.sep, "oct": row.oct, "nov": row.nov, "dec": row.dec})


# view the students whose result has been added
@app.route("/added_students", methods=["POST"])
def added_students():
    subject = request.form.get("subject")
    if subject is None:
        return jsonify({"success": False})

    exam_code = request.form.get("exam_code")
    if exam_code is None:
        return jsonify({"success": False})

    row = db.execute("SELECT name, father_name, subject, mark FROM exam INNER JOIN student ON exam.student_id = student.student_id WHERE exam.subject = :subject AND exam.exam_code = :exam_code",
                     {"subject": subject, "exam_code": exam_code}).fetchall()

    name = []
    father = []
    subject = []
    mark = []
    for i in row:
        name.append(i.name)
        father.append(i.father_name)
        subject.append(i.subject)
        mark.append(i.mark)

    return jsonify({"success": True, "name": name, "father": father, "subject": subject,
                    "mark": mark})


# logging out
@app.route("/logout")
def logout():
    # clear session storage
    session.clear()

    return redirect("/teacher")


# handling errors
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)