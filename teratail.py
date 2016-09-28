from errbot import BotPlugin, botcmd, arg_botcmd, webhook
from itertools import chain
import requests


CONFIG_TEMPLATE = {
    # Notify fetched questions
    'NOTIFY_TO': '#general',  # For slack setting
    # Fetching question's tag
    'CHECK_TAGS': ['Python', ],
}


class TeratailQuestion(object):
    def __init__(self, id, title):
        self.id = id
        self.title = title

    @property
    def url(self):
        return 'https://teratail.com/questions/{}'.format(self.id)


class Teratail(BotPlugin):
    """
    Fetch and notify teratail's newer questions
    """

    def activate(self):
        """
        Triggers on plugin activation

        You should delete it if you're not using it to override any default behaviour
        """
        super(Teratail, self).activate()
        self.start_poller(300, self.fetch_and_post)

    def configure(self, configuration):
        if configuration is not None and configuration != {}:
            config = dict(chain(CONFIG_TEMPLATE.items(),
                                configuration.items()))
        else:
            config = CONFIG_TEMPLATE
        super(Teratail, self).configure(config)

    def get_configuration_template(self):
        """
        Defines the configuration structure this plugin supports

        You should delete it if your plugin doesn't use any configuration like this
        """
        return CONFIG_TEMPLATE

    def fetch_questions(self, tag):
        url = 'https://teratail.com/api/v1/tags/{}/questions?limit=5&page=1'.format(tag)
        resp = requests.get(url)
        data = resp.json()
        return [
            TeratailQuestion(q_['id'], q_['title'])
            for q_ in data['questions']
        ]

    def fetch_and_post(self):
        self.log.debug('Start fetch')
        # Init
        msg_base = '【New!】{}\n{}'
        msg_to = self.build_identifier(self.config['NOTIFY_TO'])
        latest_ids = self..get('latest_ids', {})
        questions = {}
        # Fetch and sort questions
        for tag in self.config['CHECK_TAGS']:
            latest_id = latest_ids.get(tag, 0)
            for q_ in self.fetch_questions(tag):
                if q_.id <= latest_id:
                    continue
                questions.setdefault(q_.id, q_)
            latest_ids[tag] = latest_id
        # Post only newer questions
        for q_ in questions.values():
            msg = msg_base.format(q_.title, q_.url)
            self.send(msg_to, msg)
        # Save latest question-id for tag
        self['latest_id'] = latest_ids
        self.log.debug('End fetch')
