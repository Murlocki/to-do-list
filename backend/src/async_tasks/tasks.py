from .celery_app import app  # Относительный импорт

from .worker_logic import process_users_chunk


@app.task(bind=True, name='src.async_tasks.tasks.process_chunk')
def process_chunk(self, chunk_index):
    return process_users_chunk(chunk_index)

@app.task(name='src.async_tasks.tasks.dispatch_chunks')
def dispatch_chunks():
    for i in range(1):
        process_chunk.delay(i)