# -*- coding:utf8 -*-
from errbot.backends.test import testbot


class TestPlugin(object):
    extra_plugin_dir = '.'

    def fetch_plugin(self, testbot):
        return testbot.bot.plugin_manager.get_plugin_obj_by_name('Teratail')

    def test_config(self, testbot):
        plugin = self.fetch_plugin(testbot)
        assert plugin.config['NOTIFY_TO'] == '#general'

    def test_fetch_questions(self, testbot):
        plugin = self.fetch_plugin(testbot)
        data = plugin.fetch_questions('Python')
        q_ = data[0]
        assert q_.url.startswith('https://teratail.com/questions/')
