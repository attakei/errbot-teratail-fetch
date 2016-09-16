from errbot import BotPlugin, botcmd, arg_botcmd, webhook
from itertools import chain
import requests


CONFIG_TEMPLATE = {
    # Notify fetched questions
    'NOTIFY_TO': 'TestPerson', # For slack setting
    # Fetching question's tag 
    'CHECK_TAG': 'Python',
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
        self.start_poller(60, self.fetch_and_post)

    def deactivate(self):
        """
        Triggers on plugin deactivation

        You should delete it if you're not using it to override any default behaviour
        """
        super(Teratail, self).deactivate()

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

    def check_configuration(self, configuration):
        """
        Triggers when the configuration is checked, shortly before activation

        Raise a errbot.utils.ValidationException in case of an error

        You should delete it if you're not using it to override any default behaviour
        """
        super(Teratail, self).check_configuration(configuration)

    def callback_connect(self):
        """
        Triggers when bot is connected

        You should delete it if you're not using it to override any default behaviour
        """
        pass

    def callback_message(self, message):
        """
        Triggered for every received message that isn't coming from the bot itself

        You should delete it if you're not using it to override any default behaviour
        """
        pass

    def callback_botmessage(self, message):
        """
        Triggered for every message that comes from the bot itself

        You should delete it if you're not using it to override any default behaviour
        """
        pass

    @webhook
    def example_webhook(self, incoming_request):
        """A webhook which simply returns 'Example'"""
        return "Example"

    # Passing split_args_with=None will cause arguments to be split on any kind
    # of whitespace, just like Python's split() does
    @botcmd(split_args_with=None)
    def example(self, message, args):
        """A command which simply returns 'Example'"""
        return "Example"

    @arg_botcmd('name', type=str)
    @arg_botcmd('--favorite-number', type=int, unpack_args=False)
    def hello(self, message, args):
        """
        A command which says hello to someone.

        If you include --favorite-number, it will also tell you their
        favorite number.
        """
        if args.favorite_number is None:
            return "Hello {name}".format(name=args.name)
        else:
            return "Hello {name}, I hear your favorite number is {number}".format(
                name=args.name,
                number=args.favorite_number,
            )

    def fetch_questions(self, tag):
        url = 'https://teratail.com/api/v1/tags/{}/questions?limit=5&page=1'.format(tag)
        resp = requests.get(url)
        data = resp.json()
        return [
            TeratailQuestion(q_['id'], q_['title'])
            for q_ in data['questions']
        ]

    def fetch_and_post(self):
        # Init
        self.log.debug('Start fetch by tag "{}"'.format(tag))
        msg_base = '【{}】{}\n{}'
        msg_to = self.build_identifier(self.config['NOTIFY_TO'])
        latest_id = self.get('latest_ids', {}).get(tag, 0)
        tag = self.config['CHECK_TAG']
        # Fetch and sort questions
        questions = self.fetch_questions(tag)
        questions = sorted(questions, key=lambda q: q.id)
        # Post only newer questions
        for q_ in questions:
            if q_.id <= latest_id:
                continue
            msg = msg_base.format(tag, q_.title, q_.url)
            self.send(msg_to, msg)
        # Save latest question-id for tag
        latest_ids = self.get('latest_ids', {})
        latest_ids[tag] = questions[-1].id
        self['latest_ids'] = latest_ids
        self.log.debug('End fetch by tag "{}"'.format(tag))
