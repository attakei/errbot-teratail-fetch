# -*- coding:utf8 -*-
from errbot.backends.test import testbot


class TestPlugin(object):
    extra_plugin_dir = '.'

    def fetch_plugin(self, testbot):
        return testbot.bot.plugin_manager.get_plugin_obj_by_name('Teratail')
