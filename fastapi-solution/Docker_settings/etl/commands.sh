#!/bin/bash

source /etl/wait_services_up.sh
sleep 5 #нужно, чтобы успел выполниться скрипт по созданию схемы в БД
cd /etl/sqlite_to_postgres && python3 /etl/sqlite_to_postgres/load_data.py
#идем обратно и запускаем скрипт ETL
cd /etl && python3 /etl/etl_main.py