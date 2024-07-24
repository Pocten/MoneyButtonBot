# MoneyButtonBot

MoneyButtonBot - это автоматизированный бот для торговли акциями на основе различных стратегий, таких как Supertrend и Trendlines with Breaks. Проект поддерживает бэктестирование на исторических данных и визуализацию результатов.

## Структура проекта

- `config/`
  - `config.py`: Конфигурационный файл с параметрами для бота и стратегий.
- `data/`: Директория для хранения загруженных данных.
- `logs/`: Директория для хранения логов.
- `strategies/`
  - `base_strategy.py`: Базовый класс для всех стратегий.
  - `supertrend.py`: Реализация стратегии Supertrend.
  - `trendlines_with_breaks.py`: Реализация стратегии Trendlines with Breaks.
- `tests/`: Директория для тестов.
- `utils/`
  - `data_loader.py`: Скрипт для загрузки и сохранения исторических данных.
  - `logger.py`: Настройка логирования.
  - `plotter.py`: Скрипт для создания и сохранения графиков.
  - `results_saver.py`: Скрипт для сохранения результатов торговли.
- `bot.py`: Главный скрипт для запуска бота.
- `.gitignore`: Файл, определяющий, какие файлы/каталоги игнорировать Git.
- `Dockerfile`: Dockerfile для контейнеризации приложения.
- `README.md`: Этот файл.
- `requirements.txt`: Список зависимостей для установки через pip.

## Установка

1. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш_репозиторий/moneybuttonbot.git
    ```
2. Перейдите в директорию проекта:
    ```bash
    cd moneybuttonbot
    ```
3. Установите зависимости:
    ```bash
    pip install -r requirements.txt
    ```
4. Запустите бот:
    ```bash
    python bot.py
    ```
## Настройка

Все настройки находятся в файле config/config.py. Вы можете изменить список тикеров, интервалы, начальный баланс и параметры стратегий.

### Структура конфигурационного файла
`config.py` содержит следующие параметры:
```python
TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'BABA', 'V', 'JNJ', 'WMT', 'NVDA']

INTERVALS = {
    '1m': 7,
    '5m': 60,
    '15m': 60,
    '30m': 60,
    '1h': 730,
    '1d': None,
    '1wk': None,
    '1mo': None
}

# Общие параметры
INITIAL_BALANCE = 1000  # Начальный баланс в долларах
WHOLE_SHARES_ONLY = True  # Только целые акции (True) или доли акций (False)

# Параметры для стратегии Supertrend
BOLLINGER_PERIOD = 20  # Период для расчета Bollinger Bands
BOLLINGER_NUM_STD_DEV = 2  # Количество стандартных отклонений для Bollinger Bands
SUPER_TREND_PERIOD = 10  # Период для расчета Supertrend
ATR_MULTIPLIER = 3  # Множитель для ATR
SUPER_TREND_TAKE_PROFIT_PERCENT = 0.20  # 20% Take Profit
SUPER_TREND_STOP_LOSS_PERCENT = 0.10  # 10% Stop Loss

# Параметры для стратегии Trendlines with Breaks
TRENDLINES_LENGTH = 18  # Длина для расчета пиков и впадин
TRENDLINES_MULTIPLIER = 1.0  # Множитель для расчета наклона
TRENDLINES_CALC_METHOD = 'Atr'  # Опции: 'Atr', 'Stdev', 'Linreg'
TRENDLINES_BACKPAINT = True  # Раскрашивать ли линии в прошлом
TRENDLINES_TRAIL_PERCENT_TP = 5.0  # 5% Take Profit
TRENDLINES_TRAIL_PERCENT_SL = 3.0  # 3% Stop Loss
```

## Описание стратегий
### Supertrend Strategy

Реализация стратегии Supertrend, основанная на Bollinger Bands и Average True Range (ATR). Параметры стратегии можно настроить в `config.py`.

### Trendlines with Breaks Strategy

Реализация стратегии, использующей трендовые линии и пробои. Параметры стратегии можно настроить в `config.py`.

## Логирование 

Все логи сохраняются в директорию `logs/`. Вы можете настроить уровень логирования и формат в `utils/logger.py`.

## Визуализация результатов

Для визуализации используются библиотеки Plotly и mplfinance. Графики сохраняются в формате HTML и находятся в директории `data/results_of_strategies/`.
