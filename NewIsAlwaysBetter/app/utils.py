from collections import defaultdict
from datetime import timedelta, date
from app.models import Movie

def get_week_start(date):
    # Align each date to its release Wednesday
    return date - timedelta(days=(date.weekday() - 2) % 7)  # 2 = Wednesday

def get_history():

    # Get all movies with predictions
    movies = Movie.objects.exclude(predicted_affluence=None).order_by('date')

    # Group by release week (each Wednesday)
    weekly_groups = defaultdict(list)

    for movie in movies:
        week = get_week_start(movie.date)
        weekly_groups[week].append(movie)

    # Get top 2 by prediction per week
    top_movies_by_week = []
    previous_movie_1 = None

    for week, group in weekly_groups.items():
        sorted_group = sorted(group, key=lambda m: m.predicted_affluence, reverse=True)
        top_two = sorted_group[:2]
        if len(top_two) == 0:
            # Aucun film : cloner le movie_1 précédent
            if previous_movie_1:
                movie_1 = Movie.objects.create(
                    title=previous_movie_1.title,
                    predicted_affluence=previous_movie_1.predicted_affluence,
                    url = previous_movie_1.url,
                    picture_url = previous_movie_1.picture_url,
                    synopsis = previous_movie_1.synopsis,
                    predicted_affluence_2 = previous_movie_1.predicted_affluence_2,
                    real_affluence = previous_movie_1.real_affluence,
                    date = previous_movie_1.date,
                    shap_values = previous_movie_1.shap_values,
                    shap_values_2 = previous_movie_1.shap_values_2
                )
                movie_2 = Movie.objects.create(
                    title=movie_1.title,
                    predicted_affluence=movie_1.predicted_affluence,
                    url = movie_1.url,
                    picture_url = movie_1.picture_url,
                    synopsis = movie_1.synopsis,
                    predicted_affluence_2 = movie_1.predicted_affluence_2,
                    real_affluence = movie_1.real_affluence,
                    date = movie_1.date,
                    shap_values = movie_1.shap_values,
                    shap_values_2 = movie_1.shap_values_2
                )
            else:
                movie_1 = movie_2 = None  # Si on n'a pas de movie_1 précédent, on ne peut pas cloner.
        elif len(top_two) == 1:
            # Un seul film : cloner le film de cette semaine
            movie_1 = top_two[0]
            movie_2 = Movie.objects.create(
                    title=movie_1.title,
                    predicted_affluence=movie_1.predicted_affluence,
                    url = movie_1.url,
                    picture_url = movie_1.picture_url,
                    synopsis = movie_1.synopsis,
                    predicted_affluence_2 = movie_1.predicted_affluence_2,
                    real_affluence = movie_1.real_affluence,
                    date = movie_1.date,
                    shap_values = movie_1.shap_values,
                    shap_values_2 = movie_1.shap_values_2
            )
            previous_movie_1 = movie_1  # Met à jour previous_movie_1
        else:
            # Deux films disponibles : rien à changer, on les prend directement
            movie_1 = top_two[0]
            movie_2 = top_two[1]
            previous_movie_1 = top_two[0]

        # Build dictionary
        entry = {
            "date": week.strftime("%d/%m/%Y"),
            "movie_1": top_two[0] if len(top_two) > 0 else movie_1,
            "movie_2": top_two[1] if len(top_two) > 1 else movie_2,
        }
        top_movies_by_week.append(entry)
    
    return top_movies_by_week[::-1]

def get_next_wednesday():
    
    today = date.today()
    wednesday = 2
    
    # Calculate how many days until the next Wednesday.
    days_ahead = (wednesday - today.weekday() + 7) % 7
    # If today is Wednesday, we want the next Wednesday (7 days ahead)
    if days_ahead == 0:
        days_ahead = 7
    next_wed = today + timedelta(days=days_ahead)
    return next_wed

def get_movie_datas(force_date: date = None) :
    
    """
    Return all movies of given week. By default will return the upcoming week's movies.
    """
    
    if not force_date:
        date_to_check = get_next_wednesday()
    else:
        date_to_check = force_date
        
    img = []
    titles = []
    synopsis = []
    url = []
    predictions = []
    
    movies = Movie.objects.filter(date=date_to_check).order_by("-predicted_affluence")        
    for movie in movies:
        img.append(movie.picture_url)
        titles.append(movie.title)
        synopsis.append(movie.synopsis)
        url.append(movie.url)
        predictions.append({"title": movie.title, "id": movie.id, "predicted_affluence": movie.predicted_affluence, "predicted_affluence_2": movie.predicted_affluence_2, \
            "shap_values": movie.shap_values, "shap_values_2": movie.shap_values_2, "picture_url": movie.picture_url,\
            "url": movie.url})
    
    for i in range(len(synopsis)):
        if len(synopsis[i]) > 200:
            synopsis[i] = synopsis[i][:197] + "..."
    
    return img, titles, synopsis, url, predictions

def set_real_affluence(movie_id: int, real_affluence: int=0):
    """
    Set the real_affluence field of given movie.
    """
    
    try:
        movie = Movie.get(id=movie_id)
    except:
        print("wrong id")
        raise
    movie.real_affluence = real_affluence
    movie.save()