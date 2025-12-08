from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import HealthRecord

class TrackerViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        self.record = HealthRecord.objects.create(
            user=self.user,
            weight=70,
            height_cm=175,
            gender='Male',
            bmi=22.86,
            calories=200,
            steps=5000,
            speed=5.0
        )

    def test_edit_record_view_post(self):
        """Test POST request to edit_record redirects after saving."""
        url = reverse('tracker:edit_record', args=[self.record.pk])
        response = self.client.post(url, {
            'weight': 75,
            'height': 180,
            'gender': 'M',
            'steps': 6000,
            'speed': 6.0,
            'bmi': 23.15,      # optional
            'calories': 250.0  # optional
        })
        self.assertEqual(response.status_code, 302)  # redirect after save
        self.record.refresh_from_db()
        self.assertEqual(self.record.weight, 75)
        self.assertEqual(self.record.height_cm, 180)
