from rest_framework import serializers
from .models import Center, Subject, Level, Student, Question, Result, StudentAnswer, MentalTask


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class LevelSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = Level
        fields = ['id', 'subject', 'subject_name', 'name', 'duration_minutes']


class StudentSerializer(serializers.ModelSerializer):
    center = serializers.PrimaryKeyRelatedField(queryset=Center.objects.all(), required=False, allow_null=True, write_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    center_name = serializers.CharField(source='center.name', read_only=True)
    full_name = serializers.CharField(read_only=True)
    correct_count = serializers.SerializerMethodField()
    total_questions = serializers.SerializerMethodField()
    percent = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'subject', 'subject_name',
            'level', 'level_name', 'center', 'center_name', 'code', 'status',
            'started_at', 'finished_at', 'is_used', 'created_at', 'correct_count', 'total_questions', 'percent'
        ]
        read_only_fields = ['code', 'status', 'started_at', 'finished_at', 'is_used', 'created_at']

    def get_correct_count(self, obj):
        return getattr(getattr(obj, 'result', None), 'correct_count', None)

    def get_total_questions(self, obj):
        return getattr(getattr(obj, 'result', None), 'total_questions', None)

    def get_percent(self, obj):
        return getattr(getattr(obj, 'result', None), 'percent', None)

    def validate(self, attrs):
        subject = attrs.get('subject') or getattr(self.instance, 'subject', None)
        level = attrs.get('level') or getattr(self.instance, 'level', None)
        if subject and level and level.subject_id != subject.id:
            raise serializers.ValidationError({'level': 'Tanlangan daraja shu fanga tegishli emas.'})
        return attrs


class QuestionAdminSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)

    class Meta:
        model = Question
        fields = [
            'id', 'subject', 'subject_name', 'level', 'level_name', 'text',
            'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer', 'image', 'created_at'
        ]


class QuestionForExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'text', 'option_a', 'option_b', 'option_c', 'option_d', 'image']


class StudentAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    correct_answer = serializers.CharField(source='question.correct_answer', read_only=True)

    class Meta:
        model = StudentAnswer
        fields = ['id', 'question', 'question_text', 'selected_answer', 'correct_answer', 'is_correct']


class MentalTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentalTask
        fields = ['id', 'task_order', 'expression', 'correct_answer', 'student_answer', 'is_correct']


class ResultSerializer(serializers.ModelSerializer):
    student_full_name = serializers.CharField(source='student.full_name', read_only=True)
    student_code = serializers.CharField(source='student.code', read_only=True)
    subject_name = serializers.CharField(source='student.subject.name', read_only=True)
    level_name = serializers.CharField(source='student.level.name', read_only=True)
    center_name = serializers.CharField(source='student.center.name', read_only=True)
    answers = StudentAnswerSerializer(many=True, read_only=True)
    mental_answers = MentalTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Result
        fields = [
            'id', 'student', 'student_full_name', 'student_code', 'subject_name',
            'level_name', 'center_name', 'total_questions', 'correct_count',
            'percent', 'started_at', 'finished_at', 'spent_seconds', 'created_at', 'answers', 'mental_answers'
        ]
