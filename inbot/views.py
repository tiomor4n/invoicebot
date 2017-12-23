from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render
from linebot import LineBotApi, WebhookHandler,WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
from django.views.decorators.csrf import csrf_exempt
import os
from django.conf import settings as djangoSettings
import tempfile
import requests
import json
from .utility import ReadFromStaticBOT,WriteToStaticBOT,CheckStep,CheckDialog,RemoveDialog,isfloat,isint,writelog,readlog,clearlog,getGlShortUrl
from .invoice import chkEmail,chkInvoiceKey,getInvoice,PrintResultWord,verifyEmail,PrintResultWordB2B
from .gspread import WriteMidEmail,getGspData
from .models import oper_para






@csrf_exempt
def callback(request):
    import sys
    sys.setdefaultencoding='utf8'
    def getpara():
        strapi = oper_para.objects.get(name='strapi').content
        strparser = oper_para.objects.get(name='webhookparser').content

        return strapi,strparser


    def LineMsgOut(mid,message):
        sendmsgstr = '{"events":[{"source":{"userId":"' + mid + '"},"message":{"text":"'+ message + '"}}]}'
        WriteToStaticBOT(sendmsgstr,"reply")
        



    import json
    import requests

    def getMessageTextarr(action=[]):
        resultarr=[]
        for ar in action:
            resultarr.append(
                MessageTemplateAction(
                    label=ar,
                    text=ar
                )
            )
        print ('resultarr len:' + str(len(resultarr)))
        return resultarr


    def getParameter(purpose):
        purposedict = {
        'start':[u'領取發票',u'人工客服']
        #'option':[u'特惠商品',u'支付設定',u'測試功能']

        #'start':getGspData(fields=['functionstart'],layers={'L1':'functionstart','L2':'functionoption','L0':''},purpose='L1',shtno='4'),
        #'option':getGspData(fields=['functionoption'],layers={'L1':'functionstart','L2':'functionoption','L0':''},purpose='L2',shtno='4'),
        #'startdict':getGspData(fields=['functionoption','imgururl'],layers={'L1':'functionstart','L2':'functionoption','L0':''},purpose='L2',shtno='4',detailkey=u'領取發票')
        }
        #print (getGspData(fields=['functionoption','imgururl'],layers={'L1':'functionstart','L2':'functionoption','L0':''},purpose='detail',shtno='4',detailkey=u'領取發票'))
        return purposedict[purpose]


    def getDispname(event):
        if isinstance(event,MessageEvent):
            if isinstance(event.source,SourceUser):
                profile = line_bot_api.get_profile(event.source.user_id)
                dispname = profile.display_name
            else:
                dispname = u'使用者'

            return dispname

    def getButtontempText(titlestr='',textstr='',action=[]):
        actionarr = getMessageTextarr(action)
        button_template_result = TemplateSendMessage(
            alt_text=u'此功能僅限手機用戶使用',
            template=ButtonsTemplate(
                title=titlestr,
                text=textstr,
                actions=actionarr
            )
        )
        return button_template_result

    def getinvoiceTempArr(titlestr='',textstr='',action=[],imgurl=''):
        #http://qr-official.line.me/L/79A3UsYT5G
        actionarr=[]
        actionarr.append(
            MessageTemplateAction(
                label= ' ',
                text=' '
            )
        )
        actionarr.append(
            MessageTemplateAction(
                label=action[0],
                text=action[0]
            )
        )
        actionarr.append(
            URITemplateAction(
                label=action[1],
                uri=oper_para.objects.get(name='customer_service').content
                )
            )
        

        returnCcolumn = CarouselColumn(
                title = titlestr,
                text = textstr,
                thumbnail_image_url = imgurl,
                actions=actionarr
            )
        return returnCcolumn

    def getCcolumnTextArr(titlestr='',textstr='',action=[],imgurl='',addempty=False,resultarr=[]):
        actionarr=getMessageTextarr(action)
        if addempty==True:
            actionarr.append(
                MessageTemplateAction(
                    label='  ',
                    text='  '
                )
            )
        if imgurl != '':
            returnCcolumn = CarouselColumn(
                title = titlestr,
                text = textstr,
                thumbnail_image_url = imgurl,
                actions=actionarr
            )
        else:
            returnCcolumn = CarouselColumn(
                title = titlestr,
                text = textstr,
                actions=actionarr
            )
        resultarr.append(returnCcolumn)

        return resultarr

    strapi, strparser = getpara()

    def EndDialog(mid,event):
        if CheckDialog(mid):
            RemoveDialog(mid)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=u'我無法辨識您的輸入，建議您從下方選單選擇開始流程'),
        )

 
    def ReplyForInvoice(x):
        print('from def')
        if x['rtn_cd'] == '400':
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=u'您輸入的email有誤，請洽客服人員修正')
                )
        elif x['rtn_cd'] == '200':
            if x['random_number'] is not None:
                str1,str2,str3,str4 = PrintResultWord(x)
                line_bot_api.reply_message(
                    event.reply_token,
                    [TextSendMessage(text=str1),
                    TextSendMessage(text=str2),
                    TextSendMessage(text=str3),
                    TextSendMessage(text=str4),
                    StickerSendMessage(package_id='1',sticker_id='2')
                    ]
                )
            else:
                str1,str2 = PrintResultWordB2B(x)
                line_bot_api.reply_message(
                    event.reply_token,
                    [TextSendMessage(text=str1),
                    TextSendMessage(text=str2)
                    ]
                )

        else:     #500，會檢查第二次
            if last_reply == 'input transaction amount':   #第二次
                LineMsgOut (mid,u'can not get invoice data')
                x = getInvoice(mid,'second')
                if x['rtn_cd'] == '400':
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=u'您輸入的email有誤，請洽客服人員修正')
                )
                elif x['rtn_cd'] == '200':
                    if x['random_number'] is not None:
                        str1,str2,str3,str4 = PrintResultWord(x)
                        line_bot_api.reply_message(
                            event.reply_token,
                            [TextSendMessage(text=str1),
                            TextSendMessage(text=str2),
                            TextSendMessage(text=str3),
                            TextSendMessage(text=str4),
                            StickerSendMessage(package_id='1',sticker_id='2')
                            ]
                        )
                    else:
                        str1,str2 = PrintResultWordB2B(x)
                        line_bot_api.reply_message(
                            event.reply_token,
                            [TextSendMessage(text=str1),
                            TextSendMessage(text=str2)
                            ]
                        )


                else:    #第二次還錯
                    writelog (u'call get invoice api bad response:' + x['detail'])
                    print (str(oper_para.objects.get(name='is_public').content))
                    if str(oper_para.objects.get(name='is_public').content)== 'True':
                        line_bot_api.reply_message(
                            event.reply_token,
                            [TextSendMessage(text='您輸入的資料發生以下錯誤:' + x['detail'] + '。請確認您的輸入資訊是否正確，如確認無誤請點選以下連結與我們的人工客服聯繫'),
                                TextSendMessage(text=getGlShortUrl(oper_para.objects.get(name='customer_service').content))
                            ]
                        )
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=x['detail']),
                        )


    line_bot_api = LineBotApi(strapi)
    parser = WebhookParser(strparser)   
    username = '' 
    templatearr = []


    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        #print body
        jdata = json.loads(body)
        mid = jdata['events'][0]['source']['userId']
        events = None
        writelog('mid:' + mid)
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                if isinstance(event.message,TextMessage):
                    print (event.reply_token)
                    username = getDispname(event)
                    
                    if event.message.text == u'開始使用':
                        if CheckDialog(mid):
                            RemoveDialog(mid)
                        print('start')
                        invoicearr = getParameter('start')
                        #parr = getParameter('option')
                        #print (str(parr))
                        titlestr = username + u'你好!'
                        textstr = u'請從下方選單選擇您要使用的功能'
                        textstr2 = u'請選擇其他功能'

                        templatearr.append(getinvoiceTempArr(titlestr=titlestr,textstr=textstr,action=invoicearr,imgurl = 'https://i.imgur.com/LLlLlPi.jpg'))
                        #send_template = getButtontempText(titlestr = titlestr,textstr = textstr,action=parr)
                        
                        #if len(parr)<=2:
                        #    send_template_Ccolumn = getCcolumnTextArr(titlestr = titlestr,textstr = textstr2,imgurl='https://i.imgur.com/RLCzuKI.jpg',action=parr[0:2],resultarr=templatearr,addempty=True)
                        #elif len(parr) == 3:
                        #    send_template_Ccolumn = getCcolumnTextArr(titlestr = titlestr,textstr = textstr2,imgurl='https://i.imgur.com/RLCzuKI.jpg',action=parr,resultarr = templatearr)
                        #elif len(parr) == 4:
                        #    send_template_Ccolumn = getCcolumnTextArr(titlestr = titlestr,textstr = textstr2,imgurl='https://i.imgur.com/RLCzuKI.jpg',action=parr[0:2],resultarr=templatearr)
                        #    send_template_Ccolumn2 = getCcolumnTextArr(titlestr = titlestr,textstr = textstr2,imgurl='https://i.imgur.com/RLCzuKI.jpg',action=parr[2:4],resultarr=templatearr)
                        #elif len(parr) == 5:
                        #    send_template_Ccolumn = getCcolumnTextArr(titlestr = titlestr,textstr = textstr2,imgurl='https://i.imgur.com/RLCzuKI.jpg',action=parr[0:3],resultarr=templatearr)
                        #    send_template_Ccolumn = getCcolumnTextArr(titlestr = titlestr,textstr = textstr2,imgurl='https://i.imgur.com/RLCzuKI.jpg',action=parr[3:5],resultarr=templatearr,addempty=True)
                        


                        send_template = TemplateSendMessage(
                                alt_text=u'此功能僅限手機用戶使用',
                                template=CarouselTemplate(
                                    columns = templatearr
                                    )
                            )
                        line_bot_api.reply_message(event.reply_token, send_template)


                    elif event.message.text == u'領取發票':
                        print ('get invoice')
                        writelog('get invoice')
                        if CheckDialog(mid):
                            RemoveDialog(mid)
                        WriteToStaticBOT(body,"ask")
                        purporse,step,last_ask,last_reply,timestamp = CheckStep(mid)
                        if chkEmail(mid) != 'err':
                            line_bot_api.reply_message(
                                event.reply_token, 
                                TextSendMessage(text=u'請點擊下方的鍵盤，輸入您的正確4碼英文數字領取金鑰'),
                            )
                            LineMsgOut(mid = mid,message = 'input invoice key')
                            #有email,正常流程
                        else:
                            #沒有email,要卡在這邊
                            WriteToStaticBOT(body,"ask")
                            line_bot_api.reply_message(
                                event.reply_token, 
                                TextSendMessage(text=u'請點擊下方的鍵盤，輸入您的正確email，以利中獎時我們能通知到您'),
                            )
                            LineMsgOut(mid = mid,message = 'input email')


                    elif event.message.text == u'特惠商品':
                        if chkEmail(mid) != 'err':
                            writelog(u'step:特惠商品')
                            image_carousel_template = ImageCarouselTemplate(columns=[
                                ImageCarouselColumn(image_url='https://i.imgur.com/My1DjdX.jpg',
                                    action = URITemplateAction(
                                         label=u'新增',
                                         uri=oper_para.objects.get(name='HookBackURL').content + '/order/SendPay2Go'
                                        )
                                    ),

                                ImageCarouselColumn(image_url='https://i.imgur.com/N0grLic.png',
                                    action=MessageTemplateAction(
                                        label=u'下單',
                                        text=u'下單'))
                            ])
                            template_message = TemplateSendMessage(
                                alt_text='ImageCarousel alt text', template=image_carousel_template)
                            line_bot_api.reply_message(event.reply_token, template_message)
                        else:
                            WriteToStaticBOT(body,"ask")
                            line_bot_api.reply_message(
                                event.reply_token, 
                                TextSendMessage(text=u'請點擊下方的鍵盤，輸入您的正確email，以利能通知您交易相關資訊'),
                            )
                            LineMsgOut(mid = mid,message = 'input email')

                        


                    elif event.message.text == u'支付設定':
                        writelog(u'step:支付設定')
                        line_bot_api.reply_message(
                                event.reply_token, 
                                TextSendMessage(text=u'此功能還在開發中'),
                            )
                        RemoveDialog()

                    elif event.message.text == u'測試功能':
                        writelog(u'step:測試功能')
                        line_bot_api.reply_message(
                                event.reply_token, 
                                TextSendMessage(text=u'此功能還在開發中'),
                            )
                        RemoveDialog()



                    elif len(event.message.text) == 4 and chkInvoiceKey(event.message.text):
                        if CheckDialog(mid):
                            WriteToStaticBOT(body,"ask")
                            purporse,step,last_ask,last_reply,timestamp = CheckStep(mid)
                            print (last_reply)
                            if last_reply == 'input invoice key':
                                print (u'進入輸入金額流程')
                                writelog(u'step:input transaction amount')
                                line_bot_api.reply_message(
                                     event.reply_token,
                                     TextSendMessage(text=u'請輸入本次消費金額'),
                                )
                                LineMsgOut(mid,u'input transaction amount')
                            elif last_reply == 'input transaction amount':
                                print (u'call get invoice api')
                                writelog (u'call get invoice api')
                                x = getInvoice(mid,'first')
                                ReplyForInvoice(x)
                                LineMsgOut(mid,u'finish')
                                RemoveDialog(mid)
                            else:
                                EndDialog(mid,event)
                        else:
                            EndDialog(mid,event)

                    elif isint(event.message.text):
                        if CheckDialog(mid):
                            WriteToStaticBOT(body,"ask")
                            purporse,step,last_ask,last_reply,timestamp = CheckStep(mid)
                            print (last_reply)
                            if last_reply == 'input transaction amount':
                                print (u'進入確認發票流程')
                                writelog (u'call get invoice api')
                                x = getInvoice(mid,'first')
                                ReplyForInvoice(x)
                                LineMsgOut(mid,u'finish')
                                RemoveDialog(mid)
                            else:
                                EndDialog(mid,event)
                        else:
                            EndDialog(mid,event)

                    elif verifyEmail(event.message.text):
                        if CheckDialog(mid):
                            WriteToStaticBOT(body,"ask")
                            purporse,step,last_ask,last_reply,timestamp = CheckStep(mid)
                            print (last_reply)
                            if last_reply == 'input email':
                                writelog (u'input email')
                                WriteMidEmail(mid,event.message.text)
                                line_bot_api.reply_message(
                                        event.reply_token,
                                        TextSendMessage(text=u'您的email輸入成功，請從下方選單開始使用此機器人'),
                                    )
                                LineMsgOut(mid,u'finish')
                                RemoveDialog(mid)
                            else:
                                EndDialog(mid,event)
                        else:
                            EndDialog(mid,event)



                    else:
                        EndDialog(mid,event)


                    '''
                    elif event.message.text == u'我要下定單':
                        print ('order')
                        carousel_template = TemplateSendMessage(
                            alt_text=u'此功能僅限手機用戶使用',
                            template=CarouselTemplate(

                            columns=[
                                CarouselColumn(
                                    title='選擇商品',
                                    text='商品名稱1',
                                    thumbnail_image_url='https://i.imgur.com/RLCzuKI.jpg',
                                    actions=[
                                    MessageTemplateAction(
                                        label=u'下單',
                                        text=u'下單'
                                    ),
                                    MessageTemplateAction(
                                        label=u'說明連結',
                                        text=u'連結'
                                    )
                                ]
                            ),
                                CarouselColumn(
                                    title='選擇商品',
                                    text='商品名稱2',
                                    thumbnail_image_url='https://i.imgur.com/RLCzuKI.jpg',
                                    actions=[
                                    MessageTemplateAction(
                                        label=u'下單',
                                        text=u'下單'
                                    ),
                                    MessageTemplateAction(
                                        label=u'說明連結',
                                        text=u'連結'
                                    )
                                   
                                ]
                            )
                        ]
                        )
                    )
                        buttons_template = TemplateSendMessage(
                             alt_text='訂單服務tmplate',
                             template=ButtonsTemplate(
                             title='選擇物品',
                             text='請選擇',
                             thumbnail_image_url='https://i.imgur.com/xQF5dZT.jpg',
                             actions=[
                                        MessageTemplateAction(
                                        label='下單',
                                        text='下單'
                                        ),
                                        MessageTemplateAction(
                                        label='連結',
                                        text='連結'
                                        ),
                                        
                                    ]
                                )
                            )
                        line_bot_api.reply_message(event.reply_token, carousel_template)
                    

                    

                    
                    else:
                        if CheckDialog(mid):
                            RemoveDialog(mid)
                        line_bot_api.reply_message(
                                     event.reply_token,
                                     TextSendMessage(text=u'我無法辨識您的輸入，可能您閒置太久，建議您從下方選單重新開始輸入'),
                                )
                    '''

                   
                elif isinstance(event.message,ImageMessage):
                    print ('image event')
                    ext = 'png'
                    #static_tmp_path = '.' + djangoSettings.STATIC_URL
                    static_tmp_path = 'D:\\bot_temp'
                    print (static_tmp_path)
                    message_content = line_bot_api.get_message_content(event.message.id)
                    print ('1-1')
                    file = open(static_tmp_path + '\\tmp.png','wb')
                    for chunk in message_content.iter_content():
                        #print ('1')
                        file.write(chunk)
                    file.close()

                    
                    files = {'file': open(static_tmp_path + '\\tmp.png', 'rb')}
                    res = requests.post(url='http://api.qrserver.com/v1/read-qr-code/',files=files)
                    jdata = json.loads(res.text)
                    qrdecode=jdata[0]['symbol'][0]['data'] 
                    print (qrdecode)
                    line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text=qrdecode),
                        )




                  

        return HttpResponse()

    if request.method == 'GET':
        print ('from get')
        return HttpResponse('from get')

@csrf_exempt
def checklog(request):
    return HttpResponse(readlog())

@csrf_exempt
def refreshlog(request):
    return HttpResponse(clearlog())