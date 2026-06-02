from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Submission(models.Model):

    STATUS_CHOICES = [
        ('pending','Pending'),
        ('approved', 'Approved'),
        ('rejected','Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length= 100)
    project_title = models.CharField(max_length=200)
    email = models.EmailField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return self.project_title
