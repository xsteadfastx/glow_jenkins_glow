from bottle import Bottle
from threading import Thread
from time import sleep


class GlowJenkinsGlow(Bottle):

    def __init__(self):
        super(GlowJenkinsGlow, self).__init__()

        self.state = 'FOOBAR'

        self.route('/', callback=self._api_index)
        self.route('/moin/<name>', callback=self._api_moin)

    def _api_index(self):
        return 'index'

    def _api_moin(self, name):
        self.state = name
        return 'moin {}'.format(name)

    def hello_world(self):
        while True:
            print(self.state)
            sleep(1)


def main():
    app = GlowJenkinsGlow()

    api = Thread(target=app.run, kwargs={'host': 'localhost',
                                         'port': 8080})
    api.start()

    hello = Thread(target=app.hello_world)
    hello.start()


if __name__ == '__main__':
    main()
