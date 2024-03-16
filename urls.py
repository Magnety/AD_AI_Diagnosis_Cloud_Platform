"""ad_diag_sys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""cloudsys URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import re_path as url
from cloudsys import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',views.index,name='index'),
    path('patientinfo/',views.patientinfo,name='patientinfo'),
    path('mulimg/', views.mulimg, name='mulimg'),
    path('mulimg1/', views.mulimg1, name='mulimg1'),
    path('mulimg2/', views.mulimg2, name='mulimg2'),

    path('model/', views.model, name='model'),
    path('model_test/', views.model_test, name='model_test'),
    path('upload_test/', views.upload_test, name='upload_test'),
    path('refresh_upload_test/', views.refresh_upload_test, name='refresh_upload_test'),


    path('model_test_breast/', views.model_test_breast, name='model_test_breast'),
    path('upload_test_breast/', views.upload_test_breast, name='upload_test_breast'),
    path('refresh_upload_test_breast/', views.refresh_upload_test_breast, name='refresh_upload_test_breast'),

    path('model_test_1/', views.model_test_1, name='model_test_1'),
    path('upload_test_1/', views.upload_test_1, name='upload_test_1'),
    path('refresh_upload_test_1/', views.refresh_upload_test_1, name='refresh_upload_test_1'),
    path('model_test_2/', views.model_test_2, name='model_test_2'),
    path('upload_test_2/', views.upload_test_2, name='upload_test_2'),
    path('refresh_upload_test_2/', views.refresh_upload_test_2, name='refresh_upload_test_2'),
    path('model_test_3/', views.model_test_3, name='model_test_3'),
    path('upload_test_3/', views.upload_test_3, name='upload_test_3'),
    path('refresh_upload_test_3/', views.refresh_upload_test_3, name='refresh_upload_test_3'),
    path('model_test_4/', views.model_test_4, name='model_test_4'),
    path('upload_test_4/', views.upload_test_4, name='upload_test_4'),
    path('refresh_upload_test_4/', views.refresh_upload_test_4, name='refresh_upload_test_4'),
    path('model_test_5/', views.model_test_5, name='model_test_5'),
    path('upload_test_5/', views.upload_test_5, name='upload_test_5'),
    path('refresh_upload_test_5/', views.refresh_upload_test_5, name='refresh_upload_test_5'),
    path('signin/',views.signin,name='signin'),
    path('signup/', views.signup, name='signup'),
    path('signin_search/',views.signin_search,name='signin_search'),
    path('signup_insert/', views.signup_insert,name='signup_insert'),
    path('logout/', views.logout, name='logout'),
    path('add_patient/', views.add_patient, name='add_patient'),
    path('patient_insert/', views.patient_insert, name='patient_insert'),
    path('search_patient/', views.search_patient, name='search_patient'),
    path('patient_delete/', views.patient_delete, name='patient_delete'),
    path('update_patient/', views.update_patient, name='update_patient'),
    path('patient_update/', views.patient_update, name='patient_update'),
    path('detail_patient/', views.detail_patient, name='detail_patient'),
    path('detail_patient1/', views.detail_patient1, name='detail_patient1'),
    path('detail_patient2/', views.detail_patient2, name='detail_patient2'),
    path('detail_patient3/', views.detail_patient3, name='detail_patient3'),

    path('userinfo/', views.userinfo, name='userinfo'),
    path('doctor_update/', views.doctor_update, name='doctor_update'),
    path('mypatient/', views.mypatient, name='mypatient'),
    path('forgetpassword/', views.forgetpassword, name='forgetpassword'),
    path('patient_insert_all/', views.patient_insert_all, name='patient_insert_all'),
    path('brain_seg/', views.brain_seg, name='brain_seg'),
    path('brain_seg_1/', views.brain_seg_1, name='brain_seg_1'),

    path('mri_preprocess/', views.mri_preprocess, name='mri_preprocess'),
    path('preprocess_mri/', views.preprocess_mri, name='preprocess_mri'),
    path('preprocess_mri_return/', views.preprocess_mri_return, name='preprocess_mri_return'),
    path('seg_brain_1/', views.seg_brain_1, name='seg_brain_1'),
    path('seg_brain/', views.seg_brain, name='seg_brain'),

    path('refresh_seg_brain/', views.refresh_seg_brain, name='refresh_seg_brain'),
    path('refresh_seg_brain_1/', views.refresh_seg_brain_1, name='refresh_seg_brain_1'),

    path('diagnose/', views.diagnose, name='diagnose'),
    path('db_userinfo_handle/',views.db_userinfo_handle)

]


