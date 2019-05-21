from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

# Create your models here.
class Comment(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)#绑定的模型
    object_id = models.PositiveIntegerField()#绑定模型某个对象的主键值
    content_object = GenericForeignKey('content_type', 'object_id')#将两者组成一个更通用的外键
    
    text = models.TextField()
    comment_time = models.DateField(auto_now_add = True)
    user = models.ForeignKey(User, related_name="comments", on_delete = models.DO_NOTHING)
    #此user指此条评论的作者 不能为空，既然有这条评论 那就肯定有作者
    


    #parent_id = models.IntegerField(default=0)
    #手填的并不一定准确，通过下面parent 和tostr方法变成可选的
    root = models.ForeignKey('self', related_name="root_comment", null=True, on_delete=models.DO_NOTHING)
    parent = models.ForeignKey('self', related_name="parient_comment", null=True, on_delete=models.DO_NOTHING)
    reply_to = models.ForeignKey(User, related_name="replies", null=True, on_delete = models.DO_NOTHING)
    #此reply_to指 该评论回复的是哪个人的评论， 某篇blog第一条评论是没有回复哪个人的评论，所以可以为空

    def __str__(self):
        return self.text

    class Meta:
        ordering = ["-comment_time"]
