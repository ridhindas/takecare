"""takecare URL Configuration

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
from django.urls import path, re_path
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings



from . import views

urlpatterns = [
    path('',views.first, name='first'),
    path('homes', views.homes, name='homes'),
    path('homenurse', views.homenurse, name='homenurse'),
    path('addhomenurse', views.addhomenurse, name='addhomenurse'),
    path('adddhomelogin', views.adddhomelogin, name='adddhomelogin'),
    path('homeeee', views.homeeee, name='homeeee'),

    path('adhome', views.adhome, name='adhome'),
    path('homeee', views.homeee, name='homeee'),
    path('viewhomeuserrequest', views.viewhomeuserrequest, name='viewhomeuserrequest'),
    path('logint', views.logint, name='logint'),
    path('homelogin', views.homelogin, name='homelogin'),
    path('viewwhomereq', views.viewwhomereq, name='viewwhomereq'),
    path('dhome', views.dhome, name='dhome'),
    path('doctors', views.doctors, name='doctors'),
    path('phome', views.phome, name='phome'),
    path('phhome', views.phhome, name='phhome'),
    path('viewpa', views.viewpa, name='viewpa'),
    path('viewpha', views.viewpha, name='viewpha'),
    path('time', views.time, name='time'),
    path('timeshe', views.timeshe, name='timeshe'),
    path('labshome', views.labshome, name='labshome'),

    path('vp', views.vp, name='vp'),
    

    path('doctor/dreg', views.dreg, name='dreg'),
    path('doctor/login1', views.login1, name='login1'),
    path('labhome', views.labhome, name='labhome'),
    path('patient/preg', views.preg, name='preg'),
    path('pharmacy/phreg', views.phreg, name='phreg'),
    path('labs/labsreg', views.labsreg, name='labsreg'),
    path('labs/lg', views.lg, name='lg'),
    path('pharmacy/login4', views.login4, name='login4'),
    path('patient/log2', views.log2, name='log2'),
    path('patientt', views.patientt, name='patientt'),
    path('viewlab', views.viewlab, name='viewlab'),
    path('export_page', views.export_page, name='export_page'),

    path('approvepha/<int:id>', views.approvepha, name='approvepha'),
    path('requestapprove/<int:id>', views.requestapprove, name='requestapprove'),
    path('labs/', include('labs.urls'), name='labs'),

    path('patient/', include('patient.urls'), name='patient'),
    path('pharmacy/', include('pharmacy.urls'), name='pharmacy'),
    path('logouttt', views.logouttt, name='logouttt'),
    path('logout10', views.logout10, name='logout10'),
    path('doctor/', include('doctor.urls'), name='doctor'),

    path('lab/', include('lab.urls'),name='lab'),
    path('approvelab/<int:id>', views.approvelab, name='approvelab'),

    path('approve/<int:id>', views.approve, name='approve'),
    path('approvep/<int:id>', views.approvep, name='approvep'),

    path('admin/', admin.site.urls),
]
