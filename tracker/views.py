"""Views for the Health Tracker app."""

from typing import List, Optional
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import HealthRecord
from .forms import HealthForm

# ----------------------
# Helper Functions
# ----------------------
def bmi_suggestion(bmi: float) -> str:
    if bmi < 18.5:
        return (
            "Underweight – Consider a nutritious diet rich in protein "
            "and healthy fats, and aim for regular meals to gain healthy weight."
        )
    if 18.5 <= bmi < 25:
        return "Normal – Keep maintaining your healthy lifestyle with balanced diet and regular exercise."
    if 25 <= bmi < 30:
        return (
            "Overweight – Include regular physical activity in your routine "
            "and follow a balanced diet to manage weight."
        )
    return "Obese – Consult a healthcare professional and adopt a structured diet and exercise plan."

def workout_suggestion(bmi: float) -> str:
    if bmi < 18.5:
        return "Focus on strength training (weight lifting, push-ups, squats) and light cardio like walking or cycling."
    if 18.5 <= bmi < 25:
        return "Maintain fitness with a mix of cardio and strength training. Include core and flexibility exercises."
    if 25 <= bmi < 30:
        return "Moderate-intensity cardio plus full-body strength training. Low-impact activities to protect joints."
    return "Start with low-impact exercises and gradually increase intensity."

# ----------------------
# Authentication Views
# ----------------------
def welcome(request):
    return render(request, 'tracker/welcome.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('tracker:signup')

        User.objects.create_user(username=username, password=password)
        messages.success(request, 'Account created successfully')
        return redirect('tracker:login')

    return render(request, 'tracker/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('tracker:bmi')
        messages.error(request, 'Invalid credentials')

    return render(request, 'tracker/login.html')

def logout_view(request):
    logout(request)
    return redirect('tracker:welcome')

# ----------------------
# Health Views
# ----------------------
@login_required
def bmi_calculator(request):
    bmi = None
    calories = None
    bmi_msg = None
    bmi_workout = None
    form = HealthForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        weight = form.cleaned_data['weight']
        height_cm = form.cleaned_data['height']
        height_m = height_cm / 100
        steps = form.cleaned_data.get('steps') or 0
        speed = form.cleaned_data.get('speed') or 0
        gender = form.cleaned_data['gender']

        # Calculate BMI
        if "calculate_bmi" in request.POST:
            bmi = round(weight / (height_m ** 2), 2)
            bmi_msg = bmi_suggestion(bmi)
            bmi_workout = workout_suggestion(bmi)
            form = HealthForm(initial={
                'weight': weight,
                'height': height_cm,
                'gender': gender,
                'steps': steps,
                'speed': speed,
                'bmi': bmi
            })

        # Calculate calories
        if "calculate_calories" in request.POST:
            step_length = 0.762
            distance_km = (steps * step_length) / 1000
            speed_factor = 1 + (speed - 5) * 0.05
            calories = round(weight * distance_km * speed_factor, 2)
            form = HealthForm(initial={
                'weight': weight,
                'height': height_cm,
                'gender': gender,
                'steps': steps,
                'speed': speed,
                'calories': calories
            })

        # Save record
        if "save_record" in request.POST:
            # Always recalc BMI & calories when saving
            bmi = round(weight / (height_m ** 2), 2)
            step_length = 0.762
            distance_km = (steps * step_length) / 1000
            speed_factor = 1 + (speed - 5) * 0.05
            calories = round(weight * distance_km * speed_factor, 2)

            HealthRecord.objects.create(
                user=request.user,
                weight=weight,
                height_cm=height_cm,
                gender=gender,
                bmi=bmi,
                calories=calories,
                steps=steps,
                speed=speed
            )
            messages.success(request, "Record saved successfully!")

            form = HealthForm(initial={
                'weight': weight,
                'height': height_cm,
                'gender': gender,
                'steps': steps,
                'speed': speed,
                'bmi': bmi,
                'calories': calories
            })

    # Prepare chart data
    history_records = HealthRecord.objects.filter(user=request.user).order_by('date')
    chart_dates = [r.date.strftime('%Y-%m-%d') for r in history_records]
    chart_bmis = [r.bmi if r.bmi is not None else 0 for r in history_records]
    chart_calories = [r.calories if r.calories is not None else 0 for r in history_records]
    chart_steps = [r.steps if r.steps is not None else 0 for r in history_records]

    return render(request, 'tracker/bmi.html', {
        'form': form,
        'bmi': bmi,
        'calories': calories,
        'bmi_msg': bmi_msg,
        'bmi_workout': bmi_workout,
        'chart_dates': chart_dates,
        'chart_bmis': chart_bmis,
        'chart_calories': chart_calories,
        'chart_steps': chart_steps,
    })

@login_required
def history(request):
    records = HealthRecord.objects.filter(user=request.user).order_by('date')
    chart_dates = [r.date.strftime('%Y-%m-%d') for r in records]
    chart_bmis = [r.bmi if r.bmi is not None else 0 for r in records]
    chart_calories = [r.calories if r.calories is not None else 0 for r in records]
    chart_steps = [r.steps if r.steps is not None else 0 for r in records]

    return render(request, 'tracker/history.html', {
        'records': records,
        'chart_dates': chart_dates,
        'chart_bmis': chart_bmis,
        'chart_calories': chart_calories,
        'chart_steps': chart_steps,
    })

@login_required
def edit_record(request, pk):
    record = get_object_or_404(HealthRecord, pk=pk, user=request.user)
    if request.method == 'POST':
        form = HealthForm(request.POST)
        if form.is_valid():
            record.weight = form.cleaned_data['weight']
            record.height_cm = form.cleaned_data['height']
            record.gender = form.cleaned_data['gender']
            record.steps = form.cleaned_data.get('steps') or 0
            record.speed = form.cleaned_data.get('speed') or 0

            height_m = record.height_cm / 100
            record.bmi = round(record.weight / (height_m ** 2), 2)
            step_length = 0.762
            distance_km = (record.steps * step_length) / 1000
            speed_factor = 1 + max(0, (record.speed - 5) * 0.05)
            record.calories = round(record.weight * distance_km * speed_factor, 2)

            record.save()
            messages.success(request, "Record updated successfully!")
            return redirect('tracker:history')
    else:
        form = HealthForm(initial={
            'weight': record.weight,
            'height': record.height_cm,
            'gender': record.gender,
            'steps': record.steps,
            'speed': record.speed,
            'bmi': record.bmi,
            'calories': record.calories
        })
    return render(request, 'tracker/edit_record.html', {'form': form, 'record': record})

@login_required
def delete_record(request, record_id):
    record = get_object_or_404(HealthRecord, id=record_id, user=request.user)
    if request.method == 'POST':
        record.delete()
        messages.success(request, "Record deleted successfully!")
        return redirect('tracker:history')
    return render(request, 'tracker/delete_confirm.html', {'record': record})
