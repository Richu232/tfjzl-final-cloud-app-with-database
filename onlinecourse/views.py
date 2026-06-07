from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission, Enrollment
from .models import Course, Enrollment
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)
# Create your views here.


def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'onlinecourse/user_registration_bootstrap.html', context)
    elif request.method == 'POST':
        # Check if user exists
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("onlinecourse:index")
        else:
            context['message'] = "User already exists."
            return render(request, 'onlinecourse/user_registration_bootstrap.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['psw']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, 'onlinecourse/user_login_bootstrap.html', context)
    else:
        return render(request, 'onlinecourse/user_login_bootstrap.html', context)


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:index')


def check_if_enrolled(user, course):
    is_enrolled = False
    if user.id is not None:
        # Check if user enrolled
        num_results = Enrollment.objects.filter(user=user, course=course).count()
        if num_results > 0:
            is_enrolled = True
    return is_enrolled


# CourseListView
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list_bootstrap.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        user = self.request.user
        courses = Course.objects.order_by('-total_enrollment')[:10]
        for course in courses:
            if user.is_authenticated:
                course.is_enrolled = check_if_enrolled(user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_detail_bootstrap.html'


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user

    is_enrolled = check_if_enrolled(user, course)
    if not is_enrolled and user.is_authenticated:
        # Create an enrollment
        Enrollment.objects.create(user=user, course=course, mode='honor')
        course.total_enrollment += 1
        course.save()

    return HttpResponseRedirect(reverse(viewname='onlinecourse:course_details', args=(course.id,)))


# --- VIEW METHOD 1: PROCESS FORM SUBMISSION ---
def submit(request, course_id):
    # Retrieve course context target object or fail gracefully
    course = get_object_or_404(Course, pk=course_id)
    
    if request.method == 'POST':
        # Safely determine active application user enrollment profile 
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
        except Enrollment.DoesNotExist:
            return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))

        # Create base entry tracker object reference instance linking enrollment trace 
        submission = Submission.objects.create(enrollment=enrollment)
        
        # Pull payload inputs and collect targeted choice markers
        for key, value in request.POST.items():
            if key.startswith('choice_'):
                choice_id = int(value)
                choice_obj = get_object_or_404(Choice, pk=choice_id)
                submission.choices.add(choice_obj)
                
        submission.save()
        
        # Route logic down to results breakdown template view
        return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)

    return HttpResponseRedirect(reverse('onlinecourse:course_details', args=(course.id,)))


# An example method to collect the selected choices from the exam form from the request object
def extract_answers(request):
   submitted_anwsers = []
   for key in request.POST:
       if key.startswith('choice'):
           value = request.POST[key]
           choice_id = int(value)
           submitted_anwsers.append(choice_id)
   return submitted_anwsers


# --- VIEW METHOD 2: CALCULATE EXAM RESULT AND RENDER SUMMARY ---
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)
    
    # Trace specific chosen items 
    selected_choices = submission.choices.all()
    selected_ids = [choice.id for choice in selected_choices]
    
    total_score = 0
    earned_score = 0
    
    # Logic evaluation checklist grid
    questions_results = []
    
    for question in course.question_set.all():
        total_score += question.grade
        # Check if the choices selected match the correct items exactly
        is_correct = question.is_get_score(selected_ids)
        
        if is_correct:
            earned_score += question.grade
            
        questions_results.append({
            'question': question,
            'is_correct': is_correct
        })
        
    # Calculate score percentage
    score_percentage = (earned_score / total_score) * 100 if total_score > 0 else 0
    passed = score_percentage >= 70  # Pass mark boundary definition matching standard thresholds
    
    context = {
        'course': course,
        'submission': submission,
        'earned_score': earned_score,
        'total_score': total_score,
        'score_percentage': round(score_percentage, 1),
        'passed': passed,
        'questions_results': questions_results,
        'selected_ids': selected_ids
    }
    
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)



