# -*- coding: utf-8 -*-

import sys
from apscheduler.schedulers.blocking import BlockingScheduler
import os

bin_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.split(bin_path)[0]
parent_path = os.path.split(root_path)[0]
sys.path.append(parent_path)

import midas.bin.env as env
import midas.core.utilities.daemonize as daemonize
import midas.core.jobs.deep_rooling as deep_rolling


def task(name):
    if name == 'deeprolling':
        return deep_rolling.main

    return lambda x: x


class DeepRollingDaemon(daemonize.Daemon):
    def __init__(self):
        super(DeepRollingDaemon, self).__init__(pidfile='{tmppath}/scheduler_deep_rolling.pid'.format(tmppath=env.tmp_path),
                                                stdout='{tmppath}/scheduler_dev.stdout'.format(tmppath=env.tmp_path))

    def _run(self):
        scheduler = BlockingScheduler()
        scheduler.add_job(task('deeprolling'), 'cron', day_of_week='mon-sat', hour=17, minute=00)
        scheduler.start()


if __name__ == "__main__":
    if len(sys.argv) == 3:
        if 'deeprolling' == sys.argv[1]:
            daemon = DeepRollingDaemon()
        else:
            print('unknown project')
            sys.exit(2)

        if 'start' == sys.argv[2]:
            daemon.start()
        elif 'stop' == sys.argv[2]:
            daemon.stop()
        elif 'restart' == sys.argv[2]:
            daemon.stop()
            daemon.start()
        else:
            print('unknown command')
            sys.exit(2)
        sys.exit(0)
    else:
        print('usage: %s deeprolling start|stop|restart', sys.argv[0])
        sys.exit(2)
