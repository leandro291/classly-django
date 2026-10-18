from datetime import date, datetime, time, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from contenidos.models import Material
from cursos.models import Curso, Inscripcion
from tareas.models import Entrega, Tarea

User = get_user_model()

PASSWORD = '123'

TEACHER = ('profesor@example.com', 'profesor', 'Carlos', 'Mendoza')
DEMO_STUDENT = ('alumno@example.com', 'alumno', 'Lucía', 'Ramírez')
STUDENTS = [
    DEMO_STUDENT,
    ('ana@example.com', 'ana', 'Ana', 'Torres'),
    ('diego@example.com', 'diego', 'Diego', 'Quispe'),
    ('valeria@example.com', 'valeria', 'Valeria', 'Rojas'),
    ('mateo@example.com', 'mateo', 'Mateo', 'Flores'),
    ('camila@example.com', 'camila', 'Camila', 'Vega'),
]

# Cada tarea: (título, descripción, nota máx., días hasta vencer; negativo = ya venció)
COURSES = [
    {
        'name': 'Matemática 5° Secundaria',
        'description': 'Álgebra, funciones y trigonometría. Prepara el examen de admisión paso a paso.',
        'period': '2026-II',
        'materials': [
            ('Guía de funciones lineales', 'Resumen con ejemplos resueltos y ejercicios propuestos.'),
            ('Formulario de trigonometría', 'Identidades y razones trigonométricas para tener a la mano.'),
        ],
        'tasks': [
            ('Práctica de ecuaciones', 'Resuelve los 10 ejercicios de la guía y muestra el procedimiento.', 20, -14),
            ('Gráfica de funciones', 'Grafica las funciones indicadas e identifica pendiente e intercepto.', 20, -5),
            ('Problemas de trigonometría', 'Resuelve los problemas de aplicación del capítulo 4.', 20, 6),
        ],
    },
    {
        'name': 'Comunicación',
        'description': 'Comprensión lectora, producción de textos y análisis de obras literarias.',
        'period': '2026-II',
        'materials': [
            ('Antología de cuentos peruanos', 'Lectura obligatoria para el análisis de la unidad.'),
            ('Cómo escribir un ensayo', 'Estructura, tesis y conectores con un ejemplo comentado.'),
        ],
        'tasks': [
            ('Reseña de lectura', 'Escribe una reseña de una página sobre el cuento que más te gustó.', 20, -10),
            ('Ensayo argumentativo', 'Redacta un ensayo de 3 párrafos sobre el uso de redes sociales.', 20, -2),
            ('Exposición oral', 'Prepara una exposición de 5 minutos sobre tu autor favorito.', 20, 9),
        ],
    },
    {
        'name': 'Ciencia y Tecnología',
        'description': 'Biología y química aplicadas: del laboratorio a la vida diaria.',
        'period': '2026-II',
        'materials': [
            ('Tabla periódica interactiva', 'Consulta propiedades y configuración electrónica de cada elemento.'),
            ('Seguridad en el laboratorio', 'Normas básicas antes de la práctica del viernes.'),
        ],
        'tasks': [
            ('Informe de laboratorio', 'Entrega el informe de la práctica de densidad con tus conclusiones.', 20, -7),
            ('Mapa conceptual de la célula', 'Organiza las partes de la célula y su función.', 20, 3),
        ],
    },
]

# alumno -> (puntaje, comentario del profe) por título de tarea vencida. None = entregó y espera nota.
# Quien no aparece, no entregó. Un "tarde" suma un día al vencimiento.
GRADES = {
    'Práctica de ecuaciones': {'ana': (18, 'Muy bien ordenado.'), 'diego': (14, 'Revisa el ejercicio 7.'),
                               'valeria': (20, '¡Perfecto!'), 'alumno': (17, 'Buen procedimiento, cuida los signos.')},
    'Gráfica de funciones': {'ana': (16, 'Faltó marcar el intercepto en la 3.'), 'mateo': None,
                             'camila': (19, 'Excelente trazo.'), 'alumno': None},
    'Reseña de lectura': {'ana': (15, 'Buena idea, desarrolla más tu opinión.'), 'valeria': (18, 'Muy bien escrita.'),
                          'alumno': (19, 'Reseña clara y con buen criterio.'), 'diego': (12, 'Mejora la ortografía.')},
    'Ensayo argumentativo': {'alumno': None, 'camila': None, 'mateo': (13, 'Falta un contraargumento.')},
    'Informe de laboratorio': {'ana': (17, 'Conclusiones sólidas.'), 'diego': (11, 'Incluye las unidades.'),
                               'alumno': (16, 'Buen informe, falta el margen de error.')},
}
LATE = {('Gráfica de funciones', 'mateo'), ('Ensayo argumentativo', 'mateo')}


class Command(BaseCommand):
    help = 'Crea datos de demostración (profesor, alumnos, cursos, tareas y entregas). Idempotente.'

    @transaction.atomic
    def handle(self, *args, **options):
        teacher = self.user(*TEACHER, rol='teacher')
        students = {s[1]: self.user(*s, rol='student') for s in STUDENTS}
        today = date.today()

        for spec in COURSES:
            course, _ = Curso.objects.get_or_create(
                name=spec['name'], teacher=teacher,
                defaults={'description': spec['description'], 'period': spec['period']},
            )
            for student in students.values():
                Inscripcion.objects.get_or_create(course=course, student=student)
            for title, description in spec['materials']:
                Material.objects.get_or_create(course=course, title=title, defaults={'description': description})
            for title, description, max_score, days in spec['tasks']:
                task, _ = Tarea.objects.get_or_create(
                    course=course, title=title,
                    defaults={'description': description, 'max_score': max_score,
                              'due_date': today + timedelta(days=days)},
                )
                self.submissions(task, students)

        self.stdout.write(self.style.SUCCESS(
            f'Listo. Profesor: {TEACHER[0]} · Alumno: {DEMO_STUDENT[0]} · clave: {PASSWORD}'))

    def user(self, email, username, first, last, rol):
        user, _ = User.objects.update_or_create(
            email=email,
            defaults={'username': username, 'first_name': first, 'last_name': last, 'rol': rol},
        )
        user.set_password(PASSWORD)
        user.save()
        return user

    def submissions(self, task, students):
        for username, result in GRADES.get(task.title, {}).items():
            late = (task.title, username) in LATE
            sent_day = task.due_date + timedelta(days=1 if late else -1)
            sent_at = timezone.make_aware(datetime.combine(sent_day, time(15, 30)))
            entrega, created = Entrega.objects.get_or_create(
                assignment=task, student=students[username],
                defaults={
                    'status': Entrega.Status.TARDIA if late else Entrega.Status.A_TIEMPO,
                    'student_comment': 'Adjunto mi trabajo, profe.' if username == 'alumno' else '',
                    'score': result[0] if result else None,
                    'teacher_comment': result[1] if result else '',
                },
            )
            if created:  # submitted_at es auto_now_add, solo se puede ajustar con update
                Entrega.objects.filter(pk=entrega.pk).update(submitted_at=sent_at)
