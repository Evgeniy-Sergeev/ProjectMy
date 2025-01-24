import re
import json
import ast
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .models import User, Work, Result
from functools import lru_cache


def parse_request_body(request):
    try:
        return json.loads(request.body)
    except json.JSONDecodeError:
        return None

def normalize_code(code):
    code = re.sub(r'//.*|#.*|/\*.*?\*/', '', code, flags=re.DOTALL)  # Убираем комментарии
    code = re.sub(r'[\^\w\s{}();,]', '', code).lower().strip()  # Убираем спецсимволы, приводим к нижнему регистру
    return re.sub(r'\s+', ' ', code)  # Приводим все пробелы к одному

def calculate_similarity(code1, code2):
    jaccard = jaccard_similarity(set(code1.split()), set(code2.split()))
    lcs = lcs_length(code1, code2)
    tree1, tree2 = map(normalize_code_with_ast, (code1, code2))
    tree_similarity = compare_trees(tree1, tree2) if tree1 and tree2 else 0
    return {'jaccard_similarity': round(jaccard, 2), 'lcs_similarity': round(lcs, 2), 'tree_similarity': tree_similarity}

@lru_cache(maxsize=None)
def lcs_length(x, y):
    return 0 if not x or not y else (1 + lcs_length(x[:-1], y[:-1]) if x[-1] == y[-1] else max(lcs_length(x[:-1], y), lcs_length(x, y[:-1])))

def jaccard_similarity(set1, set2):
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return (intersection / union) * 100 if union else 0

def normalize_code_with_ast(code):
    code = re.sub(r'//.*|#.*', '', code)
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    code = code.lower()
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")
        return None
    return tree

def compare_trees(tree1, tree2):
    if not tree1 or not tree2:
        return 0
    score = 1 if type(tree1) == type(tree2) else 0
    return score + sum(compare_trees(c1, c2) for c1, c2 in zip(ast.iter_child_nodes(tree1), ast.iter_child_nodes(tree2)))

@csrf_exempt
def upload_work(request):
    if request.method == 'POST':
        data = parse_request_body(request)
        if not data:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON body'}, status=400)
        try:
            user, _ = User.objects.get_or_create(
                username=data['user_name'], defaults={'email': data.get('email', ''), 'password': 'default'}
            )
            work = Work.objects.create(user=user, work_number=data['work_number'], code=data['code'], upload_date=data.get('upload_date'))
            return JsonResponse({'status': 'success', 'work_id': work.id}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def update_work(request, work_id):
    if request.method == 'PUT':
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

    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

def check_plagiarism(request, work_number):
    if request.method == 'GET':
        works = Work.objects.filter(work_number=work_number)
        results = [{'work_1': {'id': works[i].id, 'user': works[i].user.username}, 'work_2': {'id': works[j].id, 'user': works[j].user.username},
                    'similarity': calculate_similarity(normalize_code(works[i].code), normalize_code(works[j].code))}
                   for i in range(len(works)) for j in range(i + 1, len(works))]
        return JsonResponse({'status': 'success', 'results': results}, status=200)
    return JsonResponse({'status': 'error', 'message': 'Invalid method'}, status=405)

@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return HttpResponse("Login successful")
        return HttpResponse("Invalid credentials", status=403)
    return render(request, 'login.html')

def app_upload(request):
    if request.method == 'POST':
        user_name = request.POST.get('user_name')
        work_number = request.POST.get('work_number')
        code = request.POST.get('code')
        user, _ = User.objects.get_or_create(username=user_name, defaults={'email': '', 'password': 'default'})
        Work.objects.create(user=user, work_number=work_number, code=code)
        return HttpResponse("Code successfully uploaded!")
    return render(request, 'app_upload.html')

def app_results(request):
    work_number = request.GET.get('work_number')
    if not work_number:
        return HttpResponse("Specify the work number with ?work_number=<number>.")
    works = Work.objects.filter(work_number=work_number)
    results = [{'work_1': {'id': works[i].id, 'user': works[i].user.username}, 'work_2': {'id': works[j].id, 'user': works[j].user.username},
                'similarity': calculate_similarity(normalize_code(works[i].code), normalize_code(works[j].code))}
               for i in range(len(works)) for j in range(i + 1, len(works))]
    return render(request, 'app_results.html', {'results': results})

def index(request):
    return render(request, 'index.html')
