from . import views
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path("index/", views.index, name="index"),
    path('', TemplateView.as_view(template_name="index1.html")),
    path("index/<int:myid>/", views.quiz, name="quiz"), 
    path('index/<int:myid>/data/', views.quiz_data_view, name='quiz-data'),
    path('index/<int:myid>/save/', views.save_quiz_view, name='quiz-save'),
    
    #path("signup/", views.Signup, name="signup"),
    # path("login/", views.Login, name="login"),
    #path("logout/", views.Logout, name="logout"),
    
    path('motivate/', views.motivate, name='motivate'), 
    
    path('add_quiz/', views.add_quiz, name='add_quiz'),    
    path('add_question/', views.add_question, name='add_question'),  
    path('add_options/<int:myid>/', views.add_options, name='add_options'), 
    path('results/', views.results, name='results'),    
    path('delete_question/<int:myid>/', views.delete_question, name='delete_question'),  
    path('delete_result/<int:myid>/', views.delete_result, name='delete_result'), 
    
    path('accounts/', include('allauth.urls')),
    path('logout', LogoutView.as_view()),  
    path('quiz_collection',views.QuizCollection.as_view(),name="quiz"),
    path('answer_collection',views.AnswerCollection.as_view(),name="quiz"),
    path('question_collection',views.QuestionCollection.as_view(),name="quiz"),
    path('quiz_update/<int:pk>',views.QuizUpdate.as_view(),name="quiz"),
    path('question_update/<int:pk>',views.QuestionUpdate.as_view(),name="quiz"),
    path('answer_update/<int:pk>',views.AnswerUpdate.as_view(),name="quiz"),
    path('quiz_delete/<int:pk>',views.QuizDelete.as_view(),name="quiz"),
    path('question_delete/<int:pk>',views.QuestionDelete.as_view(),name="quiz"),
    path('answer_delete/<int:pk>',views.AnswerDelete.as_view(),name="quiz"),
    path('api/token/',
         jwt_views.TokenObtainPairView.as_view(),
         name ='token_obtain_pair'),
    path('api/token/refresh/',
         jwt_views.TokenRefreshView.as_view(),
         name ='token_refresh'),
]
  
