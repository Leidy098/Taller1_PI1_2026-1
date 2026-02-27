import matplotlib.pyplot as plt
import matplotlib
import io
import base64

from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie

# Create your views here.

def home(request):
    # return HttpResponse('<h1>Welcome to Home Page</h1>')
    # return render(request, 'home.html')
    # return render(request, 'home.html', {'name': 'Leidy'})
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html', {'searchTerm': searchTerm, 'movies': movies})


def about(request):
    # return HttpResponse('<h1>Welcome to About Page</h1>')
    return render(request, 'about.html')


def signup(request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email': email})


def statistics_view(request):
    matplotlib.use('Agg')
    all_movies = Movie.objects.all()

    # Conteo por año
    movie_counts_by_year = {}
    for movie in all_movies:
        year = movie.year if movie.year else "Unknown"
        movie_counts_by_year[year] = movie_counts_by_year.get(year, 0) + 1

    sorted_year_counts = dict(sorted(movie_counts_by_year.items(), key=lambda item: str(item[0])))

    plt.figure(figsize=(10, 5))
    year_positions = range(len(sorted_year_counts))
    plt.bar(year_positions, sorted_year_counts.values(), width=0.5, align='center', color='#f8bbd0')
    plt.title('Movies per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of movies')
    plt.xticks(year_positions, sorted_year_counts.keys(), rotation=90)
    plt.subplots_adjust(bottom=0.3)

    year_buffer = io.BytesIO()
    plt.savefig(year_buffer, format='png')
    year_buffer.seek(0)
    plt.close()
    graphic_year = base64.b64encode(year_buffer.getvalue()).decode('utf-8')
    year_buffer.close()

    # Conteo por primer género
    movie_counts_by_genre = {}
    for movie in all_movies:
        raw_genre = (movie.genre or "").strip()
        if not raw_genre:
            first_genre = "Unknown"
        else:
            first_genre = raw_genre
            for separator in [",", "|", ";", "/"]:
                if separator in first_genre:
                    first_genre = first_genre.split(separator, 1)[0]
                    break
            first_genre = first_genre.strip() or "Unknown"

        if first_genre in movie_counts_by_genre:
            movie_counts_by_genre[first_genre] += 1
        else:
            movie_counts_by_genre[first_genre] = 1

    sorted_counts = dict(sorted(movie_counts_by_genre.items(), key=lambda item: item[0]))

    plt.figure(figsize=(10, 5))
    bar_positions = range(len(sorted_counts))
    plt.bar(bar_positions, sorted_counts.values(), width=0.5, align='center', color='#f8bbd0')
    plt.title('Movies per Genre (First Genre)')
    plt.xlabel('Genre')
    plt.ylabel('Number of movies')
    plt.xticks(bar_positions, sorted_counts.keys(), rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.3)

    genre_buffer = io.BytesIO()
    plt.savefig(genre_buffer, format='png')
    genre_buffer.seek(0)
    plt.close()
    graphic_genre = base64.b64encode(genre_buffer.getvalue()).decode('utf-8')
    genre_buffer.close()

    return render(
        request,
        'statistics.html',
        {
            'graphic_year': graphic_year,
            'graphic_genre': graphic_genre,
        }
    )
