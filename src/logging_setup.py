import logging
import os

def setup_logging(log_filename):
    # Создание директории для логов, если она не существует
    os.makedirs('logs', exist_ok=True)
    
    # Настройка логирования
    logging.basicConfig(filename=f'logs/{log_filename}', level=logging.DEBUG, 
                        format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')
