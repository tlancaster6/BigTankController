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
    def get_cameras(self):
        """Get list of all cameras and their status"""
        try:
            response = requests.get(self.watchtowerurl + '/api/cameras', verify=False, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f'Failed to get cameras: {response.status_code}')
                return None
        except requests.RequestException as e:
            logger.error(f'Network error getting cameras: {e}')
            return None

    @logging_decorator  
    def validate_cameras_ready(self):
        """Verify all configured cameras are connected and ready for recording"""
        cameras = self.get_cameras()
        if not cameras:
            logger.error('Cannot retrieve camera list from Watchtower')
            return False
        
        # Create a dictionary mapping serial numbers to camera info
        camera_dict = {}
        for cam in cameras:
            hostname = cam.get('Hostname', '')
            if hostname.endswith('.local.'):
                serial = hostname[:-7]  # Remove '.local.' suffix
                camera_dict[serial] = cam
        
        # Check that all our cameras are present and ready
        for serial in self.cam_serials:
            if serial not in camera_dict:
                logger.error(f'Camera {serial} not found in system')
                return False
            
            cam_info = camera_dict[serial]
            
            # Check camera status fields
            if cam_info.get('Alivestate') != 3:
                logger.error(f'Camera {serial} not alive (Alivestate: {cam_info.get("Alivestate")})')
                return False
                
            if cam_info.get('Runstate') != 1:
                logger.error(f'Camera {serial} not running (Runstate: {cam_info.get("Runstate")})')
                return False
                
            if not cam_info.get('BoundTo', {}).get('Valid'):
                logger.error(f'Camera {serial} not bound to controller')
                return False
        
        logger.info(f'All {len(self.cam_serials)} cameras ready for recording')
        return True

    @logging_decorator
    def start_recording(self, retries=2):
        # Quick validation that cameras are still connected
        if not self.validate_cameras_ready():
            logger.warning('Camera validation failed, attempting recording anyway')
        
        response = requests.post(self.watchtowerurl + '/api/cameras/action',
                                 data={'SerialGroup[]': self.cam_serials,
                                       'Action': 'RECORDGROUP'}, verify=False)
        if not response.status_code == 200:
            if not retries:
                raise RuntimeError(f'Failed to start recording: {response.status_code}')
            logger.warning(f'Failed to start recording, retrying in 10s.')
            time.sleep(10)
            self.start_recording(retries=retries-1)
        
        logger.info(f'Recording started for {len(self.cam_serials)} cameras')

    @logging_decorator  
    def stop_recording(self, retries=2):
        response = requests.post(self.watchtowerurl + '/api/cameras/action',
                                 data={'SerialGroup[]': self.cam_serials,
                                       'Action': 'STOPRECORDGROUP'}, verify=False)
        if not response.status_code == 200:
            if not retries:
                raise RuntimeError(f'Failed to stop recording: {response.status_code}')
            logger.warning(f'Failed to stop recording, retrying in 10s.')
            time.sleep(10)
            self.stop_recording(retries=retries-1)
        
        logger.info(f'Recording stopped for {len(self.cam_serials)} cameras')


