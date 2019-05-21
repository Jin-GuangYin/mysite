from django.db import models
from django.db.models.fields import exceptions
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from ckeditor_uploader.fields import RichTextUploadingField
from read_statistics.models import ReadNum, ReadNumExpandMethod, ReadDetail

#放到read_statistics.models里改名为ReadNumExpandMethod
# class Text():
#     def get_read_num(self):
#         ct = ContentType.objects.get_for_model(Blog)#等价于ct = ContentType.objects.get_for_model(self)
#         try:
#             readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)
#             return readnum.read_num 
#         except exceptions.ObjectDoesNotExist as e:
#             return 0


# Create your models here.
class BlogType(models.Model):
    type_name = models.CharField(max_length = 15)

    def __str__(self):
        return self.type_name


class Blog(models.Model,ReadNumExpandMethod):
    title = models.CharField(max_length = 50)
    blog_type = models.ForeignKey(BlogType, on_delete = models.DO_NOTHING)
    content = RichTextUploadingField()
    author = models.ForeignKey(User, on_delete = models.DO_NOTHING)
    #read_num = models.IntegerField(default=0)
    read_details = GenericRelation(ReadDetail)
    created_time = models.DateTimeField(auto_now_add = True)
    last_updated_time = models.DateTimeField(auto_now_add = True)
    is_deleted = models.BooleanField(False)

    #封装成Test抽象类
    # def get_read_num(self):
    #     ct = ContentType.objects.get_for_model(Blog)#等价于ct = ContentType.objects.get_for_model(self)
    #     try:
    #         readnum = ReadNum.objects.get(content_type=ct, object_id=self.pk)
    #         return readnum.read_num 
    #     except exceptions.ObjectDoesNotExist as e:
    #         return 0
        

    
    '''
    def get_read_num(self):
        try:
            return self.readnum.read_num
        except exceptions.ObjectDoesNotExist as e:
            return 0
    '''
        

    def __str__(self):
        return "<BLog: %s>" % self.title

    class Meta:
        ordering = ["-created_time"]
'''
class ReadNum(models.Model):
    read_num = models.IntegerField(default = 0)
    blog = models.OneToOneField(Blog, on_delete = models.DO_NOTHING)
'''