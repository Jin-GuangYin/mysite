from django.db import models
from django.db.models.fields import exceptions
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


# Create your models here.
class ReadNum(models.Model):
    read_num = models.IntegerField(default = 0)

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)#绑定的模型
    object_id = models.PositiveIntegerField()#绑定模型某个对象的主键值
    content_object = GenericForeignKey('content_type', 'object_id')#将两者组成一个更通用的外键

class ReadNumExpandMethod(object):
    def get_read_num(self):
        ct = ContentType.objects.get_for_model(self)
        try:
            readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)
            return readnum.read_num 
        except exceptions.ObjectDoesNotExist as e:
            return 0

class ReadDetail(models.Model):
    date = models.DateField(default=timezone.now)
    read_num = models.IntegerField(default = 0)

    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)#绑定的模型
    object_id = models.PositiveIntegerField()#绑定模型某个对象的主键值
    content_object = GenericForeignKey('content_type', 'object_id')#将两者组成一个更通用的外键
