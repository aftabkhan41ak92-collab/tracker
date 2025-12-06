from django import forms

class HealthForm(forms.Form):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    weight = forms.FloatField(label="Weight (kg)", required=True)
    height = forms.FloatField(label="Height (cm)", required=True)
    steps = forms.IntegerField(label="Steps", required=False)
    speed = forms.FloatField(label="Speed (km/h)", required=False)
    gender = forms.ChoiceField(label="Gender", choices=GENDER_CHOICES, required=True)
    bmi = forms.FloatField(label="BMI", required=False, widget=forms.NumberInput(attrs={'readonly':'readonly'}))
    calories = forms.FloatField(label="Calories Burned", required=False, widget=forms.NumberInput(attrs={'readonly':'readonly'}))