import os
import json
from django.conf import settings as djangoSettings
from .utility import chkDict,CheckDialog,getGlShortUrl
import re
from .gspread import getGspData
from .models import oper_para

#fileroute = djangoSettings.STATIC_ROOT  + '\\'
#prefilename = 'bot\linemsg_'
fileroute = djangoSettings.FILE_ROUTE
prefilename = djangoSettings.PREFILENAME


def verifyEmail(stremail):
    import re
    if re.match('^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$',stremail):
        return True
    else:
        return False

def chkEmail(mid):
    EmailResultArr = getGspData(fields=['email'],layers={'L1':'email','L2':'mid','L0':''},purpose='detail',shtno='1',detailkey = mid)
    print (EmailResultArr)
    if EmailResultArr[0]['querychk'] == 'ok':
        if len(EmailResultArr)>1:
            return EmailResultArr[1]['email']
        else:
            return 'err'
    else:
        return 'err'
	

def chkInvoiceKey(key):
    import re
    z = re.match('[A-Za-z0-9_]*',key.upper())
    if z[0] == key.upper():
        return True
    else:
        return False

def getinvoicedata(bot_verification_code,email,total_amount):
    def writelog(logstr):
        import logging
        logger = logging.getLogger('mylogger')  
        logger.setLevel(logging.DEBUG)  
        fh = logging.FileHandler('test.log')  
        fh.setLevel(logging.DEBUG)  
        ch = logging.StreamHandler()  
        ch.setLevel(logging.DEBUG)  
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')  
        fh.setFormatter(formatter)  
        ch.setFormatter(formatter)  
        logger.addHandler(fh)  
        logger.addHandler(ch)  
        logger.info(logstr) 
        
    def getinvoicetoken():
        import requests
        import json
        strurl = 'http://api-uat.invoicego.tw/login/api-token-auth/'
        header= {
            "Content-Type":"application/json"
        }
        payload = {
            "username":oper_para.objects.get(name='invoicego_get_id').content,
            "password":oper_para.objects.get(name='invoicego_get_pw').content
        }
        res = requests.post(strurl,headers = header,data=json.dumps(payload))
        return res.json()['token']
    
    
    import requests
    import json
    strurl = 'http://api-uat.invoicego.tw/invoice/invoice-taker-bot/'
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
        writelog('error')

def getInvoice(mid):
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
            invoicedata = getinvoicedata(InvoiceKey,email,amount)
            try:
                return invoicedata
            except:
                json.loads({'rtn_cd':'sys err','detail':'系統有誤，請通知人工客服'})        
    else:
        #eturn 'err','err','err'
        json.loads({'rtn_cd':'err','detail':'您的操作順序錯誤，請重新操作一次'})

def PrintResultWord(invoiceinfo):

    url = oper_para.objects.get(name='InvoiceSumUrl').content + '?carrier_id={}&account={}&company={}'.format(invoiceinfo['carrier_id'],invoiceinfo['account'],invoiceinfo['company'])


    resultstr1 = u'您的發票已經順利成立，\n'
    resultstr1 = resultstr1 + u'發票號碼：{}\n'.format(invoiceinfo['invoice_number'])
    resultstr1 = resultstr1 + u'金額：{}\n'.format(invoiceinfo['total_amount'])
    resultstr1 = resultstr1 + u'隨機碼：{}\n'.format(invoiceinfo['random_number'])

    resultstr2 = u'如果發票中獎，本公司將寄信通知您，並於開獎翌日起十日內，將中獎發票寄信通知您做兌獎使用'
    resultstr3 = u'建議您完成歸戶，您即可在財政部電子發票整合服務平台查詢您所有的電子發票'
    resultstr4 = u'可點選以下連結完成歸戶作業,' + getGlShortUrl(url)

    return resultstr1,resultstr2,resultstr3,resultstr4


    '''
    您的發票已經順利成立，
發票號碼：XF63515952
發票總金金額：8688元
隨機碼：0234
如果發票中獎，本公司將寄信通知您，並於開獎翌日起十日內，將中獎發票寄信通知您
並掛號郵寄給您做兌獎使用。
建議您完成歸⼾戶，您即可在財政部電子發票整合服務平台查詢您所有的電子發票
'''







