import os


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')

import django
django.setup()

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import time


from funboost import boost, BrokerEnum, ConcurrentModeEnum, FunctionResultStatus

"""
测试用户自定义记录函数消息处理的结果和状态到mysql

"""


def my_save_process_info_fun(function_result_status: FunctionResultStatus):
    """ function_result_status变量上有各种丰富的信息 ,用户可以使用其中的信息
    用户自定义记录函数消费信息的钩子函数
    """
    print('function_result_status变量上有各种丰富的信息: ',
          function_result_status.publish_time, function_result_status.publish_time_str,
          function_result_status.params, function_result_status.msg_dict,
          function_result_status.time_cost, function_result_status.result,
          function_result_status.process_id, function_result_status.thread_id,
          function_result_status.host_process, )
    print('保存到数据库', function_result_status.get_status_dict())

@boost("test_django_queue", is_using_rpc_mode=True,
       broker_kind=BrokerEnum.REDIS_ACK_ABLE, log_level=20,
       # user_custom_record_process_info_func=my_save_process_info_fun
       )
def create_report(x):
    print(f'x: {x}')
    # t0 = time.time()
    # r = [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())]
    # for item in User.objects.all():
    #     print(item.username)
    #     r.append(item.username)
    # os.system('chcp 65001')
    # os.system('dir')
    # t1 = time.time() - t0
    # r.append(str(t1))
    # print('--------'+r[0]+'-----'+str(t1)+'----')
    # return r


def bot_run_result_process_info(function_result_status: FunctionResultStatus):
    """ function_result_status变量上有各种丰富的信息 ,用户可以使用其中的信息
    用户自定义记录函数消费信息的钩子函数
    """
    print('function_result_status变量上有各种丰富的信息: ',
          function_result_status.publish_time, function_result_status.publish_time_str,
          function_result_status.params, function_result_status.msg_dict,
          function_result_status.time_cost, function_result_status.result,
          function_result_status.process_id, function_result_status.thread_id,
          function_result_status.host_process, )
    print('保存到数据库', function_result_status.get_status_dict())

from apibot.custodyAdminApiBot import run_bot

@boost("test_bot_queue", is_using_rpc_mode=True,
       broker_kind=BrokerEnum.REDIS_ACK_ABLE, log_level=20,
       # user_custom_record_process_info_func=bot_run_result_process_info
       )
def test_bot(cmd, params):
    t0 = time.time()
    r = ['BOT RUN', cmd, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())]
    run_bot()
    t1 = time.time() - t0
    r.append(str(t1))
    print(cmd, '--------'+r[2]+'-----'+str(t1)+'----')
    return r