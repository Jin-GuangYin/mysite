from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from .models import Comment
from django.urls import reverse
from django.http import JsonResponse
from .forms import CommentForm

# Create your views here.
# def update_comment(request):
#     referer = request.META.get('HTTP_REFERER', reverse('home'))
#     user = request.user
#     if not user.is_authenticated:#用户未登录
#         return render(request, 'error.html', {"message" : "Please login","redirect_to":referer})
#     text = request.POST.get("text", '').strip()
#     #虽然前端同样可以判定是否为空 但前端判定不可信，如论如何设置前端，总有方法绕过
#     if text == '':
#         return render(request, 'error.html', {"message" : "your comment is NULL,please input something",
#                                              "redirect_to":referer})

#     try:
#         content_type = request.POST.get('content_type', '')
#         object_id = int(request.POST.get('object_id', ''))
#         model_class = ContentType.objects.get(model=content_type).model_class()#获得Blog类 是泛化的不限某种类型的方式获得
#         model_obj = model_class.objects.get(pk=object_id)#获得指定id的blog
#     except Exception as e:
#         return render(request, 'error.html', {"message" : "NetError, Please re-enter", "redirect_to":referer})
#     #保存数据 
#     comment = Comment()
#     comment.user = user 
#     comment.text = text
#     comment.content_object = model_obj
#     comment.save()

#     return redirect(referer)


# def update_comment(request):
#     referer = request.META.get('HTTP_REFERER', reverse('home'))
#     comment_form = CommentForm(request.POST, user=request.user)
#     if comment_form.is_valid():
#         #保存数据 
#         comment = Comment()
#         comment.user = comment_form.cleaned_data["user"]
#         comment.text = comment_form.cleaned_data["text"]
#         comment.content_object = comment_form.cleaned_data["content_object"]
#         comment.save()

#         return redirect(referer)
#     else:
#         return render(request, 'error.html', {"message" : comment_form.errors, "redirect_to":referer})
#         

# 改用jquery ajax方式加载（去掉了提交评论后的页面刷新行为）
def update_comment(request):
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    comment_form = CommentForm(request.POST, user=request.user)
    data = {}
    if comment_form.is_valid():
        #保存数据 
        comment = Comment()
        comment.user = comment_form.cleaned_data["user"]
        comment.text = comment_form.cleaned_data["text"]
        comment.content_object = comment_form.cleaned_data["content_object"]

        parent = comment_form.cleaned_data["parent"]
        if not parent is None:
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()

        #返回数据
        data["status"] = "SUCCESS"
        data["username"] = comment.user.username
        data["comment_time"] = comment.comment_time.strftime("%Y-%m-%d %H:%M:%S")
        data["text"] = comment.text
        if not parent is None:
            data["reply_to"] = comment.reply_to.username
        else:
            data["reply_to"] = ''
        data['pk'] = comment.pk
    else:
        data["status"] = "ERROR"
        data["message"] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)


                                              