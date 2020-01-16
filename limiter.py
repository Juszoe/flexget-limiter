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
        down: 1000         # unit KB/s
        up: 100            # unit KB/s
        disk:
            read: 10000    # unit KB/s
            write: 10000   # unit KB/s
        wait: 10           # unit second
        reject: no
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
            },
            'wait': {'type': 'number', 'default': 1},
            'reject': {'type': 'boolean', 'default': False}
        },
        'additionalProperties': False,
    }

    def __init__(self):
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

    @plugin.priority(plugin.PRIORITY_FIRST)
    def on_task_start(self, task, config):
        if config.get('reject') is False:
            self.do_filter(task, config, False)

    # @plugin.priority(plugin.PRIORITY_FIRST)
    def on_task_filter(self, task, config):
        if config.get('reject'):
            self.do_filter(task, config, True)

    def do_filter(self, task, config, is_reject):
        max_down = config.get('down')
        max_up = config.get('up')
        max_disk_read = config.get('disk').get('read')
        max_disk_write = config.get('disk').get('write')
        wait = config.get('wait')

        def compare(value, max_number, msg):
            if value > max_number:
                log.info(msg)
                if is_reject:
                    for entry in task.entries:
                        entry.reject(reason=msg)
                task.abort(msg)

        download_speed, upload_speed, read_speed, write_speed = self.io_speed(wait_time=wait)
        compare(download_speed, max_down, 'download speed too high: %d KB/s' % download_speed)
        compare(upload_speed, max_up, 'upload speed too high: %d KB/s' % upload_speed)
        compare(read_speed, max_disk_read, 'disk read speed too high: %d KB/s' % read_speed)
        compare(write_speed, max_disk_write, 'disk write speed too high: %d KB/s' % write_speed)

    def io_speed(self, wait_time=1, unit='KB'):
        net_past = self.psutil.net_io_counters()
        disk_past = self.psutil.disk_io_counters()
        time.sleep(wait_time)
        net_now = self.psutil.net_io_counters()
        disk_now = self.psutil.disk_io_counters()
        unit = {
            'B': 1,
            'KB': 1024,
            'MB': 1024 * 1024
        }[unit]
        down = (net_now.bytes_recv - net_past.bytes_recv) / unit / wait_time
        up = (net_now.bytes_sent - net_past.bytes_sent) / unit / wait_time
        read = (disk_now.read_bytes - disk_past.read_bytes) / unit / wait_time
        write = (disk_now.write_bytes - disk_past.write_bytes) / unit / wait_time
        return down, up, read, write


@event('plugin.register')
def register_plugin():
    plugin.register(Limiter, 'limiter', api_ver=2)
