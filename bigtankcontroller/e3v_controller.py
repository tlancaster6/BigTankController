import urllib3
import requests
import time
import logging
from bigtankcontroller.utils import generate_logging_decorator

logger = logging.getLogger(__name__)
logging_decorator = generate_logging_decorator(logger)

class E3vController:
    @logging_decorator
    def __init__(self, config, project_file_manager):
        self.watchtowerurl = 'https://localhost:4343'
        self.cam_serials = config.cam_serials
        self.project_file_manager = project_file_manager
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @logging_decorator
    def update_daily_video_dir(self, retries=2):
        dest = self.project_file_manager.update_daily_video_dir().resolve()
        logger.debug(f'setting save path to {dest}')
        response = self.set_video_dir(dest)
        if not response.status_code == 200:
            if not retries:
                raise RuntimeError(f'failed to update daily video directory')
            logger.warning(f'daily video dir failed to update. retrying in 10s')
            time.sleep(10)
            self.update_daily_video_dir(retries=retries-1)

    @logging_decorator
    def set_video_dir(self, dest):
        response = requests.post(self.watchtowerurl + '/api/sessions/rename',
                                 data={'Filepath': str(dest)}, verify=False)
        return response

    @logging_decorator
    def start_recording(self, retries=2):
        response = requests.post(self.watchtowerurl + '/api/cameras/action',
                                 data={'SerialGroup[]': self.cam_serials,
                                       'Action': 'RECORDGROUP'}, verify=False)
        if not response.status_code == 200:
            if not retries:
                raise RuntimeError(f'failed to start recording')
            logger.warning(f'failed to start recording retrying in 10s.')
            time.sleep(10)
            self.start_recording(retries=retries-1)

    @logging_decorator
    def stop_recording(self, retries=2):
        response = requests.post(self.watchtowerurl + '/api/cameras/action',
                                 data={'SerialGroup[]': self.cam_serials,
                                       'Action': 'STOPRECORDGROUP'}, verify=False)
        if not response.status_code == 200:
            if not retries:
                raise RuntimeError(f'failed to stop recording')
            logger.warning(f'failed to stop recording. retrying in 10s.')
            time.sleep(10)
            self.stop_recording(retries=retries-1)


