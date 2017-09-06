import os
import json
from django.conf import settings as djangoSettings
from .utility import chkDict,CheckDialog
import re
from .gspread import getGspData

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

def chkEmail(stremail):
    chkarr = getGspData(['email'],{'L1':'','L2':'mid','L0':''},'L2')
    if stremail in chkarr:
        return True
    else:
        return False


	

def chkInvoiceKey(key,amount):
    import re
    if key == 'ABCD':
        return True
    else:
        return False

def getInvoice(mid):
    filename = prefilename + mid
    filepath = fileroute +  filename
    InvoiceKey = ''
    Amount = 0
    
    if CheckDialog(mid):
        with open(filepath) as json_data:
            data= json.load(json_data)
            InvoiceKey = data['step1']['ask']
            amount = data['step2']['ask']
            if chkInvoiceKey(InvoiceKey,Amount):
                return 'XF63515952','8688','0234'
            else:
                return 'err','err','err' 

    else:
        return 'err','err','err'

def PrintResultWord(invoiceno='',amount='',randomcode=''):
    resultstr1 = u'您的發票已經順利成立，\n'
    resultstr1 = resultstr1 + u'發票號碼：{}\n'.format(invoiceno)
    resultstr1 = resultstr1 + u'金額：{}\n'.format(amount)
    resultstr1 = resultstr1 + u'隨機碼：{}\n'.format(randomcode)

    resultstr2 = u'如果發票中獎，本公司將寄信通知您，並於開獎翌日起十日內，將中獎發票寄信通知您做兌獎使用'
    resultstr3 = u'建議您完成歸戶，您即可在財政部電子發票整合服務平台查詢您所有的電子發票'

    return resultstr1,resultstr2,resultstr3


    '''
    您的發票已經順利成立，
發票號碼：XF63515952
發票總金金額：8688元
隨機碼：0234
如果發票中獎，本公司將寄信通知您，並於開獎翌日起十日內，將中獎發票寄信通知您
並掛號郵寄給您做兌獎使用。
建議您完成歸⼾戶，您即可在財政部電子發票整合服務平台查詢您所有的電子發票
'''

    




