import os
import json
from django.conf import settings as djangoSettings
from .utility import chkDict,CheckDialog,getGlShortUrl,writelog
import re
from .gspread import getGspData
from .models import oper_para

#fileroute = djangoSettings.STATIC_ROOT  + '\\'
#prefilename = 'bot\linemsg_'
fileroute = djangoSettings.FILE_ROUTE
prefilename = djangoSettings.PREFILENAME


def verifyEmail(stremail):
    import re
    if stremail.find(' ') != -1:
        return False
    if stremail.find('..') != -1:
        return False
    if re.match('^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$',stremail):
        return True
    else:
        return False

def chkEmail(mid):
    writelog('proc:chkEmail')
    EmailResultArr = getGspData(fields=['email'],layers={'L1':'email','L2':'mid','L0':''},purpose='detail',shtno='1',detailkey = mid)
    print (EmailResultArr)
    #writelog('EmailResultArr:' + EmailResultArr.text)
    if EmailResultArr[0]['querychk'] == 'ok':
        if len(EmailResultArr)>1:
            return EmailResultArr[1]['email']
        else:
            return 'err'
    else:
        return 'err'
	

def chkInvoiceKey(key):
    import re
    writelog('proc:chkInvoiceKey')
    z = re.match('[A-Za-z0-9_]*',key.upper())
    if z[0] == key.upper():
        return True
    else:
        return False

def getinvoicedata(bot_verification_code,email,total_amount,exe_time):
    def getinvoicetoken():
        import requests
        import json
        writelog('proc:getinvoicedata/getinvoicetoken')
        strurl = oper_para.objects.get(name='InvoiceSumUrl').content +  '/login/api-token-auth/'
        header= {
            "Content-Type":"application/json"
        }
        if exe_time == 'first':
            payload = {
                "username":oper_para.objects.get(name='invoicego_get_id').content,
                "password":oper_para.objects.get(name='invoicego_get_pw').content
            }
        else:    #second
            payload = {
                "username":oper_para.objects.get(name='invoicego_get_id_2').content,
                "password":oper_para.objects.get(name='invoicego_get_pw_2').content
            }


        res = requests.post(strurl,headers = header,data=json.dumps(payload))
        return res.json()['token']
    
    
    import requests
    import json
    writelog('proc:getinvoicedata')
    strurl = oper_para.objects.get(name='InvoiceSumUrl').content + '/invoice/invoice-taker-bot/'
    token = getinvoicetoken()
    #print (str(token))
    header = {
        "Content-Type":"application/json",
        "Authorization":"JWT " + str(token)
    }
    payload = {
        "bot_verification_code":bot_verification_code,
        "email":email,
        "total_amount":total_amount
    }
    try:
        res = requests.post(strurl,headers = header ,data=json.dumps(payload))
        print (res.text)
        writelog('ok')
        #return res.json()['rtn_cd'],res.json()['invoice_number'],res.json()['random_number'],res.json()['total_amount'],res.json
        return res.json()
    except:
        writelog('getinvoicedata api error')

def getInvoice(mid,exe_time):
    filename = prefilename + mid
    filepath = fileroute +  filename
    InvoiceKey = ''
    Amount = 0
    
    if CheckDialog(mid):
        with open(filepath) as json_data:
            data= json.load(json_data)
            InvoiceKey = data['step1']['ask'].upper()
            amount = data['step2']['ask']
            email = chkEmail(mid)
            invoicedata = getinvoicedata(InvoiceKey,email,amount,exe_time)
            try:
                return invoicedata
            except:
                json.loads({'rtn_cd':'sys err','detail':'系統有誤，請通知人工客服'})        
    else:
        #eturn 'err','err','err'
        json.loads({'rtn_cd':'err','detail':'您的操作順序錯誤，請重新操作一次'})

def PrintResultWord(invoiceinfo):

    #url = oper_para.objects.get(name='InvoiceSumUrl').content + '?carrier_id={}&account={}&company={}'.format(invoiceinfo['carrier_id'],invoiceinfo['account'],invoiceinfo['company'])
    url = 'https://www.invoicego.tw/carriermgt/' + '?carrier_id={}&account={}&company={}'.format(invoiceinfo['carrier_id'],invoiceinfo['account'],invoiceinfo['company'])
     


    resultstr1 = u'您的發票已經順利成立，\n'
    resultstr1 = resultstr1 + u'發票號碼：{}\n'.format(invoiceinfo['invoice_number'])
    resultstr1 = resultstr1 + u'金額：{}\n'.format(invoiceinfo['total_amount'])
    resultstr1 = resultstr1 + u'隨機碼：{}\n'.format(invoiceinfo['random_number'])

    resultstr2 = u'如果發票中獎，本公司將寄信通知您，並於開獎翌日起十日內，將中獎發票寄信通知您做兌獎使用'
    resultstr3 = u'建議您完成歸戶，您即可在財政部電子發票整合服務平台查詢您所有的電子發票'
    resultstr4 = u'可點選以下連結完成歸戶作業,' + getGlShortUrl(url)

    return resultstr1,resultstr2,resultstr3,resultstr4

def PrintResultWordB2B(invoiceinfo):
    resultstr1 = u'您的發票已經順利成立，\n'
    resultstr1 = resultstr1 + u'發票號碼：{}\n'.format(invoiceinfo['invoice_number'])
    resultstr1 = resultstr1 + u'銷售額總額：{}\n'.format(invoiceinfo['sales_amount'])
    resultstr1 = resultstr1 + u'營業稅：{}\n'.format(invoiceinfo['tax_amount'])
    resultstr1 = resultstr1 + u'總計：{}\n'.format(invoiceinfo['total_amount'])

    resultstr2 = u'請記得至電子信箱列印該張進項發票，並交由稅務會計事務所抵扣當期營業稅，謝謝!'

    return resultstr1,resultstr2




    '''
    您的發票已經順利成立，
發票號碼：XF63515952
發票總金金額：8688元
隨機碼：0234
如果發票中獎，本公司將寄信通知您，並於開獎翌日起十日內，將中獎發票寄信通知您
並掛號郵寄給您做兌獎使用。
建議您完成歸⼾戶，您即可在財政部電子發票整合服務平台查詢您所有的電子發票
'''







