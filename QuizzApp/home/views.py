from django.shortcuts import render, redirect
from .models import *
from django.http import JsonResponse
from django.contrib.auth  import authenticate,  login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import QuizForm, QuestionForm
from django.forms import inlineformset_factory
from rest_framework import generics
from .serializers import *
from rest_framework.permissions import IsAdminUser

import time
from rest_framework import status
from rest_framework.response import Response
import requests
from rest_framework.decorators import api_view

def index(request):
    quiz = Quiz.objects.all()
    para = {'quiz' : quiz}
    return render(request, "index.html", para)


def get_location():
    MAX_RETRIES = 2

    attempt_num = 0  # keep track of how many times we've retried
    while attempt_num < MAX_RETRIES:
        url = "https://api.ipify.org?format=json"  # api end point
        r = requests.get(url)
        print(r)
        if r.status_code == 200:
            data = r.json()
            print(data)
            print(type(data["ip"]))  # ip address of the requesting machine in string
            return get_loc_from_ip(data["ip"])
        else:
            attempt_num += 1
            time.sleep(5)  # Wait for 5 seconds before re-trying


def get_loc_from_ip(ip):
    MAX_RETRIES = 3
    # doc of the used API
    # https://www.geojs.io/docs/v1/endpoints/geo/
    attempt_num = 0  # keep track of how many times we've retried
    while attempt_num < MAX_RETRIES:
        url = f"https://get.geojs.io/v1/ip/geo/{ip}.json"  # api end point
        r = requests.get(url)
        print(r)
        if r.status_code == 200:
            data = r.json()
            print(data)
            return data
        else:
            attempt_num += 1
            time.sleep(5)  # Wait for 5 seconds before re-trying
    return Response({"error": "Request failed"}, status=r.status_code)



@login_required(login_url = '/login')
def quiz(request, myid):
    quiz = Quiz.objects.get(id=myid)
    return render(request, "quiz.html", {'quiz':quiz})

def quiz_data_view(request, myid):
    quiz = Quiz.objects.get(id=myid)
    questions = []
    for q in quiz.get_questions():
        answers = []
        for a in q.get_answers():
            answers.append(a.content)
        questions.append({str(q): answers})
    return JsonResponse({
        'data': questions,
        'time': quiz.time,
    })
    
def motivate(request):
    return render(request, "motivation.html")

def weather(request):
    r = get_location()
    city = r.get('city', "Mumbai")
    context =  {'city': city}
    return render(request, "weather.html", context)

def save_quiz_view(request, myid):
    if request.is_ajax():
        questions = []
        data = request.POST
        data_ = dict(data.lists())

        data_.pop('csrfmiddlewaretoken')

        for k in data_.keys():
            print('key: ', k)
            question = Question.objects.get(content=k)
            questions.append(question)

        user = request.user
        quiz = Quiz.objects.get(id=myid)

        score = 0
        marks = []
        correct_answer = None

        for q in questions:
            a_selected = request.POST.get(q.content)

            if a_selected != "":
                question_answers = Answer.objects.filter(question=q)
                for a in question_answers:
                    if a_selected == a.content:
                        if a.correct:
                            score += 1
                            correct_answer = a.content
                    else:
                        if a.correct:
                            correct_answer = a.content

                marks.append({str(q): {'correct_answer': correct_answer, 'answered': a_selected}})
            else:
                marks.append({str(q): 'not answered'})
     
        Marks_Of_User.objects.create(quiz=quiz, user=user, score=score)
        
        return JsonResponse({'passed': True, 'score': score, 'marks': marks})
    

def Signup(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method=="POST":   
        username = request.POST['username']
        email = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        password = request.POST['password1']
        confirm_password = request.POST['password2']
        
        if password != confirm_password:
            return redirect('/register')
        
        user = User.objects.create_user(username, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return render(request, 'login.html')  
    return render(request, "signup.html")

def Login(request):
    if request.user.is_authenticated:
        return redirect('/')
    if request.method=="POST":
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect("/")
        else:
            return render(request, "login.html") 
    return render(request, "login.html")

def Logout(request):
    logout(request)
    return redirect('/')


def add_quiz(request):
    if request.method=="POST":
        form = QuizForm(data=request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.save()
            obj = form.instance
            return render(request, "add_quiz.html", {'obj':obj})
    else:
        form=QuizForm()
    return render(request, "add_quiz.html", {'form':form})

def add_question(request):
    questions = Question.objects.all()
    questions = Question.objects.filter().order_by('-id')
    if request.method=="POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "add_question.html")
    else:
        form=QuestionForm()
    return render(request, "add_question.html", {'form':form, 'questions':questions})

def delete_question(request, myid):
    question = Question.objects.get(id=myid)
    if request.method == "POST":
        question.delete()
        return redirect('/add_question')
    return render(request, "delete_question.html", {'question':question})


def add_options(request, myid):
    question = Question.objects.get(id=myid)
    QuestionFormSet = inlineformset_factory(Question, Answer, fields=('content','correct', 'question'), extra=4)
    if request.method=="POST":
        formset = QuestionFormSet(request.POST, instance=question)
        if formset.is_valid():
            formset.save()
            alert = True
            return render(request, "add_options.html", {'alert':alert})
    else:
        formset=QuestionFormSet(instance=question)
    return render(request, "add_options.html", {'formset':formset, 'question':question})

def results(request):
    marks = Marks_Of_User.objects.all()
    return render(request, "results.html", {'marks':marks})

def delete_result(request, myid):
    marks = Marks_Of_User.objects.get(id=myid)
    if request.method == "POST":
        marks.delete()
        return redirect('/results')
    return render(request, "delete_result.html", {'marks':marks})




class QuizCollection(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser] # only for admin users

    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class QuizUpdate(generics.UpdateAPIView):
    permission_classes = [IsAdminUser] # only for admin users

    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class QuestionCollection(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser] # only for admin users

    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class QuestionUpdate(generics.UpdateAPIView):
    permission_classes = [IsAdminUser] # only for admin users
 
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class AnswerCollection(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser] # only for admin users

    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class AnswerUpdate(generics.UpdateAPIView):
    permission_classes = [IsAdminUser] # only for admin users
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

class AnswerDelete(generics.DestroyAPIView):
    permission_classes = [IsAdminUser] # only for admin users
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
class QuestionDelete(generics.DestroyAPIView):
    permission_classes = [IsAdminUser] # only for admin users
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
class QuizDelete(generics.DestroyAPIView):
    permission_classes = [IsAdminUser] # only for admin users
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer