from django.db import models

class Users(models.Model):
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=10)
    age = models.CharField(max_length=10)
    biography = models.TextField()
    job_role = models.CharField(max_length=30)
    interest = models.CharField(max_length=30)
    active = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name


class Verify(models.Model):
    token = models.CharField(max_length=10)
    email = models.CharField(max_length=50)
    time = models.DateTimeField()
