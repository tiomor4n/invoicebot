from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render,render_to_response,redirect
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings as djangoSettings
import tempfile
import requests
import json
from .utility import GetPay2GoInfo
from inbot.utility import GetTimeStamp
#from .invoice import chkEmail,chkInvoiceKey,getInvoice,PrintResultWord,verifyEmail
#from .gspread import WriteMidEmail
from inbot.models import oper_para

# Create your views here.
@csrf_exempt
def SendPay2Go(request):
	NowTimestamp = str(GetTimeStamp())
	OrderNoStr = str(NowTimestamp) + '0001'
	AmtStr = str(97)
	ItemStr = 'test item'
	EmailStr = 'rodesmao@gmail.com'
	CheckValue,MerchantID,ReturnURL = GetPay2GoInfo(Amt=AmtStr,OrderNo=OrderNoStr,TimeStamp=NowTimestamp)
	print (CheckValue)
	Pay2GoInfo = {'MerchantID':MerchantID,'CheckValue':CheckValue,'TimeStamp':NowTimestamp,'MerchantOrderNo':OrderNoStr,'Amt':AmtStr,'ItemDesc':ItemStr,'Email':EmailStr,'ReturnURL':ReturnURL}
	return render_to_response('SendPay2Go.html',locals())
    #return HttpResponse('ok')	


@csrf_exempt
def ReturnPay2Go(request):
    if request.method == 'POST':
        JSONData = request.POST['JSONData']
        JData = json.loads(JSONData)
        Status = JData['Status']
        Message = JData['Message']
        Result =  json.loads(JData['Result'])
        
        OrderNoStr = Result['MerchantOrderNo']
        Amt = Result['Amt']

        Pay2GoReturnInfo = {'MerchantOrderNo':OrderNoStr,'Amt':Amt }

    return render_to_response('ReturnPay2Go.html',locals())

@csrf_exempt
def NotifyPay2Go(request):
    if request.method == 'POST':
        JSONData = request.POST['JSONData']
        JData = json.loads(JSONData)
        Status = JData['Status']
        Message = JData['Message']
        Result =  json.loads(JData['Result'])
        
        OrderNoStr = Result['MerchantOrderNo']
        Amt = Result['Amt']

        Pay2GoReturnInfo = {'MerchantOrderNo':OrderNoStr,'Amt':Amt }

    return render_to_response('ReturnPay2Go.html',locals())