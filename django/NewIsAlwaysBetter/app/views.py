from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from app.utils import get_movie_datas, get_history
from app.models import Movie
from datetime import datetime
import json
import shap
import matplotlib.pyplot as plt
import io
import base64
import pickle
    
class IndexView(LoginRequiredMixin, TemplateView):
    
    template_name = "app/index.html"
    login_url = ""
    
    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        img, titles, synopsis, url, predictions = get_movie_datas()        
        history = get_history()
        
        context["movie_list"] = list(zip(img, titles, synopsis, url))
        context["predictions"] = predictions
        context["history"] = history
        context["figures"] = []
        context["history_json"] = json.dumps(history, default=str)
        for x in range(1, 13):
            context["figures"].append(f"fig{x}.png")
        if self.request.GET.get("content") == "releases":
            context["is_releases"] = True
        if self.request.GET.get("content") == "predictions":
            context["is_predictions"] = True
        if self.request.GET.get("content") == "dashboard":
            context["is_dashboard"] = True
        if self.request.GET.get("content") == "history":
            context["is_history"] = True
        return context
    
class AccountingView(LoginRequiredMixin, TemplateView):
    template_name = "app/accounting.html"
    login_url = ""
    
    def get_context_data(self, **kwargs) -> dict[str, any]:
        context = super().get_context_data(**kwargs)
        img, titles, synopsis, url, predictions = get_movie_datas()        
        history = get_history()

        # Ajout : enrichir chaque semaine avec total_affluence et total_revenue
        for week in history:
            movie_1_affluence = week["movie_1"].real_affluence if week["movie_1"] else 0
            movie_2_affluence = week["movie_2"].real_affluence if week["movie_2"] else 0
            movie_1_p_affluence = week["movie_1"].predicted_affluence if week["movie_1"] else 0
            movie_2_p_affluence = week["movie_2"].predicted_affluence if week["movie_2"] else 0
            week["total_affluence"] = movie_1_affluence + movie_2_affluence
            week["total_revenue"] = week["total_affluence"] * 10
            week["predicted_total_revenue"] = movie_1_p_affluence + movie_2_p_affluence * 10
            week["benefit"] = week["total_revenue"] - 4900

        history = sorted(history, key=lambda week: datetime.strptime(week["date"], "%d/%m/%Y"))

        context["history"] = history
        return context

    
# class WipeTableView(TemplateView):
    
#     template_name = "app/delete.html"
    
#     def get(self, request, *args, **kwargs):
#         Movie.objects.all().delete()
#         return super().get(request, *args, **kwargs)

class PredictionView(LoginRequiredMixin, DetailView):
    model = Movie
    template_name = 'app/prediction.html'
    context_object_name = 'movie'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        shap_string = self.object.shap_values
        shap_string_2 = self.object.shap_values_2

        # Désérialiser
        shap_values = self.deserialize_shap(shap_string) 
        shap_values_2 = self.deserialize_shap(shap_string_2) 

        # ---------- Premier graphique ----------
        plt.clf()  # Clear figure pour être propre
        shap.plots.waterfall(shap_values[0], show=False)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        # ---------- Deuxième graphique ----------
        plt.clf()  # Clear encore !
        shap.plots.waterfall(shap_values_2[0], show=False)

        buf_2 = io.BytesIO()
        plt.savefig(buf_2, format='png', bbox_inches='tight')
        buf_2.seek(0)
        image_base64_2 = base64.b64encode(buf_2.read()).decode('utf-8')
        buf_2.close()

        # Envoyer au template
        context['shap_waterfall'] = image_base64
        context['shap_waterfall_2'] = image_base64_2

        return context
    
    @staticmethod
    def deserialize_shap(shap_string):
        shap_bytes = base64.b64decode(shap_string.encode('utf-8'))
        return pickle.loads(shap_bytes)
    

def set_affluence(request, movie_id):
    if request.method == "POST":
        movie = get_object_or_404(Movie, id=movie_id)
        movie.real_affluence = int(request.POST.get("real_affluence", 0))
        movie.save()
    return HttpResponseRedirect(f"{reverse('index')}?content=history")