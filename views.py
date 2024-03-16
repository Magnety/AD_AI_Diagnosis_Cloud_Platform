
# Create your views here.
import os
import random
import shutil
import matlab
import matlab.engine
from django.http import FileResponse,Http404
import requests
import logging
import SimpleITK as sitk
import numpy as np
from PIL import Image
from django.urls import reverse
import time
from pyheatmap.heatmap import HeatMap

import base64
import cv2
from wsgiref.util import FileWrapper
from io import BytesIO
from datetime import datetime, date, timedelta
from django import forms
from django.http import HttpResponse,JsonResponse
from django.utils.encoding import escape_uri_path

from cloudsys import models
from cloudsys.models import LoginInfo,new_PatientInfo,newnew_PatientInfo,newnewnew_PatientInfo
from django.shortcuts import render,redirect
from django.contrib import messages
from django.db.models import Max,Min
from CMFFN.main import run_model as run_model_advscn
from CMFFN.main1 import run_model as run_model_mcivscn
from CMFFN.main2 import run_model as run_model_smcivspmci
from MSNET.main import run_model
import pandas as pd
import zipfile
import scipy
import heapq
logger = logging.getLogger('django')

class patient_form(forms.Form):
    id_num = forms.CharField(max_length=32)
    name = forms.CharField(max_length=32)
    age = forms.CharField(max_length=32)
    sex = forms.CharField(max_length=32)
    year = forms.CharField(max_length=32)
    month = forms.CharField(max_length=32)
    day = forms.CharField(max_length=32)

    mri_data = forms.FileField()
    pet_data = forms.FileField()
    from_hospital = forms.CharField(max_length=32)
    disease = forms.CharField(max_length=32)
    doctor_email = forms.CharField(max_length=32)
    doctor_name = forms.CharField(max_length=32)


class test_form1(forms.Form):
    mri_data = forms.FileField()
    pet_data = forms.FileField()


def index(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    total_doctor_num = LoginInfo.objects.all().count()
    week = datetime.today() - timedelta(days=1)
    print(week)
    week_doctor_num = LoginInfo.objects.filter(in_time__gte=week).count()

    total_patient_num = newnewnew_PatientInfo.objects.all().count()
    week_patient_num = newnewnew_PatientInfo.objects.filter(in_time__gte=week).count()
    total_mri_num = total_patient_num-newnewnew_PatientInfo.objects.filter(mri_add='none').count()
    total_pet_num = total_patient_num-newnewnew_PatientInfo.objects.filter(pet_add='none').count()
    total_img_num = total_mri_num+total_pet_num

    week_mri_num = week_patient_num-newnewnew_PatientInfo.objects.filter(in_time__gte=week).filter(mri_add='none').count()
    week_pet_num = week_patient_num-newnewnew_PatientInfo.objects.filter(in_time__gte=week).filter(pet_add='none').count()
    week_img_num = week_mri_num+week_pet_num

    chart_doctor_data = []
    chart_patient_data = []
    chart_img_data = []
    for i in range(0,7):
        week1 = datetime.today() - timedelta(days=1*(7-i))
        week2 = datetime.today() - timedelta(days=1*(7-i)-1)
        chart_patient_data.append(newnewnew_PatientInfo.objects.filter(in_time__gte=week1).filter(in_time__lte=week2).count())
        chart_doctor_data.append(LoginInfo.objects.filter(in_time__gte=week1).filter(in_time__lte=week2).count())
        _week_patient_num = newnewnew_PatientInfo.objects.filter(in_time__gte=week1).filter(in_time__lte=week2).count()
        _week_mri_num = _week_patient_num-newnewnew_PatientInfo.objects.filter(in_time__gte=week1).filter(in_time__lte=week2).filter(mri_add='none').count()
        _week_pet_num = _week_patient_num-newnewnew_PatientInfo.objects.filter(in_time__gte=week1).filter(in_time__lte=week2).filter(pet_add='none').count()
        _week_img_num = _week_mri_num+_week_pet_num
        chart_img_data.append(_week_img_num)
    print("chart_doctor_data",chart_doctor_data)
    today = []
    for i in range(7):
        today.append((date.today() + timedelta(days=-(6-i))).strftime("%Y-%m-%d"))
    print('today',today)

    disease_percent = []
    disease_num = []
    cn_num = newnewnew_PatientInfo.objects.filter(disease='正常').count()
    ad_num = newnewnew_PatientInfo.objects.filter(disease='阿尔茨海默氏症').count()
    smci_num = newnewnew_PatientInfo.objects.filter(disease='稳定型轻度认知障碍').count()
    pmci_num = newnewnew_PatientInfo.objects.filter(disease='进展型轻度认知障碍').count()

    disease_num.append(cn_num)
    disease_num.append(smci_num)
    disease_num.append(pmci_num)

    disease_num.append(ad_num)
    disease_percent.append((cn_num/(total_patient_num+0.000001)*100))
    disease_percent.append((smci_num/(total_patient_num+0.000001)*100))
    disease_percent.append((pmci_num/(total_patient_num+0.000001)*100))

    disease_percent.append((ad_num/(total_patient_num+0.000001)*100))
    print(disease_percent)

    sex_num = []
    fm_num = newnewnew_PatientInfo.objects.filter(sex='女').count()
    m_num = newnewnew_PatientInfo.objects.filter(sex='男').count()
    sex_num.append(m_num)
    sex_num.append(fm_num)
    m_d_num = []
    f_d_num = []
    m_d_num.append(newnewnew_PatientInfo.objects.filter(sex='男',disease='正常').count())
    f_d_num.append(newnewnew_PatientInfo.objects.filter(sex='女',disease='正常').count())
    m_d_num.append(newnewnew_PatientInfo.objects.filter(sex='男', disease='稳定型轻度认知障碍').count())
    f_d_num.append(newnewnew_PatientInfo.objects.filter(sex='女', disease='稳定型轻度认知障碍').count())
    m_d_num.append(newnewnew_PatientInfo.objects.filter(sex='男', disease='进展型轻度认知障碍').count())
    f_d_num.append(newnewnew_PatientInfo.objects.filter(sex='女', disease='进展型轻度认知障碍').count())
    m_d_num.append(newnewnew_PatientInfo.objects.filter(sex='男', disease='阿尔茨海默氏症').count())
    f_d_num.append(newnewnew_PatientInfo.objects.filter(sex='女', disease='阿尔茨海默氏症').count())

    patient = newnewnew_PatientInfo.objects.all()
    max_age = int(patient.aggregate(Max('age'))['age__max'])
    min_age = int(patient.aggregate(Min('age'))['age__min'])
    age_list =[]
    age_num = []
    print('((((max_min_age))))',max_age,min_age)
    for i in range(min_age,max_age+1):
        n = newnewnew_PatientInfo.objects.filter(age='%s'%str(i)).count()
        age_list.append(i)
        age_num.append(n)

    return render(request, "index.html",{'total_doctor_num':total_doctor_num,'week_doctor_num':week_doctor_num,
                                         'total_patient_num':total_patient_num,'week_patient_num':week_patient_num,
                                         'total_img_num':total_img_num,'week_img_num':week_img_num,'chart_doctor_data':chart_doctor_data,
                                         'chart_patient_data':chart_patient_data,'chart_img_data':chart_img_data,'today':today,
                                         'disease_percent':disease_percent,'disease_num':disease_num,'sex_num':sex_num,
                                         'age_list':age_list,'age_num':age_num,'m_d_num':m_d_num
                                         ,'f_d_num':f_d_num})
def patientinfo(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    patient_list = newnewnew_PatientInfo.objects.all()
    return render(request,'patientinfo.html',{'p_list':patient_list})
def mypatient(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    if request.GET:
        doctor_email = request.GET['doctor_email']
    patient_list = newnewnew_PatientInfo.objects.filter(doctor_email=doctor_email)
    return render(request,'mypatient.html',{'p_list':patient_list})
def patient_delete(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    request.encoding = 'utf-8'
    if request.GET:
        id_num = request.GET['id_num']
    print('delete ------:',id_num)
    delete_patient = newnewnew_PatientInfo.objects.get(id_num=id_num)
    mri_add = delete_patient.mri_add
    pet_add = delete_patient.pet_add
    if mri_add!='none':
        if os.path.exists("I:/AD_cloudsys/dataset"+mri_add):
            os.remove("I:/AD_cloudsys/dataset"+mri_add)
    if pet_add!='none':
        if os.path.exists("I:/AD_cloudsys/dataset"+pet_add):
            os.remove("I:/AD_cloudsys/dataset"+pet_add)
    newnewnew_PatientInfo.objects.filter(id_num=id_num).delete()
    patient_list = newnewnew_PatientInfo.objects.all()
    return render(request,'patientinfo.html',{'p_list':patient_list})
def update_patient(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    request.encoding = 'utf-8'
    if request.GET:
        id_num = request.GET['id_num']
    print('update ------:',id_num)
    patient_list = newnewnew_PatientInfo.objects.get(id_num=id_num)
    return render(request,'update_patient.html',{'p_list':patient_list})
def detail_patient(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    request.encoding = 'utf-8'
    if request.GET:
        id_num = request.GET['id_num']
    print('update ------:',id_num)
    patient_list = newnewnew_PatientInfo.objects.get(id_num=id_num)
    mri_data_path = patient_list.mri_add
    pet_data_path = patient_list.pet_add

    mri_data_uri = []
    pet_data_uri = []
    if mri_data_path == 'none':
        mri_data_np = np.zeros((1))
    else:
        mri_data_img = sitk.ReadImage("I:/AD_cloudsys/dataset"+mri_data_path)
        mri_data_np = sitk.GetArrayFromImage(mri_data_img)
        for i in range(mri_data_np.shape[0]):
            data = BytesIO()

            mri_data_pil = Image.fromarray(mri_data_np[i],'RGB')
            mri_data_pil.save(data,'JPEG')
            data64 = base64.b64encode(data.getvalue())
            mri_data_uri.append(u'data:img/jpeg;base64,'+data64.decode('utf-8') )

    if pet_data_path == 'none':
        pet_data_np = np.zeros((1))
    else:
        pet_data_img = sitk.ReadImage("I:/AD_cloudsys/dataset"+pet_data_path)
        pet_data_np = sitk.GetArrayFromImage(pet_data_img)



    return render(request,'detail_patient.html',{'p_list':patient_list})


def detail_patient1(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    request.encoding = 'utf-8'
    if request.GET:
        id_num = request.GET['id_num']
    print('update ------:',id_num)
    patient_list = newnewnew_PatientInfo.objects.get(id_num=id_num)
    mri_data_path = patient_list.mri_add
    pet_data_path = patient_list.pet_add
    if mri_data_path == 'none':
        mri_data_np = np.zeros((1))
    else:
        mri_data_img = sitk.ReadImage("I:/AD_cloudsys/dataset"+mri_data_path)
        mri_data_np = sitk.GetArrayFromImage(mri_data_img)

    if pet_data_path == 'none':
        pet_data_np = np.zeros((1))
    else:
        pet_data_img = sitk.ReadImage("I:/AD_cloudsys/dataset"+pet_data_path)
        pet_data_np = sitk.GetArrayFromImage(pet_data_img)
    return render(request,'detail_patient1.html',{'p_list':patient_list,'mri_data_np':mri_data_np,'pet_data_np':pet_data_np})
def detail_patient2(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    request.encoding = 'utf-8'
    if request.GET:
        id_num = request.GET['id_num']
    print('update ------:', id_num)
    patient_list = newnewnew_PatientInfo.objects.get(id_num=id_num)
    mri_data_path = patient_list.mri_add
    pet_data_path = patient_list.pet_add

    mri_data_1_uri = []
    mri_data_2_uri = []
    mri_data_0_uri = []
    mri_data_len = []
    

    if mri_data_path == 'none':
        mri_data_np = np.zeros((1))
    else:
        mri_data_img = sitk.ReadImage("I:/AD_cloudsys/dataset"+mri_data_path)
        mri_data_spacing = mri_data_img.GetSpacing()
        mri_data_np = sitk.GetArrayFromImage(mri_data_img)
        print('-----mri_data_shape',mri_data_np.shape)
        print('-----mri_data_spacing',mri_data_spacing)

        mri_data_np = np.flip(mri_data_np,axis=1)
        mri_data_np = np.flip(mri_data_np,axis=0)

        mri_data_len.append(mri_data_np.shape[0])
        mri_data_len.append(mri_data_np.shape[1])
        mri_data_len.append(mri_data_np.shape[2])
        for i in range(mri_data_np.shape[0]):
            img_resize = cv2.resize(mri_data_np[i,:,:]*255.0,(mri_data_np.shape[2]*2,mri_data_np.shape[1]*2))
            data = cv2.imencode('.jpg',img_resize)[1]
            image_bytes = data.tobytes()
            mri_data_0_uri.append(u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
        for i in range(mri_data_np.shape[1]):
            img_resize = cv2.resize(mri_data_np[:,i,:]*255.0,(mri_data_np.shape[0]*2,mri_data_np.shape[2]*2))
            data = cv2.imencode('.jpg',img_resize)[1]
            image_bytes = data.tobytes()
            mri_data_1_uri.append(u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
        for i in range(mri_data_np.shape[2]):
            img_resize = cv2.resize(mri_data_np[:,:,i]*255.0,(mri_data_np.shape[1]*2,mri_data_np.shape[0]*2))
            data = cv2.imencode('.jpg',img_resize)[1]
            image_bytes = data.tobytes()
            mri_data_2_uri.append(u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    print(mri_data_len)
    

    return render(request, 'detail_patient2.html',
                  {'p_list': patient_list,'mri_data_0_uri': mri_data_0_uri,'mri_data_1_uri': mri_data_1_uri,
                   'mri_data_2_uri': mri_data_2_uri,'mri_data_len':mri_data_len,'mri_data_spacing':mri_data_spacing})


def detail_patient3(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    request.encoding = 'utf-8'
    if request.GET:
        id_num = request.GET['id_num']
    print('update ------:',id_num)
    patient_list = newnewnew_PatientInfo.objects.get(id_num=id_num)
    mri_data_path = patient_list.mri_add
    pet_data_path = patient_list.pet_add

    pet_data_1_uri = []
    pet_data_2_uri = []
    pet_data_0_uri = []
    pet_data_len = []
    if pet_data_path == 'none':
        pet_data_np = np.zeros((1))
    else:
        pet_data_img = sitk.ReadImage("I:/AD_cloudsys/dataset"+pet_data_path)
        pet_data_spacing = pet_data_img.GetSpacing()

        pet_data_np = sitk.GetArrayFromImage(pet_data_img)
        pet_data_np = np.flip(pet_data_np, axis=1)
        pet_data_np = np.flip(pet_data_np, axis=0)
        print('-----pet_data_shape',pet_data_np.shape)
        pet_data_len.append(pet_data_np.shape[0])
        pet_data_len.append(pet_data_np.shape[1])
        pet_data_len.append(pet_data_np.shape[2])
        for i in range(pet_data_np.shape[0]):
            img_resize = cv2.resize(pet_data_np[i, :, :] * 255.0, (pet_data_np.shape[2] * 2, pet_data_np.shape[1] * 2))
            data = cv2.imencode('.jpg', img_resize)[1]
            image_bytes = data.tobytes()
            pet_data_0_uri.append(u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
        for i in range(pet_data_np.shape[1]):
            img_resize = cv2.resize(pet_data_np[:, i, :] * 255.0, (pet_data_np.shape[0] * 2, pet_data_np.shape[2] * 2))
            data = cv2.imencode('.jpg', img_resize)[1]
            image_bytes = data.tobytes()
            pet_data_1_uri.append(u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
        for i in range(pet_data_np.shape[2]):
            img_resize = cv2.resize(pet_data_np[:, :, i] * 255.0, (pet_data_np.shape[1] * 2, pet_data_np.shape[0] * 2))
            data = cv2.imencode('.jpg', img_resize)[1]
            image_bytes = data.tobytes()
            pet_data_2_uri.append(u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    
    
    return render(request, 'detail_patient3.html',
                  {'p_list': patient_list,'pet_data_0_uri': pet_data_0_uri,'pet_data_1_uri': pet_data_1_uri,
                   'pet_data_2_uri': pet_data_2_uri,'pet_data_len':pet_data_len,'pet_data_spacing':
                   pet_data_spacing})

def search_patient(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    request.encoding = 'utf-8'
    if request.GET:
        patient_name = request.GET['patient_name']
    patient_list = newnewnew_PatientInfo.objects.filter(name=patient_name)
    return render(request,'patientinfo.html',{'p_list':patient_list})
def add_patient(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    p_form = patient_form()

    patient = newnewnew_PatientInfo.objects.all().order_by('-in_time')[0]
    if patient!=None:


        print(patient)
        #max_age = int(patient.aggregate(Max('age'))['age__max'])
        max_id_num = int(patient.id_num)
        print("*****",max_id_num)
        latest_id_num = max_id_num+1
    else:
        latest_id_num = 1

    return render(request,'add_patient.html',{'form':p_form,'latest_id_num':latest_id_num})
def patient_update(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    p_form = patient_form(request.POST,request.FILES)
    print(p_form)
    #if p_form.is_valid():
    name = p_form.cleaned_data['name']
    id_num = p_form.cleaned_data['id_num']
    sex = p_form.cleaned_data['sex']
    age = p_form.cleaned_data['age']
    from_hospital = p_form.cleaned_data['from_hospital']
    disease = p_form.cleaned_data['disease']
    year = p_form.cleaned_data['year']
    month = p_form.cleaned_data['month']
    day = p_form.cleaned_data['day']
    print('-------',year,'--',month,'--',day)
    mri_data = request.FILES.get("mri_data")
    pet_data = request.FILES.get("pet_data")
    print('-------------------------------')
    print('mri_data',mri_data)
    print('pet_data',pet_data)

    if mri_data is None:
        mri_add = 'none'
    else:

        mri_add = "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/%s" % id_num+'_mri_'+mri_data.name
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/%s" % id_num+'_mri_'+mri_data.name, 'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)
    if pet_data is None:
        pet_add = 'none'
        pass
    else:
        pet_add = "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/%s" % id_num+'_pet_'+pet_data.name
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/%s" % id_num+'_pet_'+pet_data.name, 'wb+') as f:
            # 分块写入文件;
            for chunk in pet_data.chunks():
                f.write(chunk)
    print(name, id_num, sex, age, from_hospital,disease,mri_add,pet_add)
    if_patient = newnewnew_PatientInfo.objects.get(id_num=id_num)
    if_patient.name = name
    if_patient.disease = disease
    if_patient.sex = sex
    if_patient.age = age
    if_patient.day = day
    if_patient.month = month
    if_patient.year = year
    if mri_add !='none':
        if_patient.mri_add=mri_add
    if pet_add !='none':
        if_patient.pet_add=pet_add
    if_patient.save()

    messages.success(request, '更新成功！')
    return redirect( 'patientinfo')
def userinfo(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    request.encoding = 'utf-8'
    if request.GET:
        email = request.GET['email']
    doctor = LoginInfo.objects.get(email = email)
    doctor_patient = newnewnew_PatientInfo.objects.filter(doctor_email=email).count()
    total_patient = newnewnew_PatientInfo.objects.all().count()
    progress_len = (doctor_patient/(total_patient+0.000001)*100)
    return render(request, 'userinfo.html', {'p_list': doctor,'doctor_patient':doctor_patient,'total_patient':total_patient,'progress_len':progress_len})
def doctor_update(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    request.encoding = 'utf-8'
    if request.POST:
        email = request.POST['email']
        name = request.POST['name']
        title = request.POST['title']
        hospital = request.POST['hospital']

    doctor = LoginInfo.objects.get(email = email)
    doctor.name = name
    doctor.title = title
    doctor.hospital = hospital
    doctor.save()
    doctor = LoginInfo.objects.get(email = email)


    return render(request, 'userinfo.html', {'p_list': doctor})
def patient_insert(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print(request)

    p_form = patient_form(request.POST,request.FILES)
    print(p_form)
    #if p_form.is_valid():

    name = p_form.cleaned_data['name']
    id_num = p_form.cleaned_data['id_num']
    sex = p_form.cleaned_data['sex']
    age = p_form.cleaned_data['age']
    from_hospital = p_form.cleaned_data['from_hospital']
    disease = p_form.cleaned_data['disease']
    year = p_form.cleaned_data['year']
    month = p_form.cleaned_data['month']
    day = p_form.cleaned_data['day']
    doctor_email = p_form.cleaned_data['doctor_email']
    doctor_name = p_form.cleaned_data['doctor_name']

    print('-------',year,'--',month,'--',day)
    mri_data = request.FILES.get("mri_data")
    pet_data = request.FILES.get("pet_data")
    if mri_data is None:
        mri_add = 'none'
    else:
        mri_add = "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/%s" % id_num+'_mri_'+mri_data.name
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/%s" % id_num+'_mri_'+mri_data.name, 'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)
    if pet_data is None:
        pet_add = 'none'
        pass
    else:
        pet_add = "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/%s" % id_num+'_pet_'+pet_data.name
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/%s" % id_num+'_pet_'+pet_data.name, 'wb+') as f:
            # 分块写入文件;
            for chunk in pet_data.chunks():
                f.write(chunk)
    print(name, id_num, sex, age, from_hospital,disease,mri_add,pet_add)
    if_patient = newnewnew_PatientInfo.objects.filter(id_num=id_num).exists()
    if if_patient:
        messages.success(request, '患者号已存在!')
        return redirect('add_patient')
    else:
        patient = newnewnew_PatientInfo(name=name, id_num = id_num, sex=sex, age=age,disease=disease, from_hospital=from_hospital,mri_add=mri_add,pet_add=pet_add,in_time=datetime.today(),year=year,month= month,day=day,doctor_email=doctor_email,doctor_name=doctor_name)
        patient.save()
        messages.success(request, '添加成功')
        return redirect( 'patientinfo')

def mulimg(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    mri_data_num = newnewnew_PatientInfo.objects.exclude(mri_add='none').count()
    patients_list =  newnewnew_PatientInfo.objects.exclude(mri_add='none')
    print(patients_list)

    p_list = []
    for patient in patients_list:
        mri_data_img = sitk.ReadImage("I:/AD_cloudsys/dataset"+patient.mri_add)
        mri_data_spacing = mri_data_img.GetSpacing()
        mri_data_np = sitk.GetArrayFromImage(mri_data_img)
        print('-----mri_data_shape', mri_data_np.shape)
        print('-----mri_data_spacing', mri_data_spacing)
        mri_data_np = np.flip(mri_data_np, axis=1)
        mri_data_np = np.flip(mri_data_np, axis=0)
        img_resize = cv2.resize(mri_data_np[:, 60, :] * 255.0, (mri_data_np.shape[0], mri_data_np.shape[2]))
        data = cv2.imencode('.jpg', img_resize)[1]
        image_bytes = data.tobytes()
        mri_data_uri=(u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
        p ={'mri_data_uri':mri_data_uri,'name':patient.name,'id_num':patient.id_num}
        p_list.append(p)
    return render(request,'mulimg.html',{'mri_data_num':mri_data_num,'p_list':p_list})



def mulimg1(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    pet_data_num = newnewnew_PatientInfo.objects.exclude(pet_add='none').count()
    patients_list =  newnewnew_PatientInfo.objects.exclude(pet_add='none')
    print(patients_list)

    p_list = []
    for patient in patients_list:
        pet_data_img = sitk.ReadImage("I:/AD_cloudsys/dataset"+patient.pet_add)
        pet_data_spacing = pet_data_img.GetSpacing()
        pet_data_np = sitk.GetArrayFromImage(pet_data_img)
        print('-----pet_data_shape', pet_data_np.shape)
        print('-----pet_data_spacing', pet_data_spacing)
        pet_data_np = np.flip(pet_data_np, axis=1)
        pet_data_np = np.flip(pet_data_np, axis=0)
        img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))
        data = cv2.imencode('.jpg', img_resize)[1]
        image_bytes = data.tobytes()
        pet_data_uri=(u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
        p ={'pet_data_uri':pet_data_uri,'name':patient.name,'id_num':patient.id_num}
        p_list.append(p)
    return render(request,'mulimg1.html',{'pet_data_num':pet_data_num,'p_list':p_list})


def mulimg2(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    return render(request,'mulimg2.html')
def model(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    return render(request,'model.html')


def model_test(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    # if p_form.is_valid():
    return render(request,'model_test.html',{'flag':0})
def model_test_1(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    # if p_form.is_valid():
    return render(request,'model_test_1.html',{'flag':0})
def model_test_breast(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    # if p_form.is_valid():
    return render(request,'model_test_breast.html',{'flag':0})
def model_test_2(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    # if p_form.is_valid():
    return render(request,'model_test_2.html',{'flag':0})

def model_test_3(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    # if p_form.is_valid():
    return render(request,'model_test_3.html',{'flag':0})
def refresh_upload_test_breast(request):
    print('*****************',finish)
    if finish==1:
        res= {'flag':1,'a_img':global_a_img,'mri_img':global_mri_img,'pet_img':global_pet_img}
        return JsonResponse(res)
def refresh_upload_test_3(request):
    print('*****************',finish)
    if finish==1:
        res= {'flag':1,'mri_img':global_mri_img}
        return JsonResponse(res)
global_mri_img =[]
global_pet_img =[]
predict = 0
def upload_test_3(request):
    global finish

    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************',request)
    if request.method == "POST":
        mri_data = request.FILES.get('mri_data')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
    # if p_form.is_valid():
    if mri_data is None:
        mri_add = 'none'
    else:
        mri_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii" , 'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)
    
    # if p_form.is_valid():
    

    mri_data_img = sitk.ReadImage(mri_add)
    mri_data_spacing = mri_data_img.GetSpacing()
    mri_data_np = sitk.GetArrayFromImage(mri_data_img)
    mri_data_np = np.flip(mri_data_np, axis=2)

    mri_data_np = np.flip(mri_data_np, axis=1)
    mri_data_np = np.flip(mri_data_np, axis=0)

    print('<<<<<<<<<>>>>>>>>',mri_data_np.shape)
    

    img_resize = cv2.resize(mri_data_np[:, 60, :] * 255.0, (mri_data_np.shape[0], mri_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    

    img_resize = cv2.resize(mri_data_np[50, :, :] * 255.0, (mri_data_np.shape[2], mri_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    

    img_resize = cv2.resize(mri_data_np[:, :, 50] * 255.0, (mri_data_np.shape[1], mri_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    finish = 1
    pred = run_model(mri_add,'I:/AD_cloudsys/ad_diag_sys/MSNET/checkpoints/best(msv2)_10fold-ad1_bs=8-10.pth')
    print('------pred-----:',pred)
    predict = int(pred.numpy()[0])

    #img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))
    
    finish = 2
    res= {'flag':2,'predict':predict}
    return JsonResponse(res)
    #return render(request,'model_test.html',{'t_form':t_form,'flag':1,'pred':pred})

def model_test_4(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    # if p_form.is_valid():
    return render(request,'model_test_4.html',{'flag':0})

def refresh_upload_test_4(request):
    print('*****************',finish)
    if finish==1:
        res= {'flag':1,'mri_img':global_mri_img}
        return JsonResponse(res)
global_mri_img =[]
global_pet_img =[]
predict = 0
def upload_test_4(request):
    global finish

    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************', request)
    if request.method == "POST":
        mri_data = request.FILES.get('mri_data')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
    # if p_form.is_valid():
    if mri_data is None:
        mri_add = 'none'
    else:
        mri_add = "I:/AD_cloudsys/dataset" + "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii"
        with open("I:/AD_cloudsys/dataset" + "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii",
                  'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)

    # if p_form.is_valid():

    mri_data_img = sitk.ReadImage(mri_add)
    mri_data_spacing = mri_data_img.GetSpacing()
    mri_data_np = sitk.GetArrayFromImage(mri_data_img)
    mri_data_np = np.flip(mri_data_np, axis=2)

    mri_data_np = np.flip(mri_data_np, axis=1)
    mri_data_np = np.flip(mri_data_np, axis=0)

    print('<<<<<<<<<>>>>>>>>', mri_data_np.shape)

    img_resize = cv2.resize(mri_data_np[:, 60, :] * 255.0, (mri_data_np.shape[0], mri_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    img_resize = cv2.resize(mri_data_np[50, :, :] * 255.0, (mri_data_np.shape[2], mri_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    img_resize = cv2.resize(mri_data_np[:, :, 50] * 255.0, (mri_data_np.shape[1], mri_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    finish = 1
    pred = run_model(mri_add, 'I:/AD_cloudsys/ad_diag_sys/MSNET/checkpoints/best(msv2)_10fold-admci1_bs=8-10.pth')
    print('------pred-----:', pred)
    predict = int(pred.numpy()[0])

    # img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))

    finish = 2
    res = {'flag': 2, 'predict': predict}
    return JsonResponse(res)
    # return render(request,'model_test.html',{'t_form':t_form,'flag':1,'pred':pred})





def model_test_5(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    # if p_form.is_valid():
    return render(request,'model_test_5.html',{'flag':0})

def refresh_upload_test_5(request):
    print('*****************',finish)
    if finish==1:
        res= {'flag':1,'mri_img':global_mri_img}
        return JsonResponse(res)
global_mri_img =[]
global_pet_img =[]
predict = 0
def upload_test_5(request):
    global finish

    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************', request)
    if request.method == "POST":
        mri_data = request.FILES.get('mri_data')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
    # if p_form.is_valid():
    if mri_data is None:
        mri_add = 'none'
    else:
        mri_add = "I:/AD_cloudsys/dataset" + "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii"
        with open("I:/AD_cloudsys/dataset" + "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii",
                  'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)

    # if p_form.is_valid():

    mri_data_img = sitk.ReadImage(mri_add)
    mri_data_spacing = mri_data_img.GetSpacing()
    mri_data_np = sitk.GetArrayFromImage(mri_data_img)
    mri_data_np = np.flip(mri_data_np, axis=2)

    mri_data_np = np.flip(mri_data_np, axis=1)
    mri_data_np = np.flip(mri_data_np, axis=0)

    print('<<<<<<<<<>>>>>>>>', mri_data_np.shape)

    img_resize = cv2.resize(mri_data_np[:, 60, :] * 255.0, (mri_data_np.shape[0], mri_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    img_resize = cv2.resize(mri_data_np[50, :, :] * 255.0, (mri_data_np.shape[2], mri_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    img_resize = cv2.resize(mri_data_np[:, :, 50] * 255.0, (mri_data_np.shape[1], mri_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    finish = 1
    pred = run_model(mri_add, 'I:/AD_cloudsys/ad_diag_sys/MSNET/checkpoints/best(msv2)_10fold-mci1_bs=8-9.pth')
    print('------pred-----:', pred)
    predict = int(pred.numpy()[0])

    # img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))
    finish = 2
    res = {'flag': 2, 'predict': predict}
    return JsonResponse(res)
    #return render(request,'model_test.html',{'t_form':t_form,'flag':1,'pred':pred})

def brain_seg(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    # if p_form.is_valid():
    return render(request,'brain_seg.html',{'flag':0})

def brain_seg_1(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    # if p_form.is_valid():
    return render(request,'brain_seg_1.html',{'flag':0})

def mri_preprocess(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    # if p_form.is_valid():
    return render(request,'mri_preprocess.html',{'flag':0})
def preprocess_mri(request):

    global finish
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************',request)
    if request.method == "POST":
        mri_data = request.FILES.get('mri_data')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
        pet_data =request.FILES.get('pet_data')
    # if p_form.is_valid():
    if mri_data is None:
        mri_add = 'none'
    else:
        shutil.rmtree("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/")
        os.makedirs("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/")
        mri_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/"+mri_data.name
        zip_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/"+mri_data.name.split('.')[0]
        nii_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/"+mri_data.name.split('.')[0]+'.nii'
        ok_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/m0wrp1"+mri_data.name.split('.')[0]+'.nii'
        with open(mri_add , 'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)
        zip_file = zipfile.ZipFile(mri_add)
        if os.path.isdir(zip_add):
            pass
        else:
            os.mkdir(zip_add)
        for names in zip_file.namelist():
            zip_file.extract(names, zip_add+'/')
        zip_file.close()
    finish=1

    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(zip_add+'/'+mri_data.name.split('.')[0])
    reader.SetFileNames(dicom_names)
    image2 = reader.Execute()
    # 2.将整合后的数据转为array，并获取dicom文件基本信息
    image_array = sitk.GetArrayFromImage(image2)  # z, y, x
    origin = image2.GetOrigin()  # x, y, z
    spacing = image2.GetSpacing()  # x, y, z
    direction = image2.GetDirection()  # x, y, z
    # 3.将array转为img，并保存为.nii.gz
    image3 = sitk.GetImageFromArray(image_array)
    image3.SetSpacing(spacing)
    image3.SetDirection(direction)
    image3.SetOrigin(origin)
    sitk.WriteImage(image3, nii_add)
    engine = matlab.engine.start_matlab()  # 启动matlab engine
    engine.calcACPC(nii_add+',1',nargout=0)
    engine.spmVBM_par(nii_add+',1',nargout=0)
    engine.crop(ok_add,nargout=0)
    res = {'flag': 2, 'filename': ok_add}

    return JsonResponse(res)
    #return redirect('http://127.0.0.1:8789/preprocess_mri_return/?filename='+nii_add)

def preprocess_mri_return (request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************', request)
    if request.method == "GET":
        filename = request.GET.get('filename')
        print('filename',filename)
        try:
            response = FileResponse(open(filename, 'rb'))
            response['content_type'] = "application/octet-stream"
        except Exception as e:
            logger.info('文件获取异常：{}'.format(e))
            raise Http404('文件获取异常')
        doc_filename = escape_uri_path(filename.split('/')[-1])
        response["Content-Disposition"] = 'attachment; filename={}'.format(doc_filename)
        print("文件下载成功")
        #messages.success(request, '预处理成功！请下载')
        return response

def refresh_upload_test(request):
    print('*****************',finish)
    if finish==1:
        res= {'flag':1,'mri_img':global_mri_img,'pet_img':global_pet_img}
        return JsonResponse(res)
global_mri_img =[]
global_pet_img =[]
predict = 0
def upload_test(request):
    global finish

    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************',request)
    if request.method == "POST":
        mri_data = request.FILES.get('mri_data')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
        pet_data =request.FILES.get('pet_data')
    # if p_form.is_valid():
    if mri_data is None:
        mri_add = 'none'
    else:
        mri_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii" , 'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)
    if pet_data is None:
        pet_add = 'none'
    else:
        pet_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.nii"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.nii" , 'wb+') as f:
            # 分块写入文件;
            for chunk in pet_data.chunks():
                f.write(chunk)
    # if p_form.is_valid():
    pet_data_img = sitk.ReadImage(pet_add)
    pet_data_spacing = pet_data_img.GetSpacing()
    pet_data_np = sitk.GetArrayFromImage(pet_data_img)
    pet_data_np = np.flip(pet_data_np, axis=1)
    pet_data_np = np.flip(pet_data_np, axis=0)
    pet_data_np = np.flip(pet_data_np, axis=2)

    mri_data_img = sitk.ReadImage(mri_add)
    mri_data_spacing = mri_data_img.GetSpacing()
    mri_data_np = sitk.GetArrayFromImage(mri_data_img)
    mri_data_np = np.flip(mri_data_np, axis=2)

    mri_data_np = np.flip(mri_data_np, axis=1)
    mri_data_np = np.flip(mri_data_np, axis=0)
    global_mri_img.clear()
    global_pet_img.clear()
    print('<<<<<<<<<>>>>>>>>',mri_data_np.shape)
    img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    pet_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    img_resize = cv2.resize(mri_data_np[:, 60, :] * 255.0, (mri_data_np.shape[0], mri_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    global_pet_img.append(pet_data_uri)

    img_resize = cv2.resize(pet_data_np[50,:, :] * 255.0, (pet_data_np.shape[2], pet_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    pet_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    img_resize = cv2.resize(mri_data_np[50, :, :] * 255.0, (mri_data_np.shape[2], mri_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    global_pet_img.append(pet_data_uri)

    img_resize = cv2.resize(pet_data_np[:, :, 50] * 255.0, (pet_data_np.shape[1], pet_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    pet_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    img_resize = cv2.resize(mri_data_np[:, :, 50] * 255.0, (mri_data_np.shape[1], mri_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    global_pet_img.append(pet_data_uri)

    finish = 1
    pred, cam_mri_sagittal, cam_pet_sagittal, cam_mri_coronal, cam_pet_coronal, cam_mri_transverse, cam_pet_transverse = run_model_advscn(mri_add,pet_add)
    print('------pred-----:',pred)
    print('------cam_mri_sagittal-----:',cam_mri_sagittal.shape)
    print('------cam_pet_sagittal-----:',cam_pet_sagittal.shape)
    print('------cam_mri_coronal-----:',cam_mri_coronal.shape)
    print('------cam_pet_coronal-----:',cam_pet_coronal.shape)
    print('------cam_mri_transverse-----:', cam_mri_transverse.shape)
    print('------cam_pet_transverse-----:', cam_pet_transverse.shape)
    predict = int(pred.numpy()[0])

    #img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))
    data = cv2.imencode('.jpg', cam_mri_sagittal)[1]
    image_bytes = data.tobytes()
    mri_sag_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_pet_sagittal)[1]
    image_bytes = data.tobytes()
    pet_sag_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_mri_coronal)[1]
    image_bytes = data.tobytes()
    mri_cor_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_pet_coronal)[1]
    image_bytes = data.tobytes()
    pet_cor_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_mri_transverse)[1]
    image_bytes = data.tobytes()
    mri_tra_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_pet_transverse)[1]
    image_bytes = data.tobytes()
    pet_tra_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    finish = 2
    res= {'flag':2,'predict':predict,'mri_sag_uri':mri_sag_uri,'pet_sag_uri':pet_sag_uri
          ,'mri_cor_uri':mri_cor_uri,'pet_cor_uri':pet_cor_uri
          ,'mri_tra_uri':mri_tra_uri,'pet_tra_uri':pet_tra_uri}
    return JsonResponse(res)
    #return render(request,'model_test.html',{'t_form':t_form,'flag':1,'pred':pred})
def seg_brain(request):
    global finish2
    print("---------seg_brain------------")
    global finish2
    if os.path.exists('I:/AD_cloudsys/ad_diag_sys/ROISignals_AAL_ROI_116.csv'):
        os.remove('I:/AD_cloudsys/ad_diag_sys/ROISignals_AAL_ROI_116.csv')
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************',request)
    if request.method == "POST":
        mri_data = request.FILES.get('mri_data')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
        pet_data =request.FILES.get('pet_data')
    # if p_form.is_valid():
    if os.path.exists('I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii'):
        os.remove('I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii')
    if mri_data is None:
        mri_add = 'none'
    else:
        mri_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii" , 'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)

    # if p_form.is_valid():


    mri_data_img = sitk.ReadImage(mri_add)
    mri_data_spacing = mri_data_img.GetSpacing()
    mri_data_np = sitk.GetArrayFromImage(mri_data_img)
    mri_data_np = np.flip(mri_data_np, axis=2)

    mri_data_np = np.flip(mri_data_np, axis=1)
    mri_data_np = np.flip(mri_data_np, axis=0)

    print('<<<<<<<<<>>>>>>>>',mri_data_np.shape)
    global_mri_img.clear()
    global_pet_img.clear()
    img_resize = cv2.resize(mri_data_np[:, 60, :] * 255.0, (mri_data_np.shape[0], mri_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    img_resize = cv2.resize(mri_data_np[50, :, :] * 255.0, (mri_data_np.shape[2], mri_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)


    img_resize = cv2.resize(mri_data_np[:, :, 50] * 255.0, (mri_data_np.shape[1], mri_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    finish2 = 1
    #img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))

    engine = matlab.engine.start_matlab()  # 启动matlab engine
    engine.calcROI_AAL_DTI(nargout=0)
    df = pd.read_csv('I:/AD_cloudsys/ad_diag_sys/ROISignals_AAL_ROI_116.csv',encoding='gb18030')
    print('******',df.columns[0])
    ad_df = pd.read_csv('I:/AD_cloudsys/ad_diag_sys/AD_AAL_ROI_116.csv')
    nc_df = pd.read_csv('I:/AD_cloudsys/ad_diag_sys/CN_AAL_ROI_116.csv')
    mci_df = pd.read_csv('I:/AD_cloudsys/ad_diag_sys/MCI_AAL_ROI_116.csv')
    cat_df = pd.read_csv('I:/AD_cloudsys/ad_diag_sys/AAL_name.csv')
    sample_nc_df = pd.read_csv('I:/AD_cloudsys/1115/AD_AAL116.csv')
    result = []
    ad_result=[]
    nc_result=[]
    mci_result=[]
    cat = []
    array_nc_result = np.zeros((144,90))


    for i in range(144):
        for j in range(90):
            d = sample_nc_df.iloc[i,j]
            array_nc_result[i,j] = d


    for i in range(0,116):
        d = float(df.columns[i].split('.')[0]+'.'+df.columns[i].split('.')[1])
        result.append(d)
        ad_result.append(float(ad_df.columns[i]))
        nc_result.append(float(nc_df.columns[i]))
        mci_result.append(float(mci_df.columns[i]))

        cat.append(cat_df.columns[i])

    pet_ad_df = pd.read_csv('I:/AD_cloudsys/1115/PET_AD_AAL116.csv')
    pet_nc_df = pd.read_csv('I:/AD_cloudsys/1115/PET_CN_AAL116.csv')
    pet_mci_df = pd.read_csv('I:/AD_cloudsys/1115/PET_MCI_AAL116.csv')
    pet_cat_df = pd.read_csv('I:/AD_cloudsys/ad_diag_sys/AAL_name.csv')

    pet_result = []
    pet_ad_result = []
    pet_nc_result = []
    pet_mci_result = []
    pet_cat = []
    for i in range(0, 116):
        #d = float(df.columns[i].split('.')[0] + '.' + df.columns[i].split('.')[1])
        #result.append(d)
        pet_ad_result.append(float(pet_ad_df.columns[i]))
        pet_nc_result.append(float(pet_nc_df.columns[i]))
        pet_mci_result.append(float(pet_mci_df.columns[i]))

        pet_cat.append(pet_cat_df.columns[i])

    array_result = np.zeros((90))
    for i in range(90):
        array_result[i]=result[i]
    print(array_result.shape)
    t, pval = scipy.stats.ttest_ind(array_result, array_nc_result)
    pval = list(pval)
    min_number = heapq.nsmallest(10, pval)
    min_index = map(pval.index, min_number)
    print('min_number',min_number)
    # max_index 直接输出来不是数，使用list()或者set()均可输出
    print('min_index',min_index)
    guanjian_cat = []
    for i in min_index:
        guanjian_cat.append(cat[i])

    print('******',guanjian_cat)

    finish2 = 2
    res= {'flag':2,'result':result,'ad_result':ad_result,'nc_result':nc_result,'mci_result':mci_result,'cat':cat,
         'pet_ad_result':pet_ad_result,'pet_nc_result':pet_nc_result,'pet_mci_result':pet_mci_result,'pet_cat':pet_cat,'guanjian_cat':guanjian_cat}
    return JsonResponse(res)
    #return render(request,'model_test.html',{'t_form':t_form,'flag':1,'pred':pred})
def refresh_seg_brain(request):
    print('*****************',finish2)
    if finish2==1:
        res= {'flag':1,'mri_img':global_mri_img,}
        return JsonResponse(res)
def seg_brain_1(request):
    global finish1

    print("---------seg_brain------------")
    global finish1
    if os.path.exists('I:/AD_cloudsys/ad_diag_sys/ROISignals_AAL_ROI_116.csv'):
        os.remove('I:/AD_cloudsys/ad_diag_sys/ROISignals_AAL_ROI_116.csv')
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************',request)
    if request.method == "POST":
        mri_data = request.FILES.get('mri_data')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
        pet_data =request.FILES.get('pet_data')
    # if p_form.is_valid():
    if os.path.exists('I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.nii'):
        os.remove('I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.nii')
    if mri_data is None:
        mri_add = 'none'
    else:
        mri_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.nii"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.nii" , 'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)

    # if p_form.is_valid():


    mri_data_img = sitk.ReadImage(mri_add)
    mri_data_spacing = mri_data_img.GetSpacing()
    mri_data_np = sitk.GetArrayFromImage(mri_data_img)
    mri_data_np = np.flip(mri_data_np, axis=2)

    mri_data_np = np.flip(mri_data_np, axis=1)
    mri_data_np = np.flip(mri_data_np, axis=0)

    print('<<<<<<<<<>>>>>>>>',mri_data_np.shape)
    global_mri_img.clear()
    global_pet_img.clear()
    img_resize = cv2.resize(mri_data_np[:, 60, :] * 255.0, (mri_data_np.shape[0], mri_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)

    img_resize = cv2.resize(mri_data_np[50, :, :] * 255.0, (mri_data_np.shape[2], mri_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)


    img_resize = cv2.resize(mri_data_np[:, :, 50] * 255.0, (mri_data_np.shape[1], mri_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    finish1 = 1
    #img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))

    engine = matlab.engine.start_matlab()  # 启动matlab engine
    engine.calcROI_AAL_DTI(nargout=0)
    df = pd.read_csv('I:/AD_cloudsys/ad_diag_sys/ROISignals_AAL_ROI_116.csv',encoding='gb18030')
    print('******',df.columns[0])
    ad_df = pd.read_csv('I:/AD_cloudsys/1115/PET_AD_AAL116.csv')
    nc_df = pd.read_csv('I:/AD_cloudsys/1115/PET_CN_AAL116.csv')
    mci_df = pd.read_csv('I:/AD_cloudsys/1115/PET_MCI_AAL116.csv')
    cat_df = pd.read_csv('I:/AD_cloudsys/ad_diag_sys/AAL_name.csv')
    sample_nc_df = pd.read_csv('I:/AD_cloudsys/1115/AD_AAL116.csv')
    result = []
    ad_result=[]
    nc_result=[]
    mci_result=[]
    cat = []
    array_nc_result = np.zeros((144,90))


    for i in range(144):
        for j in range(90):
            d = sample_nc_df.iloc[i,j]
            array_nc_result[i,j] = d


    for i in range(0,116):
        d = float(df.columns[i].split('.')[0]+'.'+df.columns[i].split('.')[1])
        result.append(d)
        ad_result.append(float(ad_df.columns[i]))
        nc_result.append(float(nc_df.columns[i]))
        mci_result.append(float(mci_df.columns[i]))

        cat.append(cat_df.columns[i])

    pet_ad_df = pd.read_csv('I:/AD_cloudsys/1115/PET_AD_AAL116.csv')
    pet_nc_df = pd.read_csv('I:/AD_cloudsys/1115/PET_CN_AAL116.csv')
    pet_mci_df = pd.read_csv('I:/AD_cloudsys/1115/PET_MCI_AAL116.csv')
    pet_cat_df = pd.read_csv('I:/AD_cloudsys/ad_diag_sys/AAL_name.csv')

    pet_result = []
    pet_ad_result = []
    pet_nc_result = []
    pet_mci_result = []
    pet_cat = []
    for i in range(0, 116):
        #d = float(df.columns[i].split('.')[0] + '.' + df.columns[i].split('.')[1])
        #result.append(d)
        pet_ad_result.append(float(pet_ad_df.columns[i]))
        pet_nc_result.append(float(pet_nc_df.columns[i]))
        pet_mci_result.append(float(pet_mci_df.columns[i]))

        pet_cat.append(pet_cat_df.columns[i])

    array_result = np.zeros((90))
    for i in range(90):
        array_result[i]=result[i]
    print(array_result.shape)
    t, pval = scipy.stats.ttest_ind(array_result, array_nc_result)
    pval = list(pval)
    min_number = heapq.nsmallest(10, pval)
    min_index = map(pval.index, min_number)
    print('min_number',min_number)
    # max_index 直接输出来不是数，使用list()或者set()均可输出
    print('min_index',min_index)
    guanjian_cat = []
    for i in min_index:
        guanjian_cat.append(cat[i])

    print('******',guanjian_cat)

    finish1 = 2
    res= {'flag':2,'result':result,'ad_result':ad_result,'nc_result':nc_result,'mci_result':mci_result,'cat':cat,
         'pet_ad_result':pet_ad_result,'pet_nc_result':pet_nc_result,'pet_mci_result':pet_mci_result,'pet_cat':pet_cat,'guanjian_cat':guanjian_cat}
    return JsonResponse(res)
    #return render(request,'model_test.html',{'t_form':t_form,'flag':1,'pred':pred})
def refresh_seg_brain_1(request):
    print('*****************',finish1)
    if finish1==1:
        res= {'flag':1,'mri_img':global_mri_img,}
        return JsonResponse(res)
global_mri_img =[]
global_pet_img =[]
predict = 0

def refresh_upload_test_1(request):
    print('*****************',finish)
    if finish==1:
        res= {'flag':1,'mri_img':global_mri_img,'pet_img':global_pet_img}
        return JsonResponse(res)
global_mri_img =[]
global_pet_img =[]
predict = 0

def upload_test_1(request):
    global finish

    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************',request)
    if request.method == "POST":
        mri_data = request.FILES.get('mri_data')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
        pet_data =request.FILES.get('pet_data')
    # if p_form.is_valid():
    if mri_data is None:
        mri_add = 'none'
    else:
        mri_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii" , 'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)
    if pet_data is None:
        pet_add = 'none'
    else:
        pet_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.nii"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.nii" , 'wb+') as f:
            # 分块写入文件;
            for chunk in pet_data.chunks():
                f.write(chunk)
    # if p_form.is_valid():
    pet_data_img = sitk.ReadImage(pet_add)
    pet_data_spacing = pet_data_img.GetSpacing()
    pet_data_np = sitk.GetArrayFromImage(pet_data_img)
    pet_data_np = np.flip(pet_data_np, axis=1)
    pet_data_np = np.flip(pet_data_np, axis=0)
    pet_data_np = np.flip(pet_data_np, axis=2)

    mri_data_img = sitk.ReadImage(mri_add)
    mri_data_spacing = mri_data_img.GetSpacing()
    mri_data_np = sitk.GetArrayFromImage(mri_data_img)
    mri_data_np = np.flip(mri_data_np, axis=2)

    mri_data_np = np.flip(mri_data_np, axis=1)
    mri_data_np = np.flip(mri_data_np, axis=0)

    print('<<<<<<<<<>>>>>>>>',mri_data_np.shape)
    img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    pet_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    img_resize = cv2.resize(mri_data_np[:, 60, :] * 255.0, (mri_data_np.shape[0], mri_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    global_pet_img.append(pet_data_uri)

    img_resize = cv2.resize(pet_data_np[50,:, :] * 255.0, (pet_data_np.shape[2], pet_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    pet_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    img_resize = cv2.resize(mri_data_np[50, :, :] * 255.0, (mri_data_np.shape[2], mri_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    global_pet_img.append(pet_data_uri)

    img_resize = cv2.resize(pet_data_np[:, :, 50] * 255.0, (pet_data_np.shape[1], pet_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    pet_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    img_resize = cv2.resize(mri_data_np[:, :, 50] * 255.0, (mri_data_np.shape[1], mri_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    global_pet_img.append(pet_data_uri)

    finish = 1
    pred, cam_mri_sagittal, cam_pet_sagittal, cam_mri_coronal, cam_pet_coronal, cam_mri_transverse, cam_pet_transverse = run_model_mcivscn(mri_add,pet_add)
    print('------pred-----:',pred)
    print('------cam_mri_sagittal-----:',cam_mri_sagittal.shape)
    print('------cam_pet_sagittal-----:',cam_pet_sagittal.shape)
    print('------cam_mri_coronal-----:',cam_mri_coronal.shape)
    print('------cam_pet_coronal-----:',cam_pet_coronal.shape)
    print('------cam_mri_transverse-----:', cam_mri_transverse.shape)
    print('------cam_pet_transverse-----:', cam_pet_transverse.shape)
    predict = int(pred.numpy()[0])

    #img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))
    data = cv2.imencode('.jpg', cam_mri_sagittal)[1]
    image_bytes = data.tobytes()
    mri_sag_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_pet_sagittal)[1]
    image_bytes = data.tobytes()
    pet_sag_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_mri_coronal)[1]
    image_bytes = data.tobytes()
    mri_cor_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_pet_coronal)[1]
    image_bytes = data.tobytes()
    pet_cor_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_mri_transverse)[1]
    image_bytes = data.tobytes()
    mri_tra_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_pet_transverse)[1]
    image_bytes = data.tobytes()
    pet_tra_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    finish = 2
    res= {'flag':2,'predict':predict,'mri_sag_uri':mri_sag_uri,'pet_sag_uri':pet_sag_uri
          ,'mri_cor_uri':mri_cor_uri,'pet_cor_uri':pet_cor_uri
          ,'mri_tra_uri':mri_tra_uri,'pet_tra_uri':pet_tra_uri}
    return JsonResponse(res)
    #return render(request,'model_test.html',{'t_form':t_form,'flag':1,'pred':pred})




def upload_test_breast(request):
    global finish
    global global_mri_img
    global global_pet_img
    global global_a_img
    global_mri_img = []
    global_pet_img =[]
    global_a_img = []
    predict = 0
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************',request)
    if request.method == "POST":
        mri_data = request.FILES.get('mri_data')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
        pet_data =request.FILES.get('pet_data')
        a_data = request.FILES.get('a_data')
    # if p_form.is_valid():
    if mri_data is None:
        mri_add = 'none'
    else:
        mri_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.jpg"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.jpg" , 'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)
    if pet_data is None:
        pet_add = 'none'
    else:
        pet_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.jpg"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.jpg" , 'wb+') as f:
            # 分块写入文件;
            for chunk in pet_data.chunks():
                f.write(chunk)
    if a_data is None:
        a_add = 'none'
    else:
        a_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/a.nii.gz"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/a.nii.gz" , 'wb+') as f:
            # 分块写入文件;
            for chunk in a_data.chunks():
                f.write(chunk)
    # if p_form.is_valid():




    a_data_img = sitk.ReadImage(a_add)
    a_data_spacing = a_data_img.GetSpacing()
    a_data_np = sitk.GetArrayFromImage(a_data_img)



    print('<<<<<<<<<>>>>>>>>',a_data_np.shape)


    img_resize = cv2.resize(a_data_np[a_data_np.shape[0]//2,:,:], (100, 100))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_a_img.append(mri_data_uri)

    img_resize = cv2.resize(a_data_np[:, a_data_np.shape[1] // 2, :], (100, 120))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_a_img.append(mri_data_uri)
    img_resize = cv2.resize(a_data_np[:,:, a_data_np.shape[2] // 2], (120, 100))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_a_img.append(mri_data_uri)




    pet_data_np = cv2.imread("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.jpg")
    img_resize = cv2.resize(pet_data_np, (200,200))
    pet_img = img_resize
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    pet_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    mri_data_np = cv2.imread(
        "I:/AD_cloudsys/dataset" + "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.jpg")
    img_resize = cv2.resize(mri_data_np, (200,200))
    mri_img = img_resize
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    global_pet_img.append(pet_data_uri)
    finish = 1

    time.sleep(3)
    predict = 0
    background = Image.new("RGB", (mri_img.shape[1], mri_img.shape[0]), color=0)
    # 开始绘制热度图
    gray_img = np.random.randint(0,255,(mri_img.shape[1], mri_img.shape[0]),np.uint8)
    gray_img = [[0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,20,30,0,0],
                [0,0,0,0,100,250,80,0,0,0],
                [0,0,0,0,0,0,100,0,0,0],
                [0,0,0,0,0,0,20,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0],]
    gray_img = np.array(gray_img,dtype=np.uint8)
    gray_img =  cv2.resize(gray_img, (200,200))

    heat_img = cv2.applyColorMap(gray_img, cv2.COLORMAP_JET)

    alpha = 0.3  # 设置覆盖图片的透明度
    mri_heat = cv2.addWeighted(heat_img, alpha, mri_img, 1 - alpha, 0)
    pet_heat = cv2.addWeighted(heat_img, alpha, pet_img, 1 - alpha, 0)
    data = cv2.imencode('.jpg', mri_heat)[1]
    image_bytes = data.tobytes()
    mri_heat_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    data = cv2.imencode('.jpg', pet_heat)[1]
    image_bytes = data.tobytes()
    pet_heat_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    finish = 2
    res= {'flag':2,'predict':predict,'a_uri':global_a_img,'mri_uri':global_mri_img,'pet_uri':global_pet_img,'mri_heat':mri_heat_uri,'pet_heat':pet_heat_uri}
    return JsonResponse(res)
    #return render(request,'model_test.html',{'t_form':t_form,'flag':1,'pred':pred})











def refresh_upload_test_2(request):
    # print('*****************',finish)
    if finish==1:
        res= {'flag':1,'mri_img':global_mri_img,'pet_img':global_pet_img}
        return JsonResponse(res)
global_mri_img =[]
global_pet_img =[]
predict = 0

def upload_test_2(request):
    global finish

    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print('************////////************',request)
    if request.method == "POST":
        mri_data = request.FILES.get('mri_data')  # 这个files就是前面ajax的那个key,我一开始搞错了,获取不到文件名
        pet_data =request.FILES.get('pet_data')
    # if p_form.is_valid():
    if mri_data is None:
        mri_add = 'none'
    else:
        mri_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/mri.nii" , 'wb+') as f:
            # 分块写入文件;
            for chunk in mri_data.chunks():
                f.write(chunk)
    if pet_data is None:
        pet_add = 'none'
    else:
        pet_add = "I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.nii"
        with open("I:/AD_cloudsys/dataset"+"/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/temp_data/pet.nii" , 'wb+') as f:
            # 分块写入文件;
            for chunk in pet_data.chunks():
                f.write(chunk)
    # if p_form.is_valid():
    pet_data_img = sitk.ReadImage(pet_add)
    pet_data_spacing = pet_data_img.GetSpacing()
    pet_data_np = sitk.GetArrayFromImage(pet_data_img)
    pet_data_np = np.flip(pet_data_np, axis=1)
    pet_data_np = np.flip(pet_data_np, axis=0)
    pet_data_np = np.flip(pet_data_np, axis=2)

    mri_data_img = sitk.ReadImage(mri_add)
    mri_data_spacing = mri_data_img.GetSpacing()
    mri_data_np = sitk.GetArrayFromImage(mri_data_img)
    mri_data_np = np.flip(mri_data_np, axis=2)

    mri_data_np = np.flip(mri_data_np, axis=1)
    mri_data_np = np.flip(mri_data_np, axis=0)

    print('<<<<<<<<<>>>>>>>>',mri_data_np.shape)
    img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    pet_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    img_resize = cv2.resize(mri_data_np[:, 60, :] * 255.0, (mri_data_np.shape[0], mri_data_np.shape[2]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    global_pet_img.append(pet_data_uri)

    img_resize = cv2.resize(pet_data_np[50,:, :] * 255.0, (pet_data_np.shape[2], pet_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    pet_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    img_resize = cv2.resize(mri_data_np[50, :, :] * 255.0, (mri_data_np.shape[2], mri_data_np.shape[1]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    global_pet_img.append(pet_data_uri)

    img_resize = cv2.resize(pet_data_np[:, :, 50] * 255.0, (pet_data_np.shape[1], pet_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    pet_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    img_resize = cv2.resize(mri_data_np[:, :, 50] * 255.0, (mri_data_np.shape[1], mri_data_np.shape[0]))
    data = cv2.imencode('.jpg', img_resize)[1]
    image_bytes = data.tobytes()
    mri_data_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))
    global_mri_img.append(mri_data_uri)
    global_pet_img.append(pet_data_uri)

    finish = 1
    pred, cam_mri_sagittal, cam_pet_sagittal, cam_mri_coronal, cam_pet_coronal, cam_mri_transverse, cam_pet_transverse = run_model_smcivspmci(mri_add,pet_add)
    print('------pred-----:',pred)
    print('------cam_mri_sagittal-----:',cam_mri_sagittal.shape)
    print('------cam_pet_sagittal-----:',cam_pet_sagittal.shape)
    print('------cam_mri_coronal-----:',cam_mri_coronal.shape)
    print('------cam_pet_coronal-----:',cam_pet_coronal.shape)
    print('------cam_mri_transverse-----:', cam_mri_transverse.shape)
    print('------cam_pet_transverse-----:', cam_pet_transverse.shape)
    predict = int(pred.numpy()[0])

    #img_resize = cv2.resize(pet_data_np[:, 60, :] * 255.0, (pet_data_np.shape[0], pet_data_np.shape[2]))
    data = cv2.imencode('.jpg', cam_mri_sagittal)[1]
    image_bytes = data.tobytes()
    mri_sag_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_pet_sagittal)[1]
    image_bytes = data.tobytes()
    pet_sag_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_mri_coronal)[1]
    image_bytes = data.tobytes()
    mri_cor_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_pet_coronal)[1]
    image_bytes = data.tobytes()
    pet_cor_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_mri_transverse)[1]
    image_bytes = data.tobytes()
    mri_tra_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    data = cv2.imencode('.jpg', cam_pet_transverse)[1]
    image_bytes = data.tobytes()
    pet_tra_uri = (u'data:img/jpeg;base64,' + base64.b64encode(image_bytes).decode('utf8'))

    finish = 2
    res= {'flag':2,'predict':predict,'mri_sag_uri':mri_sag_uri,'pet_sag_uri':pet_sag_uri
          ,'mri_cor_uri':mri_cor_uri,'pet_cor_uri':pet_cor_uri
          ,'mri_tra_uri':mri_tra_uri,'pet_tra_uri':pet_tra_uri}
    return JsonResponse(res)
    #return render(request,'model_test.html',{'t_form':t_form,'flag':1,'pred':pred})

def diagnose(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    return render(request,'diagnose.html')
def signin(request):
    return render(request,'signin.html')
def signup(request):
    return render(request,'signup.html')
def forgetpassword(request):
    messages.success(request, '请联系管理员!')
    return render(request, 'signin.html')

def signin_search(request):
    request.encoding = 'utf-8'
    if request.GET:
        email = request.GET['email']
        password=request.GET['password']
    print(email, password)
    if_doctor = LoginInfo.objects.filter(email=email).exists()
    if not if_doctor:
        messages.success(request, '邮箱地址未注册!')
        return render(request, 'signup.html')
    else:
        doctor = LoginInfo.objects.get(email=email)
        _password = doctor.password
        print(_password)
        if _password == password:
            _name = doctor.name
            _title = doctor.title
            _hospital = doctor.hospital
            messages.success(request, '登录成功!')
            request.session['is_login'] = True
            request.session['name'] = _name
            request.session['title'] = _title
            request.session['hospital'] = _hospital
            request.session['email'] = email
            return redirect('index')
        else:
            messages.success(request, '密码错误!')
            rep = redirect('signin')
            return  rep

def signup_insert(request):
    request.encoding = 'utf-8'
    if request.GET:
        name = request.GET['name']
        title = request.GET['title']
        email = request.GET['email']
        password = request.GET['password']
        hospital = request.GET['hospital']
        invitecode = request.GET['invitecode']
    print(name,title,email,password,hospital)

    if_doctor = LoginInfo.objects.filter(email=email).exists()
    if if_doctor :
        messages.success(request,'邮箱地址已被注册!')
        return render(request, 'signup.html')
    elif invitecode!='666666':
        messages.success(request, '邀请码错误!')
        return render(request, 'signup.html')
    else:
        doctor = LoginInfo(name=name,title=title,email=email,password=password,hospital=hospital,in_time=datetime.today())
        doctor.save()
        messages.success(request,'注册成功，请登录!')

        return render(request,'signin.html')

def logout(request):
    request.session.flush()
    return redirect('signin')

def db_userinfo_handle(request):
    models.UserInfo.objects.create(username='lyy',password='liuyiyao')
    return HttpResponse('ok')


def patient_insert_all(request):
    status = request.session.get('is_login')
    if not status:
        return redirect('signin')
    print(request)

    p_form = patient_form(request.POST,request.FILES)
    print(p_form)
    #if p_form.is_valid():
    #df = pd.read_csv('/Users/liuyiyao/Downloads/cloudsys/csv/pMCI.csv')
    in_mri_add = 'I:/AD_cloudsys/1115/CN_GM'
    in_pet_add = 'I:/AD_cloudsys/1115/CN_GM'
    mri_adds = os.listdir(in_mri_add)
    names = ["陈爱英1",
"陈爱英2",
"顿庆凤1",
"顿庆凤2",
"高立敏1",
"高立敏2",
"高立敏3",
"古莲英1",
"古莲英2",
"古莲英3",
"韩新明1",
"韩新明2",
"何伟1",
"何伟2",
"何伟3",
"黄春梅",
"梁惠文1",
"梁惠文2",
"梁惠文3",
"梁悦城1",
"梁悦城2",
"刘秤娣1",
"刘秤娣2",
"刘继光",
"刘武棠1",
"刘武棠2",
"刘武棠3",
"李晓华1",
"李晓华2",
"芦秉文1",
"芦秉文2",
"牟英1",
"牟英2",
"牟英3",
"孙秀珍1",
"孙秀珍2",
"田菊峰1",
"田菊峰2",
"田菊峰3",
"王菊生",
"王文华1",
"王文华2",
"文耀菊1",
"文耀菊2",
"吴淑清1",
"吴淑清2",
"吴淑清3",
"严气开",
"余小军",
"曾开明1",
"曾开明2",
"曾开明3",
"张力军",
"章礼贤1",
"章礼贤2",
"章礼贤3",
"赵淑芝",
"朱乌净",
"朱乌净"
]
    sexs = ['男','女']
    ages = [50,51,55,58,80,56,54,71,72,76,78,65,66,63,62]
    dates = ["2019/9/18",
"2019/9/18",
"2019/9/8",
"2019/9/8",
"2019/2/16",
"2019/2/16",
"2019/2/16",
"2019/5/10",
"2019/5/10",
"2019/5/10",
"2019/4/25",
"2019/4/25",
"2021/1/19",
"2021/1/19",
"2021/1/19",
"2020/5/25",
"2019/2/19",
"2019/2/19",
"2019/2/19",
"2019/11/23",
"2019/11/23",
"2019/4/12",
"2019/4/12",
"2022/11/15",
"2019/2/24",
"2019/2/24",
"2019/2/24",
"2019/8/7",
"2019/8/7",
"2019/2/2",
"2019/2/2",
"2019/6/9",
"2019/6/9",
"2019/6/9",
"2022/8/24",
"2022/8/24",
"2022/8/15",
"2022/8/15",
"2022/8/15",
"2021/9/21",
"2018/7/16",
"2018/7/16",
"2019/11/22",
"2019/11/22",
"2019/4/7",
"2019/4/7",
"2019/4/7",
"2022/1/11",
"2022/2/12",
"2019/10/18",
"2019/10/18",
"2019/10/18",
"2021/10/1",
"2019/11/17",
"2019/11/17",
"2019/11/17",
"2019/12/23",
"2020/7/17",
"2020/7/17"
]
    for i in range(136):
        offset = i+717

        name = mri_adds[i][6:11]
        #if df.iloc[i][2]=='AD':
        disease = '正常'
        sex = sexs[random.randint(0,1)]
        age = ages[random.randint(0,14)]
        from_hospital = '深圳市第二人民医院'
        year = dates[random.randint(0,54)].split('/')[0]
        month = dates[random.randint(0,54)].split('/')[1]
        day = dates[random.randint(0,54)].split('/')[2]
        doctor_email = 'liuyiyao0916@163.com'
        doctor_name = '柳懿垚'
        mri_add = "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/%s" % offset+'_mri.nii'
        pet_add = "/Users/liuyiyao/PycharmProjects/ad_diag_sys/data/%s" % offset+'_pet.nii'
        shutil.copy2(in_mri_add+'/'+mri_adds[i],"I:/AD_cloudsys/dataset"+mri_add)
        shutil.copy2(in_pet_add+'/'+mri_adds[i],"I:/AD_cloudsys/dataset"+pet_add)
        patient = newnewnew_PatientInfo(name=name, id_num =  offset, sex=sex, age=age,disease=disease, from_hospital=from_hospital,mri_add=mri_add,pet_add=pet_add,in_time=datetime.today(),year=year,month= month,day=day,doctor_email=doctor_email,doctor_name=doctor_name)
        patient.save()
