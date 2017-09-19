from inbot.models import oper_para

def GetPay2GoInfo(Amt='',OrderNo='',TimeStamp=''):
    import hashlib
    MerchantID = oper_para.objects.get(name='MerchantID').content
    HashKey = oper_para.objects.get(name='HashKey').content
    HashIV = oper_para.objects.get(name='HashIV').content
    ReturnURL = oper_para.objects.get(name='HookBackURL').content + '/order/ReturnPay2Go'
    line = 'HashKey={}&Amt={}&MerchantID={}&MerchantOrderNo={}&TimeStamp={}&Version=1.2&HashIV={}'.format(HashKey,Amt,MerchantID,OrderNo,TimeStamp,HashIV)
    #line = 'HashKey=NM9pCGBH6cekcJg1738DyoEEAhBqrSle&Amt=93&MerchantID=MS12338986&MerchantOrderNo=1505147507&TimeStamp=1505147507&Version=1.2&HashIV=FvDhbfZisdCEWSG3'
    ax = line.encode('utf-8')
    m = hashlib.sha256(ax).hexdigest().upper()
    return m,MerchantID,ReturnURL