import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and not "/.git/" in event.src_path and not "/.tmp/" in event.src_path:
            print(f"[MODIFIED] {event.src_path}")
    def on_created(self, event):
        if not event.is_directory and not "/.git/" in event.src_path and not "/.tmp/" in event.src_path:
            print(f"[CREATED] {event.src_path}")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    observer = Observer()
    observer.schedule(ChangeHandler(), path, recursive=True)
    observer.start()
    print(f"Watching for file changes in {path}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
