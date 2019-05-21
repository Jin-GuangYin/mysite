from django import forms
from django.db.models import ObjectDoesNotExist
from django.contrib.contenttypes.models import ContentType
from ckeditor.widgets import CKEditorWidget

class CommentForm(forms.Form):
    content_type = forms.CharField(widget = forms.HiddenInput)
    object_id =  forms.IntegerField(widget = forms.HiddenInput)
    text = forms.CharField(widget = CKEditorWidget(config_name='comment_ckeditor'))
    reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id':'reply_comment_id'}))
    #因为blog_detail里对commentform的处理没有user项 所以此处重写了 构造函数 有user则添加， 无则不添加
    def __init__(self, *args, **kwargs):
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        super(CommentForm, self).__init__(*args, **kwargs)

    def clean(self):
        #判断用户是否登陆
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError("user is NOT login")
        content_type = self.cleaned_data["content_type"]
        object_id = self.cleaned_data["object_id"]
        try:
            model_class = ContentType.objects.get(model=content_type).model_class()#获得Blog类 是泛化的不限某种类型的方式获得
            model_obj = model_class.objects.get(pk=object_id)#获得指定id的blog
            self.cleaned_data["content_object"] = model_obj
        except ObjectDoesNotExist:
            raise forms.ValidationError("comment object is NOT exist")

        return self.cleaned_data


       

    def clean_reply_comment_id(self):
        reply_comment_id = self.cleaned_data["reply_comment_id"]
        if reply_comment_id < 0:
            raise forms.ValidationError("REPLAY_ERROR")
        elif reply_comment_id == 0:
            self.cleaned_data["parent"] = None
        elif Comment.objexts.filter(pk=reply_comment_id).exits():
            self.cleaned_data["parent"] = Comment.objexts.get(pk=reply_comment_id)
        else:
            raise forms.ValidationError("REPLAY_ERROR")
        return reply_comment_id