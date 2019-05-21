from django.shortcuts import render_to_response,get_object_or_404, render
from django.core.paginator import Paginator
from .models import Blog,BlogType
from django.conf import settings
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from read_statistics.models import ReadNum
from read_statistics.utils import read_statistics_once_read
from comment.models import Comment
from comment.forms import CommentForm

def get_blog_list_common_date(request,blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.BLOGS_NUMBER_IN_EACH_PAGE)
    page_num = request.GET.get("page", 1)#获取url的页码参数
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number
    page_range = [i for i in range(current_page_num-2, current_page_num+3) if i > 0 and (i <= paginator.num_pages)]

    if page_range[0] - 1 >= 2:
        page_range.insert(0, "...")
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append("...")

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)


    # blog_types = BlogType.objects.all()
    # blog_types_list = []
    # for blog_type in blog_types:
    #     blog_type.blog_count = Blog.objects.filter(blog_type = blog_type).count()
    #     #在每一个blog_type对象里增加一个blog_count属性
    #     #等价于BlogType.objects.annotate(blog_count = Count("blog"))  annotate:注释注解
    #     blog_types_list.append(blog_type)
    blog_dates = Blog.objects.dates("created_time", "month", order="DESC")
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year = blog_date.year,
                                         created_time__month = blog_date.month).count()
        #blog_date是日期类型 并不像blog_type那样可以加一个属性
        blog_dates_dict[blog_date] = blog_count


    context = {}
    context["page_of_blogs"] = page_of_blogs
    #context["blog_types"] = BlogType.objects.all()
    #context["blog_types"] = blog_types_list
    context["blog_types"] = BlogType.objects.annotate(blog_count = Count("blog"))
    context["page_range"] = page_range
    context["blog_dates"] = blog_dates_dict
    return context

def blog_list(request): 
    blogs_all_list = Blog.objects.all() 
    context = get_blog_list_common_date(request,blogs_all_list)
    #return render_to_response("blog/blog_list.html", context)
    return render(request, "blog/blog_list.html", context)

def blog_detail(request,blog_pk):
    context = {}
    blog = get_object_or_404(Blog, pk = blog_pk)
    read_cookie_key = read_statistics_once_read(request, blog)
    blog_content_type = ContentType.objects.get_for_model(blog)
    comments = Comment.objects.filter(content_type=blog_content_type, object_id = blog_pk, parent=None)
    #封装到read_statistics.utils
    # if not request.COOKIES.get('blog_%s_read' % blog_pk):
    #     ct = ContentType.objects.get_for_model(Blog)
    #     if ReadNum.objects.filter(content_type=ct, object_id=blog.pk).count():
    #         readnum = ReadNum.objects.get(content_type=ct, object_id=blog.pk)
    #     else:
    #         readnum = ReadNum(content_type=ct, object_id=blog.pk)
    #     readnum.read_num += 1
    #     readnum.save()


        # if ReadNum.objects.filter(blog=blog).count():
        #     readnum = ReadNum.objects.get(blog=blog)
        # else:
        #     readnum = ReadNum(blog = blog)
        # readnum.read_num += 1
        # readnum.save()
        

    context["blog"] = blog
    context["previous_blog"] = Blog.objects.filter(created_time__gt = blog.created_time).last()
    context["next_blog"] = Blog.objects.filter(created_time__lt = blog.created_time).first()
    context['comments'] = comments
    data = {}
    data["content_type"] = blog_content_type.model#blog_content_type是一个对象 需要用到其字符串形式所以加.model
    data["object_id"] = blog_pk
    data["reply_comment_id"] = 0
    context["comment_form"] = CommentForm(initial = data) 
    # #initial参数是个字典 等价于下面一行
    #context["comment_form"] = CommentForm(initial = {"content_type"：blog_content_type.model, "object_id"：blog_pk})
    #context["user"] = request.user
    #response = render_to_response("blog/blog_detail.html", context)/django2已遗弃虽然少写参数request 但处理表单不方便推荐用render
    response = render(request,"blog/blog_detail.html", context)
    #render功能相当于上面被注释的两行
    response.set_cookie(read_cookie_key, "true")
    return response 

# def blog_detail(request,blog_pk):
#     context = {}
#     blog = get_object_or_404(Blog, pk = blog_pk)
#     if not request.COOKIES.get('blog_%s_read' % blog_pk):
#         blog.read_num += 1
#         blog.save()

#     context["blog"] = blog
#     context["previous_blog"] = Blog.objects.filter(created_time__gt = blog.created_time).last()
#     context["next_blog"] = Blog.objects.filter(created_time__lt = blog.created_time).first()
#     response = render_to_response("blog/blog_detail.html", context)
#     response.set_cookie('blog_%s_read' % blog_pk, "True")
#     return response 

def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk = blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type = blog_type)
    #blogs_all_list = Blog.objects.filter(blog_type__id = blog_type_pk)

    context = get_blog_list_common_date(request,blogs_all_list)
    context["blog_type"] = blog_type
    return render(request,"blog/blogs_with_type.html", context)
    #return render_to_response("blog/blogs_with_type.html", context)
    # 继承关系下（就是html的extemds）比如B继承A，C继承B
    #C只需填写B对A的扩城部分，除非C需要修改B对A的已填写部分，否则不用填写B对A的已填写部分。
    #当然前提是views中对C的处理方法包含fc的返回值包含对B的处理方法fb.

def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year = year, created_time__month = month )
    #blogs_all_list = Blog.objects.filter(blog_type__id = blog_type_pk)

    context = get_blog_list_common_date(request,blogs_all_list)
    context["blogs_with_date"] = "%syear年%sdate" %(year, month)
    context["blog_dates"] = Blog.objects.dates("created_time", "month", order="DESC")
    return render_to_response("blog/blogs_with_date.html", context)


# def blog_list(request):
#     blogs_all_list = Blog.objects.all()
#     paginator = Paginator(blogs_all_list, settings.BLOGS_NUMBER_IN_EACH_PAGE)
#     page_num = request.GET.get("page", 1)#获取url的页码参数
#     page_of_blogs = paginator.get_page(page_num)
#     current_page_num = page_of_blogs.number
#     page_range = [i for i in range(current_page_num-2, current_page_num+3) if i > 0 and (i <= paginator.num_pages)]

#     if page_range[0] - 1 >= 2:
#         page_range.insert(0, "...")
#     if paginator.num_pages - page_range[-1] >= 2:
#         page_range.append("...")

#     if page_range[0] != 1:
#         page_range.insert(0, 1)
#     if page_range[-1] != paginator.num_pages:
#         page_range.append(paginator.num_pages)

#     context = {}
#     context["page_of_blogs"] = page_of_blogs
#     context["blog_types"] = BlogType.objects.all()
#     context["page_range"] = page_range
#     context["blog_dates"] = Blog.objects.dates("created_time", "month", order="DESC")
#     return render_to_response("blog/blog_list.html", context)

# def blog_detail(request,blog_pk):
#     context = {}
#     blog = get_object_or_404(Blog, pk = blog_pk)
#     context["blog"] = blog
#     context["previous_blog"] = Blog.objects.filter(created_time__gt = blog.created_time).last()
#     context["next_blog"] = Blog.objects.filter(created_time__lt = blog.created_time).first()
#     return render_to_response("blog/blog_detail.html", context)

# def blogs_with_type(request, blog_type_pk):
#     blog_type = get_object_or_404(BlogType, pk = blog_type_pk)
#     blogs_all_list = Blog.objects.filter(blog_type = blog_type)
#     #blogs_all_list = Blog.objects.filter(blog_type__id = blog_type_pk)
#     paginator = Paginator(blogs_all_list, settings.BLOGS_NUMBER_IN_EACH_PAGE)
#     page_num = request.GET.get("page", 1)#获取url的页码参数
#     page_of_blogs = paginator.get_page(page_num)
#     current_page_num = page_of_blogs.number
#     page_range = [i for i in range(current_page_num-2, current_page_num+3) if i > 0 and (i <= paginator.num_pages)]

#     if page_range[0] - 1 >= 2:
#         page_range.insert(0, "...")
#     if paginator.num_pages - page_range[-1] >= 2:
#         page_range.append("...")

#     if page_range[0] != 1:
#         page_range.insert(0, 1)
#     if page_range[-1] != paginator.num_pages:
#         page_range.append(paginator.num_pages)

#     context = {}
#     context["blog_type"] = blog_type
#     context["blog_types"] = BlogType.objects.all()
#     context["page_of_blogs"] = page_of_blogs
#     context["page_range"] = page_range
#     context["blog_dates"] = Blog.objects.dates("created_time", "month", order="DESC")
#     return render_to_response("blog/blogs_with_type.html", context)
#     # 继承关系下（就是html的extemds）比如B继承A，C继承B
#     #C只需填写B对A的扩城部分，除非C需要修改B对A的已填写部分，否则不用填写B对A的已填写部分。
#     #当然前提是views中对C的处理方法包含fc的返回值包含对B的处理方法fb.

# def blogs_with_date(request, year, month):
#     blogs_all_list = Blog.objects.filter(created_time__year = year, created_time__month = month )
#     #blogs_all_list = Blog.objects.filter(blog_type__id = blog_type_pk)
#     paginator = Paginator(blogs_all_list, settings.BLOGS_NUMBER_IN_EACH_PAGE)
#     page_num = request.GET.get("page", 1)#获取url的页码参数
#     page_of_blogs = paginator.get_page(page_num)
#     current_page_num = page_of_blogs.number
#     page_range = [i for i in range(current_page_num-2, current_page_num+3) if i > 0 and (i <= paginator.num_pages)]

#     if page_range[0] - 1 >= 2:
#         page_range.insert(0, "...")
#     if paginator.num_pages - page_range[-1] >= 2:
#         page_range.append("...")

#     if page_range[0] != 1:
#         page_range.insert(0, 1)
#     if page_range[-1] != paginator.num_pages:
#         page_range.append(paginator.num_pages)

#     context = {}
#     context["blogs_with_date"] = "%syear年%sdate" %(year, month)
#     context["page_of_blogs"] = page_of_blogs
#     context["page_range"] = page_range
#     context["blog_dates"] = Blog.objects.dates("created_time", "month", order="DESC")
#     return render_to_response("blog/blogs_with_date.html", context)