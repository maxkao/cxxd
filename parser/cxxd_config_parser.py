import json
import logging
import os

class CxxdConfigParser():
    def __init__(self, cxxd_config_filename):
        self.blacklisted_directories = self._extract_blacklisted_directories(cxxd_config_filename) if os.path.exists(cxxd_config_filename) else []
        logging.info('Blacklisted directories {0}'.format(self.blacklisted_directories))

    def get_blacklisted_directories(self):
        return self.blacklisted_directories

    def is_file_blacklisted(self, filename):
        for dir in self.blacklisted_directories:
            if filename.startswith(dir):
                return True
        return False

    def _extract_blacklisted_directories(self, cxxd_config_filename):
        with open(cxxd_config_filename) as f:
            config = json.load(f)
            base_dir = os.path.dirname(os.path.realpath(cxxd_config_filename))
            dirs = [os.path.join(base_dir, dir) for dir in config['indexer']['exclude-dirs']]
        return dirs
