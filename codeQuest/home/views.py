from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import user_questions_solved,question_details,user_question_details,user_code_sub
from django.contrib.auth.models import User
from home.forms import CodeSubmissionForm
from django.conf import settings
from pathlib import Path
import os
import uuid
import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError


def logout_user(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')
    return redirect('/login')

@login_required



def home_page(request):
    user_questions, created = user_questions_solved.objects.get_or_create(solver=request.user)
    
    x=question_details.objects.all()
    context = {
        'nops': user_questions.no_of_questions,
        'data_from_another_model':x
    }
    return render(request, 'user_home_page.html', context)

@login_required

def problem_page(request, name):
    problem = get_object_or_404(question_details, name=name)
    form = CodeSubmissionForm()

    # Fetch the latest submission for this user and question
    existing_submission = user_code_sub.objects.filter(user=request.user, question=problem).last()

    if existing_submission:
        # Pre-fill the form with the existing submission data
        form = CodeSubmissionForm(initial={
            'language': existing_submission.language,
            'code': existing_submission.code
        })

    context = {
        'form': form,
        'ques_name': problem.name,
        'desc': problem.description,
        'samp_in': problem.sample_input,
        'samp_out': problem.sample_output
    }
    return render(request, 'question_view.html', context)


def leaderboard(request):
    # Get all user_questions_solved entries and sort them by no_of_questions in descending order
    leaderboard_data = user_questions_solved.objects.all().order_by('-no_of_questions')

    # Prepare the data for rendering
    leaderboard_data = [
        {
            'username': user.solver.username,
            'solved_count': user.no_of_questions
        }
        for user in leaderboard_data
    ]

    return render(request, 'leader_board.html', {'leaderboard_data': leaderboard_data})


def validate_input(data):
    return True

@csrf_exempt
def run(request):
    if request.method == "POST":
        form = CodeSubmissionForm(request.POST)
        if form.is_valid():
            input_data = form.cleaned_data.get('input_data', '').strip().split('\n')

            if all(validate_input(data) for data in input_data):
                submission = form.save()
                output = run_code(submission.language, submission.code, '\n'.join(input_data))
                submission.output_data = output
                submission.save()
                return JsonResponse({'success': True, 'output_data': output})
            else:
                return JsonResponse({'success': False, 'error': 'Invalid input data.'})
        else:
            return JsonResponse({'success': False, 'error': form.errors.as_json()})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})

def submit(request,ques_name):
    if request.method == "POST":
        form = CodeSubmissionForm(request.POST)
        
        
        if form.is_valid():
            submission = form.save()
            output = submit_code(submission.language, submission.code,ques_name,request.user)
            submission.output_data = output
            submission.save()
            return JsonResponse({'success': True, 'output_data': output})
        else:
            return JsonResponse({'success': False, 'error': form.errors.as_json()})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


        
def submit_code(language, code, ques_name, user):
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]

    question_instance = question_details.objects.get(name=ques_name)
    existing_submission = user_code_sub.objects.filter(user=user, question=question_instance).exists()
    if existing_submission:
        return "already submitted"

    for directory in directories:
        dir_path = project_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

    codes_dir = project_path / "codes"
    input_dir = project_path / "inputs"
    output_dir = project_path / "outputs"

    unique = str(uuid.uuid4())

    code_file_name = f"{unique}.{language}"
    input_file_name = f"{ques_name}_input.txt"
    output_file_name = f"{unique}.txt"
    output_file_test_case = f"{ques_name}_output.txt"

    code_file_path = codes_dir / code_file_name
    input_file_path = input_dir / input_file_name
    output_file_path = output_dir / output_file_name
    output_file_path_test_case = output_dir / output_file_test_case

    # Write code to file
    with open(code_file_path, "w") as code_file:
        code_file.write(code)

    output_results = []

    if language == "cpp" or language == "c":
        executable_path = codes_dir / unique
        compiler = "gcc" if language == "c" else "g++"
        compile_result = subprocess.run(
            [compiler, str(code_file_path), "-o", str(executable_path)],
            capture_output=True, text=True
        )

        if compile_result.returncode == 0:
            with open(input_file_path, "r") as input_file:
                input_data_list = input_file.read().strip().split("\n\n")

            for input_data_case in input_data_list:
                temp_input_file_path = input_dir / f"{unique}_{ques_name}_input.txt"
                with open(temp_input_file_path, "w") as temp_input_file:
                    temp_input_file.write(input_data_case)

                with open(output_file_path, "w") as output_file:
                    subprocess.run(
                        [str(executable_path)],
                        stdin=open(temp_input_file_path, "r"),
                        stdout=output_file
                    )

                with open(output_file_path, "r") as output_file:
                    output_data = output_file.read()
                    output_results.append(output_data)

    elif language == "py":
        with open(input_file_path, "r") as input_file:
            input_data_list = input_file.read().strip().split("\n\n")

        for input_data_case in input_data_list:
            temp_input_file_path = input_dir / f"{unique}_input.txt"
            with open(temp_input_file_path, "w") as temp_input_file:
                temp_input_file.write(input_data_case)

            with open(output_file_path, "w") as output_file:
                subprocess.run(
                    ["python3", str(code_file_path)],
                    stdin=open(temp_input_file_path, "r"),
                    stdout=output_file
                )

            with open(output_file_path, "r") as output_file:
                output_data = output_file.read().strip()
                output_results.append(output_data)

    is_correct = True
    count = 0
    if output_file_path_test_case.exists():
        with open(output_file_path_test_case, "r") as expected_output_file:
            expected_outputs = expected_output_file.read().strip().split("\n\n")

        for output_data, expected_output in zip(output_results, expected_outputs):
            output_check = (output_data.strip() == expected_output.strip())
            is_correct = is_correct and output_check
            count += 1

    if is_correct:
        user_code_sub.objects.create(
            language=language,
            code=code,
            question=question_instance,
            user=user
        )
        user_question_details.objects.create(
            problem=question_instance,
            user=user,
            solved=True
        )
        lb = user_questions_solved.objects.filter(solver=user).first()
        lb.no_of_questions += 1
        lb.save()
        return is_correct

    return f"code not correct at {count} test case"


def run_code(language, code, input_data):
    project_path = Path(settings.BASE_DIR)
    directories = ["codes", "inputs", "outputs"]
    input_lines = input_data.strip().split('\n')
    cleaned_input_data = '\n'.join(line.strip() for line in input_lines)

    for directory in directories:
        dir_path = project_path / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

    codes_dir = project_path / "codes"
    input_dir = project_path / "inputs"
    output_dir = project_path / "outputs"
    unique = str(uuid.uuid4())

    code_file_name = f"{unique}.{language}"
    input_file_name = f"{unique}.txt"
    output_file_name = f"{unique}.txt"

    code_file_path = codes_dir / code_file_name
    input_file_path = input_dir / input_file_name
    output_file_path = output_dir / output_file_name

    # Write code to file
    with open(code_file_path, "w") as code_file:
        code_file.write(code)

    # Write input data to file
    with open(input_file_path, "w") as input_file:
        input_file.write(cleaned_input_data)

    if language == "cpp" or language == "c":
        executable_path = codes_dir / unique
        compiler = "gcc" if language == "c" else "g++"
        compile_result = subprocess.run(
            [compiler, str(code_file_path), "-o", str(executable_path)]
        )

        if compile_result.returncode == 0:
            with open(output_file_path, "w") as output_file:
                subprocess.run(
                    [str(executable_path)],
                    stdin=open(input_file_path, "r"),
                    stdout=output_file
                )

    elif language == "py":
        with open(output_file_path, "w") as output_file:
            subprocess.run(
                ["python3", str(code_file_path)],
                stdin=open(input_file_path, "r"),
                stdout=output_file
            )

    with open(output_file_path, "r") as output_file:
        output_data = output_file.read()

    return output_data

@login_required
def profile(request):
    user = request.user
    submissions = user_question_details.objects.filter(user=user)
    solved_problems = user_question_details.objects.filter(user=user, solved=True)
    # Calculate total solved questions and accuracy
    total_solved_questions = submissions.filter(solved=True).count()
    total_attempts = submissions.count()
    accuracy = (total_solved_questions / total_attempts * 100) if total_attempts > 0 else 0

    context = {
        'user': user,
        'total_solved_questions': total_solved_questions,
        'accuracy': accuracy,
        'submissions': submissions,
        'probs': solved_problems
    }
    return render(request, 'profile.html', context)