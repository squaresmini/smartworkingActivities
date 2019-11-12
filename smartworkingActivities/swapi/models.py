from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class ActivityType(models.Model):
    label = models.CharField(max_length=30,db_index=True,unique=True)



class Activity(models.Model):
    user = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE, editable=False,db_index=True)
    type = models.ForeignKey(ActivityType, on_delete=models.PROTECT, db_index=True)
    jira_id = models.IntegerField(null=True, default=None)
    description = models.CharField(max_length=400)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)
    smartworking_date = models.DateField(db_index=True)
    hours = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(7.5)],choices=[(n/10,n/10) for n in range(5,80,5)])

    class Meta:
        unique_together = ('type', 'user', 'jira_id','description','smartworking_date')