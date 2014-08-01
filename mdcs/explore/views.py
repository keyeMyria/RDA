################################################################################
#
# File Name: views.py
# Application: explore
# Description:   
#
# Author: Sharief Youssef
#         sharief.youssef@nist.gov
#
#         Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext, loader
from django.shortcuts import redirect
from datetime import date
from mongoengine import *
from mgi.models import Template

def currentYear():
    return date.today().year

################################################################################
#
# Function Name: index(request)
# Inputs:        request - 
# Outputs:       Data Exploration homepage
# Exceptions:    None
# Description:   renders the main data exploration home page from template 
#                (index.html)
#
################################################################################
def index(request):
    template = loader.get_template('explore.html')
    request.session['currentYear'] = currentYear()
    if request.user.is_authenticated():
        connect('mgi')

        context = RequestContext(request, {
                'templates': Template.objects,
                })
        return HttpResponse(template.render(context))
    else:
        if 'loggedOut' in request.session:
            del request.session['loggedOut']
        request.session['next'] = '/explore'
        return redirect('/login')

