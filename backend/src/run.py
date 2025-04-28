import subprocess
import sys
import time
from multiprocessing import Process
from pathlib import Path


def run_service(module_name: str, port: int):
    """Запускает сервис как subprocess"""
    cmd = [sys.executable, "-m", f"src.{module_name}.main", "--port", str(port)]
    subprocess.run(cmd)


def run_service_in_process(module_name: str, port: int):
    """Альтернатива: запуск в отдельном процессе"""
    from uvicorn import run
    run(app=f"src.{module_name}.main:app", host="0.0.0.0", port=port)


if __name__ == "__main__":
    services = {
        "user_service": 8000,
        "profile_service": 8001,
        "session_service": 8002,
    }

    processes = []

    try:
        # Запуск всех сервисов
        for name, port in services.items():
            p = Process(target=run_service_in_process, args=(name, port))
            p.start()
            processes.append(p)
            time.sleep(1)  # Небольшая задержка между запусками

        print("Все сервисы запущены. Нажмите Ctrl+C для остановки")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nОстановка сервисов...")
        for p in processes:
            p.terminate()
        sys.exit(0)