import re
import json
import ast
import difflib
from functools import lru_cache
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from .models import Submission, Work, Student
from .forms import SubmissionForm, LessonSelectForm


# Аутентификация через email
def user_login(request):
    if request.method == 'POST':
        return handle_login(request)
    return render(request, 'login.html')


def handle_login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    user = authenticate(request, username=email, password=password)

    if user:
        login(request, user)
        return HttpResponse("Login successful")
    return HttpResponse("Invalid credentials", status=403)


# Парсинг запроса и нормализация кода
def parse_request_body(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None


def normalize_code(code):
    # Убираем комментарии и спецсимволы
    code = re.sub(r'//.*|#.*|/\*.*?\*/', '', code, flags=re.DOTALL)
    code = re.sub(r'[\^\w\s{}();,]', '', code).lower().strip()
    return re.sub(r'\s+', ' ', code)  # Приводим пробелы к одному


# Сравнение кода
def calculate_similarity(code1, code2):
    return {
        'jaccard_similarity': round(jaccard_similarity(set(code1.split()), set(code2.split())), 2),
        'lcs_similarity': round(lcs_length(code1, code2), 2),
        'tree_similarity': compare_trees(*map(normalize_code_with_ast, (code1, code2)))
    }


@lru_cache(maxsize=None)
def lcs_length(x, y):
    if not x or not y:
        return 0
    return 1 + lcs_length(x[:-1], y[:-1]) if x[-1] == y[-1] else max(lcs_length(x[:-1], y), lcs_length(x, y[:-1]))


def jaccard_similarity(set1, set2):
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return (intersection / union) * 100 if union else 0


def normalize_code_with_ast(code):
    code = re.sub(r'//.*|#.*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = code.lower()
    try:
        return ast.parse(code)
    except SyntaxError:
        return None


def compare_trees(tree1, tree2):
    if not tree1 or not tree2:
        return 0
    score = 1 if type(tree1) == type(tree2) else 0
    return score + sum(
        compare_trees(c1, c2) for c1, c2 in zip(ast.iter_child_nodes(tree1), ast.iter_child_nodes(tree2)))


# Представления

def results(request):
    lesson_id = request.GET.get('lesson')
    students = Student.objects.all().order_by('full_name')

    if lesson_id:
        submissions = Submission.objects.filter(lesson_id=lesson_id).select_related('student', 'lesson')
    else:
        submissions = Submission.objects.none()  # если нет lesson_id, то просто пустой набор

    # создаем матрицу результатов
    results_matrix = create_results_matrix(students, submissions)

    # создаем форму для выбора урока
    form = LessonSelectForm(request.GET or None)

    return render(request, 'app_results.html', {
        'form': form,
        'results_matrix': results_matrix,
        'students': students,
        'submissions': submissions if lesson_id else None
    })


def create_results_matrix(students, submissions):
    matrix = {student.full_name: {other.full_name: '-' for other in students} for student in students}

    if not submissions:
        return matrix  # если нет submissions, возвращаем пустую матрицу

    for sub1 in submissions:
        for sub2 in submissions:
            if sub1 != sub2:
                similarity = difflib.SequenceMatcher(None, sub1.code, sub2.code).ratio() * 100
                matrix[sub1.student.full_name][sub2.student.full_name] = f"{similarity:.2f}%"

    return matrix



# Работа с заданиями
@csrf_exempt
def upload_work(request):
    if request.method == 'POST':
        return handle_work_upload(request)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def handle_work_upload(request):
    data = parse_request_body(request)
    if not data:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON body'}, status=400)

    try:
        user = get_or_create_user(data)
        work = Work.objects.create(user=user, work_number=data['work_number'], code=data['code'],
                                   upload_date=data.get('upload_date'))
        return JsonResponse({'status': 'success', 'work_id': work.id}, status=201)

    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def get_or_create_user(data):
    return User.objects.get_or_create(
        username=data['user_name'], defaults={'email': data.get('email', ''), 'password': 'default'}
    )[0]


@csrf_exempt
def update_work(request, work_id):
    if request.method == 'PUT':
        return handle_work_update(request, work_id)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)


def handle_work_update(request, work_id):
    data = parse_request_body(request)
    if not data:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON body'}, status=400)

    try:
        work = Work.objects.get(id=work_id)
        work.code = data.get('code', work.code)
        work.save()
        return JsonResponse({'status': 'success', 'work_id': work.id}, status=200)

    except Work.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Work not found'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


# Результаты загрузки работ
def app_results(request):
    works = Work.objects.filter(work_number=request.GET.get('work_number')) if request.GET.get('work_number') else Work.objects.all()

    if not works:
        return HttpResponse("No works found.")

    results = compare_work_results(works)

    return render(request, 'app_results.html', {'results': results})


def compare_work_results(works):
    results = []
    for i in range(len(works)):
        for j in range(i + 1, len(works)):
            similarity = calculate_similarity(
                works[i].code,
                works[j].code
            )
            results.append({
                'work_1': {'id': works[i].id, 'user': works[i].user},
                'work_2': {'id': works[j].id, 'user': works[j].user},
                'similarity': similarity  # передаем словарь с результатами сравнения
            })
    return results


# Прочие представления
def index(request):
    return render(request, 'index.html')


def app_upload(request):
    return render(request, 'app_upload.html')


# Функция для обработки кода отправки
def submit_code(request):
    return render(request, 'submit_code.html')
