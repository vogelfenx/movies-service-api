import logging.handlers

from config import etl_conf

log = logging.getLogger('base_log')
log.setLevel(logging.DEBUG)

file_handler = logging.handlers.RotatingFileHandler(
    etl_conf.log_file_path
)
logs = logging.StreamHandler()
logs.setLevel(logging.DEBUG)
fmtstr = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
fmtdate = '%H:%M:%S'
formatter = logging.Formatter(fmtstr, fmtdate)
file_handler.setFormatter(formatter)
logs.setFormatter(formatter)

log.addHandler(file_handler)
log.addHandler(logs)
