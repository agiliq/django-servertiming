import resource
import time

from django.db import connection


class ServerTimingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        start_rusage = resource.getrusage(resource.RUSAGE_SELF)
        response = self.get_response(request)
        num_queries = len(connection.queries)
        db_time = self.get_sqlquery_time()
        utime, stime = self.get_total_time(start_rusage)
        total_time = utime + stime
        end_time = time.time()
        elapsed_time = (end_time - start_time) * 1000
        response['Server-Timing'] = \
            f'db={db_time},' \
            f' user_cpu_time={utime}, system_cpu_time={stime}, total_cpu_time={total_time},' \
            f' elapsed_time={elapsed_time}'

        return response

    def get_total_time(self, start_rusage):
        rusage = resource.getrusage(resource.RUSAGE_SELF)
        utime = rusage.ru_utime - start_rusage.ru_utime
        stime = rusage.ru_stime - start_rusage.ru_stime
        return utime * 1000, stime * 1000

    def get_sqlquery_time(self):
        sqltime = 0.0
        for query in connection.queries:
            sqltime += float(query["time"])
        return sqltime * 1000

