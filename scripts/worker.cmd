set QUEUE_URL=amqp://myuser:mypassword@192.168.1.9:5672/myvhost
celery worker -A mltool.tasks
