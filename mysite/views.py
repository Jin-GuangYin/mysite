import datetime
from django.shortcuts import render_to_response, render, redirect
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from read_statistics.utils import get_seven_days_read_data, \
                                  get_today_hot_data, \
                                  get_yesterday_hot_data
                                 
from blog.models import Blog
from django.contrib import auth 
from django.urls import reverse
'''from django.contrib.auth import authenticate, login 为了避免与自定义的login冲突 引用到上一层...'''
from .forms import LoginForm, RegForm
from django.contrib.auth.models import User

def get_7_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects \
                .filter(read_details__date__lt = today, read_details__date__gte = date) \
                .values('id', 'title') \
                .annotate(read_num_sum = Sum("read_details__read_num")) \
                .order_by('-read_num_sum')
    return  blogs[:7]

def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_seven_days_read_data(blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)
    yesterday_hot_data = get_yesterday_hot_data(blog_content_type)

    sevenday_hot_data = cache.get("sevenday_hot_data")

    if sevenday_hot_data is None:
        sevenday_hot_data = get_7_hot_data()
        cache.set("sevenday_hot_data", sevenday_hot_data, 3600)

    context = {}
    context["read_nums"] = read_nums
    context["dates"] =  dates
    context["today_hot_data"] =  today_hot_data
    context["yesterday_hot_data"] =  yesterday_hot_data
    context["sevenday_hot_data"] =  sevenday_hot_data
    #return render_to_response("home.html", context)
    return render(request,"home.html", context)

def login(request):
    #注释部分为在原网页登陆
    #方法1为另立单独的登录页面
    '''username = request.POST.get("username", '')
    password = request.POST.get("password", '')


    user = auth.authenticate(request, username=username, password=password)
    #referer = request.META.get('HTTP_REFERER', '/')
    referer = request.META.get('HTTP_REFERER', reverse('home'))
    if user is not None:
        auth.login(request, user)
        # Redirect to a success page.
        return redirect(referer)#重定向到主页
    else:
        # Return an 'invalid login' error message.
        return render(request, 'error.html', {"message" : "username or password is wrong","redirect_to":referer})'''
    
    #方法2 没有将验证过程封装到loginform
    # if request.method == "POST" :
    #     login_form = LoginForm(request.POST) #request.POST得到传输数据的字典 如果要用某一个key的value则例如：username = request.POST.get("username", '') password = request.POST.get("password", '')
    #     if login_form.is_valid():
    #         username = login_form.cleaned_data['username']
    #         password = login_form.cleaned_data['password']
    #         user = auth.authenticate(request, username=username, password=password)#利用验证过程request非必需 将其封装到loginform类中
                                                                                   #因为登陆过程auth.login(request, user) request是必需的
                                                                                   #所以登陆过程不能封装到loginform类中
    #         if user is not None:
    #             auth.login(request, user)
    #             # Redirect to a success page.
    #             return redirect(request.GET.get('from', reverse('home')))
    #         else:
    #             login_form.add_error(None,"username or password is wrong")
    # else:   
    #     login_form = LoginForm() 
    
    # context = {}
    # context['login_form'] = login_form
    # return render(request, "login.html",context)



    #方法3将验证过程封装到loginform
    if request.method == "POST" :
        login_form = LoginForm(request.POST) #request.POST得到传输数据的字典 如果要用某一个key的value则例如：username = request.POST.get("username", '') password = request.POST.get("password", '')
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            # Redirect to a success page.
            return redirect(request.GET.get('from', reverse('home')))
    else:   
        login_form = LoginForm() 
    
    context = {}
    context['login_form'] = login_form
    return render(request, "login.html",context)

def register(request):
    if request.method == "POST" :
        reg_form = RegForm(request.POST) 
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']

            #创建用户
            user = User.objexts.create_user(username, email, password)
            user.save()

            # 等价的创建user方法
            # user = User()
            # user.username = username
            # user.email = email
            # user.set_password(password) 由于password要经过加密处理所以不能用user.password = password
            # user.save()
            
            #验证，登录用户并跳转页面
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))
    else:   
        reg_form = RegForm() 
    
    context = {}
    context['reg_form'] = reg_form
    return render(request, "register.html",context)