from django.db import models
from django.utils.timezone import now

# Create your models here.
class Movie(models.Model):
    
    title = models.CharField(verbose_name="titre", max_length=256, blank=False, default="")
    url = models.CharField(max_length=256, default="")
    picture_url = models.CharField(max_length=256, default="")
    synopsis = models.CharField(max_length=1500, default="")
    predicted_affluence = models.PositiveIntegerField(verbose_name="Affluence prédite", default=0)
    predicted_affluence_2 = models.PositiveIntegerField(verbose_name="Affluence prédite 2", default=0)
    real_affluence = models.PositiveBigIntegerField(verbose_name="Affluence réelle", default=0)
    date = models.DateField(default=now)
    shap_values = models.TextField(verbose_name="Shap values", default="")
    shap_values_2 = models.TextField(verbose_name="Shap values 2", default="")
 
    