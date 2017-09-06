from inbot.models import oper_para
aa = oper_para.objects.all()
aa.delete()
s1 = oper_para(name = 'shtkey',content = '1bCAYb2AlqEMcDezraXYU3QepIvKXh9EOJxkfOfs2Yps')
s1.save()
s2 = oper_para(name = 'webhookparser',content = 'de37de5d2ea219a9a45de09b55b0729c')
s2.save()
s3 = oper_para(name = 'strapi',content = 'qzQbZczY8BaDBFUUMAKaznB9XIgkSZFkCHHX7V6dAayn5q2SzH39KbSGomm7qCwJWGUarAnHFrRV2ijZYl/vPq3AGqEY0s89hZRPQODfrf74JgCL5eVpMm8Fce5CkUZQ02jCDkoVCzC9lPF4yz27xgdB04t89/1O/w1cDnyilFU=')
s3.save()