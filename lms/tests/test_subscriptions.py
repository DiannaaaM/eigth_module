from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, CourseSubscription


User = get_user_model()


class CourseSubscriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='subscriber@example.com', password='password123')
        self.course = Course.objects.create(title='Subscription Course', description='Test', owner=self.user)
        self.subscription_url = reverse('course-subscription-toggle')
        self.course_detail_url = reverse('course-detail', args=[self.course.id])

    def test_subscription_toggle_adds_and_removes_subscription(self):
        self.client.force_authenticate(self.user)

        response_add = self.client.post(self.subscription_url, {'course': self.course.id}, format='json')
        self.assertEqual(response_add.status_code, status.HTTP_200_OK)
        self.assertEqual(response_add.data['message'], 'Подписка добавлена')
        self.assertTrue(CourseSubscription.objects.filter(user=self.user, course=self.course).exists())

        course_detail = self.client.get(self.course_detail_url)
        self.assertEqual(course_detail.status_code, status.HTTP_200_OK)
        self.assertTrue(course_detail.data['is_subscribed'])

        response_remove = self.client.post(self.subscription_url, {'course': self.course.id}, format='json')
        self.assertEqual(response_remove.status_code, status.HTTP_200_OK)
        self.assertEqual(response_remove.data['message'], 'Подписка удалена')
        self.assertFalse(CourseSubscription.objects.filter(user=self.user, course=self.course).exists())

        course_detail_after = self.client.get(self.course_detail_url)
        self.assertEqual(course_detail_after.status_code, status.HTTP_200_OK)
        self.assertFalse(course_detail_after.data['is_subscribed'])
