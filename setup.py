from setuptools import setup, find_packages

setup(
    name='ClipMaster',           # Имя вашего пакета
    version='0.1.0',             # Версия (можно обновлять позже)
    packages=find_packages(),    # Автоматически находит пакеты
    install_requires=[           # Зависимости из requirements.txt
        'PyQt5',
        'python-vlc',
        'moviepy'
    ],
    entry_points={               # Создает команду для запуска
        'console_scripts': [
            'clipmaster=clipmaster.app:run'
        ]
    },
)