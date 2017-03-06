import logging


def init_file_and_console_logging(console_log_level, details_file_name, summary_file_name):
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    details_file_handler = logging.FileHandler("{0}".format(details_file_name))
    details_file_handler.setFormatter(log_formatter)
    details_file_handler.setLevel(logging.INFO)
    root_logger.addHandler(details_file_handler)

    summary_file_handler = logging.FileHandler("{0}".format(summary_file_name))
    summary_file_handler.setFormatter(log_formatter)
    summary_file_handler.setLevel(logging.WARNING)
    root_logger.addHandler(summary_file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(console_log_level)
    root_logger.addHandler(console_handler)
