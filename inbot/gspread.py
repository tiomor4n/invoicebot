import json
import requests
from bs4 import BeautifulSoup as bs
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from django.conf import settings as djangoSettings
from .models import oper_para 


#https://github.com/burnash/gspread
def GetGsht():
    

    fileroute = djangoSettings.FILE_ROUTE
    scope = ['https://spreadsheets.google.com/feeds']
    
    credentials = ServiceAccountCredentials.from_json_keyfile_name(fileroute + 'auth.json', scope)
    gc = gspread.authorize(credentials)
    sht1 = gc.open_by_key(oper_para.objects.get(name='shtkey').content)
    

    return sht1



def WriteMidEmail(mid,email):
    from datetime import datetime as dt
    nowstr = dt.now().strftime('%Y/%m/%d %H:%M:%S')
    sht1 = GetGsht()
    sht12 = sht1.get_worksheet(0)
    #acnt = len(sht12.col_values(1))-1000
    sht12.append_row([mid,email])
    return 'ok'



def getGspData(fields=[],layers={},purpose='',shtno='1' ,detailkey=''):
    arr=[]
    aa ={}
    querychk={}
    sheetid = oper_para.objects.get(name='shtkey').content
    #fieldarr = ['authorize']
    #layerdic = {'L1':'functionstart','L2':'functionoption','L0':''}
    fieldarr = fields
    layerdic = layers
    
    def checkquery(jsondata):
        try:
            ax = jsondata['feed']['entry']
            return 'ok'
        except KeyError:
            return 'error'
        
    
    def getLayer(jsondata,L):
        qcheck = {}
        resultarr = []
        L1str = 'gsx$' + layerdic[L]
        try:
            ax = jsondata['feed']['entry']
            for en in ax:
                resultarr.append(en[L1str]['$t'])
            resultarr = list(set(resultarr))
            return resultarr
        except:
            resultarr.append('error')
            return resultarr
        
    def getDetail(jsondata,L2):
        resultarr = []
        try:
            if checkquery(jsondata) == 'ok':
                querychk['querychk'] = 'ok'
                resultarr.append(querychk)
                for en in jsondata['feed']['entry']:
                    aa = {}
                    if en['gsx$' + layerdic['L2']]['$t'] == L2:
                        for fi in fieldarr:
                            fieldstr = 'gsx$' + fi
                            aa[fi] = en[fieldstr]['$t']
            
                        resultarr.append(aa)
            
    
            else:
                querychk['querychk'] = 'err'
                resultarr.append(querychk)
            return resultarr
        except:
            querychk['querychk'] = 'err'
            reultarr.append(querychk)
            return arr
        
        
    
    res = requests.get('https://spreadsheets.google.com/feeds/list/{}/{}/public/values?alt=json'.format(sheetid,shtno))
    jsondata =json.loads(res.text)

    if purpose == 'L0':
        return getLayer(jsondata,'L0')
    elif purpose == 'L1':
        return getLayer(jsondata,'L1')
    elif purpose == 'L2':
        return getLayer(jsondata,'L2')
    elif purpose == 'detail':
        return getDetail(jsondata,detailkey)
    else:
        return ['err']