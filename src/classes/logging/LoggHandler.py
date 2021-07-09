from time import time, ctime
import logging
import os


class LoggHandler:

    def __init__(self, date):
        self.date = date

    def logg_driver_error(self, error, network_name, submissions_type):
        log_path = F"Logs/{self.date}/{network_name}/{submissions_type}/"
        self.logg_error(error, log_path)

    def logg_ui_error(self, error):
        log_path = F"Logs/{self.date}/UI_Web_Server/"
        self.logg_error(error, log_path)

    def logg_error(self, error, log_path):
        # create logs file if not found
        if not os.path.exists(log_path):
            os.makedirs(log_path)

        # create error logger
        logging.basicConfig(
            filename=F'{log_path}/errors.log', level=logging.INFO)

        # log error
        logging.error(
            F'\nError: {ctime(time())}\n{str(error)}\n', exc_info=True)
