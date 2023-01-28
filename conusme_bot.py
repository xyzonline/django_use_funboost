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



if __name__ == '__main__':
    # test_bot.consume()
    test_bot.multi_process_consume(4)

