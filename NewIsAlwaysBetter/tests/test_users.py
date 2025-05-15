import pytest
from app.models import Movie

@pytest.mark.django_db
def test_user_creation(django_user_model):
    user = django_user_model.objects.create(username="User", password="azerty1234")
    assert user.username == "User"
    
@pytest.mark.django_db
def test_movie_creation(django_user_model):
    movie = Movie.objects.create(title="Matrix")
    assert movie.title == "Matrix"
    assert movie.synopsis == ""