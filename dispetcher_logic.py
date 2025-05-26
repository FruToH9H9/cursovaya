import psutil
from PyQt6.QtGui import QColor, QBrush

class dispetcher_logic():
    def __init__(self):
        self.prev_io = {} 
        self.prev_net = {}
    
    def info_zadachi(self):
        process_dict = {}  #словарь чтобы обьединять процессы с 1 именем
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'] == "System Idle Process": #скип процессов к которым нет доступа(они выдают странные данные)
                    continue
                
                name = proc.info['name'] #имя процесса
                pid = proc.info['pid'] #айди процесса
                try:
                    memory_info = proc.memory_info().rss / 1024**2  #память
                except:
                    memory_info = 0
                
                #ЦП
                try:
                    cpu_percent = proc.cpu_percent(interval=0.0)/psutil.cpu_count(logical=False)
                except:
                    cpu_percent = 0
                #сделал ср арифметическое между двумя процессами тк большой интервал, должно чуть чуть улучшить результат
                
                #диск
                """Логика диска заключена в том, что выдается разница между двумя вычислениями, если выдавать просто значение в данный
                момент, то будет слишком огромное значение"""
                io_counters = proc.io_counters()
                prev_read, prev_write = self.prev_io.get(pid, (io_counters.read_bytes, io_counters.write_bytes))
                self.prev_io[pid] = (io_counters.read_bytes, io_counters.write_bytes) #сохраняем текущие
                disk_usage = ((io_counters.read_bytes - prev_read) + (io_counters.write_bytes-prev_write)) / 1024**2  # МБ/с
                
                #сеть
                net_counters = proc.io_counters()
                prev_read_bytes = self.prev_net.get(pid, net_counters.read_bytes) #тут логика аналогична диску
                prev_other_bytes = self.prev_net.get(pid, net_counters.other_bytes)
                net_speed = ((net_counters.other_bytes - prev_other_bytes) + (net_counters.read_bytes - prev_read_bytes)) * 8 / 10**6  # Мбит/с
                
                #энергопотребление
                power_usage = self.estimate_power_usage(cpu_percent, net_speed, memory_info)

#                if pid in process_dict:
#                    process_dict[name]['name'] = name
#                    process_dict[name]['cpu_percent'] += cpu_percent
#                    process_dict[name]['memory_info'] += memory_info
#                    process_dict[name]['disk_usage'] += disk_usage
#                    process_dict[name]['net_speed'] += net_speed
#                    process_dict[name]['power_usage'] = self.estimate_power_usage(
#                        process_dict[name]['cpu_percent'],
#                        process_dict[name]['net_speed'],
#                        process_dict[name]['memory_info']
#                    )
                process_dict[pid] = {
                    'name': name,
                    'cpu_percent': cpu_percent,
                    'memory_info': memory_info,
                    'disk_usage': disk_usage,
                    'net_speed': net_speed,
                    'power_usage': power_usage
                }

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        result = []
        for pid, values in process_dict.items():
            row = [
                pid,
                values['name'],  # Имя процесса   
                f"{values['cpu_percent']:.2f}%",  # Использование CPU в %
                f"{values['memory_info']:.2f} MB",  # Использование памяти в МБ
                f"{values['disk_usage']:.2f} MB/s",  # Скорость диска в МБ/с
                f"{values['net_speed']:.2f} Mb/s",  # Скорость сети в Мбит/c
                values['power_usage']  # Использование аккумулятора в статусе
            ]
            result.append(row)

        return result
    
    def estimate_power_usage(self, cpu: float, network: float, memory: float) -> str:
        power_score = (cpu * 0.7) + (network * 0.1) + (memory * 0.1)
        if power_score < 10:
            return "Очень низкое"
        elif power_score < 30:
            return "Низкое"
        elif power_score < 60:
            return "Среднее"
        elif power_score < 90:
            return "Высокое"
        else:
            return "Очень высокое"
        
    def paint(self, data: dict) -> None:
        value = float(data['value'].replace(data['sign'], ''))
        if data['compare_to'] < value < data['compare_to']*4:
            return data['item'].setBackground(QBrush(QColor('light green')))
        elif data['compare_to']*4 < value < data['compare_to']*16:  
            return data['item'].setBackground(QBrush(QColor('yellow')))
        elif value > data['compare_to']*16:  
            return data['item'].setBackground(QBrush(QColor('red')))
