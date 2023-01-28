from django.shortcuts import render
from django.http import HttpResponse
import json
# Create your views here.

from .func import create_report, test_bot

def show_result(status_and_result: dict):
    """
    :param status_and_result: 一个字典包括了函数入参、函数结果、函数是否运行成功、函数运行异常类型
    """
    print(status_and_result)

def test(request):
    async_result = test_bot.push('run', {'a': 1, 'b': 2})
    # async_result.set_callback(show_result)
    print(async_result.result)
    return HttpResponse(json.dumps(async_result.result))
