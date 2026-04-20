from flask import Flask, render_template, request, redirect, send_file, session
import pickle
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, ListFlowable
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "secret123"

# ================= LOAD MODEL =================
model = pickle.load(open("model/water_quality_model.pkl", "rb"))

# ================= USERS =================
users = {"admin": "1234"}

# ================= HISTORY =================
history = []

# ================= FEATURE IMPORTANCE =================
importance = {
    "pH": 0.015,
    "Temperature": 0.019,
    "DO": 0.037,
    "Turbidity": 0.875,
    "Salinity": 0.052
}

# ======================================================
# ---------------- LOGIN PAGE --------------------------
# ======================================================
@app.route("/")
def login_page():
    return render_template("login.html")


# ======================================================
# ---------------- LOGIN FUNCTION ----------------------
# ======================================================
@app.route("/login", methods=["POST"])
def login():
    user = request.form["username"]
    pwd = request.form["password"]

    if user in users and users[user] == pwd:
        session["user"] = user
        return redirect("/dashboard")

    return "Invalid Login ❌"


# ======================================================
# ---------------- DASHBOARD ---------------------------
# ======================================================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template(
        "dashboard.html",
        history=history[-5:] if history else []
    )


# ======================================================
# ---------------- PREDICT -----------------------------
# ======================================================
@app.route("/predict", methods=["POST"])
def predict():
    if "user" not in session:
        return redirect("/")

    try:
        # ================= INPUT =================
        ph = float(request.form["ph"])
        temp = float(request.form["temp"])
        do = float(request.form["do"])
        turbidity = float(request.form["turbidity"])
        salinity = float(request.form["salinity"])

        # ================= VALIDATION =================
        if ph < 0 or ph > 14:
            return "Invalid pH value"
        if temp < 0 or temp > 100:
            return "Invalid Temperature"
        if do < 0 or do > 20:
            return "Invalid Dissolved Oxygen value"
        if turbidity < 0 or turbidity > 1000:
            return "Invalid Turbidity value"
        if salinity < 0 or salinity > 100:
            return "Invalid Salinity value"

        # ================= MODEL INPUT =================
        df = pd.DataFrame(
            [[ph, temp, do, turbidity, salinity]],
            columns=['pH', 'Temperature', 'Dissolved Oxygen', 'Turbidity', 'Salinity']
        )

        # ================= PREDICTION =================
        pred = model.predict(df)
        prob = model.predict_proba(df)
        confidence = round(max(prob[0]) * 100, 2)

        result = "Safe Water ✅" if pred[0] == 1 else "Unsafe Water ❌"

        # ================= SAFETY LEVEL =================
        if pred[0] == 1:
            safety_level = "Very Safe" if confidence >= 90 else "Moderately Safe"
        else:
            safety_level = "High Risk" if confidence >= 90 else "Unsafe"

        # ================= TECHNICAL REASONS =================
        reasons = []

        if ph < 6.5:
            reasons.append("pH is too acidic")
        elif ph > 8.5:
            reasons.append("pH is too alkaline")

        if do < 5:
            reasons.append("Low dissolved oxygen")

        if turbidity > 5:
            reasons.append("Water is turbid (dirty/muddy)")

        if salinity > 20:
            reasons.append("High salinity (salty water)")

        if temp > 35:
            reasons.append("Water temperature is high")

        if not reasons:
            reasons.append("All parameters are within safe range")

        # ================= EASY EXPLANATION =================
        easy_points = []

        if pred[0] == 1:
            easy_points.append("✔ Safe for drinking")
            easy_points.append("✔ Safe for cooking and daily use")
            easy_points.append("✔ Safe for bathing and washing clothes")

            if turbidity > 3:
                easy_points.append("⚠ Slight dirt present, filter before drinking")

        else:
            easy_points.append("❌ Not safe for drinking directly")

            if turbidity > 5:
                easy_points.append("⚠ Water is dirty, filtration needed")

            if ph < 6.5 or ph > 8.5:
                easy_points.append("⚠ May cause skin or stomach irritation")

            if salinity > 20:
                easy_points.append("⚠ Salty water may not be suitable for regular use")

            easy_points.append("✔ Can be used for washing after filtration")
            easy_points.append("⚠ Not safe for children or elderly")
            easy_points.append("⚠ Boiling removes germs but not chemicals")

        easy_points.append("✔ Use RO/UV filter for safer water")

        # ================= PARAMETER STATUS =================
        param_status = {
            "pH": "Normal" if 6.5 <= ph <= 8.5 else "Unbalanced",
            "DO": "Good" if do >= 5 else "Low",
            "Turbidity": "Clear" if turbidity <= 5 else "Dirty",
            "Salinity": "Normal" if salinity <= 20 else "High",
            "Temperature": "Normal" if temp <= 35 else "High"
        }

        # ================= SUGGESTIONS =================
        suggestions = []

        if turbidity > 5:
            suggestions.append("Use cloth filtration or RO filter")

        if do < 5:
            suggestions.append("Water may be stagnant, aeration may help")

        if salinity > 20:
            suggestions.append("Avoid drinking, use desalination or purified water")

        if ph < 6.5 or ph > 8.5:
            suggestions.append("pH imbalance detected — use a purifier")

        if temp > 35:
            suggestions.append("Store water in a cool place before use")

        if not suggestions:
            suggestions.append("Water is good for daily usage")

        # ================= SPECIAL CASE =================
        special_case = ""

        if 6.5 <= ph <= 7.5 and turbidity <= 6:
            special_case = "Borderline water: filter before drinking"

        if turbidity > 20 or salinity > 30:
            special_case = "Industrial wastewater: not suitable for any use"

        # ================= USAGE =================
        if turbidity > 20 or ph < 5 or ph > 9:
            usage = "Not usable"
        elif turbidity > 5 or do < 5:
            usage = "Use after filtration"
        elif pred[0] == 1:
            usage = "Safe for drinking"
        else:
            usage = "Not safe"

        # ================= RISK SCORE =================
        risk_score = round((100 - confidence) if pred[0] == 1 else confidence, 2)

        if risk_score < 30:
            risk_color = "green"
        elif risk_score < 60:
            risk_color = "orange"
        else:
            risk_color = "red"

        # ================= ALERT =================
        if pred[0] == 0 and confidence > 85:
            alert = "🚨 High Risk Water Detected!"
            alert_type = "danger"

        elif turbidity > 10:
            alert = "⚠ Water quality is poor"
            alert_type = "warning"

        else:
            alert = "✔ Water condition acceptable"
            alert_type = "success"

        # ================= HISTORY SAVE =================
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d %b %Y")

        history.append({
            "ph": ph,
            "temp": temp,
            "do": do,
            "turbidity": turbidity,
            "salinity": salinity,
            "result": result,
            "confidence": confidence,
            "reasons": reasons,
            "easy_points": easy_points,
            "time": current_time,
            "date": current_date,
            "alert": alert,
            "usage": usage
        })

        # Keep only latest 20 records
        if len(history) > 20:
            history.pop(0)

        # ================= TREND DATA =================
        times = [h["time"] for h in history[-5:]]
        scores = [h["confidence"] for h in history[-5:]]

        # ================= RETURN TO DASHBOARD =================
        return render_template(
            "dashboard.html",
            prediction_text=result,
            confidence=confidence,
            safety_level=safety_level,
            reasons=reasons,
            easy_points=easy_points,
            usage=usage,
            alert=alert,
            alert_type=alert_type,
            risk_score=risk_score,
            risk_color=risk_color,
            param_status=param_status,
            suggestions=suggestions,
            special_case=special_case,
            times=times,
            scores=scores,
            ph=ph,
            temp=temp,
            do=do,
            turbidity=turbidity,
            salinity=salinity,
            importance=importance,
            history=history[-5:]
        )

    except Exception as e:
        return f"Error during prediction: {str(e)}"


# ======================================================
# ---------------- DOWNLOAD PDF REPORT -----------------
# ======================================================
@app.route("/download")
def download():
    if "user" not in session:
        return redirect("/")

    doc = SimpleDocTemplate("report.pdf")
    styles = getSampleStyleSheet()
    content = []

    if history:
        last = history[-1]

        content.append(Paragraph("AI Water Quality Report", styles["Title"]))
        content.append(Spacer(1, 10))

        content.append(Paragraph("This report is AI-generated for awareness purposes.", styles["Normal"]))
        content.append(Paragraph(f"Generated on: {last['date']} at {last['time']}", styles["Normal"]))
        content.append(Spacer(1, 12))

        content.append(Paragraph(f"<b>Prediction Result:</b> {last['result']}", styles["Normal"]))
        content.append(Paragraph(f"<b>Confidence:</b> {last['confidence']}%", styles["Normal"]))
        content.append(Paragraph(f"<b>Usage:</b> {last['usage']}", styles["Normal"]))
        content.append(Paragraph(f"<b>Alert:</b> {last['alert']}", styles["Normal"]))
        content.append(Spacer(1, 12))

        # ================= INPUT VALUES =================
        content.append(Paragraph("<b>Input Parameters:</b>", styles["Heading2"]))
        content.append(Paragraph(f"pH: {last['ph']}", styles["Normal"]))
        content.append(Paragraph(f"Temperature: {last['temp']} °C", styles["Normal"]))
        content.append(Paragraph(f"Dissolved Oxygen: {last['do']} mg/L", styles["Normal"]))
        content.append(Paragraph(f"Turbidity: {last['turbidity']} NTU", styles["Normal"]))
        content.append(Paragraph(f"Salinity: {last['salinity']}", styles["Normal"]))
        content.append(Spacer(1, 12))

        # ================= TECHNICAL REASONS =================
        content.append(Paragraph("<b>Technical Reasons:</b>", styles["Heading2"]))
        tech = [Paragraph(r, styles["Normal"]) for r in last["reasons"]]
        content.append(ListFlowable(tech))
        content.append(Spacer(1, 12))

        # ================= EASY EXPLANATION =================
        content.append(Paragraph("<b>Simple Explanation:</b>", styles["Heading2"]))
        easy = [Paragraph(p, styles["Normal"]) for p in last["easy_points"]]
        content.append(ListFlowable(easy))
        content.append(Spacer(1, 12))

        # ================= GRAPH =================
        labels = ['pH', 'Temp', 'DO', 'Turbidity', 'Salinity']
        values = [last['ph'], last['temp'], last['do'], last['turbidity'], last['salinity']]

        plt.figure(figsize=(8, 4))
        plt.bar(labels, values)
        plt.title("Water Parameter Graph")
        plt.xlabel("Parameters")
        plt.ylabel("Values")
        plt.tight_layout()
        plt.savefig("graph.png")
        plt.close()

        content.append(Paragraph("<b>Parameter Graph:</b>", styles["Heading2"]))
        content.append(Spacer(1, 10))
        content.append(Image("graph.png", width=420, height=220))

    else:
        content.append(Paragraph("No prediction history available.", styles["Title"]))

    doc.build(content)
    return send_file("report.pdf", as_attachment=True)


# ======================================================
# ---------------- LOGOUT ------------------------------
# ======================================================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ======================================================
# ---------------- RUN APP -----------------------------
# ======================================================
if __name__ == "__main__":
    app.run(debug=True)
