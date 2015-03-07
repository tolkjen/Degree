import os

BROKER_URL = os.environ.get('RABBITMQ_BIGWIG_TX_URL', 'amqp://guest@localhost//')
CELERY_RESULT_BACKEND = os.environ.get('RABBITMQ_BIGWIG_RX_URL', 'amqp://guest@localhost//')
#CELERY_ACCEPT_CONTENT = ['json']
#CELERY_TASK_SERIALIZER = 'json'
CELERY_TRACK_STARTED = True
