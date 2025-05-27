import pathlib
import sys
import datetime
import logging
import subprocess as sp
import shutil
import cv2
import time
from bigtankcontroller.utils import generate_logging_decorator

# establish  filesystem locations
FILE = pathlib.Path(__file__).resolve()
REPO_ROOT_DIR = FILE.parent.parent  # repository root
DEFAULT_DATA_DIR = REPO_ROOT_DIR / 'projects'
if str(REPO_ROOT_DIR) not in sys.path:
    sys.path.append(str(REPO_ROOT_DIR))

logger = logging.getLogger(__name__)
logging_decorator = generate_logging_decorator(logger)

class ProjectFileManager:

    @logging_decorator
    def __init__(self, project_id, config):

        self.project_id = project_id
        self.project_dir = DEFAULT_DATA_DIR / project_id
        self.video_dir = self.project_dir / 'videos'
        self.log_dir = REPO_ROOT_DIR / 'logs'
        self.cloud_project_dir = pathlib.PurePosixPath(config.cloud_data_dir) / self.project_id
        self.cloud_video_dir = self.cloud_project_dir / 'videos'
        self.cloud_log_dir = self.cloud_project_dir / 'logs'
        self.daily_video_dir = self.update_daily_video_dir()

    @logging_decorator
    def update_daily_video_dir(self):
        daily_dir_path = self.video_dir / 'originals' / datetime.date.today().isoformat()
        daily_dir_path.mkdir(exist_ok=True, parents=True)
        logger.debug(f'daily video dir path updated to {daily_dir_path}')
        self.daily_video_dir = daily_dir_path
        return daily_dir_path

    @logging_decorator
    def prep_videos_for_upload(self, rotate=True, video_dir=None):
        if not video_dir:
            video_dir = self.daily_video_dir
        logger.debug(f'prepping videos from {str(video_dir)} for upload')
        video_paths = video_dir.glob('*.mp4')
        for vp in video_paths:
            try:
                self.prep_video(vp, rotate=rotate)
            except Exception as e:
                logger.warning(f'video prep failed for {vp.name} with exception {e}')

    @logging_decorator
    def prep_video(self, video_path, rotate=True):
        start = time.time()
        vp = video_path
        logger.debug(f'prepping {vp.stem}')
        output_path = pathlib.Path(str(vp).replace('originals', 'prepped'))
        output_path.parent.mkdir(exist_ok=True, parents=True)
        cap = cv2.VideoCapture(str(vp))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (frame_width, frame_height))
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if rotate:
                frame = cv2.rotate(frame, cv2.ROTATE_180)
            writer.write(frame)
        cap.release()
        writer.release()
        logger.debug(f'prep completed in {time.time() - start} seconds')
        return 0


    @logging_decorator
    def upload_data(self):
        # self.prep_videos_for_upload()
        logger.debug('moving videos to cloud')
        video_move_command = ['rclone', 'move', str(self.video_dir.resolve()), str(self.cloud_video_dir)]
        video_move_out = sp.run(video_move_command, capture_output=True, encoding='utf-8')
        if video_move_out.stderr:
            logger.warning(f'moving videos to cloud may have failed: \n {video_move_out.stderr}')
        else:
            logger.debug('video move completed')
        logger.debug('copying logs to project folder')
        shutil.copytree(str(self.log_dir), str(self.project_dir / 'logs'), dirs_exist_ok=True)
        logger.debug('moving copied logs to cloud')
        log_move_command = ['rclone', 'move', str(self.project_dir / 'logs'), str(self.cloud_log_dir)]
        log_move_out = sp.run(log_move_command, capture_output=True, encoding='utf-8')
        if log_move_out.stderr:
            logger.warning(f'copying logs to cloud may have failed: \n {log_move_out.stderr}')
        else:
            logger.debug('log copy completed')



