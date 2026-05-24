from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from olympiad.models import Center, Level, Question, Subject
from .seed_demo import ENGLISH_TESTS, MATH_TESTS, RUS_TESTS


class Command(BaseCommand):
    help = 'Production uchun admin, fanlar, darajalar va testlarni xavfsiz seed qiladi. O‘quvchilar/natijalar o‘chirilmaydi.'

    def handle(self, *args, **options):
        with transaction.atomic():
            admin_user, _ = User.objects.get_or_create(
                username='ulugbek',
                defaults={
                    'email': 'ulugbek@example.com',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                }
            )
            admin_user.email = admin_user.email or 'ulugbek@example.com'
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.is_active = True
            # Parol faqat birinchi deploy yoki admin paroli yo‘qolgan holat uchun bir xil ushlab turiladi.
            admin_user.set_password('codingwithulugbek20030313')
            admin_user.save()

            Center.objects.get_or_create(name='LIDER.Uz Onlayn Olimpiada')

            total = 0

            mental_subject, _ = Subject.objects.get_or_create(name='Mental arifmetika')
            for level_name in ['5 yosh', '6 yosh', '8 yosh', '9 yosh']:
                Level.objects.update_or_create(
                    subject=mental_subject,
                    name=level_name,
                    defaults={'duration_minutes': 10},
                )

            def seed_subject(subject_name, tests, duration_minutes):
                nonlocal total
                subject, _ = Subject.objects.get_or_create(name=subject_name)
                for level_name, questions in tests.items():
                    level, _ = Level.objects.update_or_create(
                        subject=subject,
                        name=level_name,
                        defaults={'duration_minutes': duration_minutes},
                    )
                    existing_questions = list(Question.objects.filter(level=level).order_by('id'))

                    for index, item in enumerate(questions):
                        text = item[0]
                        defaults = {
                            'subject': subject,
                            'level': level,
                            'text': text,
                            'option_a': item[1],
                            'option_b': item[2],
                            'option_c': item[3],
                            'option_d': item[4],
                            'correct_answer': item[5],
                            'image': item[6] if len(item) > 6 else '',
                        }

                        if index < len(existing_questions):
                            question = existing_questions[index]
                            for field, value in defaults.items():
                                setattr(question, field, value)
                            question.save()
                        else:
                            Question.objects.create(**defaults)
                        total += 1

                    if len(existing_questions) > len(questions):
                        extra_ids = [question.id for question in existing_questions[len(questions):]]
                        Question.objects.filter(id__in=extra_ids).delete()

            seed_subject('Ingliz tili', ENGLISH_TESTS, 30)
            seed_subject('Rus tili', RUS_TESTS, 30)
            seed_subject('Matematika', MATH_TESTS, 30)

        self.stdout.write(self.style.SUCCESS(f'Deploy seed tayyor. Testlar tekshirildi/yangilandi: {total} ta.'))
        self.stdout.write(self.style.SUCCESS('Admin: ulugbek / codingwithulugbek20030313'))
