import resource
import time

from django.db import connection
from django.conf import settings

MSEC_CONVERT_FACTOR = 1000
SERVER_TIMING_SETTING_NAME = "SERVER_TIMING"


class ServerTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.add_header = self.should_add_server_timing_header()

    def __call__(self, request):

        if self.add_header:
            start_time = time.time()
            start_rusage = resource.getrusage(resource.RUSAGE_SELF)
            response = self.get_response(request)
            db_time = self.get_sqlquery_time()
            utime, stime = self.get_total_time(start_rusage)
            total_time = utime + stime
            end_time = time.time()
            elapsed_time = (end_time - start_time) * MSEC_CONVERT_FACTOR
            response['Server-Timing'] = \
                f'db={db_time},' \
                f' user_cpu_time={utime}, system_cpu_time={stime}, total_cpu_time={total_time},' \
                f' elapsed_time={elapsed_time}'
            return response
        else:
            response = self.get_response(request)
            return response

    def should_add_server_timing_header(self):
        add_header = getattr(settings, SERVER_TIMING_SETTING_NAME,
                             settings.DEBUG
                             )
        return add_header

    def get_total_time(self, start_rusage):
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        utime = rusage.ru_utime - start_rusage.ru_utime
        stime = rusage.ru_stime - start_rusage.ru_stime
        return utime * MSEC_CONVERT_FACTOR, stime * MSEC_CONVERT_FACTOR

    def get_sqlquery_time(self):

        return sum(float(query["time"]) for query in connection.queries) * MSEC_CONVERT_FACTOR
