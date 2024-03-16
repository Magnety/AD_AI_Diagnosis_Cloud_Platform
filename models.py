from django.db import models

# Create your models here.
class UserInfo(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=32)


class DoctorInfo(models.Model):
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    email = models.CharField(max_length=32)
    password = models.CharField(max_length=32)
    hospital = models.CharField(max_length=32)

class LoginInfo(models.Model):
    name = models.CharField(max_length=32)
    title = models.CharField(max_length=32)
    email = models.CharField(max_length=32)
    in_time = models.DateTimeField()
    password = models.CharField(max_length=32)
    hospital = models.CharField(max_length=32)

class PatientInfo(models.Model):
    name = models.CharField(max_length=32)
    age = models.CharField(max_length=32)
    sex = models.CharField(max_length=32)
    in_time = models.CharField(max_length=32)
    mri_add = models.CharField(max_length=64)
    dti_add = models.CharField(max_length=64)
    from_hospital = models.CharField(max_length=32)
    disease = models.CharField(max_length=32)

class new_PatientInfo(models.Model):
    id_num = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    age = models.CharField(max_length=32)
    sex = models.CharField(max_length=32)
    in_time = models.CharField(max_length=32)
    mri_add = models.CharField(max_length=64)
    dti_add = models.CharField(max_length=64)
    from_hospital = models.CharField(max_length=32)
    disease = models.CharField(max_length=32)

class newnew_PatientInfo(models.Model):
    id_num = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    age = models.CharField(max_length=32)
    sex = models.CharField(max_length=32)
    in_time = models.CharField(max_length=32)
    mri_add = models.CharField(max_length=64)
    pet_add = models.CharField(max_length=64)
    from_hospital = models.CharField(max_length=32)
    disease = models.CharField(max_length=32)
    year = models.CharField(max_length=32)
    month = models.CharField(max_length=32)
    day = models.CharField(max_length=32)

class newnewnew_PatientInfo(models.Model):
    id_num = models.CharField(max_length=32)
    name = models.CharField(max_length=32)
    age = models.CharField(max_length=32)
    sex = models.CharField(max_length=32)
    in_time = models.CharField(max_length=32)
    mri_add = models.CharField(max_length=64)
    pet_add = models.CharField(max_length=64)
    from_hospital = models.CharField(max_length=32)
    disease = models.CharField(max_length=32)
    year = models.CharField(max_length=32)
    month = models.CharField(max_length=32)
    day = models.CharField(max_length=32)
    doctor_email = models.CharField(max_length=32)
    doctor_name = models.CharField(max_length=32)