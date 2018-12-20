from django.shortcuts import render,redirect,HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from dwebsocket import require_websocket
from . import forms
from .admin_base import site
from .core.haproxy import haproxy
import json

# Create your views here.
def account_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username,password=password)
        if user:
            login(request,user)
            return  redirect(request.GET.get('next') or '/apps/asset/list/')
    return render(request, 'login.html', locals())

def account_logout(request,**kwargs):
    request.session.clear()
    logout(request)
    return redirect('/accounts/login/')

def index(request):
    for app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name]['asset']
        querysets = queryset(request,admin_class)
    return render(request,'index.html',locals())

def admin_func(model_name):
    for app_name in site.registered_admins:
        admin_class = site.registered_admins[app_name][model_name]
        return admin_class

@login_required
def table_obj_list(request,model_name):
    admin_class = admin_func(model_name)
    form = forms.create_dynamic_modelform(admin_class.model)
    form_obj = form()
    querysets=queryset(request,admin_class)

    return render(request,'gloab-form/list_form.html',locals())

@login_required
def table_obj_add(request,model_name):
    admin_class = admin_func(model_name)
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == 'POST':
        try:
            file = request.FILES.get('ssl')
            print('file',file)
            if file:
                filepath = haproxy.savessl(file)
                request.POST._mutable = True  # QueryDict允许被修改
                request.POST.update({'ssl': filepath})
        except FileNotFoundError as e:
            print('error',e)
        form_obj = form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            haproxy.buildcfg(admin_class)
            return redirect("/apps/%s/list"%model_name)
    elif request.method == 'GET':
        form_obj = form()

    return render(request,'gloab-form/add_form.html',locals())

@login_required
def table_obj_change(request,model_name,no_render=False):
    admin_class = admin_func(model_name)
    object_id = request.GET.get('project_id')
    obj = admin_class.model.objects.get(id=object_id)
    form = forms.create_dynamic_modelform(admin_class.model)
    if request.method == 'GET':
        form_obj = form(instance=obj)

    elif request.method == 'POST':
        try:
            file = request.FILES.get('ssl')
            if file:
                filepath = haproxy.savessl(file)
                request.POST._mutable = True   #QueryDict允许被修改
                request.POST.update({'ssl':filepath})
        except FileNotFoundError as e:
            print('error File',e)
        except TypeError as e:
            print('error Tye',e)
            pass
        form_obj = form(instance=obj, data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            haproxy.buildcfg(admin_class)
            return redirect("/apps/%s/list" % model_name)
    if no_render:
        return locals()
    else:
        return render(request, 'gloab-form/change_form.html', locals())

@login_required
@csrf_exempt
def table_obj_del(request,model_name):
    admin_class = admin_func(model_name)
    obj_id = request.GET.get('idAll')
    if ',' in obj_id:
        status = {'success':None,'error':None}
        success_count = 0
        error_count = 0
        for id in obj_id.split(','):
            if id:
                admin_class.model.delete(admin_class.model.objects.get(id=id))
                success_count += 1
            error_count += 1
        haproxy.buildcfg(admin_class)
        status.update({'success':success_count,'error':error_count})
        return HttpResponse(json.dumps(status))
    else:
        admin_class.model.delete(admin_class.model.objects.get(id=obj_id))
        haproxy.buildcfg(admin_class)
        return redirect("/apps/%s/list" %model_name)

def queryset(request,admin_class,no_render=False):
    querysets, filter_conditions = get_filter_objs(request, admin_class)
    querysets, q_val = get_search_objs(request, querysets, admin_class)
    querysets, new_order_key, order_column, last_orderby_key = get_orderby_objs(request, querysets)
    paginator = Paginator(querysets, admin_class.list_per_page)  # Show 25 contacts per page
    page = request.GET.get('_page')
    try:
        querysets = paginator.page(page)
    except PageNotAnInteger:
        querysets = paginator.page(1)
    except EmptyPage:
        querysets = paginator.page(paginator.num_pages)
    if no_render:
        return locals()
    return locals()

def get_filter_objs(request, admin_class):
    """返回filter的结果queryset"""

    filter_condtions = {}
    for k, v in request.GET.items():
        if k in ['_page', '_q', '_o']:
            continue
        if v:  # valid condtion
            filter_condtions[k] = v
    print('filter',filter_condtions)
    queryset = admin_class.model.objects.filter(**filter_condtions)
    return queryset, filter_condtions

def get_search_objs(request, querysets, admin_class):
    """
    1.拿到_q的值
    2.拼接Q查询条件
    3.调用filter(Q条件)查询
    4. 返回查询结果
    :param request:
    :param querysets:
    :param admin_class:
    :return:
    """
    q_val = request.GET.get('_q')  # None
    if q_val:
        q_obj = Q()
        q_obj.connector = "OR"
        for search_field in admin_class.search_fields:  # 2
            q_obj.children.append(("%s__contains" % search_field, q_val))
        search_results = querysets.filter(q_obj)  # 3
    else:
        search_results = querysets

    return search_results, q_val

def get_orderby_objs(request, querysets):
    """
    排序
    1.获取_o的值
    2.调用order_by(_o的值)
    3.处理正负号，来确定下次的排序的顺序
    4.返回
    :param request:
    :param querysets:
    :return:
    """
    orderby_key = request.GET.get('_o')  # -id
    last_orderby_key = orderby_key or ''
    if orderby_key:
        order_column = orderby_key.strip('-')
        order_results = querysets.order_by(orderby_key)
        if orderby_key.startswith('-'):
            new_order_key = orderby_key.strip('-')
        else:
            new_order_key = "-%s" % orderby_key

        return order_results, new_order_key, order_column, last_orderby_key
    else:
        return querysets, None, None, last_orderby_key

def haproxyd(request,*args,**kwargs):
    print('request',request)
    status = haproxy.checkservice()
    return render(request,'asset/haproxy.html',locals())

@require_websocket
def ha_cfg_list(request):
    pass

@require_websocket
def ha_cfg_save(request):
    pass

@require_websocket
def ha_command(request,*args,**kwargs):
    msg = request.websocket.wait()
    if type(msg) is bytes: msg = msg.decode('utf-8')
    print('command_msg', msg)
    if msg == 'quit':
        request.websocket.close()
    elif msg == 'status':
        status = haproxy.status(request)
        request.websocket.send(status)


    # request.websocket.close()

@csrf_exempt
def ha_content(request,*args,**kwargs):
    if request.method == 'POST':
        ha_cfg = haproxy.display_cfg()
        response = FileResponse(open(ha_cfg, 'rb'))
        response['Content-Type'] = 'application/octet-stream'
        response['Content=Disposition'] = 'application;filename="haproxy.cfg"'
        return HttpResponse(response)

def ha_status(request):
    status = haproxy.shell('systemctl status haproxy')
    return HttpResponse(status.stdout.readlines())

@csrf_exempt
def save_cfg(request):
    if request.method == 'POST':
        fileObj = request.POST.get('textarea')
        saveFile = haproxy.savecfg(fileObj)
        return HttpResponse(saveFile)
    return request.path

@csrf_exempt
def restart(request):
    if request.method == 'POST':
        saveFile = haproxy.restart()
        return HttpResponse(saveFile)
    return request.path