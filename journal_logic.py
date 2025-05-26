import psutil
import time

class journal_logic():
    def __init__(self):
        pass
    def update_list(self):
        current_processes = {}
        
        for proc in psutil.process_iter(['pid', 'name', 'create_time']):
            try:
                name = proc.name()
                if not name:
                    continue
                    
                process_time = time.time() - proc.create_time()
                current_processes[name] = {
                    'name': name,
                    'time': process_time
                }
            except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                continue
        
        return current_processes