from rest_framework import serializers
from .models import Course, Lesson
from .validators import validate_youtube_link


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для урока"""
    video_link = serializers.URLField(
        required=False,
        allow_null=True,
        validators=[validate_youtube_link]
    )

    class Meta:
        model = Lesson
        fields = '__all__'
        extra_kwargs = {
            'owner': {'read_only': True},
        }


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для курса"""
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id',
            'title',
            'preview',
            'description',
            'owner',
            'lessons',
            'lessons_count',
            'is_subscribed',
        )
        extra_kwargs = {
            'owner': {'read_only': True},
        }

    def get_lessons_count(self, obj):
        """Возвращает количество уроков в курсе"""
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """Определяем, подписан ли текущий пользователь на курс"""
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            return False

        return obj.subscriptions.filter(user=user).exists()


class LessonListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка уроков"""
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Lesson
        fields = ('id', 'title', 'course', 'course_title', 'preview', 'video_link')
        extra_kwargs = {
            'owner': {'read_only': True},
        }


class LessonDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального представления урока"""
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Lesson
        fields = '__all__'
        extra_kwargs = {
            'owner': {'read_only': True},
        }

