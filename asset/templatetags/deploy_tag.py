# -*- coding:utf-8-*-
from django.template import Library
from django.utils.safestring import mark_safe

register = Library()

@register.simple_tag
def build_project_verbose_name(admin_class):
    return admin_class.model._meta.verbose_name

@register.simple_tag
def get_filter_condtions_string(filter_conditions,q_val):
    condtion_str = ""
    if q_val:#拼接search 字段
        condtion_str += "&_q=%s" % q_val
    return condtion_str

@register.simple_tag
def generate_orderby_icon(new_order_key):
    if new_order_key.startswith('-'):
        icon_ele = """<i class="fa fa-angle-down" aria-hidden="true"></i>"""
    else:
        icon_ele = """<i class="fa fa-angle-up" aria-hidden="true"></i>"""
    return mark_safe(icon_ele)

@register.simple_tag
def get_abs_value(loop_num , curent_page_number):
    """返回当前页与循环loopnum的差的绝对值"""
    return abs(loop_num - curent_page_number)

@register.simple_tag
def get_readonly_field_val(field_name,obj_instance):
    """
    1.根据obj_instance反射出field_name 的值
    :param field_name:
    :param obj_instance:
    :return:
    """
    field_type =  obj_instance._meta.get_field(field_name).get_internal_type()
    if field_type == "ManyToManyField":
        m2m_obj = getattr(obj_instance,field_name)
        return ",".join([ i.__str__() for i in m2m_obj.all()])
    return getattr(obj_instance,field_name)

@register.simple_tag
def get_selected_m2m_objects(form_obj,field_name):
    """
    1.根据field_name反射出form_obj.instance里的字段对象
    2. 拿到字段对象关联的所有数据
    :param form_obj:
    :param field:
    :return:
    """

    if form_obj.instance.id:
        field_obj = getattr(form_obj.instance, field_name)
        return field_obj.all()
    else:
        return []

@register.simple_tag
def get_m2m_objects(admin_class,field_name,selected_objs):
    """
    1.根据field_name从admin_class.model反射出字段对象
    2.拿到关联表的所有数据
    3.返回数据
    :param admin_class:
    :param field_name:
    :return:
    """

    field_obj = getattr(admin_class.model,field_name)
    all_objects = field_obj.rel.to.objects.all()
    return set(all_objects) - set(selected_objs)

@register.simple_tag
def build_groups(admin_class,row):
    return admin_class.model.objects.filter(id=row.id).values('assetgroup__name')[0]['assetgroup__name']

@register.simple_tag
def build_asset_code(row,admin_class):
    ele_td = ''

    ids = admin_class.model.objects.filter(name=row).values('assetcheck__status_code')
    if ids[0]['assetcheck__status_code'] == 200:
        td = "<td style='text-align: center;font-size: 14px;color: #37c532;font-weight: bold'>可访问</td>"
    else:
        td = "<td style='text-align: center;font-size: 14px;color:#FF0018 ;font-weight: bold'>不可访问</td>"
    ele_td += td
    return mark_safe(ele_td)

@register.simple_tag
def build_logs_info(obj):
    ele = ""
    for content in obj.values():
        ele_tr = "<tr>"
        ele_td = "<td>%s</td>" %content["date"].strftime("%Y-%m-%d %H:%M:%S")
        ele_td += "<td>%s</td>" %content["user"]
        ele_td += "<td>%s</td>" %content["action"]
        ele_td += "<td>%s</td>" %content["content"]
        ele_tr += ele_td
        ele_tr += "</tr>"
        ele += ele_tr
    return mark_safe(ele)

@register.simple_tag
def build_option_user(obj):
    ele = ""
    for user in obj.values('user').distinct():
        ele_option = "<option label='%s' value='%s'></option>" %(user['user'],user['user'])
        ele += ele_option
    return mark_safe(ele)

@register.simple_tag
def build_option_action(obj):
    ele = ""
    for user in obj.values('action').distinct():
        ele_option = "<option label='%s' value='%s'></option>" %(user['action'],user['action'])
        ele += ele_option
    return mark_safe(ele)