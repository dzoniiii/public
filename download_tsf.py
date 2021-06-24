# -*- coding: utf-8 -*-
#import json
import os
import time
from datetime import datetime
from threading import Thread, Semaphore
import requests
import getpass
import urllib3
import xml.etree.ElementTree as ET


def retry(func):
    """Helper to retry if download fails"""
    def retried_func(*args, **kwargs):
        MAX_TRIES = 3
        tries = 0
        while True:
            resp = func(*args, **kwargs)
            if resp.status_code != 200 and tries < MAX_TRIES:
                tries += 1
                print('Retry #{}:'.format(tries), resp.url)
                continue
            break
        return resp
    return retried_func


class Client():
    def __init__(self, device_ip, user, password):
        self.device_ip = device_ip
        self.panos_api_key = self.generate_api_key(user, password)
        self.hostname = self.get_hostname()

    @property
    def base_url(self):
        """Common base URL"""
        return 'https://{}/api/'.format(self.device_ip)

    def generate_api_key(self, user, password):
        """Generate API key given user credentials"""
        payload = {'type': 'keygen', 'user': user, 'password': password}
        post_request = requests.post(self.base_url, data=payload, verify=False)
        post_request.raise_for_status()
        xml = ET.fromstring(post_request.text)
        return xml.findtext('result/key')

    def get_hostname(self):
        """Retreive hostname from system info"""
        payload = {'type': 'op', 'cmd': '<show><system><info></info></system></show>', 'key': self.panos_api_key}
        post_request = requests.post(self.base_url, data=payload, verify=False)
        post_request.raise_for_status()
        response = ET.fromstring(post_request.text)
        return response.findtext('result/system/hostname')

    #def create_export_job(self, category='tech-support'):
    def create_export_job(self, category='device-state`'):
        """Create an export job.

        Args:
            category: 'tech-support' or 'stats-dump'

        Returns:
            A job ID.
        """
        payload = {
            'key': self.panos_api_key,
            'type': 'export',
            'category': category
        }
        get_request = requests.get(self.base_url, params=payload, verify=False)
        get_request.raise_for_status()
        response = ET.fromstring(get_request.text)
        return response.findtext('result/job')

    def job_complete(self, job_id):
        """Checks whether a job has finished running."""
        payload = {
            'key': self.panos_api_key,
            'type': 'op',
            'cmd': '<show><jobs><id>{}</id></jobs></show>'.format(job_id),
        }
        get_request = requests.get(self.base_url, params=payload, verify=False)
        get_request.raise_for_status()
        response = ET.fromstring(get_request.text)
        return response.findtext('result/job/status') == 'FIN'

    @retry
    def get_file_content(self, job_id, category):
        """Retreive file contents via API call."""
        payload = {
            'key': self.panos_api_key,
            'type': 'export',
            'category': category,
            'action': 'get',
            'job-id': job_id,
        }
        return requests.get(self.base_url, params=payload, verify=False, stream=True)

    def save_file(self, job_id, category):
        """Saves file to disk"""
        get_request = self.get_file_content(job_id, category)
        extension = '.tgz' if category == 'tech-support' else '.tar.gz'
        dt = datetime.strftime(datetime.today(), '%Y%m%d_%H%M')
        filename = '{dt}_{category}_{hostname}{extension}'.format(
            dt=dt, category=category, hostname=self.hostname, extension=extension)
        if get_request.status_code != 200:
            print('Unable to download', filename)
            return
        with open(os.path.join(os.path.dirname(__file__), filename), 'wb') as fd:
            for chunk in get_request.iter_content(chunk_size=1024):
                fd.write(chunk)
        print('Saved file', filename)

    def export_tsf_sdf(self):
        """Exports Tech Support File and Stats Dump File"""
        for category in ['tech-support']:
            job = self.create_export_job(category)
            while not self.job_complete(job):
                time.sleep(5)
            self.save_file(job, category)


def run(device_ip,user,password):
    """Helper to instantiate client and call export_tsf_sdf method"""
    screen_lock.acquire()
    print('Connecting to ', device_ip)
    screen_lock.release()
    c = Client(device_ip, user, password)
    c.export_tsf_sdf()


if __name__ == '__main__':
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    screen_lock = Semaphore(value=1)
    user = input('Username: ')
    password = getpass.getpass()
    device_ip = input('Device IP: ')
    run(device_ip,user,password)
    # threads = []
    # with open(os.path.join(os.path.dirname(__file__), 'devices.json')) as jsonfile:
    #    devices = json.load(jsonfile)
    #    for row in devices:
    #        t = Thread(target=run, args=(row,password))
    #        t.start()
    #        threads.append(t)
    #for t in threads:
    #    t.join()
    print('DONE!')
