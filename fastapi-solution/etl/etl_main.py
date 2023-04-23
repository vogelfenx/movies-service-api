from time import sleep

from config import etl_conf
from dispatcher import Dispatcher
from storage import JsonFileStorage
from logger import log


log = log.getChild(__name__)

log.info('Etl daemon is started.')
while True:
    disp = Dispatcher(storage=JsonFileStorage)
    log.info('Start another etl iteration')
    disp.run_etl()
    log.info(f'Etl iteration is finished. Sleep for {etl_conf.sleep_time}s...')
    sleep(etl_conf.sleep_time)
