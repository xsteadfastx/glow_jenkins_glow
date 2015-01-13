from bottle import Bottle
from threading import Thread
from time import sleep
from piglow import PiGlow
from urlparse import urljoin
import requests


# GLOBALS
JENKINS_HOST = 'localhost'
JENKINS_PORT = 8080

API_HOST = '0.0.0.0'
API_PORT = 8000


# piglow stuff
piglow = PiGlow()


def build_url(url):
    '''Building Jenkins API urls.
    '''
    base = 'http://{}:{}'.format(JENKINS_HOST, JENKINS_PORT)
    return urljoin(base, url)


class GlowJenkinsGlow(Bottle):

    def __init__(self):
        super(GlowJenkinsGlow, self).__init__()

        # where the current state is saved
        self.state = 'updating'

        # all the api bottle routes and its callbacks
        self.route('/', callback=self._api_index)
        self.route('/state/<name>', callback=self._api_state)

    def _api_index(self):
        '''Index function for the API. Just returns the current state.
        '''
        return self.state

    def _api_state(self, name):
        '''Function to set state through the API.
        '''
        if name in ['success', 'fail', 'building']:
            self.state = name
        else:
            pass
        return self.state

    @staticmethod
    def led_success():
        '''Makes all green leds shine on success.
        '''
        piglow.all(0)

        for i in [4, 10, 16]:
            piglow.led(i, 5)
            sleep(5)
            piglow.all(0)

    @staticmethod
    def led_fail():
        '''Makes all red leds on and off on fail.
        '''
        piglow.all(0)

        piglow.red(10)
        sleep(1)

        piglow.all(0)

    @staticmethod
    def led_updating():
        '''Little spinner for updating state.
        '''
        piglow.all(0)

        for i in [18, 12, 6]:
            piglow.led(i, 5)
            sleep(0.1)
            piglow.all(0)

    @staticmethod
    def led_building():
        '''Let some leds dance while jenkins is building.
        '''
        piglow.all(0)

        for i in [1, 2, 3, 4, 5,
                  7, 8, 9, 10, 11,
                  13, 14, 15, 16, 17, 18, 12, 6]:
            piglow.led(i, 10)
            sleep(0.1)

    def led_state(self):
        '''Loop for constant state checking and led handling.
        '''
        while True:
            if self.state == 'updating':
                self.led_updating()
            elif self.state == 'building':
                self.led_building()
            elif self.state == 'success':
                self.led_success()
            elif self.state == 'fail':
                self.led_fail()

    @staticmethod
    def if_building():
        '''Asks the Jenkins API if something is building right now.
        '''
        building = False
        r = requests.get(build_url('/api/json'))
        for i in r.json()['jobs']:
            if 'anime' in i['color']:
                building = True
        return building

    @staticmethod
    def all_items():
        '''Getting all project items out of the Jenkins API.
        '''
        r = requests.get(build_url('/api/json'))
        return [i['name'] for i in r.json()['jobs']]

    @staticmethod
    def latest_job(name):
        '''Getting the latest job for a project item out of Jenkins API.
        '''
        r = requests.get(build_url('/job/{}/api/json'.format(name)))
        return sorted([i['number'] for i in r.json()['builds']],
                      reverse=True)[0]

    @staticmethod
    def job_success(name, job):
        '''Asks Jenkins API if a job was building successful.
        '''
        result = False
        r = requests.get(build_url('/job/{}/{}/api/json'.format(name, job)))

        if r.json()['result'] == 'SUCCESS':
            result = True

        return result

    def overall_success(self):
        '''Walks through all the latest jobs for all projects and looks
        if they was successful.
        '''
        success = False
        result_list = []
        for item in self.all_items():
            result = self.job_success(item, self.latest_job(item))
            result_list.append(result)
        if False not in result_list:
            success = True

        return success

    def jenkins_state(self):
        '''Requests Jenkins state every 10 seconds.
        '''
        while True:
            try:
                if self.if_building():
                    self.state = 'building'
                else:
                    if self.overall_success():
                        self.state = 'success'
                    else:
                        self.state = 'fail'
            except:
                self.state = 'updating'

            sleep(10)


def main():
    app = GlowJenkinsGlow()

    # starting API thread
    api = Thread(target=app.run, kwargs={'host': API_HOST,
                                         'port': API_PORT})
    api.start()

    # starting led handling thread
    led_state = Thread(target=app.led_state)
    led_state.start()

    # starting jenkins watcher thread
    jenkins_state = Thread(target=app.jenkins_state)
    jenkins_state.start()


if __name__ == '__main__':
    main()
