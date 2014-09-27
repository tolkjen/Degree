from celery import Celery, current_task
from time import sleep

app = Celery('proj', broker='amqp://guest@localhost/')

app.conf.update(
    CELERY_RESULT_BACKEND = 'amqp://',
	CELERY_IGNORE_RESULT = False,
	CELERY_RESULT_PERSISTENT = True,
	CELERY_TRACK_STARTED = True,

	CELERY_TASK_SERIALIZER = 'json',
	CELERY_RESULT_SERIALIZER = 'json',
	CELERY_ACCEPT_CONTENT=['json'],
	CELERY_ENABLE_UTC = True,
)

@app.task
def sample_task():
	for i in range(100):
		current_task.update_state(state="PROGRESS", meta={"value": i})
		sleep(0.1)
