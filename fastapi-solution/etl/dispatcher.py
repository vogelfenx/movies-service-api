from config import etl_conf
from storage import JsonFileStorage
from connectors import ESconnector, PGconnector
from transform import transformer
from logger import log


log = log.getChild(__name__)


class Dispatcher:

    def __init__(self, storage: JsonFileStorage):
        self.storage = storage(etl_conf.storage_file_path)
        self.state = self.storage.retrieve_state()

        if not self.state.keys():
            self.state = etl_conf.state_template

    def set_state(self) -> None:
        self.storage.save_state(self.state)

    def get_state(self) -> None:
        self.state = self.storage.retrieve_state()

    def rotate_state(self) -> None:
        for etl_job in self.state.keys():
            self.state[etl_job]['start_load'] = self.state[etl_job]['end_load']
            self.state[etl_job]['end_load'] = None
            self.state[etl_job]['is_done'] = False

    def etl_process(self, etl_job, src_connector, trg_connector):

        if not self.state[etl_job]['end_load']:
            self.state[etl_job]['end_load'] = src_connector.get_current_dttm()
        self.set_state()

        log.info('Start extraction process')
        extracted_data = src_connector.get_upd_films(extr_type=etl_job,
                                                     etl_param=[self.state[etl_job]['start_load'],
                                                                self.state[etl_job]['end_load']])
        log.info('Extraction process is finished')
        log.info('Start transform and loading process')
        for batch in extracted_data:
            trg_connector.load(transformer(batch))
        log.info('Loading finished!')
        self.state[etl_job]['is_done'] = True
        self.set_state()

        log.info(f'ETL job {etl_job} is finished')

    def run_etl(self):
        with ESconnector() as es, PGconnector() as pg:
            if not es.has_index():
                log.info('Target index is not exists. Creating...')
                es.create_index()

            for etl_job in self.state.keys():
                if not self.state[etl_job]['is_done']:
                    log.info(f'Starting {etl_job} ETL job...')
                    self.etl_process(etl_job=etl_job,
                                     src_connector=pg,
                                     trg_connector=es)
                else:
                    log.info(f'ETL job {etl_job} is passed by state status. Go next.')

        self.rotate_state()
        self.set_state()
