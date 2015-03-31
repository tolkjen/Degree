set QUEUE_URL=amqp://myuser:mypassword@192.168.1.13:5672/myvhost
celery worker -A mltool.tasks
