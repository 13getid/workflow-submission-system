from django.db import models

# Create your models here.
class Submission(models.Model):
    full_name = models.CharField(max_length= 100)
    project_title = models.CharField(max_length=200)
    email = models.EmailField()
    description = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return self.full_name
