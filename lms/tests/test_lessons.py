from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson


User = get_user_model()


class LessonCRUDTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='user@example.com')
        self.user.set_password('password123')
        self.user.save()
        self.course = Course.objects.create(title='Test Course', description='Test', owner=self.user)
        self.moderator_group, _ = Group.objects.get_or_create(name='Модераторы')
        self.lesson_url = reverse('lesson-list-create')

    def test_create_lesson_with_valid_youtube_link(self):
        self.client.force_authenticate(self.user)
        payload = {
            'course': self.course.id,
            'title': 'Lesson 1',
            'description': 'Description',
            'video_link': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        }

        response = self.client.post(self.lesson_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 1)
        lesson = Lesson.objects.first()
        self.assertEqual(lesson.owner, self.user)

    def test_create_lesson_with_invalid_link_fails(self):
        self.client.force_authenticate(self.user)
        payload = {
            'course': self.course.id,
            'title': 'Lesson 2',
            'description': 'Description',
            'video_link': 'https://vimeo.com/example'
        }

        response = self.client.post(self.lesson_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('video_link', response.data)

    def test_moderator_cannot_create_lesson(self):
        moderator = User.objects.create(email='moderator@example.com')
        moderator.set_password('password123')
        moderator.save()
        moderator.groups.add(self.moderator_group)
        self.client.force_authenticate(moderator)

        payload = {
            'course': self.course.id,
            'title': 'Lesson 3',
            'description': 'Description',
            'video_link': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        }

        response = self.client.post(self.lesson_url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_list_lessons_returns_paginated_results(self):
        self.client.force_authenticate(self.user)
        lessons_to_create = 12
        Lesson.objects.bulk_create([
            Lesson(course=self.course, title=f'Lesson {i}', owner=self.user)
            for i in range(lessons_to_create)
        ])

        response = self.client.get(self.lesson_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertLessEqual(len(response.data['results']), 10)
