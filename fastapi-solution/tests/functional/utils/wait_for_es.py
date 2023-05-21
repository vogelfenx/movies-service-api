import time
from os import getenv

from elasticsearch import Elasticsearch

es_host = getenv("ELASTIC_HOST", default="localhost")
es_port = getenv("ELASTIC_PORT", default=9200)

if __name__ == "__main__":
    es_client = Elasticsearch(
        hosts=f"http://{es_host}:{es_port}",
        verify_certs=False,
    )

    print(f"try elastic on {es_host}:{es_port}")
    while True:
        print("ping elasticsearch")
        if es_client.ping():
            break
        time.sleep(1)
