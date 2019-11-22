# Project 10

## 1. 데이터베이스 설계

* settings 설정

  ```python
  STATIC_URL = '/static/'
  
  AUTH_USER_MODEL = 'accounts.User'
  
  LOGIN_URL = '/accounts/login'
  ```

* accounts

  ```python
  from django.db import models
  from django.contrib.auth.models import AbstractUser
  from django.conf import settings
  # Create your models here.
  
  class User(AbstractUser):
      followers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followings', blank=True)
  
  ```

   AbstractUser를 불러와서 사용
* movies

    ```python
    from django.db import models
          from django.conf import settings
          # Create your models here.

          class Genre(models.Model):
              name = models.CharField(max_length=30)

          class Movie(models.Model):
              title = models.CharField(max_length=40)
              audience = models.IntegerField()
              poster_url = models.CharField(max_length=100)
              description =  models.TextField()
              genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
              like_users = models.ManyToManyField(
                  settings.AUTH_USER_MODEL,
                  related_name='like_movies',
                  blank=True
                  )

          class Review(models.Model):
              content = models.CharField(max_length=100)
              score = models.IntegerField()
              movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
              user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    ```



## 2. Seed Data 구성

* movies 폴더에 fixtures 폴더를 생성하고 추가할 json 파일 저장
* 저장 후 다음 명령어 실행

    ```bash
    $ python manage.py loaddata genre.json
    $ python manage.py loaddata movie.json
    ```



## 3. `accounts` App

* url

  ```python
  from django.contrib import admin
  from django.urls import path,include
  from . import views
  app_name= 'movies'
  
  urlpatterns = [
      path('', views.index, name='index'),
      path('<int:movie_pk>/', views.detail, name='detail'),
      path('<int:movie_pk>/reivew', views.review, name='review'),
      path('<int:movie_pk>/reviews/<int:review_pk>/delete', views.reviewDelete, name='reviewDelete'),
      path('<int:movie_pk>/like/', views.like , name='like_movie')
      ]
  
  ```

* base.html

  ```html
  <!DOCTYPE html>
  <html lang="en">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <title>Document</title>
  </head>
  <body>  
    <a href="{% url 'movies:index' %}">home</a>
    <a href="{% url 'accounts:index' %}">유저목록</a>
      {% if user.is_active %}
    
    <a href="{% url 'accounts:logout' %}">로그아웃 </a><hr>
    {% else %}
    <a href="{% url 'accounts:signup' %}">회원가입</a>
    <a href="{% url 'accounts:login' %}">로그인 </a><br>
    <hr>
    {% endif %}
    {% block body %}
    {% endblock %}
  
  </body>
  </html>
  ```

  

1. 유저 목록(`/accounts/`)

   views.py

   ```python
   def index(request):
       users = User.objects.all()
       context = {
           'users': users
       }
       return render(request,'accounts/index.html',context)
   ```

   index.html

   ```html
   {% extends 'base.html' %}
   {% block body %}
   <h1>유저목록</h1>
   {% for user in users %}
   
     <li><a href="{% url 'accounts:detail' user.pk %}">{{ user.username }}</a></li>
   {% endfor %}
   {% endblock %}
   
   ```

2. 유저 상세보기(`/accounts/{user_pk}/`)

   views.py

   ```python
   def detail(request, user_pk):
       User = get_user_model()
       user = User.objects.get(pk=user_pk)
       context = {
           'user_profile' : user,
       }
       return render(request,'accounts/detail.html', context)
   ```

   detail.html

   ```html
   {% extends 'base.html' %}
   {% block body %}
   
   {% with user_profile.followers.all as followers %}
     <a href="{% url 'accounts:follow' user_profile.pk %}">
         {% if user in followers %} 
         팔로우취소
         {% else %}
         팔로우
         {% endif %}
     </a>
     <h2> 팔로우 : {{ user_profile.followings.all.count }} </h2>
     <h2> 팔로워 : {{ followers|length }}</h2>
   {% endwith %}
   
   <p>내가 작성한 평점 정보 </p>
   {% for review in user_profile.review_set.all %}
     <p>영화 : {{review.movie.title}} <br> 내용 : {{review.content}} <br> 평점 : {{ review.score }}</p>
   
   {% endfor %}
   <hr>
   <p>내가 좋아하는 영화 </p>
   {% for like in user_profile.like_movies.all %}
      {{like.title}}<br>
   
   {% endfor %}
   {% endblock %} 
   
   ```

3. 회원가입

   views

   ```python
   def signup(request):
       if request.user.is_authenticated:
           return redirect('movies:index')
       if request.method == 'POST': 
           form = CustomUserCreationForm(request.POST)
           if form.is_valid():
               user = form.save()
               auth_login(request,user)
               return redirect('movies:index')
       else:
           form = CustomUserCreationForm()
       context = {
           'form' : form
       }
       return render(request, 'accounts/signup.html', context)
   ```

   signup.html

   ```html
   {% extends 'base.html' %}
   {% block body %}
   <form action='' method='POST'>
       {% csrf_token %}
       {{ form.as_p }}
       <button type='submit'>회원가입</button>
   {% endblock %}
   ```

4. 로그인

   views

   ```python
   def login(request):
       if request.method == 'POST':
           form = AuthenticationForm(request, request.POST)
           if form.is_valid():
               user = form.get_user()
               auth_login(request,user)
               return redirect('movies:index')
       else:
           form = AuthenticationForm()
       context = {
           'form': form
       }
       return render(request,'accounts/login.html', context)
   ```

   login.html

   ```html
   {% extends 'base.html' %}
   {% block body %}
   <form action="" method="POST">
     {% csrf_token %}
     {{form.as_p}}
     <input type="submit" value="로그인">
   </form>
   {% endblock %}
   ```

5. 로그아웃

   views

   ```python
   def logout(request):
       auth_logout(request)
       return redirect('movies:index')
   ```



## 4. `movies` App

0. url

   ```python
   from django.contrib import admin
   from django.urls import path,include
   from . import views
   app_name= 'movies'
   
   urlpatterns = [
       path('', views.index, name='index'),
       path('<int:movie_pk>/', views.detail, name='detail'),
       path('<int:movie_pk>/reivew', views.review, name='review'),
       path('<int:movie_pk>/reviews/<int:review_pk>/delete', views.reviewDelete, name='reviewDelete'),
       path('<int:movie_pk>/like/', views.like , name='like_movie')
       ]
   
   ```

1. 영화 목록(`/movies/`)

   views

   ```python
   def index(request):
       movies = Movie.objects.all()
       context = {
           'movies': movies
       }
       return render(request,'movies/index.html',context)
   ```

   index.html

   ```html
   {% extends 'base.html' %}
   {% block body %}
       {% for movie in movies %}
       <a href='{% url 'movies:detail' movie.pk %}'>
       <img src={{movie.poster_url}} width='300px' height='300px'>
       </a>
       {% endfor %}
       {% endblock %}
   ```

2. 영화 상세보기(`/movies/{movie_pk}/`)

   views

   ```python
   def detail(request,movie_pk):
       movie = get_object_or_404(Movie,pk=movie_pk)
       reviewform = ReviewForm()
       context = {
           'movie' : movie,   
           'form' : reviewform
       }
       return render(request,'movies/detail.html', context)
   ```

   detail.html

   ```html
   {% extends 'base.html' %}
   {% block body %}
       <div>
           제목 : {{movie.title}}<hr>
           관객수 : {{movie.audience}}<hr>
           url : {{movie.poster_url}}<hr>
           요약 : {{movie.description}}<hr>
           장르 : {{movie.genre.name}}<hr>
       </div>
   {% endblock %}
   
   ```

3. 평점 생성

   views

   ```python
   @login_required
   def review(request, movie_pk):
       movie = get_object_or_404(Movie,pk=movie_pk)
       reviewForm = ReviewForm(request.POST)
       if reviewForm.is_valid():
           review = reviewForm.save(commit=False)
           review.movie_id = movie_pk
           review.user = request.user
           review.save()
           return redirect('movies:detail', movie_pk)
       context = {
           'movie' : movie,   
           'form' : reviewForm
       }
       return render(request,'movies/detail.html', context)
   ```

   `detail.html`에 추가

   ```html
   {% for review in movie.review_set.all %}
       <p>
           <hr>작성자: {{review.user}} <br> 점수 : {{review.score}}<br> 내용 :{{review.content}}<br>
       </p>
   {% endfor %}
   
   <form action="{% url 'movies:review' movie.pk %}" method='POST'>
       {% csrf_token %}
       {{form.as_p}}
       <input type='submit' value='등록'>
   </form>
   ```

4. 평점 삭제

   views

   ```python
   def reviewDelete(request, movie_pk,review_pk):
       review = get_object_or_404(Review,pk=review_pk)
       if request.user == review.user:
           review.delete()
       
       return redirect('movies:detail', movie_pk)
   ```

   `detail.html`에 추가

    ```html
   <form action='reviews/{{review.pk}}/delete' method='POST'>
       {% csrf_token %}
       <input type='submit' value='삭제'>
   </form>
    ```

5. 영화 좋아요 기능 구현

   views

   ```python
   @login_required
   def like(request, movie_pk):
       movie = Movie.objects.get(pk=movie_pk)
       if request.user in movie.like_users.all():
           movie.like_users.remove(request.user)
       else:
           movie.like_users.add(request.user)
       return redirect('movies:detail', movie_pk)
   ```

   `detail.html`에 추가

   ```html
   {% if user.is_authenticated %}
   <form action="{% url 'movies:like_movie' movie.pk %}" method="POST">
       {% csrf_token %}
       {% if user in movie.like_users.all %}
       <input type="submit" value="좋아요 취소">
       {% else %}
       <input type="submit" value="좋아요">
       {% endif %}
   </form>
   {% endif %}
   
   <p>
       {{ movie.like_users.all.count }} 명이 좋아합니다.
   </p>
   ```



## 5. 결과

index

![image-20191122100142626](.\images\pjt1.png)

detail

![image-20191122100314058](.\images\pjt2.png)

좋아요

![image-20191122100351611](.\images\pjt3.png)



느낀 점

협업을 통해 혼자 했을때 힘들었던 부분을 서로가 보완해줄 수 있어서 효율적이었던 것 같습니다.