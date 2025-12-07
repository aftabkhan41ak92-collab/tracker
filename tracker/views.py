from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HealthRecord
from .forms import HealthForm

def bmi_suggestion(bmi):
    if bmi < 18.5:
        return "Underweight – Consider a nutritious diet rich in protein and healthy fats, and aim for regular meals to gain healthy weight."
    elif 18.5 <= bmi < 25:
        return "Normal – Keep maintaining your healthy lifestyle with balanced diet and regular exercise."
    elif 25 <= bmi < 30:
        return "Overweight – Include regular physical activity in your routine and follow a balanced diet to manage weight."
    else:
        return "Obese – Consult a healthcare professional and adopt a structured diet and exercise plan."

def workout_suggestion(bmi):
    if bmi < 18.5:
        return "Focus on strength training (weight lifting, push-ups, squats) and light cardio like walking or cycling."
    elif 18.5 <= bmi < 25:
        return "Maintain fitness with a mix of cardio (running, swimming) and strength training. Include core and flexibility exercises."
    elif 25 <= bmi < 30:
        return "Moderate-intensity cardio (brisk walking, cycling) plus full-body strength training. Low-impact activities to protect joints."
    else:
        return "Start with low-impact exercises like walking, water aerobics, chair exercises, and light strength training. Gradually increase intensity."

def welcome(request):
    return render(request, 'tracker/welcome.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('tracker:signup')

        User.objects.create_user(username=username, password=password)
        messages.success(request, 'Account created successfully')
        return redirect('tracker:login')

    return render(request, 'tracker/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('tracker:bmi')
        else:
            messages.error(request, 'Invalid credentials')

    return render(request, 'tracker/login.html')

def logout_view(request):
    logout(request)
    return redirect('tracker:welcome')

@login_required
def bmi_calculator(request):
    bmi = None
    calories = None
    bmi_msg = None
    bmi_workout = None
    form = HealthForm(request.POST or None)

    if request.method == "POST":
        if "calculate_bmi" in request.POST and form.is_valid():
            weight = form.cleaned_data['weight']
            height_cm = form.cleaned_data['height']
            height_m = height_cm / 100
            bmi = round(weight / (height_m ** 2), 2)
            form.initial['bmi'] = bmi
            form.fields['bmi'].widget.attrs['value'] = bmi

            bmi_msg = bmi_suggestion(bmi)
            bmi_workout = workout_suggestion(bmi)

        if "calculate_calories" in request.POST and form.is_valid():
            weight = form.cleaned_data['weight']
            steps = form.cleaned_data.get('steps') or 0
            speed = form.cleaned_data.get('speed') or 0

            step_length = 0.762
            distance_km = (steps * step_length) / 1000
            speed_factor = 1 + (speed - 5) * 0.05
            calories = round(weight * distance_km * speed_factor, 2)
            form.initial['calories'] = calories
            form.fields['calories'].widget.attrs['value'] = calories

        if "save_record" in request.POST and form.is_valid():
            HealthRecord.objects.create(
                user=request.user,
                weight=form.cleaned_data['weight'],
                height_cm=form.cleaned_data['height'],
                gender=form.cleaned_data['gender'],
                bmi=form.cleaned_data.get('bmi'),
                calories=form.cleaned_data.get('calories'),
                steps=form.cleaned_data.get('steps'),
                speed=form.cleaned_data.get('speed')
            )
            bmi = form.cleaned_data.get('bmi')
            calories = form.cleaned_data.get('calories')

            if bmi:
                bmi_msg = bmi_suggestion(bmi)
                bmi_workout = workout_suggestion(bmi)

            form = HealthForm()

    history = HealthRecord.objects.filter(user=request.user).order_by('date')
    chart_dates = [record.date.strftime('%Y-%m-%d') for record in history]
    chart_bmis = [record.bmi for record in history]
    chart_calories = [record.calories for record in history]
    chart_steps = [record.steps for record in history]

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

    chart_dates = [record.date.strftime('%Y-%m-%d') for record in records]
    chart_bmis = [record.bmi for record in records]
    chart_calories = [record.calories for record in records]
    chart_steps = [record.steps for record in records]

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
            speed_factor = 1 + (record.speed - 5) * 0.05
            record.calories = round(record.weight * distance_km * speed_factor, 2)

            record.save()
            messages.success(request, 'Record updated successfully!')
            return redirect('tracker:history')
    else:
        form = HealthForm(initial={
            'weight': record.weight,
            'height': record.height_cm,
            'gender': record.gender,
            'bmi': record.bmi,
            'calories': record.calories,
            'steps': record.steps,
            'speed': record.speed
        })

    return render(request, 'tracker/edit_record.html', {'form': form, 'record': record})

@login_required
def delete_record(request, record_id):
    record = get_object_or_404(HealthRecord, id=record_id, user=request.user)

    if request.method == "POST":
        record.delete()
        messages.success(request, "Record deleted successfully!")
        return redirect('tracker:history')

    return render(request, 'tracker/delete_confirm.html', {'record': record})
