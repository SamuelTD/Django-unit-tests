from .views import IndexView, set_affluence, AccountingView, PredictionView
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, reverse_lazy

urlpatterns = [
    # path("", HomeView.as_view(), name="home"),
    path("", LoginView.as_view(template_name="app/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("index/", IndexView.as_view(), name="index"),
    path("accounting/", AccountingView.as_view(), name="accounting"),
    path("predictions/<int:pk>/", PredictionView.as_view(), name="predictions"),
    path('set_affluence/<int:movie_id>/', set_affluence, name='set_affluence')
    # path('delete/', WipeTableView.as_view(), name="delete")
]
