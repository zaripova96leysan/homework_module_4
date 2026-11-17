from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Course, Lesson, Subscription

User = get_user_model()


class LessonAPITestCase(APITestCase):
    def setUp(self):

        self.user = User.objects.create_user(
            email='student@test.com',
            password='password123'
        )


        self.moderator = User.objects.create_user(
            email='moder@test.com',
            password='password123',
            is_staff=True
        )


        self.course = Course.objects.create(title='Python Course', description='Best course')


        self.lesson = Lesson.objects.create(
            title='Lesson 1',
            description='Intro',
            video_link='https://youtube.com/watch?v=123',
            course=self.course,
            owner=self.user
        )

        self.lesson_list_url = reverse('lesson-list')
        self.lesson_detail_url = reverse('lesson-detail', args=[self.lesson.id])
        self.subscribe_url = reverse('subscribe')

    def test_lesson_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.lesson_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_create(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Lesson',
            'description': 'New description',
            'video_link': 'https://youtube.com/watch?v=999',
            'course': self.course.id
        }
        response = self.client.post(self.lesson_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_invalid_youtube_link(self):
        self.client.force_authenticate(user=self.user)
        data = {
            'title': 'New Lesson',
            'description': 'New description',
            'video_link': 'https://stepik.org/course/123',
            'course': self.course.id
        }
        response = self.client.post(self.lesson_list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe(self):

        self.client.force_authenticate(user=self.user)
        data = {'course_id': self.course.id}


        response = self.client.post(self.subscribe_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')


        response = self.client.post(self.subscribe_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка удалена')