"""
import datetime
from django.db import connection
from Django_Online_Shop.settings import DEBUG

def profiling_middleware(get_response):

    def middleware(request):
        request.initial_time = datetime.datetime.now()
        response = get_response(request)
        request.final_time = datetime.datetime.now()
        request.delta_time = request.final_time - request.initial_time
        print("TIMES\nRequest time: {}\nResponse time: {}\nProcessing time: {}".format(request.initial_time, request.final_time, request.delta_time))
        print("SQL count: {}".format(len(connection.queries)))
    return middleware
"""