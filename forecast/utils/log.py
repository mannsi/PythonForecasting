import logging


def init_file_and_console_logging(console_log_level, file_log_level, file_name):
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("{0}".format(file_name))
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(file_log_level)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(console_log_level)
    root_logger.addHandler(console_handler)
