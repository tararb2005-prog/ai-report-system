# 🔥 FIX matplotlib error
import matplotlib
matplotlib.use('Agg')

import pandas as pd
import matplotlib.pyplot as plt

from django.shortcuts import render, redirect
from django.http import FileResponse

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from reportlab.platypus import SimpleDocTemplate, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet

from .models import Report

import os
from datetime import datetime
import base64
from io import BytesIO


# 🔐 LOGIN + SIGNUP
def auth_page(request):
    if request.method == "POST":
        action = request.POST.get("action")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if action == "signup":
            if User.objects.filter(username=email).exists():
                return render(request, "auth.html", {"error": "User already exists"})

            User.objects.create_user(username=email, password=password)
            return render(request, "auth.html", {"success": "Account created! Login now."})

        elif action == "login":
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('/home/')
            else:
                return render(request, "auth.html", {"error": "Invalid credentials"})

    return render(request, "auth.html")


# 🚪 LOGOUT
def logout_view(request):
    logout(request)
    return redirect('/')


# 📊 MAIN PAGE
@login_required
def index(request):

    # 🔁 AFTER DOWNLOAD → SHOW GRAPH
    if request.method == "GET":
        context = {
            "graph": request.session.pop('graph', None),
            "avg": request.session.pop('avg', None),
            "highest": request.session.pop('highest', None),
            "lowest": request.session.pop('lowest', None),
            "topper": request.session.pop('topper', None),
        }
        return render(request, "index.html", context)

    # 📤 FILE UPLOAD
    if request.method == "POST":
        uploaded_file = request.FILES["file"]
        data = pd.read_csv(uploaded_file)

        numeric_cols = data.select_dtypes(include=['number']).columns
        text_cols = data.select_dtypes(include=['object']).columns

        num_col = numeric_cols[0]
        text_col = text_cols[0] if len(text_cols) > 0 else None

        # 📊 ANALYSIS (CONVERT TYPES 🔥)
        avg = float(round(data[num_col].mean(), 2))
        highest = float(data[num_col].max())
        lowest = float(data[num_col].min())
        topper = str(data.loc[data[num_col].idxmax()][text_col]) if text_col else "N/A"

        # 📈 GRAPH
        plt.figure()
        if text_col:
            plt.bar(data[text_col], data[num_col])
        else:
            plt.plot(data[num_col])

        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        graph = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        # Save for PDF
        plt.savefig("chart.png")
        plt.close()

        # 📁 MEDIA
        if not os.path.exists("media"):
            os.makedirs("media")

        file_name = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join("media", file_name)

        # 📄 PDF
        doc = SimpleDocTemplate(file_path)
        styles = getSampleStyleSheet()

        content = []
        content.append(Paragraph("📊 AI Generated Report", styles["Title"]))
        content.append(Paragraph(f"Average: {avg}", styles["Normal"]))
        content.append(Paragraph(f"Highest: {highest}", styles["Normal"]))
        content.append(Paragraph(f"Lowest: {lowest}", styles["Normal"]))
        content.append(Paragraph(f"Top Performer: {topper}", styles["Normal"]))
        content.append(Image("chart.png", width=400, height=250))

        doc.build(content)

        # 💾 SAVE DB
        Report.objects.create(file_name=file_name, pdf_file=file_name)

        # 🔥 STORE SAFE TYPES IN SESSION
        request.session['graph'] = graph
        request.session['avg'] = avg
        request.session['highest'] = highest
        request.session['lowest'] = lowest
        request.session['topper'] = topper

        # 🔥 AUTO DOWNLOAD
        return FileResponse(open(file_path, "rb"), as_attachment=True)


# 📂 DASHBOARD
@login_required
def dashboard(request):
    reports = Report.objects.all().order_by('-created_at')
    return render(request, 'dashboard.html', {'reports': reports})