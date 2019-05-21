import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail


def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)

    if not request.COOKIES.get(key):
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        #等价于下文的if.else.判断详情参照官网文档
        # if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():
        #     readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk)
        # else:
        #     readnum = ReadNum(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        date = timezone.now().date()
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        # if ReadDetail.objects.filter(content_type=ct, object_id=obj.pk, date=date).count(): #存在则取到
        #     readDetail = ReadDetail.objects.get(content_type=ct, object_id=obj.pk, date=date)
        # else:#不存在则创建
        #     readDetail = ReadDetail(content_type=ct, object_id=obj.pk,date=date)
        readDetail.read_num += 1
        readDetail.save()
    return key

def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    read_nums = []
    dates = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_details = ReadDetail.objects.filter(content_type=content_type, date = date)
        result = read_details.aggregate(read_num_sum = Sum('read_num'))#aggregate其聚合函数返回一个字典key为read_num_sum
                                                                      #value为对相应属性求得到sum
        read_nums.append(result["read_num_sum"] or 0)
    return dates, read_nums

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date = today).order_by('-read_num')
    return read_details[:7]#切片器取前七条

def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    date = today - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type, date = date).order_by('-read_num')
    return read_details[:7]#切片器取前七条

# def get_7_hot_data(content_type):
#     today = timezone.now().date()
#     date = today - datetime.timedelta(days=7)
#     read_details = ReadDetail.objects \
#                              .filter(content_type=content_type, date = date) \
#                              .values('content_type', 'object_id') \
#                              .annotate(read_num_sum = Sum("read_num")) \
#                              .order_by('-read_num')
#                              #等价于.values("content_object")
#                              #先分组group再求和
#     return read_details[:7]
#     
#     
