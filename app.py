print("APP.PY STARTED")
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

import mysql.connector
from openai import OpenAI

from config import DB_CONFIG, OPENAI_API_KEY


app = Flask(__name__)

app.secret_key = "change-this-secret-key"


# -----------------------------
# DATABASE CONNECTION
# -----------------------------

def get_db_connection():

    return mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )


# -----------------------------
# HOME
# -----------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------
# PRODUCTS
# -----------------------------

@app.route("/products")
def products():

    return render_template("products.html")


# -----------------------------
# ENQUIRY PAGE
# -----------------------------

@app.route("/enquiry")
def enquiry():

    return render_template("enquiry.html")


# -----------------------------
# SAVE LEAD
# -----------------------------

@app.route("/submit-enquiry", methods=["POST"])
def submit_enquiry():

    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    company = request.form.get("company")
    product = request.form.get("product")
    quantity = request.form.get("quantity")
    message = request.form.get("message")

    if not name or not phone:

        return "Name and phone are required", 400

    db = get_db_connection()

    cursor = db.cursor()

    query = """
        INSERT INTO leads
        (name, phone, email, company, product, quantity, message)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        name,
        phone,
        email,
        company,
        product,
        quantity,
        message
    )

    cursor.execute(query, values)

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("success"))


# -----------------------------
# SUCCESS
# -----------------------------

@app.route("/success")
def success():

    return render_template("success.html")


# -----------------------------
# ADMIN LOGIN
# -----------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db_connection()

        cursor = db.cursor(dictionary=True)

        query = """
            SELECT * FROM admin
            WHERE username = %s
            AND password = %s
        """

        cursor.execute(query, (username, password))

        admin = cursor.fetchone()

        cursor.close()
        db.close()

        if admin:

            session["admin"] = username

            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")


# -----------------------------
# LOGOUT
# -----------------------------

@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect(url_for("login"))


# -----------------------------
# DASHBOARD
# -----------------------------

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:

        return redirect(url_for("login"))

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM leads")

    total = cursor.fetchone()["total"]

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM leads
        WHERE status = 'New'
    """)

    new_leads = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM leads
        WHERE status = 'Contacted'
    """)

    contacted = cursor.fetchone()["count"]

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM leads
        WHERE status = 'Converted'
    """)

    converted = cursor.fetchone()["count"]

    cursor.close()
    db.close()

    return render_template(
        "dashboard.html",
        total=total,
        new_leads=new_leads,
        contacted=contacted,
        converted=converted
    )


# -----------------------------
# LEADS
# -----------------------------

@app.route("/leads")
def leads():

    if "admin" not in session:

        return redirect(url_for("login"))

    db = get_db_connection()

    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM leads
        ORDER BY created_at DESC
    """)

    leads_data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "leads.html",
        leads=leads_data
    )


# -----------------------------
# UPDATE LEAD STATUS
# -----------------------------

@app.route("/update-status/<int:lead_id>", methods=["POST"])
def update_status(lead_id):

    if "admin" not in session:

        return redirect(url_for("login"))

    status = request.form.get("status")

    db = get_db_connection()

    cursor = db.cursor()

    cursor.execute("""
        UPDATE leads
        SET status = %s
        WHERE id = %s
    """, (status, lead_id))

    db.commit()

    cursor.close()
    db.close()

    return redirect(url_for("leads"))


# -----------------------------
# AI ASSISTANT
# -----------------------------

@app.route("/ai", methods=["POST"])
def ai():

    data = request.get_json()

    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({
            "reply": "Please enter a question."
        }), 400

    if not OPENAI_API_KEY:
        return jsonify({
            "reply": "OpenAI API key is not configured."
        }), 500

    try:

        client = OpenAI(
            api_key=OPENAI_API_KEY
        )

        response = client.responses.create(

            model="gpt-5.6-luna",

            instructions="""
You are the AI assistant for Sabarish Garments,
a professional garment manufacturing company.

Company:
Sabarish Garments

Products:
- Cotton T-Shirts
- Polo T-Shirts
- Hoodies
- Oversized T-Shirts

Minimum Order Quantity:
100 pieces

Services:
- Bulk garment manufacturing
- Custom branding
- Wholesale orders

Your responsibilities:
- Answer customer questions clearly.
- Explain products and services.
- Help customers understand the ordering process.
- Ask for required information when they want a quotation.

Important rules:
- Never invent prices.
- Never invent stock availability.
- Never promise delivery dates.
- Never make guarantees that the company has not provided.
- For quotation requests, ask for:
  Name
  Phone number
  Product
  Quantity
  Company name
""",

            input=user_message
        )

        reply = response.output_text

        return jsonify({
            "reply": reply
        })

    except Exception as e:
     print("========== AI ERROR ==========")
     print("ERROR TYPE:", type(e).__name__)
     print("ERROR:", str(e))
     print("==============================")

     return jsonify({
        "reply": f"AI Error: {type(e).__name__}: {str(e)}"
    }), 500


# -----------------------------
# RUN SERVER
# -----------------------------

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)
    