set QUEUE_URL=amqp://myuser:mypassword@192.168.1.7:5672/myvhost
celery worker -A tools.worker
