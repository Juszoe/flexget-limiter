# coding=utf-8
from __future__ import unicode_literals, division, absolute_import
from builtins import *

import logging
import time

from flexget import plugin
from flexget.event import event

log = logging.getLogger('limiter')


class Limiter(object):
    """
    # config example
    limiter:
        down: 1000    # unit KB/s
        up: 100      # unit KB/s
        disk:
            read: 10000    # unit KB/s
            write: 10000   # unit KB/s
    """
    schema = {
        'type': 'object',
        'properties': {
            'down': {'type': 'number', 'default': float('inf')},
            'up': {'type': 'number', 'default': float('inf')},
            'disk': {
                'type': 'object',
                'properties': {
                    'read': {'type': 'number', 'default': float('inf')},
                    'write': {'type': 'number', 'default': float('inf')},
                },
                'default': {
                    'read': float('inf'),
                    'write': float('inf')
                }
            }
        },
        'additionalProperties': False,
    }

    def __init__(self):
        self.psutil = None

    @plugin.priority(plugin.PRIORITY_FIRST)
    def on_task_start(self, task, config):
        try:
            import psutil
        except ImportError as e:
            log.debug('Error importing psutil: %s' % e)
            raise plugin.DependencyError(
                'limiter',
                'psutil',
                'psutil is required. `pip install psutil` to install.',
                log,
            )
        self.psutil = psutil
        max_down = config.get('down')
        max_up = config.get('up')
        max_disk_read = config.get('disk').get('read')
        max_disk_write = config.get('disk').get('write')

        def compare(src, max_number, msg):
            if src > max_number:
                log.info(msg)
                task.abort(msg)

        download_speed, upload_speed = self.net_io_speed()
        compare(download_speed, max_down, 'download speed too high: %d KB/s' % download_speed)
        compare(upload_speed, max_up, 'upload speed too high: %d KB/s' % upload_speed)

        read_speed, write_speed = self.disk_io_speed()
        compare(read_speed, max_disk_read, 'disk read speed too high: %d KB/s' % read_speed)
        compare(write_speed, max_disk_write, 'disk write speed too high: %d KB/s' % write_speed)

    def net_io_speed(self, wait_time=1, unit='KB'):
        past = self.psutil.net_io_counters()
        time.sleep(wait_time)
        now = self.psutil.net_io_counters()
        unit = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024
        }[unit]
        down = (now.bytes_recv - past.bytes_recv) / unit / wait_time
        up = (now.bytes_sent - past.bytes_sent) / unit / wait_time
        return down, up

    def disk_io_speed(self, wait_time=1, unit='KB'):
        past = self.psutil.disk_io_counters()
        time.sleep(wait_time)
        now = self.psutil.disk_io_counters()
        unit = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024
        }[unit]
        read = (now.read_bytes - past.read_bytes) / unit / wait_time
        write = (now.write_bytes - past.write_bytes) / unit / wait_time
        return read, write


@event('plugin.register')
def register_plugin():
    plugin.register(Limiter, 'limiter', api_ver=2)
