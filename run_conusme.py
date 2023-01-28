# import os
#
#
# # set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
#
# import django
# from django.contrib import admin
#
# django.setup()
import datetime

import apscheduler
from funboost import boost, BrokerEnum, fsdf_background_scheduler, timing_publish_deco
from funboost.timing_job.apscheduler_use_redis_store import funboost_background_scheduler_redis_store

from index.func import create_report, test_bot

def my_push(): # 推荐这样做，自己写个发布函数
    test_bot.push('run', {'a': 1, 'b': 2})

if __name__ == '__main__':
    test_bot.push('run', {'a': 1, 'b': 2})
    create_report.push('first run')
    # for i in range(100):
    #     test_bot.push('run', {'a': 1, 'b': 2})  # 发布者发布任务
    fsdf_background_scheduler.add_job(timing_publish_deco(create_report), 'interval', id='60_second_job', seconds=60,
                                      kwargs={"x": "run every 60 seconds"})
    fsdf_background_scheduler.add_job(timing_publish_deco(test_bot), 'interval', id='600_second_job', seconds=600,
                                      kwargs={"cmd": "run every 600 seconds", "params": {"a": 1, "b": 2}})
    fsdf_background_scheduler.add_job(timing_publish_deco(test_bot), 'date',
                                      run_date=datetime.datetime(2023, 1, 25, 2, 32, 6), args=('run one time', {'a': 1, 'b': 2}))  # 定时，只执行一次
    fsdf_background_scheduler.start()

    # funboost_background_scheduler_redis_store.start(paused=False)
    # try:
    #     funboost_background_scheduler_redis_store.add_job(my_push,       # 这样做是可以的，用户自己定义一个函数，可picke序列化存储到redis或者mysql mongo。推荐这样。
    #                                                       'interval', id='6', name='namexx', seconds=15,
    #                                                       kwargs={},
    #                                                       replace_existing=False)
    # except apscheduler.jobstores.base.ConflictingIdError as e:
    #     print('定时任务id已存在： {e}')

    # create_report.consume()  # 当前进程内启动，可以这样，也可以下面使用多进程启动。
    # # create_report.multi_process_consume(2)
    # test_bot.consume()
    # # test_bot.multi_process_consume(4)

