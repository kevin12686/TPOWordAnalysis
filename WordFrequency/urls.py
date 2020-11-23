"""WordFrequency URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import RegistrationView, Tools, UploadArticle, WordRestore, Ranking, StopwordsList, StopwordsCreate, StopwordsDelete, LearnedList, LearnedCreate, LearnedDelete, ArticleDetail, WordDetail

urlpatterns = [
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('registration/', RegistrationView.as_view(), name='registration'),
    path('', Ranking.as_view(), name='rank'),
    path('tools', Tools.as_view(), name='tools'),
    path('upload/article/', UploadArticle.as_view(), name='uploadArticle'),
    path('restore/', WordRestore.as_view(), name='restore'),
    path('stopword/', StopwordsList.as_view(), name='stopwords'),
    path('stopword/create/', StopwordsCreate.as_view(), name='addStopwords'),
    path('stopword/delete/', StopwordsDelete.as_view(), name='delStopwords'),
    path('learn/list/', LearnedList.as_view(), name='learnedList'),
    path('learn/', LearnedCreate.as_view(), name='learned'),
    path('unlearn/', LearnedDelete.as_view(), name='unlearned'),
    path('article/<str:article>/', ArticleDetail.as_view(), name='article'),
    path('word/<str:word>/', WordDetail.as_view(), name='word'),
]
