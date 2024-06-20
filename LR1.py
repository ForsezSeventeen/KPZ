import pandas as pd
from time import strftime
from os.path import exists

# Определение имени файла
file_path = 'filename.csv'

# Проверка существования файла и его чтение
if exists(file_path):
    data = pd.read_csv(file_path)
else:
    data = pd.DataFrame({'year': [], 'month': [], 'day': [], 'hour': [], 'minute': [], 'second': []})

# Получение текущего времени
current_time = strftime('%Y %m %d %H %M %S').split()

# Создание новой строки и добавление её в DataFrame
new_row = pd.DataFrame([current_time], columns=['year', 'month', 'day', 'hour', 'minute', 'second'])
data = pd.concat([data, new_row], ignore_index=True)

# Сохранение данных в CSV файл
data.to_csv(file_path, index=False)

# Вывод на экран
print(data)
