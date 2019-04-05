import os
import yaml

LOG_DIR = os.environ['LOG_DIR']
dirname = os.path.join(os.path.dirname(__file__),'..')

class LoggerConfig:
    def get_logger_config(self):
        with open(os.path.join(dirname, 'logging.yaml'), 'r') as f:
            config = yaml.safe_load(f.read())
            info_file = config['handlers']['info_file_handler']['filename']
            error_file = config['handlers']['error_file_handler']['filename']
            config['handlers']['info_file_handler']['filename']=os.path.join(LOG_DIR, info_file)
            config['handlers']['error_file_handler']['filename']=os.path.join(LOG_DIR, error_file)
        return config