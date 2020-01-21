from elasticsearch import Elasticsearch


class ESWrapper:
    """
    Elasticsearch wrapper
    """
    @staticmethod
    def connect_elasticsearch(host='es', port=9200):
        """
        Establish connection with Elasticsearch database.
        """
        es = None
        es = Elasticsearch([{'host': host, 'port': port}])
        if es.ping():
            print('Connected')
        else:
            print('Cannot connect')
        return es
