import logging
import pathlib
import argparse
import pause
from datetime import datetime, time, timedelta
from bigtankcontroller.file_manager import ProjectFileManager
from bigtankcontroller.utils import configure_logger, generate_logging_decorator
from bigtankcontroller.config_manager import ConfigManager
from bigtankcontroller.e3v_controller import E3vController

log_dir = pathlib.Path('logs')
log_dir.mkdir(exist_ok=True)
logger = logging.getLogger()
configure_logger(logger, log_dir)
logging_decorator = generate_logging_decorator(logger)

class Runner:

    @logging_decorator
    def __init__(self, project_id):
        self.project_id = project_id
        self.config_manager = self._init_config_manager()
        self.config = self.config_manager.config_as_namespace()
        self.start_time = time(hour=self.config.start_hour)
        self.stop_time = time(hour=self.config.stop_hour)
        self.project_file_manager = self._init_project_file_manager()
        self.e3v_controller = E3vController(self.config, self.project_file_manager)

    @logging_decorator
    def _init_config_manager(self):
        config_manager = ConfigManager(pathlib.Path('resources') / 'config.yaml')
        if not config_manager.config_exists():
            logger.debug('generating blank config.yaml file')
            config_manager.generate_new_config()
            print("\nNo config file was found, which likely means this is the first time this device has been\n"
                  "used to run this code. A blank config.yaml file has been created in the resources directory.\n"
                  "Please fill it in now, then re-run this script.\n")
            exit(0)
        return config_manager

    @logging_decorator
    def _init_project_file_manager(self):
        if self.project_id == 'test_project':
            logger.warning('Using default projectID. A Unique PID is recommended for actual data collection')
        return ProjectFileManager(self.project_id, self.config)

    @logging_decorator
    def collect_data(self):
        while True:
            if self.start_time <= datetime.now().time() <= self.stop_time:
                self.active_mode()
            else:
                self.passive_mode()

    @logging_decorator
    def active_mode(self):
        self.e3v_controller.update_daily_video_dir()
        self.e3v_controller.start_recording()
        current_datetime = datetime.now()
        next_stop = current_datetime.replace(hour=self.stop_time.hour, minute=0, second=0, microsecond=0)
        logger.info(f'recording started. stop scheduled for {next_stop}')
        pause.until(next_stop)
        self.e3v_controller.stop_recording()
        logger.info('recording stopped')
        pause.seconds(10)

    @logging_decorator
    def passive_mode(self):
        self.project_file_manager.upload_data()
        logger.info('data upload complete')
        current_datetime = datetime.now()
        next_start = current_datetime.replace(hour=self.start_time.hour, minute=0, second=0, microsecond=0)
        if current_datetime.time() > self.stop_time:
            next_start = next_start + timedelta(days=1)
        logger.info(f'pausing until {next_start}')
        pause.until(next_start)

    @logging_decorator
    def test(self, iters=3):
        logger.info('initiating test')
        for i in range(iters):
            logger.info(f'running test iteration {i}')
            # active mode
            self.e3v_controller.set_video_dir(self.project_file_manager.video_dir / f'iter_{i}')
            self.e3v_controller.start_recording()
            current_datetime = datetime.now()
            next_stop = current_datetime + timedelta(seconds=30)
            logger.info(f'recording started. stop scheduled for {next_stop}')
            pause.until(next_stop)
            self.e3v_controller.stop_recording()
            logger.info('recording stopped')
            pause.seconds(10)

            #passive mode
            current_datetime = datetime.now()
            next_start = current_datetime + timedelta(seconds=30)
            self.project_file_manager.upload_data()
            logger.info('data upload complete')
            logger.info(f'pausing until {next_start}')
            pause.until(next_start)
        logger.info('test complete')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("project_id", help="project id", default='test_project', nargs='?')
    parser.add_argument('--test', action='store_true', help='run a test, then exit')
    args = parser.parse_args()
    runner = Runner(args.project_id)
    if args.test:
        runner.test()
    else:
        runner.collect_data()