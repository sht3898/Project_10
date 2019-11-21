from django.shortcuts import render,redirect,get_object_or_404
from .models import Movie, Genre, Review
from .forms import ReviewForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
# Create your views here.
def index(request):
    movies = Movie.objects.all()
    context = {
        'movies': movies
    }
    return render(request,'movies/index.html',context)

def detail(request,movie_pk):
    movie = get_object_or_404(Movie,pk=movie_pk)
    reviewform = ReviewForm()
    context = {
        'movie' : movie,   
        'form' : reviewform
    }
    return render(request,'movies/detail.html', context)

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

def reviewDelete(request, movie_pk,review_pk):
    review = get_object_or_404(Review,pk=review_pk)
    if request.user == review.user:
        review.delete()
    
    return redirect('movies:detail', movie_pk)

@login_required
def like(request, movie_pk):
    movie = Movie.objects.get(pk=movie_pk)
    if request.user in movie.like_users.all():
        movie.like_users.remove(request.user)
    else:
        movie.like_users.add(request.user)
    return redirect('movies:detail', movie_pk)
