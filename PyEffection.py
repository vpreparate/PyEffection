'''
Это типа мы цепляем модуль sys,
он нужен чтобы рулить системными приколами — там путь, выход из проги,
такие дела.
'''
import sys
'''
"""
Смотри, тут мы затаскиваем из PyQt5.QtWidgets кучу деталей,
это такие кирпичи для постройки окна.

QWidget — это типа сама коробка окна.

QVBoxLayout и QHBoxLayout — это разметка,
чтоб виджеты ровненько лежали по вертикали или горизонтали.

QLabel — текст в окошке.

QPushButton — кнопка, на которую жмёшь.

QComboBox — выпадающий список.

QProgressBar — полоска загрузки, чтобы видно было, как движуха идёт.

QFileDialog — окно для выбора файла.

QApplication — главный движок всего окна.

QMessageBox — всплывающие сообщения (типа "брат, ошибка").

QGroupBox — рамочка для группировки элементов.

QSpacerItem, QSizePolicy — штуки для того,
чтоб правильно растягивались/сжимались элементы.
"""
'''
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QProgressBar,
    QFileDialog, QApplication, QMessageBox, QHBoxLayout, QGroupBox, QSpacerItem, QSizePolicy,
    QDialog, QComboBox, 
)
"""
Тут мы берём ядро Qt:

Qt — константы всякие (например, выравнивание текста).

QThread — запуск отдельного потока,
чтоб прога не зависала, пока видос обрабатывается.

pyqtSignal — типа сигнализация: "эй, поток закончил, шли инфу".
"""
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
#Это про шрифты, чтоб текст выглядел не как у бомжа на заборе.
from PyQt5.QtGui import QFont, QMovie
"""
— os, pathlib.Path — возня с файлами и папками.
— shutil — копировать, двигать, удалять файлы пачками.
— subprocess — запускать левую прогу типа "ffmpeg".
— re — регулярки, искать шаблоны в тексте.
— cv2 — OpenCV, мощная штука для ковыряния картинок и видео.
"""
import os
from pathlib import Path
import shutil
import subprocess
import re
import cv2
'''
Тут мы тянем moviepy, он нужен для работы с видосами.
VideoFileClip — открыть видос, VideoClip — сделать новый.
'''
from moviepy.editor import VideoFileClip, VideoClip # 1.0.3 version moviepy
"""

numpy — чтоб с цифрами и матрицами работать по красоте.

math — математика, типа синусы-косинусы.

random — ну, рандомчик, чтоб чё-то случайно происходило.
"""
import numpy as np
import math
import random



'''
Это мы мутим свой класс EffectProcessor,
он наследуется от QThread.
Короче, будет отдельный рабочий поток,
чтоб видосы обрабатывать без лагов в интерфейсе.
'''
class EffectProcessor(QThread):
    '''
Тут мы делаем два сигнала:

progress — будет слать проценты (сколько уже обработано).

finished — шлёт сообщение, когда работа закончена,
и отдаёт путь к готовому видосу.
    '''
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)




    '''
self — это как "я сам" для объекта.

Когда ты делаешь класс и потом создаёшь из него объект,
self внутри методов этого класса — это и есть тот самый объект,
типа "я сам, мой карман".

Пример:

У тебя есть кореш Петя (объект).

У него в кармане телефон (свойство объекта).

Когда он говорит self.phone, это значит "мой телефон", а не чей-то другой.

Как работает:

Когда вызываешь метод у объекта,
питон сам подсовывает этого объекта в self.

То есть obj.method() внутри метода выглядит как method(self=obj).

Всё, что ты записываешь через self.что-то,
будет храниться именно у этого объекта, а не у всех подряд.

Короче, self — это типа "ссылка на самого себя",
чтоб у каждого пацана (объекта) были свои шмотки (переменные).
    '''
    
    '''
Это типа конструктор
Он принимает: какой видос входящий, какой выходящий, и какой эффект юзать.
    '''
    def __init__(self, input_video, output_video, effect_type):
        '''
Запускаем инициализацию родительского класса (QThread).
        '''
        super().__init__()
        '''
— self.input_video — путь к входящему ролику.
— self.output_video — куда скинуть готовый ролик.
— self.effect_type — какой эффект применять.
— self.frame_cache — хранилище кадров,
если нужно юзать старые кадры (типа "эффект тоннеля").
        '''
        self.input_video = input_video
        self.output_video = output_video
        self.effect_type = effect_type
        self.frame_cache = []
    '''
Когда поток запускается — выполняется эта функция.
    '''
    def run(self):
        '''
Открываем входящий ролик через moviepy.
        '''
        clip = VideoFileClip(self.input_video)
        '''
Берём характеристики ролика:

duration — длина в секундах.

fps — кадров в секунду.

width, height — размер картинки.
        '''
        duration = clip.duration
        fps = clip.fps
        width, height = clip.size
        self.frame_cache = []  # Очищаем кэш

        '''
Тут мы делаем функцию, которая создаёт кадр для времени t (секунда).
moviepy будет юзать её, чтобы собирать новый видос.
        '''
        def make_frame(t):
            #Достаём кадр из исходного ролика в момент времени t.
            frame = clip.get_frame(t)
            '''
Кадр идёт в формате RGB, а cv2 любит BGR — перекрашиваем.
            '''
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # В BGR для OpenCV
            #тут наши эффекты:
            if self.effect_type == 1: frame = self.particle_fly_out(frame, t, duration)
            elif self.effect_type == 2: frame = self.strip_slicing(frame, t, duration)
            elif self.effect_type == 3: frame = self.vortex_rotation(frame, t, duration)
            elif self.effect_type == 4: frame = self.explosion_shatter_forward(frame, t, duration)
            elif self.effect_type == 5: frame = self.wave_morphing(frame, t, duration)
            elif self.effect_type == 6: frame = self.cartoonify(frame, t, duration)
            elif self.effect_type == 7: frame = self.infinity_spiral(frame, t, duration)
            elif self.effect_type == 8: frame = self.mirror_maze(frame, t, duration)
            elif self.effect_type == 9: frame = self.glitch_art(frame, t, duration)
            elif self.effect_type == 10: frame = self.fire_burst(frame, t, duration)
            elif self.effect_type == 11: frame = self.water_ripple(frame, t, duration)
            elif self.effect_type == 12: frame = self.pixel_rain(frame, t, duration)
            elif self.effect_type == 13: frame = self.kaleidoscope(frame, t, duration)
            elif self.effect_type == 14: frame = self.time_tunnel(frame, t, duration, clip)
            elif self.effect_type == 15: frame = self.neon_glow(frame, t, duration)
            elif self.effect_type == 16: frame = self.glitch_shift(frame, t, duration)
            elif self.effect_type == 17: frame = self.starburst_explosion(frame, t, duration)
            elif self.effect_type == 18: frame = self.mirror_shatter(frame, t, duration)
            elif self.effect_type == 19: frame = self.color_wave_glitch(frame, t, duration)
            elif self.effect_type == 20: frame = self.pixel_fly_out(frame, t, duration)
            elif self.effect_type == 21: frame = self.hologram_flicker(frame, t, duration)
            elif self.effect_type == 22: frame = self.fireworks_overlay(frame, t, duration)
            elif self.effect_type == 23: frame = self.liquid_melt(frame, t, duration)
            elif self.effect_type == 24: frame = self.neon_glow2(frame, t, duration)
            elif self.effect_type == 25: frame = self.time_warp(frame, t, duration)
            elif self.effect_type == 26: frame = self.explosion_shatter_backward(frame, t, duration)
            elif self.effect_type == 27: frame = self.explosion_shatter_sides(frame, t, duration)
            elif self.effect_type == 28: frame = self.cartoonify2(frame, t, duration)
            elif self.effect_type == 29: frame = self.infinity_spiral2(frame, t, duration)
            elif self.effect_type == 30: frame = self.mirror_maze2(frame, t, duration)
            elif self.effect_type == 31: frame = self.glitch_art2(frame, t, duration)
            elif self.effect_type == 32: frame = self.glitch_art3(frame, t, duration)
            elif self.effect_type == 33: frame = self.glitch_art4(frame, t, duration)
            elif self.effect_type == 34: frame = self.kaleidoscope2(frame, t, duration)
            elif self.effect_type == 35: frame = self.time_tunnel2(frame, t, duration, clip)
            elif self.effect_type == 36: frame = self.neon_glow3(frame, t, duration)
            elif self.effect_type == 37: frame = self.glitch_shift2(frame, t, duration)
            elif self.effect_type == 38: frame = self.starburst_explosion2(frame, t, duration)
            elif self.effect_type == 39: frame = self.mirror_shatter2(frame, t, duration)
            elif self.effect_type == 40: frame = self.color_wave_glitch2(frame, t, duration)
            elif self.effect_type == 41: frame = self.liquid_melt2(frame, t, duration)

            elif self.effect_type == 42: frame = self.neon_glitch(frame, t, duration)
            elif self.effect_type == 43: frame = self.hologram_flicker44(frame, t, duration)
            elif self.effect_type == 44: frame = self.matrix_digital_rain(frame, t, duration)
            elif self.effect_type == 45: frame = self.crt_wave_distortion(frame, t, duration)
            elif self.effect_type == 46: frame = self.neon_edge_glow(frame, t, duration)
            elif self.effect_type == 47: frame = self.smoke_screen_dissolve(frame, t, duration)
            elif self.effect_type == 48: frame = self.raid_flashbang(frame, t, duration)
            elif self.effect_type == 49: frame = self.contraband_scan_lines(frame, t, duration)
            elif self.effect_type == 50: frame = self.territory_split_pan(frame, t, duration)
            elif self.effect_type == 51: frame = self.amnesty_color_shift(frame, t, duration)
            elif self.effect_type == 52: frame = self.blur_pulse(frame, t, duration)
            elif self.effect_type == 53: frame = self.pixelation(frame, t, duration)
            elif self.effect_type == 54: frame = self.heat_haze(frame, t, duration)
            elif self.effect_type == 55: frame = self.edge_sketch(frame, t, duration)
            elif self.effect_type == 56: frame = self.color_invert_pulse44(frame, t, duration)
            elif self.effect_type == 57: frame = self.zoom_shake(frame, t, duration)
            elif self.effect_type == 58: frame = self.vhs_noise44(frame, t, duration)
            elif self.effect_type == 59: frame = self.glow_aura(frame, t, duration)
            elif self.effect_type == 60: frame = self.circle_ripple44(frame, t, duration)
            elif self.effect_type == 61: frame = self.neon_glitch2(frame, t, duration)
            elif self.effect_type == 62: frame = self.raid_flashbang2(frame, t, duration)

            '''
Вернули кадр обратно в RGB, чтобы moviepy не психовал.
            '''
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Обратно в RGB
            '''
Считаем процент прогресса и кидаем его наружу сигналом.
            '''
            self.progress.emit(int((t / duration) * 100))
            #Возвращаем готовый кадр.
            return frame

        '''
Создаём новый ролик, который генерится кадр за кадром через make_frame.
        '''
        new_clip = VideoClip(make_frame, duration=duration)
        '''
Сохраняем новый видос в файл, юзаем кодек libx264 (нормальное качество и вес).
        '''
        new_clip.write_videofile(self.output_video, fps=fps, codec='libx264')
        '''
Когда закончили — сигналим наружу: "Брат, готово! Вот путь к файлу".
        '''
        self.finished.emit(self.output_video)

    '''
функция берёт кадр (frame), время (t), и общую длину видоса (duration).
На выходе возвращает новый кадр с эффектом.
    '''
    def particle_fly_out(self, frame, t, duration):
    
        # --- параметры эффекта ---
        '''
Считаем, сколько времени прошло от начала — от 0 до 1.
max(duration, 1e-6) — чтоб не делить на ноль.
np.clip — обрезаем значение, если ушло за рамки (0–1).
        '''
        progress = float(t) / float(max(duration, 1e-6))
        progress = np.clip(progress, 0.0, 1.0)

        # Не начинать эффект сразу
        '''
Короче, эффект не сразу включается.
Первые 25% времени кадр идёт как есть, без фокусов.
Если время меньше порога — просто возвращаем оригинал.
        '''
        start_thresh = 0.25
        if progress <= start_thresh:
            return frame
        
        #Берём высоту и ширину кадра.
        h, w = frame.shape[:2]

        # Подбираем размер частицы в зависимости от разрешения
        #(баланс скорость/качество)
        '''
Считаем размер "частицы" (квадратик, на который делим картинку).
— Если ещё не считали, делим маленький размер кадра на 40.
— Но чтоб не было слишком мелко/крупно: минимум 8 пикселей, максимум 24.
        '''
        if not hasattr(self, '_pf_particle_size'):
            self._pf_particle_size = max(8, min(24, int(min(h, w) / 40)))
        particle_size = self._pf_particle_size

        # Число блоков по вертикали/горизонтали
        '''
Считаем, сколько блоков (частиц) помещается:

nby — по вертикали,

nbx — по горизонтали.
        '''
        nby = (h + particle_size - 1) // particle_size
        nbx = (w + particle_size - 1) // particle_size

        # Инициализация состояния
        #(один раз, либо после изменения размера кадра)
        '''
Проверяем, есть ли у нас уже сохранённое состояние для этих частиц.
Если первый запуск или размеры изменились — создаём новое.
        '''
        state = getattr(self, '_pf_state', None)
        if (state is None) or (state.get('shape') != (h, w, particle_size)):
            '''
Фиксируем рандом, чтобы эффект всегда выглядел одинаково (не хаос).
            '''
            rng = np.random.RandomState(12345)  #можно убрать
            # направление и сила движения для каждого блока
            '''
Для каждой частицы задаём:

angles — направление, куда она полетит (от 0 до 360 градусов).

speeds — скорость (от 0.6 до 1.0).

vx_blocks и vy_blocks — это разложение направления по осям (X и Y).
            '''
            angles = rng.uniform(0, 2 * np.pi, size=(nby, nbx)).astype(np.float32)
            speeds = rng.uniform(0.6, 1.0, size=(nby, nbx)).astype(np.float32)
            vx_blocks = np.cos(angles) * speeds
            vy_blocks = np.sin(angles) * speeds
            # немного случайной базовой прозрачности/шумовой вариации
            alpha_base = rng.uniform(0.6, 1.0, size=(nby, nbx)).astype(np.float32)
            #Сохраняем всё это в self, чтоб потом заново не считать.
            self._pf_state = {
                'vx': vx_blocks,
                'vy': vy_blocks,
                'alpha_base': alpha_base,
                'shape': (h, w, particle_size)
            }
            state = self._pf_state
        '''
Достаём сохранённые данные.
        '''
        vx_blocks = state['vx']
        vy_blocks = state['vy']
        alpha_base = state['alpha_base']

        '''
s — нормализованный прогресс эффекта (от 0 до 1 после старта).

ease — плавное замедление: сначала медленно, потом быстрее (кубическая формула).
        '''
        # Нормализуем прогресс в интервале [0,1] относительно начала эффекта
        s = np.clip((progress - start_thresh) / (1.0 - start_thresh), 0.0, 1.0)
        # ease out cubic (плавный старт/быстрый конец)
        ease = 1.0 - (1.0 - s) ** 3

        
        '''
Максимальное расстояние, куда может улететь частица
(примерно половина диагонали кадра).
        '''
        max_dist = np.hypot(w, h) * 0.55 #настраиваемое

        # Смещения для блоков
        '''
Считаем смещение каждой частицы по X и Y в зависимости от прогресса.
        '''
        dx_blocks = vx_blocks * ease * max_dist
        dy_blocks = vy_blocks * ease * max_dist

        # Создаем карту координат (vectorized)
        '''
Делаем сетку координат для всего кадра.
Каждому пикселю назначаем, к какому блоку (частице) он относится.
        '''
        ys, xs = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')  # shape (h,w)
        block_x = (xs // particle_size).astype(np.int32)
        block_y = (ys // particle_size).astype(np.int32)

        # Берем смещения из блоковой карты
        dx = dx_blocks[block_y, block_x]  # shape (h,w)
        dy = dy_blocks[block_y, block_x]

        # remap: координата источника для пикселя (x, y) = (x - dx, y - dy)
        '''
Карта координат: где теперь должен быть каждый пиксель.
        '''
        map_x = (xs - dx).astype(np.float32)
        map_y = (ys - dy).astype(np.float32)

        # Выполняем remap — это C-оптимизированная операция
        # используем линейную интерполяцию и заполнение пустот нулями
        '''
Берём исходный кадр и переставляем пиксели по новым координатам.
— INTER_LINEAR — сглаживание.
— borderValue=0 — пустые места закрашиваем чёрным.
        '''
        new_frame = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=0)

        # Лёгкое выцветание частиц по мере вылета (альфа мультипликатор)
        # alpha_base — случайная база в блоке, постепенно уменьшается с ease
        alpha_block = np.clip(1.0 - ease * 1.05, 0.0, 1.0) * alpha_base[block_y, block_x]
        # Применяем к каждому каналу (если цветное)
        '''
Если кадр цветной (3 канала) — растягиваем альфу под все каналы.
Перемножаем — пиксели становятся тусклее.
Если кадр серый — просто умножаем.
        '''
        if new_frame.ndim == 3 and new_frame.shape[2] == 3:
            alpha_3 = alpha_block[:, :, None]
            # приводим к float для перемножения, затем обратно в исходный тип
            new_frame = (new_frame.astype(np.float32) * alpha_3).astype(frame.dtype)
        else:
            new_frame = (new_frame.astype(np.float32) * alpha_block).astype(frame.dtype)
        '''
Возвращаем обработанный кадр, где частицы разлетаются и тают.
        '''
        return new_frame
    '''
Брат, это у тебя прям киношный эффект
— картинка разваливается на куски, и они красиво улетают в стороны. 🔥
    '''


    '''
Функция. Берёт кадр (frame), время (t), длительность (duration)
и параметры эффекта:

num_strips — сколько полос нарежем;

max_angle — на сколько градусов каждая полоса может крутиться;

max_shift_frac — насколько сильно полоса может
съехать в сторону (часть ширины кадра).
    '''
    def strip_slicing(self, frame, t, duration, num_strips=12, max_angle=30, max_shift_frac=0.25):
        """
    Ну чё, брат, давай разберём этот движ по феншую.
    Это у нас эффект "полосы раздвигаются и поворачиваются"
    — типа картинка режется на полосы и каждая по-своему смещается и крутится.
    Разложу тебе строчку за строчкой, как в хате карты на стол.
        """
        h, w = frame.shape[:2] #Снимаем размеры кадра: высота и ширина.
        '''
Считаем прогресс эффекта — от 0 (начало) до 1 (конец).
clip ограничивает, чтоб не вылезло за рамки.
        '''
        progress = np.clip(t / duration, 0.0, 1.0)
        '''
Тут делаем плавное движение: сначала тихо,
потом быстрее (кубическая "ease out").
        '''
        ease = 1.0 - (1.0 - progress) ** 3 #(можно менять на другой easing)

        # Начинаем с исходного кадра, будем частично его смешивать с эффектом
        out = frame.copy()

        # равномерно разбиваем вертикали,
        #чтобы не потерять нижнюю/верхнюю часть
        ys = np.linspace(0, h, num_strips + 1, dtype=int)

        for i in range(num_strips): #Запускаем цикл: идём по каждой полосе.
            '''
Берём полосу от y0 до y1. Если вдруг полоса пустая — скипаем.
            '''
            y0, y1 = ys[i], ys[i + 1]
            strip = frame[y0:y1, :, :]
            sh = y1 - y0
            if sh <= 0:
                continue

            '''
Задаём направление движения.
— Чётные полосы идут влево (-1).
— Нечётные — вправо (+1).
Типа шахматный порядок.
            '''
            direction = -1 if (i % 2 == 0) else 1  # чередование направлений

            # Плавный угол и смещение
            '''
Считаем:

angle — насколько повернуть полосу (зависит от прогресса).

dx — насколько сместить её вбок.
            '''
            angle = direction * max_angle * ease
            dx = int(direction * w * max_shift_frac * ease)

            # Центр поворота координат в пределах полосы
            '''
— center — центр полосы, вокруг него крутим.
— M — матрица поворота.
— M[0,2] += dx — сразу в матрицу докидываем горизонтальный сдвиг.
            '''
            center = (w / 2.0, sh / 2.0)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            M[0, 2] += dx  # добавляем горизонтальный сдвиг прямо в матрицу

            # Применяем аффинное преобразование к полосе
            '''
Применяем преобразование:
— warpAffine крутит и сдвигает полосу по матрице M.
— Если пикселей не хватает — берём отражение с краёв, чтоб дыр не было.
            '''
            rotated = cv2.warpAffine(strip, M, (w, sh),
                                 flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_REFLECT_101)
            '''
Смешиваем оригинал и повернутую полосу:

Когда эффект только стартует — больше оригинала.

Когда под конец — больше кручёной версии.
            '''
            # Смешиваем оригинал и трансформированную полосу (мягкий переход)
            alpha = ease  # можно смещать (например ease*0.9) для более мягкого эффекта
            blended = cv2.addWeighted(strip, 1.0 - alpha, rotated, alpha, 0)

            '''
Ставим обратно обработанную полосу на её место в картинку.
            '''
            out[y0:y1, :, :] = blended

            '''
Возвращаем готовый кадр, где полосы уже красиво разъехались.
            '''
        return out
    '''
Короче, брат, этот эффект делает так,
что картинка как будто нарезана на ленты,
и они поочерёдно разлетаются в разные стороны,
ещё и слегка крутятся — смотрится как киношная заставка. 🔥
    '''





    
    def vortex_rotation(self, frame, t, duration):
        h, w = frame.shape[:2]
        cx, cy = w / 2, h / 2
        progress = t / duration

        # сетка координат
        '''
Строим сетку координат: для каждого пикселя знаем его x и y.
        '''
        x, y = np.meshgrid(np.arange(w), np.arange(h))
        '''
— dx, dy — смещение пикселя от центра.
— r — расстояние до центра (радиус).
— theta — угол этого пикселя относительно центра (в радианах).
Типа мы переводим картинку в полярные координаты.
        '''
        dx = x - cx
        dy = y - cy
        r = np.sqrt(dx**2 + dy**2)
        theta = np.arctan2(dy, dx)

        # угол поворота (усиление по радиусу для эффекта "вихря")
        '''
— swirl_strength — сила закрутки, растёт с прогрессом (от 0 до 2π).
— theta_new — новый угол: чем дальше от центра (r), тем сильнее пихаем поворот.
Короче, чем дальше пиксель, тем сильнее его закрутило в вихрь.
        '''
        swirl_strength = 2 * math.pi * progress
        theta_new = theta + swirl_strength * (r / max(cx, cy))

        # масштабирование к центру
        '''
Делаем масштабирование: всё постепенно тянется к центру.
scale уменьшается с прогрессом, и радиус r_new становится меньше.
        '''
        scale = 1 - 0.3 * progress
        r_new = r * scale

        # новые координаты
        '''
Считаем новые координаты для каждого пикселя:
берём уменьшенный радиус и повернутый угол, переводим обратно в XY.
        '''
        map_x = (cx + r_new * np.cos(theta_new)).astype(np.float32)
        map_y = (cy + r_new * np.sin(theta_new)).astype(np.float32)

        # ремапим картинку (быстро!)
        '''
cv2.remap — быстро переставляем пиксели на новые места.
— INTER_LINEAR — сглаживаем, чтоб не было ступенек.
— BORDER_REFLECT — если координаты вылезли за границу,
отражаем от края, как будто в зеркало.
        '''
        new_frame = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR,
                              borderMode=cv2.BORDER_REFLECT)

        '''
Короче, брат, этот эффект делает так,
будто картинка уходит в чёрную дыру:
всё закручивается по спирали и затягивается внутрь. 🔥
        '''
        return new_frame




    '''
Функция эффекта. Берёт кадр (frame), время (t), длительность (duration).
grid_size=10 — это сколько кусочков по сетке
(типа делим картинку на квадраты 10×10).
    '''
    def explosion_shatter_forward(self, frame, t, duration, grid_size=10):
        """Фрагменты вылетают ВПЕРЁД (увеличиваются)"""
        progress = t / duration
        h, w = frame.shape[:2]
        '''
Делаем пустой кадр (чёрный), на него будем рисовать все обломки.
        '''
        new_frame = np.zeros_like(frame)


        '''
Делим картинку на сетку: gh × gw квадратиков. Идём по каждой клетке.
        '''
        gh, gw = grid_size, grid_size
        for i in range(gh):
            for j in range(gw):
                '''
Вычисляем границы текущего фрагмента (слева сверху и справа снизу).
                '''
                x1, y1 = j * w // gw, i * h // gh
                x2, y2 = (j+1) * w // gw, (i+1) * h // gh
                '''
Вырезаем кусок (frag) из кадра и смотрим его размеры.
                '''
                frag = frame[y1:y2, x1:x2]
                fh, fw = frag.shape[:2]

                # Увеличение (вылетает на камеру)
                '''
Каждый кусок увеличиваем со временем:
— scale растёт от 1 до 3 (т.е. в 3 раза больше к концу).
— Ресайзим кусок.
— rh, rw — новые размеры этого фрагмента.
                '''
                scale = 1 + progress * 2.0
                frag_resized = cv2.resize(frag, (max(1, int(fw*scale)), max(1, int(fh*scale))))
                rh, rw = frag_resized.shape[:2]

                # Центрируем
                '''
Ставим кусок так, чтобы он вылетал из своего центра
(а не сдвигался куда попало).
Фактически двигаем картинку назад, чтобы масштабирование было «в камеру».
                '''
                fx = (x1 + x2)//2 - rw//2
                fy = (y1 + y2)//2 - rh//2

                # Отрисовка
                '''
Проверяем, чтоб кусок не вылез за границы кадра.
— frag_crop — обрезаем его, если он всё-таки больше экрана.
— roi — область на пустом кадре, куда этот кусок будет вставляться.
                '''
                if 0 <= fx < w and 0 <= fy < h:
                    x_end, y_end = min(w, fx+rw), min(h, fy+rh)
                    frag_crop = frag_resized[:y_end-fy, :x_end-fx]
                    roi = new_frame[fy:y_end, fx:x_end]
                    '''
Прозрачность: в начале куски чёткие (alpha ~ 1),
к концу почти исчезают (alpha ~ 0).
                    '''
                    alpha = max(0, 1 - progress**1.8)
                    '''
Накладываем кусок на фон с плавным затуханием.
cv2.addWeighted смешивает две картинки с разными весами.
                    '''
                    blended = cv2.addWeighted(frag_crop, alpha, roi, 1 - alpha, 0)
                    new_frame[fy:y_end, fx:x_end] = blended
                    '''
Короче, брат, этот эффект выглядит так,
будто экран взорвался на осколки,
и они летят прямо в камеру.
Чисто как нарезка в кино, когда граната залетела в изолятор 💥.
                    '''
        return new_frame

    

    def wave_morphing(self, frame, t, duration):
        # Эффект: Волновое искажение, как разрезание волнами
        progress = t / duration
        '''
Амплитуда волны. Чем дальше во времени,
тем сильнее колбасит картинку
(в начале чуть-чуть, под конец — ваще крутит).
        '''
        amplitude = 50 * progress
        '''
Частота волны — насколько часто будет рябить по экрану.
        '''
        frequency = 0.1

        h, w = frame.shape[:2]

        # Создаем сетку координат
        y, x = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")

        # Смещение по x и y
        '''
Вот тут вся магия:

Для каждой точки по X добавляем смещение в виде синуса → это даёт «змейку»,
как волна.

Для каждой точки по Y добавляем смещение в виде косинуса → ещё больше кривит,
типа волна идёт по диагонали.

t * 10 — анимация, чтобы рябь двигалась, а не стояла.

Короче, пиксели тупо плавают туда-сюда,
как будто смотришь через горячий воздух над костром 🔥.
        '''
        new_x = (x + amplitude * np.sin(2 * np.pi * frequency * y + t * 10)).astype(np.float32)
        new_y = (y + amplitude * np.cos(2 * np.pi * frequency * x + t * 10)).astype(np.float32)

        # Используем cv2.remap для быстрой интерполяции
        new_frame = cv2.remap(frame, new_x, new_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        '''
⚡ Короче, этот эффект, братан, это как будто картинку в натуре гнёт
водяной рябью, она двигается туда-сюда, прямо глаза дурит.
Чисто иллюзия, будто сидишь у речки после «малявы» и смотришь,
как течение воду колышет 🌊.
        '''
        return new_frame


    '''
Функция cartoonify делает из обычного кадра такую «мультяшку»,
прям как будто художник фломастером обвёл и красками залил.
    '''
    def cartoonify(self, frame, t, duration):
        '''
тут оно особо не решает, просто чтоб был расчёт.
        '''
        progress = t / duration

        '''
cv2.pyrDown(frame)
Тут мы картинку «сжимаем»,
типа в полраза уменьшаем. Зачем?
Ну чтоб быстрее дальше мутить, меньше деталей — меньше возни.
        '''
        small = cv2.pyrDown(frame) #(опционально)

        # Делаем сглаживание цветов (мягкие заливки)
        '''
cv2.bilateralFilter(...)
Это такой фильтр,
который сглаживает цвета, но не размывает края.
Типа как если бы «размазал» пятна,
но чёткие границы оставил.
Делается пару раз, чтоб мягче смотрелось, как краской залили.
        '''
        for _ in range(2):
            small = cv2.bilateralFilter(small, d=9, sigmaColor=75, sigmaSpace=75)

        # Возвращаем обратно в нормальный размер
        smooth = cv2.pyrUp(small)

        # Переводим в серый и ищем края
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        '''
Вот тут прям ищем «контуры» — линии, где картинка меняется сильно.
Типа очертания персонажей.
        '''
        edges = cv2.Canny(gray, 50, 150)
        '''
dilate — утолщает линии, чтоб жирно смотрелось.

bitwise_not — переворачивает: белый фон, чёрные линии.
Чтобы было по-мультяшному.
        '''
        edges = cv2.dilate(edges, None)   # утолщаем линии
        edges = cv2.bitwise_not(edges)    # инвертируем (чтобы белый фон, чёрные линии)

        # Маска контуров в 3 канала
        '''
Красим эти линии обратно в 3 канала, чтоб совпадало с цветной картинкой.
        '''
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # Комбинируем мультяшные заливки + линии
        '''
И вот финт ушами: склеиваем «цветные заливки» (smooth)
и «чёрные линии» (edges).
Получается такой эффект — как будто мультик или комикс.
        '''
        cartoon = cv2.bitwise_and(smooth, edges_colored)

        return cartoon


    
    def infinity_spiral(self, frame, t, duration):
        progress = t / duration
        h, w = frame.shape[:2]
        '''
Вычисляем середину кадра — где центр экрана находится.
        '''
        center_x, center_y = w / 2, h / 2

        # Координатная сетка
        '''
Строим такую решётку координат — каждый пиксель
получает свой адрес «где он живёт».
        '''
        y, x = np.indices((h, w))
        '''
Считаем смещения: насколько каждый пиксель отъехал от центра
по горизонтали (dx) и вертикали (dy).
        '''
        dx = x - center_x
        dy = y - center_y

        # Полярные координаты
        '''
Считаем расстояние каждого пикселя от центра (как длину вектора).
И ещё растягиваем его в зависимости от progress, типа всё время дальше тянется.
        '''
        r = np.sqrt(dx**2 + dy**2) * (1 + progress)
        '''
Это угол поворота для каждого пикселя — куда он смотрит относительно центра
        '''
        theta = np.arctan2(dy, dx)
        '''
А вот тут движуха: каждому углу мы подкидываем смещение,
чтоб оно закручивалось в спираль.
Если радиус (r) не ноль, добавляем к углу штуку, зависящую от времени.
В итоге получается такое бесконечное закручивание.
        '''
        theta += np.where(r != 0, progress * 10 * np.pi / r, 0)

        # Новые координаты
        '''
Переводим обратно из полярных координат в обычные.
Берём новый X и Y для каждого пикселя,
округляем их и делаем так, чтоб они не вываливались за края (по модулю %).
        '''
        src_x = (center_x + r * np.cos(theta)).astype(np.int32) % w
        src_y = (center_y + r * np.sin(theta)).astype(np.int32) % h

        # Берём пиксели из исходного изображения
        '''
Теперь берём картинку и переставляем пиксели по новым адресам.
Типа каждый пиксель встал не на своё место, а на закрученное.
        '''
        new_frame = frame[src_y, src_x]

        return new_frame

    '''
Оформляем движуху: функция, которая мутит с кадром такую тему,
будто ты попал в лабиринт из зеркал.
    '''
    def mirror_maze(self, frame, t, duration):
        '''
Считаем, сколько времени прошло от начала эффекта.
Типа если вся ходка (duration) — 5 лет, а отсидел уже 2 (t), то progress = 0.4
        '''
        progress = t / duration
        h, w = frame.shape[:2]
        '''
Делаем копию кадра, чтобы было куда мутить отражения.
Оригинал не трогаем, как «общак» — святое.
        '''
        new_frame = frame.copy()
        '''
Определяем, сколько будет зеркал. Чем дальше прогресс, тем больше отражений.
Типа сначала 2 зеркала, потом 3, потом 4, и так до 6.
        '''
        num_mirrors = int(2 + progress * 4)  # Увеличиваем количество
        '''
Запускаем цикл: для каждого зеркала мутим копию кадра.
        '''
        for i in range(1, num_mirrors):
            '''
Рассчитываем, насколько уменьшить картинку.
Чем больше i (номер зеркала), тем меньше картинка.
Типа дальние отражения становятся мелкими.
            '''
            scale = 1 - i * 0.1 * progress
            '''
Создаём уменьшенную версию кадра.
            '''
            small = cv2.resize(frame, (int(w * scale), int(h * scale)))
            '''
Сдвигаем копию чуть в сторону от центра.
Чем больше i и progress, тем дальше эта копия уезжает.
            '''
            offset = int(i * 20 * progress)
            '''
Ставим уменьшенную картинку в левый верхний угол с учётом сдвига (offset).
            '''
            new_frame[offset:offset+small.shape[0], offset:offset+small.shape[1]] = small
            '''
Делаем зеркальную копию уменьшенного кадра (по горизонтали).
Типа как будто смотришь в зеркало.
            '''
            flipped = cv2.flip(small, 1)  # Зеркальное
            '''
Ставим зеркальную версию в правую часть кадра.
Получается эффект коридора из зеркал:
слева обычное отражение, справа — зеркальное.
            '''
            new_frame[offset:offset+small.shape[0], w - offset - small.shape[1]:w - offset] = flipped
            '''
Возвращаем готовый кадр, где ты уже в «зеркальном лабиринте».
            '''
        return new_frame

    '''
Оформляем функцию: берём кадр и делаем из него глюк-анимацию,
как будто телек через фольгу смотришь или кассета перемоталась.
max_shift = 20 — это типа максимальное смещение пикселей.
    '''
    def glitch_art(self, frame, t, duration, max_shift=20):
            # безопасный прогресс 0..1
            progress = float(np.clip(t / float(duration), 0.0, 1.0))

            new_frame = frame.copy()
            h, w = new_frame.shape[:2]

            # динамический максимальный сдвиг (обеспечиваем хотя бы небольшой эффект)
            '''
Считаем, насколько сильно можно будет двигать пиксели.
В начале (малый прогресс) — смещение маленькое,
дальше оно растёт, эффект жёстче.
            '''
            shift = max(1, int(max_shift * (0.15 + 0.85 * progress)))

            # 1) Хроматическая аберрация: разные сдвиги для каналов
            '''
Разделяем картинку на каналы: синий (b), зелёный (g), красный (r).
            '''
            b, g, r = cv2.split(new_frame)
            '''
Двигаем каналы по-разному: каждый уезжает в сторону случайно.
Из-за этого появляется эффект «расходящихся цветов»,
как на старых VHS кассетах.
            '''
            b = np.roll(b, int(random.uniform(-shift, shift)), axis=1)
            g = np.roll(g, int(random.uniform(-shift//2, shift//2)), axis=1)
            r = np.roll(r, int(random.uniform(-shift, shift)), axis=1)
            '''
Склеиваем каналы обратно в цветную картинку. Теперь она уже с «расфокусом».
            '''
            new_frame = cv2.merge([b, g, r])

            # 2) Горизонтальные полосы — сдвигаем случайные полосы по X
            '''
Считаем, сколько будет глюк-полос. Чем дальше по времени, тем больше полос.
            '''
            num_bands = 1 + int(progress * 6)  # от 1 до ~7 полос в зависимости от прогресса
            '''
Выбираем случайную полоску по вертикали (band_h), где будем глючить.
Определяем её стартовую точку (y).
И решаем, насколько сместить её по горизонтали (shift_x).
            '''
            for _ in range(num_bands):
                band_h = random.randint(1, max(1, int(h * 0.06)))
                y = random.randint(0, max(0, h - band_h))
                shift_x = random.randint(-shift, shift)
                '''
Если сдвиг есть — крутим эту полоску влево или вправо.
Получается эффект, будто картинка рвётся на куски.
                '''
                if shift_x != 0:
                    new_frame[y:y + band_h] = np.roll(new_frame[y:y + band_h], shift_x, axis=1)

            # 3) Блоковые глитчи:
            #копируем небольшие прямоугольники и вставляем смещёнными
            '''
запускаем ещё один эффект: блочные глюки.
            '''
            if random.random() < 0.8 * progress:
                '''
Чем дальше эффект, тем больше блоков-обрывков будет вставлено.
                '''
                blocks = 1 + int(4 * progress)
                '''
Выбираем случайный кусок картинки (маленький прямоугольник).
bw — ширина блока, bh — высота, x/y — его место на экране.
                '''
                for _ in range(blocks):
                    bw = random.randint(8, max(8, int(w * 0.18)))
                    bh = random.randint(2, max(2, int(h * 0.12)))
                    x = random.randint(0, max(0, w - bw))
                    y = random.randint(0, max(0, h - bh))
                    '''
Берём этот кусок, двигаем его в сторону (dx),
и вставляем в новое место (nx).
Получается эффект «глючащих квадратиков».
                    '''
                    dx = random.randint(-shift, shift)
                    nx = np.clip(x + dx, 0, w - bw)
                    patch = new_frame[y:y + bh, x:x + bw].copy()
                    new_frame[y:y + bh, nx:nx + bw] = patch

            # 4) Сканлайны (тонкое затемнение каждой второй строки)
            '''
Рисуем такие тонкие горизонтальные полоски (как на старых мониторах).
Чем больше прогресс, тем темнее полоски.
            '''
            line_dark = int(18 * progress)
            '''
Берём каждую вторую строчку пикселей и затемняем её.
Сначала переводим в int16,
чтобы не было «переполнения»,
потом обрезаем значения и возвращаем в нормальный диапазон (0–255).
            '''
            if line_dark > 0:
                # использовать int16, затем обрезать, чтобы избежать wrap-around
                tmp = new_frame[::2].astype(np.int16) - line_dark
                new_frame[::2] = np.clip(tmp, 0, 255).astype(np.uint8)

            # 5) Шум — аддитивно с saturating add, чтобы не было wrap-around
            '''
Добавляем шум. Чем дальше, тем сильнее он лезет.
            '''
            noise_amp = int(28 * progress)  # амплитуда шума
            '''
Создаём случайный шум (рандомные точки),
размножаем его на три канала и прибавляем к картинке.
Используем cv2.add, чтобы не было переполнения — вместо ухода в минус,
значения прижимаются к максимуму.
            '''
            if noise_amp > 0:
                noise = np.random.randint(0, noise_amp, (h, w, 1), dtype=np.uint8)
                noise = np.repeat(noise, 3, axis=2)
                new_frame = cv2.add(new_frame, noise)  # cv2.add — saturating

                '''
Возвращаем готовый кадр: глюки, полосы, шум,
всё вместе — чисто артовый хаос,
будто телек с антенны ловит «РЕН-ТВ» через носок на балконе.
                '''
            return new_frame

    def fire_burst(self, frame, t, duration):
        progress = float(np.clip(t / duration, 0.0, 1.0))
        '''
Усиливаем прогресс: в два раза быстрее растёт.
Чтобы «огонь» быстрее включался.
        '''
        eff = float(np.clip(progress * 2.0, 0.0, 1.0))
        '''
Если эффект почти не включился — возвращаем оригинал.
Типа «огня пока нет».
        '''
        if eff < 0.02:
            return frame

        h, w = frame.shape[:2]
        '''
Вычисляем интенсивность огня.
Мягко нарастает (через степень).
        '''
        intensity = eff ** 0.9
        '''
Общий коэффициент «мощности пожара». Чем выше intensity,
тем сильнее все эффекты.
        '''
        global_strength = 0.9 + 1.5 * intensity

        '''
Делаем сид для рандома, завязанный на время t.
Чтобы шум был случайный, но повторяемый для конкретного момента.
        '''
        seed = int(t * 1000) & 0xFFFFFFFF
        rng = np.random.RandomState(seed)

        '''
Создаём шум с нормальным распределением (гауссовский).
Это основа «помех» и «искр».
        '''
        noise_sigma = 80.0 * global_strength
        base_noise = rng.normal(0.0, noise_sigma, size=(h, w)).astype(np.float32)

        '''
Делаем «скрученный шум»:
— по строкам синусом сдвигаем пиксели,
— каждая строка по-своему едет влево-вправо,
— получается эффект «дрожащего огня».
        '''
        rows = np.arange(h)
        roll_amp = int(38 * global_strength)
        roll = (np.sin(rows * 0.12 + t * 5.0) * roll_amp).astype(np.int32)
        x_idx = (np.arange(w)[None, :] - roll[:, None]) % w
        rolled_noise = base_noise[np.arange(h)[:, None], x_idx]

        '''
Имитируем «провалы» строк — некоторые строки частично выгорают.
Типа в огне появляются пустоты и рваные дыры.
        '''
        dropout_prob = 0.03 + 0.28 * intensity
        rnd_rows = rng.rand(h)
        dropout_mask = (rnd_rows < dropout_prob).astype(np.float32)[:, None]
        dropout_depth = (0.25 + 0.70 * rng.rand(h) * intensity)[:, None].astype(np.float32)
        rolled_noise *= (1.0 - dropout_mask * dropout_depth)

        '''
Добавляем «сканлайны» — тёмные полоски через строку.
Огонь как будто мерцает.
        '''
        scan_strength = 0.65 * intensity
        scan = 1.0 - scan_strength * ((rows % 2)[:, None].astype(np.float32))
        rolled_noise *= scan

        '''
Формируем цвет пламени:
— синий почти пропадает,
— зелёный средний.
        '''
        noise_b = rolled_noise * 0.45
        noise_g = rolled_noise * 0.9
        '''
Красный канал ведёт себя отдельно:
— его смещаем сильнее,
— он ярче остальных.
В итоге весь эффект тянет в красно-оранжевую гамму, как пламя.
        '''
        shift_r = (np.sin(rows * 0.08 + t * 3.2) * (6.0 * global_strength)).astype(np.int32)
        x_idx_r = (np.arange(w)[None, :] - shift_r[:, None]) % w
        noise_r = base_noise[np.arange(h)[:, None], x_idx_r].astype(np.float32) * 1.35
        noise_r *= (1.0 - dropout_mask * dropout_depth) * scan

        '''
Собираем три канала (BGR) обратно в цветное шумовое изображение.
        '''
        noise_rgb = np.stack([noise_b, noise_g, noise_r], axis=2)

        '''
Делаем «мигание огня»:
— создаём маленькую матрицу шума,
— растягиваем её блоками на весь кадр,
— получается крупнозернистое мерцание, будто пламя дышит.
        '''
        block_h = max(4, h // 36)
        block_w = max(4, w // 56)
        bh = (h + block_h - 1) // block_h
        bw = (w + block_w - 1) // block_w
        small = rng.rand(bh, bw).astype(np.float32) - 0.5
        flicker = np.repeat(np.repeat(small, block_h, axis=0)[:h, :], block_w, axis=1)[:h, :w]
        flicker = 1.0 + flicker * (0.5 * global_strength)
        flicker = flicker[..., None]  # shape (h,w,1), будет broadcast по каналам

        '''
Накладываем шум поверх оригинального кадра.
Типа картинка уже начинает «гореть».
        '''
        frame_f = frame.astype(np.float32)
        overlay_strength = 1.05 * global_strength
        noisy_overlay = frame_f + noise_rgb * (0.95 * intensity) * overlay_strength

        # исправлено: intensity — скаляр, используем напрямую (broadcast автоматически)
        '''
Тушим часть яркости и добавляем эффект мерцания (flicker).
Теперь огонь «пульсирует».
        '''
        noisy_overlay = noisy_overlay * (1.0 - 0.7 * intensity)
        noisy_overlay = noisy_overlay * (1.0 - 0.9 * intensity) + noisy_overlay * (0.9 * intensity) * flicker

        '''
Когда прогресс доходит почти до конца (92%),
картинка начинает полностью перекрываться огнём.
cover — насколько экран уже сгорел.
        '''
        cover_start = 0.92
        if progress <= cover_start:
            cover = 0.0
        else:
            c = (progress - cover_start) / (1.0 - cover_start + 1e-6)
            cover = float(np.clip(c ** 2.0, 0.0, 1.0))
        
        '''
Финальная стадия: всё закрывается «чистым огнём».
— создаём новое шумовое красно-жёлтое поле (pure_noise),
— перекрываем кадр им постепенно.
В итоге к концу экран полностью заполняется пламенем.
        '''
        if cover > 0.0:
            pure_sigma = 100.0 * global_strength
            pure_base = rng.normal(127.0, pure_sigma, size=(h, w)).astype(np.float32)
            pure_b = pure_base * 0.5 + 80.0
            pure_g = pure_base * 0.9 + 50.0
            pure_r = pure_base * 1.1 + 40.0
            pure_noise = np.stack([pure_b, pure_g, pure_r], axis=2)
            gs = (np.sin(rows * 0.11 + t * 7.0) * 3.0).astype(np.int32)
            x_idx_end = (np.arange(w)[None, :] - gs[:, None]) % w
            pure_noise[..., 2] = pure_noise[np.arange(h)[:, None], x_idx_end, 2]
            out = noisy_overlay * (1.0 - cover) + pure_noise * cover
            '''
Если ещё не дошло до полного перекрытия — оставляем промежуточный результат.
            '''
        else:
            out = noisy_overlay
            '''
Корректируем цвета:
— убавляем синий и зелёный,
— усиливаем красный.
Чтобы пламя было настоящим, а не фиолетовым.
            '''
        out[..., 0] *= 1.0 - (0.06 * intensity)
        out[..., 1] *= 1.0 - (0.03 * intensity)
        out[..., 2] *= 1.0 + (0.08 * intensity)
        '''
Обрезаем значения, чтоб не вылетели за пределы (0–255).
        '''
        np.clip(out, 0, 255, out=out)
        return out.astype(np.uint8)


    def water_ripple(self, frame, t, duration):
        H, W = frame.shape[:2]
        '''
Пробуем взять из объекта кеш — чтоб
заново не считать сетку координат каждый раз.
Если нет, вернёт None.
        '''
        cache = getattr(self, "_ripple_cache_cv", None)
        '''
Если кеша нет или размер картинки поменялся — надо пересоздать.
        '''
        if cache is None or cache.get("shape") != (H, W):
            '''
Создаём координаты по X и Y:
— xs это ряд от 0 до W (горизонталь),
— ys это колонка от 0 до H (вертикаль).
            '''
            xs = np.arange(W, dtype=np.float32)[None, :]
            ys = np.arange(H, dtype=np.float32)[:, None]
            '''
Сохраняем всё в кеш, чтоб потом не париться.
            '''
            self._ripple_cache_cv = {"shape": (H, W), "xs": xs, "ys": ys}
            cache = self._ripple_cache_cv
        '''
Берём из кеша готовые сетки X и Y.
        '''
        xs = cache["xs"]; ys = cache["ys"]

        '''
Считаем, сколько времени прошло.
Если duration = 0, то сразу ставим прогресс 1 (чтоб не делить на ноль).
        '''
        progress = float(t) / float(duration) if duration != 0 else 1.0
        progress = np.clip(progress, 0.0, 1.0)
        '''
Амплитуда колебаний: чем больше прогресс, тем сильнее рябь.
        '''
        amplitude = 20.0 * progress
        '''
Фаза колебаний — типа угол волны.
Чем дальше по времени, тем волны сильнее гуляют.
        '''
        phi = float(t) * 5.0

        '''
Считаем смещения по X:
берём синус, зависящий от строки (ys).
То есть каждая строка колышется, как волна.
        '''
        offset_x = amplitude * np.sin(phi + 0.05 * ys)
        '''
Считаем смещения по Y:
берём косинус, зависящий от столбца (xs).
То есть каждый столбец тоже колышется.
        '''
        offset_y = amplitude * np.cos(phi + 0.05 * xs)
        '''
Делаем новые карты координат:
каждый пиксель смещаем на рассчитанные офсеты.
        '''
        map_x = (xs + offset_x).astype(np.float32)  # (H, W)
        map_y = (ys + offset_y).astype(np.float32)

        # remap ожидает map_x/map_y формата (H, W) float32
        # cv2.remap: dst(y,x) = src(map_y(y,x), map_x(y,x))
        '''
Используем cv2.remap:
берём оригинальный кадр и переносим пиксели по новым координатам.
BORDER_REFLECT значит: если вылез за край — отражаем картинку,
как зеркало по границе.
В итоге выходит рябь — будто смотришь на картинку через воду.
        '''
        return cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    def pixel_rain(self, frame, t, duration):

        h, w = frame.shape[:2]
        progress = float(np.clip(t / duration, 0.0, 1.0))

        '''
👉 Создаём рандомайзер, зависящий от времени, чтоб каждый кадр имел свои случайные значения.
        '''
        rng = np.random.RandomState(int(t * 1000) % 100000)

        # Колонки с разной скоростью
        '''
Короче тут мы моделируем разную скорость падения для колонок (типа пиксельные струи дождя).

base_speed — базовая скорость, чем дальше по времени, тем быстрее.

noise_col — шум для каждой колонки, чтоб всё было хаотично.

offsets — реальные смещения для каждой колонки.
        '''
        base_speed = 6 + int(90 * progress)
        noise_col = rng.rand(w).astype(np.float32)
        offsets = (base_speed * (0.35 + 0.9 * noise_col)).astype(int)

        # Векторизованный roll по столбцам
        '''
Тут мутим "сдвиг по вертикали".

rows_idx говорит какие строки брать для каждой колонки, типа сдвигаем вниз.

rolled — итоговый кадр после этих сдвигов: колонки падают вниз как дождь.
        '''
        rows_idx = (np.arange(h)[:, None] - offsets[None, :]) % h
        rolled = np.take_along_axis(frame, rows_idx[:, :, None], axis=0)

        # Motion trails: экспоненциальный вес
        '''
Здесь мы делаем затухание (шлейф за каплями).

trail_len — длина следа (чем дальше, тем длиннее).

decay — коэффициенты убывания яркости, нормализуем чтоб сумма = 1.
        '''
        trail_len = 1 + int(20 * progress)
        decay = np.exp(-np.linspace(0.0, 3.0, trail_len)).astype(np.float32)
        decay = decay / decay.sum()  # суммы 1

        '''
👉 Преобразуем картинку в float32, чтоб умножать и складывать нормально.
        '''
        rolled_f = rolled.astype(np.float32)

        # Вместо cv2.filter2D — суммируем сдвинутые копии (работает с wrap)
        # Это выполняет вертикальную свертку с kernel=(decay,1)
        '''
Тут руками делаем типа вертикальное размытие вниз.
Берём копии кадра с разными смещениями и складываем их с весами (decay).
Так создаётся красивый шлейф.
        '''
        trailed_f = np.zeros_like(rolled_f)
        # применяем сдвиги: weight * np.roll(rolled_f, shift=k, axis=0)
        for k, wgt in enumerate(decay):
            if wgt == 0.0:
                continue
            # сдвиг: положительный k сдвигает элементы вниз — подберите направление как нужно
            trailed_f += np.roll(rolled_f, shift=-k, axis=0) * wgt
        '''
👉 Возвращаем картинку в нормальный диапазон пикселей (0–255), тип uint8.
        '''
        trailed = np.clip(trailed_f, 0, 255).astype(np.uint8)

        # Хроматическая аберрация
        '''
Добавляем гоп-эффект "раздвоенные цвета" (хроматическая аберрация).

Сдвигаем синий вправо, красный влево, зелёный оставляем.

Складываем обратно в картинку.
        '''
        max_ch_shift = 2 + int(6 * progress)
        b = np.roll(trailed[:, :, 0],  max_ch_shift, axis=1)
        g = np.roll(trailed[:, :, 1],  0, axis=1)
        r = np.roll(trailed[:, :, 2], -max_ch_shift, axis=1)
        out = np.stack([b, g, r], axis=2)

        # Highlights (капли)
        '''
Готовим яркие "капли дождя".

highlights — пустая маска.

drop_prob — вероятность что в колонке будет капля.

cols_with_drop — какие колонки выбрались.

ys — случайные позиции по высоте для капель.
        '''
        highlights = np.zeros((h, w), dtype=np.float32)
        drop_prob = 0.02 + 0.25 * progress
        cols_with_drop = rng.rand(w) < drop_prob
        ys = (rng.rand(cols_with_drop.sum()) * (0.6 * h)).astype(int)
        drop_idx = np.where(cols_with_drop)[0]
        '''
👉 Проставляем капли на картинке, делаем их длиннее со временем.
        '''
        for j, y0 in zip(drop_idx, ys):
            y0 = np.clip(y0, 1, h - 2)
            height = 1 + int(3 + 6 * progress)
            y1 = min(h, y0 + height)
            highlights[y0:y1, j] = 1.0

        # Подготовка нечётного ksize для GaussianBlur
        '''
👉 Размываем капли по вертикали, чтоб не были резкие.
        '''
        ksize_x = 1
        ksize_y = 1 + int(5 * progress)
        if ksize_y % 2 == 0:
            ksize_y += 1
        highlights = cv2.GaussianBlur(highlights, (ksize_x, ksize_y), 0)

        '''
👉 Красим капли в светлый цвет и накладываем поверх основной картинки.
        '''
        highlight_color = np.array([220, 240, 255], dtype=np.float32)
        highlight_layer = (highlights[:, :, None] * highlight_color).astype(np.uint8)
        out = cv2.addWeighted(out, 1.0, highlight_layer, 0.55 * progress, 0)

        # Отражение снизу с волной
        '''
👉 Будем добавлять отражение снизу, как будто дождь отражается на мокрой земле.
        '''
        refl_h = int(h * 0.22 * progress)
        '''
👉 Берём кусок снизу для отражения.
        '''
        if refl_h >= 2:
            src_start = max(0, h - refl_h * 2)
            src = out[src_start: h - refl_h, :, :]
            if src.shape[0] > 0:
                '''
👉 Переворачиваем по вертикали (чтоб получилось отражение).
                '''
                refl = cv2.flip(src, 0)
                rows, cols = refl.shape[:2]
                # карты координат
                '''
Мутим волновое искажение, чтоб отражение выглядело как на воде.
Считаем синусоиду по X и прибавляем к координатам Y.
                '''
                map_x, map_y = np.meshgrid(np.arange(cols, dtype=np.float32),
                                       np.arange(rows, dtype=np.float32))
                # волна по X, добавляем к координате Y
                wave = np.sin((map_x / 12.0) + (t * 6.0)) * (1.0 + 4.0 * progress)
                map_y = map_y + wave.astype(np.float32)

                # Собираем 2-канальную карту и явно приводим тип
                '''
👉 Перестраиваем отражение по волне.
                '''
                map_xy = np.dstack((map_x, map_y)).astype(np.float32)  # CV_32FC2
                # вызываем remap с map2 = None
                remapped = cv2.remap(refl, map_xy, None,
                                     interpolation=cv2.INTER_LINEAR,
                                     borderMode=cv2.BORDER_REFLECT)
                '''
👉 Чуть размываем отражение, чтоб мягче смотрелось.
                '''
                ksize = 1 + int(5 * progress)
                if ksize % 2 == 0:
                    ksize += 1
                remapped = cv2.GaussianBlur(remapped, (ksize, 1), 0)
                '''
👉 Склеиваем отражение с нижней частью кадра.
                '''
                target_y0 = h - refl_h
                bottom_slice = out[target_y0:h, :, :].astype(np.float32)
                remapped = remapped.astype(np.float32)
                blended = cv2.addWeighted(bottom_slice, 0.35, remapped, 0.65, 0)
                out[target_y0:h, :, :] = np.clip(blended, 0, 255).astype(np.uint8)

        # Цветокоррекция
        '''
В конце делаем цветокоррекцию: чуть синевы и контраста добавляем, чтоб картинка выглядела киношно.
        '''
        out_f = out.astype(np.float32) / 255.0
        color_grade = out_f * np.array([0.95, 0.98, 1.06], dtype=np.float32)
        color_grade = np.clip((color_grade - 0.5) * (1.0 + 0.25 * progress) + 0.5, 0.0, 1.0)
        out = (color_grade * 255.0).astype(np.uint8)

        return out


    def kaleidoscope(self, frame, t, duration):
        progress = t / duration
        '''
👉 Угол поворота — чем дальше идёт эффект, тем больше крутим картинку. Полный круг — 360 градусов.
        '''
        angle = progress * 360
        h, w = frame.shape[:2]
        '''
👉 Берём верхний левый кусок картинки — типа одну четвертинку. С неё будем мутить все зеркала.
        '''
        segment = frame[0:h//2, 0:w//2]
        '''
Тут мы делаем матрицу для поворота.

Центр вращения — середина того кусочка (w//4, h//4).

angle — сколько крутим.

1 — масштаб (оставляем размер как есть).
        '''
        M = cv2.getRotationMatrix2D((w//4, h//4), angle, 1)
        '''
👉 Крутим ту четвертинку по матрице, получаем повернутый кусок.
        '''
        rotated = cv2.warpAffine(segment, M, (w//2, h//2))
        '''
👉 Создаём пустой кадр, весь чёрный — как пустая малява, куда будем вставлять куски.
        '''
        new_frame = np.zeros_like(frame)
        # Создаём 4 симметричные части
        '''
👉 Вставляем повернутый кусок в верхний левый угол.
        '''
        new_frame[0:h//2, 0:w//2] = rotated
        '''
👉 В правый верхний угол вставляем зеркалку по горизонтали.
        '''
        new_frame[0:h//2, w//2:] = cv2.flip(rotated, 1)
        '''
👉 В нижний левый угол — зеркалку по вертикали.
        '''
        new_frame[h//2:, 0:w//2] = cv2.flip(rotated, 0)
        '''
👉 В нижний правый угол — двойное зеркало: и по горизонтали, и по вертикали.
        '''
        new_frame[h//2:, w//2:] = cv2.flip(rotated, -1)
        return new_frame

    def time_tunnel(self, frame, t, duration, clip):
        '''
👉 Считаем прогресс эффекта, от 0 до 1, типа "сколько срока уже отсидел".
        '''
        progress = t / duration
        '''
Смотрим, если в кеше кадров больше пяти — выкидываем самый старый.
Чтобы память не жрала как голодный бич на хавчике.
        '''
        if len(self.frame_cache) > 5: self.frame_cache.pop(0)  # Лимит кэша для ресурсов
        '''
👉 Запоминаем текущий кадр в кэш.
        '''
        self.frame_cache.append(frame.copy())
        '''
👉 Делаем копию кадра, будем в неё всё складывать — типа чистый лист под рисунки.
        '''
        new_frame = frame.copy()
        '''
👉 Бежим по всем прошлым кадрам (кроме самого последнего).
i — номер кадра в списке, prev_frame — сам кадр.
        '''
        for i, prev_frame in enumerate(self.frame_cache[:-1]):
            '''
👉 Прозрачность (альфа-канал). Чем дальше старый кадр, тем прозрачнее.
            '''
            alpha = 0.5 / (i + 1) * progress
            '''
👉 Масштаб: каждый прошлый кадр делаем меньше, чтоб был эффект тоннеля.
            '''
            scale = 1 - 0.1 * i * progress
            '''
👉 Сжимаем старый кадр по этому масштабу.
            '''
            small = cv2.resize(prev_frame, (int(frame.shape[1] * scale), int(frame.shape[0] * scale)))
            '''
👉 Считаем отступы, чтобы вставить уменьшенный кадр ровно по центру.
            '''
            offset = (frame.shape[1] - small.shape[1]) // 2, (frame.shape[0] - small.shape[0]) // 2
            '''
Вот тут самый движ:

Берём маленький кадр и кладём его в центр большого.

cv2.addWeighted мешает старый кадр и текущий кусок картинки с разной прозрачностью (alpha и 1-alpha).

Так получается, что кадры наслаиваются друг на друга — и выходит тоннель.
            '''
            new_frame[offset[1]:offset[1]+small.shape[0], offset[0]:offset[0]+small.shape[1]] = cv2.addWeighted(
                small, alpha, new_frame[offset[1]:offset[1]+small.shape[0], offset[0]:offset[0]+small.shape[1]], 1 - alpha, 0)
        return new_frame

    def neon_glow(self, frame, t, duration):
        # Защита от пустого кадра
        '''
Тут проверка на косяки: если кадра нет —

Если мы до этого уже что-то показывали (last_frame), то отдаем его.

Если вообще пусто, то делаем черный экран 480х640.
Это чтоб прога не вырубилась как бич без хавки.
        '''
        if frame is None:
            if hasattr(self, 'last_frame') and self.last_frame is not None:
                return self.last_frame.copy()
            return np.zeros((480, 640, 3), dtype=np.uint8)

        # Приведение к ожидаемому формату
        '''
Тут чистим входные данные:

Если картинка чёрно-белая (2D), превращаем в цветную.

Если есть альфа-канал (4 канала), убираем его, оставляем 3.

Переводим в обычный тип uint8.

Запоминаем кадр как last_frame, чтоб в следующий раз можно было подстраховаться.
        '''
        frame = np.asarray(frame)
        if frame.ndim == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif frame.ndim == 3 and frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        frame = frame.astype(np.uint8)
        self.last_frame = frame.copy()

        h, w = frame.shape[:2]
        progress = float(t) / max(1e-6, float(duration))
        progress = np.clip(progress, 0.0, 1.0)

        # Параметры визуала (настраивайте)
        '''
Тут задаём движуху:

pulse — пульсирует синусом, даёт эффект "мигания" неона.

hue_base — цветовая тональность (меняется от зелёного к фиолетовому и обратно).

edge_blur_levels — три уровня блюра (размытия), чтобы сделать мягкие неоновые слои.
        '''
        pulse = 0.5 * (1.0 + math.sin(t * 6.0))        # 0..1 пульсация
        hue_base = int((90 + 100.0 * math.sin(t * 3.0)) % 180)  # базовый тон (0..179)
        edge_blur_levels = [(3, 0.55), (8, 0.32), (20, 0.13)]   # (sigma, weight)

        # Получаем краевые контуры
        '''
Достаём края объектов:

Переводим в серый.

Размываем для мягкости.

Считаем пороги (low_thr, high_thr), чем дальше эффект, тем жестче границы.

Запускаем Canny — получаем чёрно-белые линии краёв.
        '''
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        low_thr = max(1, int(40 * (0.7 + 0.6 * progress)))
        high_thr = max(low_thr + 1, int(120 * (0.9 + 0.6 * progress)))
        edges = cv2.Canny(blurred, low_thr, high_thr)

        # Маска краёв -> усиление и мягкое растушёвывание
        '''
Из контуров делаем маску:

Нормализуем к 0..1.

Делаем эллиптическое ядро (kernel).

Расширяем края (dilate), чтоб линии были толще и плавней.
        '''
        mask = edges.astype(np.float32) / 255.0
        kernel_size = max(3, int(3 + progress * 10))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
        mask = cv2.dilate((mask * 255).astype(np.uint8), kernel, iterations=1).astype(np.float32) / 255.0

        # Многоуровневое цветное глоу (суммируем слои)
        '''
Вот тут магия неона:

Для каждого уровня блюра (sigma) делаем мягкое свечение.

Красим его в цвет по hue_base, насыщенность и яркость зависят от пульса и прогресса.

Суммируем все слои с весами (weight), получаем красивый многоцветный глоу.
        '''
        glow_acc = np.zeros_like(frame, dtype=np.float32)
        for sigma, weight in edge_blur_levels:
            # блюрим маску
            g = cv2.GaussianBlur((mask * 255).astype(np.uint8), (0, 0), sigmaX=sigma)
            # создаём RGB-цвет по hue + value = g
            hsv_col = np.zeros((h, w, 3), dtype=np.uint8)
            hsv_col[..., 0] = hue_base                             # H (0..179)
            sat_val = int(np.clip(180 * (0.6 + 0.4 * pulse * (1.0 - progress)), 0, 255))
            hsv_col[..., 1] = sat_val                              # S
            hsv_col[..., 2] = g                                    # V = маска-блюр
            col = cv2.cvtColor(hsv_col, cv2.COLOR_HSV2BGR).astype(np.float32)
            glow_acc += col * weight
        '''
👉 Ограничиваем значения, чтоб не улетело за пределы яркости.
        '''
        glow_acc = np.clip(glow_acc, 0.0, 255.0)
        
        # Композит: "color dodge" (яркий неон) + частичное смешивание с оригиналом
        '''
Мутим режим "color dodge" — он делает светлые области ещё ярче.
Типа пиксели начинают гореть как лампы в ночном клубе.
        '''
        frame_f = frame.astype(np.float32)
        dodge = frame_f * 255.0 / (255.0 - glow_acc + 1.0)   # безопасно на float
        dodge = np.clip(dodge, 0.0, 255.0)

        '''
👉 Смешиваем оригинал и неоновое свечение, постепенно усиливая эффект по мере прогресса.
        '''
        mix_strength = 0.6 * (0.25 + 0.75 * progress)  # сила эффекта по прогрессу
        out = cv2.addWeighted(frame_f, 1.0 - mix_strength, dodge, mix_strength, 0.0)

        # Немного подчёркиваем насыщенность/яркость
        '''
Финальная доводка:

Переводим в HSV, где легко крутить насыщенность и яркость.

Делаем цвета ярче и сочнее.

Яркость качает вместе с пульсом — типа лампа моргает.

Возвращаем всё обратно в BGR.
        '''
        hsv = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] = np.clip(hsv[..., 1] * (1.0 + 0.9 * progress), 0, 255)  # S boost
        hsv[..., 2] = np.clip(hsv[..., 2] * (1.0 + 0.45 * progress + 0.18 * pulse), 0, 255)  # V boost с пульсом
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        return result

    
    def glitch_shift(self, frame, t, duration):
        # Глитч с RGB-сдвигами и разрезанием на дергающиеся части
        progress = t / duration
        '''
👉 Считаем величину сдвига, зависящую от прогресса.
Чем дальше, тем сильнее двигает картинку, до 50 пикселей.
        '''
        shift = int(progress * 50)
        '''
👉 Сюда накидываем шум, как будто телек ловит сигнал через вешалку вместо антенны.
np.random.randint выдаёт числа от -10 до 10 для каждого пикселя.
        '''
        noise = np.random.randint(-10, 10, frame.shape, dtype=np.int16)
        '''
Переводим кадр в int16, чтоб при сложении с шумом не вылетело за границы.

Добавляем шум.

np.clip ограничивает значения от 0 до 255, иначе будут выжженные пиксели.

Возвращаем обратно в uint8, как нормальную картинку.
        '''
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        '''
👉 Делим кадр на три канала: красный, зелёный и синий.
        '''
        r, g, b = cv2.split(frame)
        '''
👉 Красный канал двигаем вправо на shift пикселей.
        '''
        r = np.roll(r, shift, axis=1)
        '''
👉 Зелёный наоборот двигаем влево на shift.
(Так создаётся RGB-расхождение, типа двоение картинки).
        '''
        g = np.roll(g, -shift, axis=1)
        '''
👉 Собираем всё обратно в одно изображение, уже глючное и цветастое.
        '''
        frame = cv2.merge([r, g, b])
        '''
👉 Пробегаем по всей картинке по вертикали, каждые 50 пикселей берём полосу.
        '''
        for i in range(0, frame.shape[0], 50):  # Разрезание на полосы
            '''
👉 Для каждой полосы считаем случайный сдвиг влево/вправо. Чем дальше прогресс — тем сильнее дёргает.
            '''
            dx = int(random.uniform(-shift, shift) * progress)
            '''
👉 Берём эту полосу и двигаем её на dx пикселей.
Каждая полоса едет в свою сторону — вот тебе и эффект "битого VHS".
            '''
            frame[i:i+50] = np.roll(frame[i:i+50], dx, axis=1)
        return frame


    
    def starburst_explosion(self, frame, t, duration):
        # прогресс 0..1 с easing (плавный выход)
        '''
Берём время t и делим на всю длительность эффекта.
Делаем ограничение от 0 до 1, чтоб не улетело за рамки.
1e-6 нужен, чтобы деление на ноль не случилось.
        '''
        progress = float(t) / max(1e-6, duration)
        progress = max(0.0, min(1.0, progress))
        '''
👉 Математическая приблуда — делает движение плавным:
сначала быстро, потом замедляется. Чтобы взрыв выглядел не как дерганый, а как кино.
        '''
        # easing: мягкий ease-out для красивого ускорения
        def ease_out_cubic(x): return 1 - (1 - x) ** 3
        p = ease_out_cubic(progress)

        h, w = frame.shape[:2]
        out = frame.copy().astype(np.uint8)

        # ---- BLOOM / звездочки (на уменьшенном слое для скорости) ----
        '''
Создаём пустую картинку поменьше (уменьшаем размер в 4 раза).
На ней будем рисовать свечение/звёздочки, потом увеличим обратно.
Экономия ресурсов, брат.
        '''
        scale = 4  # чем больше — тем быстрее и более мягкий bloom
        sw, sh = max(1, w // scale), max(1, h // scale)
        glow = np.zeros((sh, sw, 3), dtype=np.uint8)

        '''
👉 Чем дальше прогресс, тем больше звёздочек появляется (но не больше 200).
        '''
        max_stars = 80
        num_stars = int(max_stars * (p ** 0.9))
        num_stars = min(num_stars, 200)

        '''
👉 Генерим случайные координаты для каждой звезды на уменьшенной картинке.
        '''
        for _ in range(num_stars):
            # координаты и радиус в маленьком пространстве
            gx = random.randint(0, sw - 1)
            gy = random.randint(0, sh - 1)
            # радиус растёт по прогрессу, но остаётся мягким
            '''
👉 Радиус звезды зависит от прогресса: чем ближе к концу, тем они больше.
            '''
            r = max(1, int(1 + 6 * p * (0.6 + random.random() * 0.8)))
            # цвет: преимущественно тёплый/розоватый с лёгкой вариацией
            '''
👉 Цвет делаем в розово-тёплых тонах, с небольшой рандомной вариацией.
👉 Рисуем круг (звезду).
            '''
            color = (int(180 + random.random() * 75),
                     int(150 + random.random() * 105),
                     int(200 + random.random() * 55))
            cv2.circle(glow, (gx, gy), r, color, -1, lineType=cv2.LINE_AA)

        # мягкий blur на маленьком слое и апскейл
        '''
Размываем свечения, чтобы выглядело мягко и красиво.
Потом растягиваем обратно до оригинального размера кадра.
        '''
        k = max(1, int(3 + 10 * p))
        if k % 2 == 0:
            k += 1
        glow = cv2.GaussianBlur(glow, (k, k), 0)
        glow_up = cv2.resize(glow, (w, h), interpolation=cv2.INTER_LINEAR)
        # добавляем bloom с контролируемой интенсивностью
        '''
👉 Накладываем glow на оригинал, постепенно усиливая яркость к финалу взрыва.
        '''
        intensity = 0.18 + 0.6 * p
        out = cv2.addWeighted(out, 1.0, glow_up, intensity, 0)

        # ---- стрипы-хвосты (мягкие) ----
        '''
👉 Создаём отдельный слой для "хвостов" — светлых полос, как от взрыва.
👉 Чем дальше прогресс, тем больше полос.
        '''
        streaks = np.zeros_like(out)
        num_streaks = int(20 * p) + 6
        '''
👉 Для каждой полоски случайное место старта и угол направления.
        '''
        for _ in range(num_streaks):
            x = random.randint(0, w - 1)
            y = random.randint(0, h - 1)
            angle = random.uniform(0, 2 * math.pi)
            '''
👉 Полоски длинные, светлые, чуть суженные по вертикали, толщину тоже увеличиваем по прогрессу.
            '''
            length = int(30 + 220 * (p ** 1.1))
            dx = int(math.cos(angle) * length)
            dy = int(math.sin(angle) * length * 0.7)
            thickness = max(1, int(1 + 2 * p))
            col = (230, 230, 255)
            '''
👉 Рисуем светлые полоски, чтоб выглядело как разлетающиеся искры.
            '''
            cv2.line(streaks, (x, y), (max(0, min(w - 1, x + dx)), max(0, min(h - 1, y + dy))),
                     col, thickness, lineType=cv2.LINE_AA)
        # мягко размываем streaks
        '''
👉 Размываем полоски для мягкости и накладываем их поверх картинки.
        '''
        streaks = cv2.GaussianBlur(streaks, (7, 7), 0)
        out = cv2.addWeighted(out, 1.0, streaks, 0.28 * p, 0)

        # ---- Шарды: плавные "разрезы" с мягкими краями ----
        '''
👉 После 30% прогресса начинаем добавлять эффект осколков (фрагментов картинки).
        '''
        if p > 0.3:
            # shard_size адаптируется к разрешению
            '''
— Размер осколков зависит от размера кадра.
— move_strength — насколько сильно двигаются осколки (увеличивается с прогрессом).
— move_prob — вероятность, что кусок будет двигаться.
— Ограничиваем количество поворотов (поворот ресурсоёмкий).
            '''
            shard_size = max(64, min(160, int(min(h, w) / 8)))
            move_strength = (p - 0.3) / (1.0 - 0.3)
            move_strength = max(0.0, min(1.0, move_strength))
            # только часть шардов подвергается трансформации (экономия)
            move_prob = 0.35 + 0.55 * move_strength
            # ограничиваем количество поворотов (warpAffine дороже)
            max_rotates = 12
            rotates_done = 0

            '''
👉 Двигаемся по кадру блоками — типа режем изображение на квадраты (осколки).
            '''
            for i in range(0, h, shard_size):
                ph = min(shard_size, h - i)
                for j in range(0, w, shard_size):
                    pw = min(shard_size, w - j)
                    # вероятность задействования фрагмента
                    '''
👉 Не каждый фрагмент двигается — для экономии и случайности.
                    '''
                    if random.random() > move_prob:
                        continue

                    '''
👉 Берём кусочек кадра.
                    '''
                    src = frame[i:i + ph, j:j + pw].astype(np.uint8)

                    # Смещение: мягкое, направленное наружу от центра
                    '''
👉 Считаем смещение осколка от центра кадра.
                    '''
                    cx, cy = w / 2.0, h / 2.0
                    sx = (j + pw / 2.0) - cx
                    sy = (i + ph / 2.0) - cy
                    # нормализуем и усиливаем по прогрессу
                    '''
👉 Нормализуем направление: получаем вектор наружу от центра.
                    '''
                    dist = math.hypot(sx, sy) + 1e-6
                    nx, ny = sx / dist, sy / dist
                    '''
👉 Чем ближе к концу эффекта, тем дальше улетают осколки наружу.
                    '''
                    base_shift = 0.2 + 0.8 * move_strength  # множитель
                    max_shift = int(min(w, h) * 0.5 * base_shift)
                    dx = int(nx * max_shift * (0.4 + 0.6 * random.random()))
                    dy = int(ny * max_shift * (0.2 + 0.6 * random.random()))


                    '''
👉 Корректируем новые координаты осколка, чтоб не вылетал за картинку.
                    '''
                    new_j = j + dx
                    new_i = i + dy
                    # корректируем, чтобы фрагмент помещался
                    new_j = max(0, min(w - pw, new_j))
                    new_i = max(0, min(h - ph, new_i))

                    '''
👉 Иногда осколки чуть поворачиваем, чтоб выглядело натуральнее.
                    '''
                    dst_patch = src

                    # иногда делаем аккуратный поворот для натуральности, но редко
                    if rotates_done < max_rotates and random.random() < 0.18:
                        angle = random.uniform(-8.0, 8.0) * move_strength
                        M = cv2.getRotationMatrix2D((pw / 2.0, ph / 2.0), angle, 1.0)
                        rotated = cv2.warpAffine(src, M, (pw, ph), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                        dst_patch = rotated
                        rotates_done += 1
                    
                    # создаём мягкую маску (по яркости) и размываем её
                    '''
👉 Создаём мягкую маску, чтобы края осколков выглядели не жёстко, а с размытием.
                    '''
                    gray = cv2.cvtColor(dst_patch, cv2.COLOR_BGR2GRAY)
                    _, mask = cv2.threshold(gray, 6, 255, cv2.THRESH_BINARY)
                    mk = max(3, int(5 + 6 * (1 - move_strength)))
                    if mk % 2 == 0:
                        mk += 1
                    mask = cv2.GaussianBlur(mask, (mk, mk), 0).astype(np.float32) / 255.0
                    mask3 = np.repeat(mask[:, :, None], 3, axis=2)

                    # мягкое смешивание фрагмента с текущим фреймом
                    '''
👉 Накладываем осколок на новое место с плавным смешиванием.
                    '''
                    dst_roi = out[new_i:new_i + ph, new_j:new_j + pw].astype(np.float32)
                    src_f = dst_patch.astype(np.float32)
                    blended = (src_f * mask3 + dst_roi * (1.0 - mask3)).astype(np.uint8)
                    out[new_i:new_i + ph, new_j:new_j + pw] = blended

                    # добавляем тонкую подсветку края, чтобы разрез выглядел аккуратно
                    '''
👉 Добавляем подсветку края, чтобы выглядело аккуратнее, будто это реально треснуло.
                    '''
                    if pw > 6 and ph > 6:
                        edge_alpha = 0.25 * (0.3 + move_strength)
                        # рисуем светлую тонкую линию сверху-фрагмента
                        cv2.line(out, (new_j, new_i), (new_j + pw - 1, new_i), (230, 230, 255),
                                 max(1, int(1 + move_strength)), lineType=cv2.LINE_AA)

        # ---- лёгкое финальное свечение и виньетка (для фокусировки) ----
        # лёгкая виньетка, чтобы кадр выглядел глубже
        '''
👉 Делаем виньетку — затемнение по краям кадра.
        '''
        vx = cv2.getGaussianKernel(w, w * 0.9)
        vy = cv2.getGaussianKernel(h, h * 0.9)
        vignette = vy * vx.T
        '''
👉 Нормализуем виньетку (маску), чтобы значения были от 0 до 1.
        '''
        vmin = vignette.min()
        vmax = vignette.max()
        vnorm = (vignette - vmin) / (vmax - vmin + 1e-9)
        # усиливаем виньетку по мере прогресса
        '''
👉 Накладываем виньетку на кадр: чем дальше прогресс, тем сильнее затемнение по краям.
        '''
        vign_strength = 0.25 * p
        for c in range(3):
            out[:, :, c] = (out[:, :, c].astype(np.float32) * (1.0 - vign_strength * (1.0 - vnorm))).astype(np.uint8)

        return out

    def mirror_shatter(self, frame, t, duration):
        # Зеркальное отражение с разбиением на улетающие куски
        progress = t / duration
        '''
— Берём кадр и отражаем его по горизонтали.
То есть как будто в зеркало глянул — справа налево поменялось.
        '''
        mirrored = cv2.flip(frame, 1)  # Зеркальное отражение
        '''
— Тут мы мешаем оригинал и зеркалку в равных долях 50/50.
Получается эффект типа "раздвоение реальности" — половина настоящая, половина зеркальная.
        '''
        new_frame = cv2.addWeighted(frame, 0.5, mirrored, 0.5, 0)
        '''
— Проверка: эффект осколков включается только после того, как прошло 30% времени.
До этого просто зеркало мутит, а потом — начинается разлёт кусков.
        '''
        if progress > 0.3:
            '''
— Количество осколков растёт со временем.
Чем дальше, тем больше кусочков отлетает.
            '''
            num_shards = int(10 * progress)
            '''
— Берём высоту (h) и ширину (w) кадра, чтоб знать, где резать и кидать куски.
            '''
            h, w = frame.shape[:2]
            '''
— Цикл по количеству осколков.
То есть для каждого куска делаем отдельное "разлетание".
            '''
            for _ in range(num_shards):
                '''
— Выбираем случайные координаты (левый верхний угол кусочка) в пределах половины кадра.
Типа осколки не по всему экрану сразу, а с половины начинают.
                '''
                sx, sy = random.randint(0, w//2), random.randint(0, h//2)
                '''
— Вырезаем квадратик размером 50x50 пикселей из кадра — это и есть осколок (shard).
                '''
                shard = new_frame[sy:sy+50, sx:sx+50]
                '''
— Считаем смещение: куда улетит осколок.
Берём случайное число в пределах ширины/высоты кадра и умножаем на прогресс.
То есть сначала двигаются чуть-чуть, а под конец уже разлетаются по полной.
                '''
                dx, dy = int(random.uniform(-w, w) * progress), int(random.uniform(-h, h) * progress)
                '''
— Проверяем, чтобы осколок не вылетел за границы кадра.
Если слишком ушёл влево/вверх — прижимаем к 0,
если вправо/вниз — ограничиваем размером кадра минус 50 (размер осколка).
                '''
                new_sx = max(0, min(w - 50, sx + dx))
                new_sy = max(0, min(h - 50, sy + dy))
                '''
— Ставим осколок в новое место.
Типа кусочек стекла улетел и приклеился в другом месте.
                '''
                new_frame[new_sy:new_sy+50, new_sx:new_sx+50] = shard
        '''
Короче, брат, этот код мутит такую движуху:
сначала экран становится зеркально-двойным,
а потом маленькие квадраты-осколки начинают
рандомно разлетаться в разные стороны,
но аккуратно — чтобы не улетели за экран.
        '''
        return new_frame

    def color_wave_glitch(self, frame, t, duration):
        """
        Улучшенный color + wave + glitch эффект.
        frame: BGR uint8 numpy array
        t: время в секундах (float)
        duration: общая длительность эффекта (float)
        """

        # Параметры эффекта (можете подправить)
        hue_amp_max = 45           # максимальное смещение hue в градусах (0..179)
        hue_freq = 1.5             # частота изменения hue (Hz)
        slice_width = 24           # ширина "полос" для срезов
        slice_freq = 0.9           # частота смещений полос
        channel_shift_max = 12     # макс сдвиг каналов по X
        scanline_strength = 0.12   # сила сканлайнов (0..1)
        noise_amount = 0.025       # доля пикселей с шумом (0..1)

        # Безопасный прогресс 0..1
        progress = float(t) / max(float(duration), 1e-6)
        progress = max(0.0, min(1.0, progress))

        h, w = frame.shape[:2]

        # 1) Hue-волна: работаем в HSV на signed dtype, чтобы не было переполнений
        '''
— Переводим картинку в HSV (оттенок, насыщенность, яркость).
Делаем её int16, чтоб цвета не обрезались, когда их крутить будем.
        '''
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.int16)
        # вычисляем сдвиг по hue (целое, может быть отрицательным)
        '''
— Считаем, насколько надо сместить цветовой тон (hue).
Берём синус, умножаем на частоту и прогресс — и получаем, что оттенки по кругу бегают.
        '''
        hue_shift = int(round(hue_amp_max * progress * math.sin(2 * math.pi * hue_freq * t)))
        # корректно применяем % 180 на signed массиве и остаёмся в диапазоне 0..179
        '''
— Добавляем сдвиг к оттенку и загоняем в диапазон 0..179.
Иначе hue в OpenCV сходит с ума.
        '''
        hsv[..., 0] = (hsv[..., 0] + hue_shift) % 180

        # (опционально) немного потрясём насыщенность для живости
        '''
— Добавляем немного колебаний в насыщенность, чтоб цвета живее смотрелись.
Считай, краски дышат туда-сюда.
        '''
        sat_variation = 1.0 + 0.25 * math.sin(t * 3.0 + progress * 5.0)
        hsv[..., 1] = np.clip((hsv[..., 1].astype(np.float32) * sat_variation), 0, 255).astype(np.int16)

        # Переконвертируем назад в uint8
        '''
— Возвращаем всё обратно в нормальный формат uint8 и снова в BGR.
        '''
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        colored = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # 2) Полосовой (slice) глитч: сдвиги по вертикали для каждых полос
        '''
— Тут начинается глитч-полосы.
Берём по кускам (шириной slice_width) и сдвигаем их по вертикали на случайную величину.
Из-за cos эти полосы дёргаются туда-сюда.
        '''
        out = colored.copy()
        # Векторизуем: перебор по столбцам с шагом slice_width
        for x in range(0, w, slice_width):
            x2 = min(w, x + slice_width)
            # shift может быть отрицательным – roll корректно работает
            shift = int(round((10.0 * progress) * math.cos(t * slice_freq + x * 0.03)))
            if shift != 0:
                out[:, x:x2] = np.roll(out[:, x:x2], shift, axis=0)

        # 3) Хроматическая дисперсия / сдвиг каналов по X (мини глитч)
        '''
— Разделяем картинку на три канала: синий, зелёный, красный.
        '''
        b, g, r = cv2.split(out)
        # динамический сдвиг для каналов
        '''
— Считаем смещение и двигаем каналы:
синий уходит вправо, красный влево.
Из-за этого картинка как будто ломается на старом VHS.
        '''
        dx = int(round(channel_shift_max * (0.2 + 0.8 * progress) * math.sin(t * 2.5)))
        if dx != 0:
            b = np.roll(b, dx, axis=1)
            r = np.roll(r, -dx, axis=1)
        out = cv2.merge([b, g, r])

        # 4) Лёгкие сканлайны для "видеощума"
        '''
— Рисуем горизонтальные полоски, как на старых телевизорах.
Каждая вторая строка становится чуть темнее.
        '''
        if scanline_strength > 0:
            # делаем каждые 2-й пиксели чуть темнее
            mask = np.ones((h, 1), dtype=np.float32)
            mask[::2, 0] = 1.0 - scanline_strength
            out = (out.astype(np.float32) * mask[:, :, None]).astype(np.uint8)

        # 5) Небольшой полосовой случайный шум (для глитч-стиля)
        '''
— Добавляем рандомный шум:
в некоторых пикселях раскидываем случайные значения от -40 до +40.
Это придаёт эффект "помех" на экране.
        '''
        if noise_amount > 0:
            noise_mask = (np.random.rand(h, w) < noise_amount)
            if noise_mask.any():
                # создаём шумные полосы вертикально-сжатыми значениями
                noise_vals = np.random.randint(-40, 41, size=(h, w, 1)).astype(np.int16)
                tmp = out.astype(np.int16)
                tmp += (noise_mask[:, :, None].astype(np.int16) * noise_vals)
                out = np.clip(tmp, 0, 255).astype(np.uint8)

        '''
Короче, братан, этот эффект делает так:
сначала цвет по кругу бегает и переливается,
потом вертикальные полосы дёргаются,
каналы красный/синий разъезжаются,
сверху накидывается ретро-телевизор (полосы),
а в конце картинка трещит от шумов. 💥📺
        '''
        return out

    def pixel_fly_out(self, frame, t, duration, pixel_size=8, max_disp_factor=1.2, star_chance=0.12):
        """
        Эффект: пиксели улетают из центра блока с мягкой интерполяцией, добавляются
        мерцающие звезды и лёгкий «шлейф».
        - self: объект, в котором можно хранить кэш (self._pf_cache)
        - frame: BGR uint8 image
        - t: текущее время
        - duration: общая длительность
        - pixel_size: размер блока пикселя (влияет на стиль)
        - max_disp_factor: множитель максимального смещения относительно диагонали кадра
        - star_chance: базовая вероятность появления звезды в блоке (умножается на прогресс)
        """

        h, w = frame.shape[:2]
        '''
Считаем, сколько прошло времени в процентах (progress).
Делим текущее время t на duration, и зажимаем от 0 до 1.
Чтобы эффект плавно шёл, без выхода за рамки.
        '''
        progress = np.clip(float(t) / float(max(duration, 1e-9)), 0.0, 1.0)
        # ease-out (cubic)
        '''
Это "ease-out" — плавное замедление в конце.
Типа сначала быстро пиксели разлетаются, потом — медленнее,
как пацан, что бегал от ментов, а потом подустал.
        '''
        eased = 1 - (1 - progress) ** 3

        # Инициализация кэша (векторы движения для каждого блока, флаги звёзд)
        '''
Тут мутим кэш — храним данные про пиксели, чтоб каждый раз заново не генерить.
Если кэша ещё нет, или размеры кадра изменились — создаём заново.
        '''
        if not hasattr(self, "_pf_cache") or self._pf_cache.get("shape") != (h, w, pixel_size):
            '''
Создаём пустой словарь cache и туда кидаем размеры.
Типа "паспорт" для кэша.
            '''
            cache = {}
            cache["shape"] = (h, w, pixel_size)
            # количество блоков по вертикали и горизонтали
            '''
Считаем сколько блоков по вертикали (bh) и горизонтали (bw).
То есть на сколько "кирпичиков" разрежем картинку.
            '''
            bh = (h + pixel_size - 1) // pixel_size
            bw = (w + pixel_size - 1) // pixel_size
            # Для стабильности используем numpy RNG с фиксированным сидом, зависящим от размеров
            '''
Генератор случайных чисел, привязанный к размеру кадра.
Чтобы эффект был одинаковый для одинакового размера,
а не каждый раз новый хаос.
            '''
            rng = np.random.RandomState(abs(h * 1231 + w * 7919) % (2**31 - 1))
            '''
Каждому блоку задаём угол, куда он будет лететь.
В радианах, от -π до π.
            '''
            angles = rng.uniform(-math.pi, math.pi, size=(bh, bw)).astype(np.float32)
            # базовая максимальная дистанция для блока (чтобы красиво вылетало за кадр)
            '''
Считаем диагональ картинки, типа максимальное расстояние.
И умножаем на коэффициент — это лимит, насколько далеко куски могут улететь.
            '''
            diag = math.hypot(w, h)
            max_disp = max_disp_factor * diag
            # распределим разные скорости: небольшая часть мелкомоторная, часть сильно улетает
            '''
Скорость разлёта для каждого блока: от медленного до дикого.
Часть пикселей чуть дернется, часть — улетит далеко.
            '''
            speeds = rng.uniform(0.15, 1.0, size=(bh, bw)).astype(np.float32) * max_disp
            # флаги появления звезды и их фазы/яркости
            '''
Задаём, где могут появляться звёзды. Только в части блоков (0.25).
А ещё — фазы звёзд, чтоб мерцали по-разному.
            '''
            star_flags = rng.rand(bh, bw) < 0.25  # только в некоторых блоках вообще возможны звёзды
            star_phases = rng.uniform(0.8, 1.4, size=(bh, bw)).astype(np.float32)
            cache["angles"] = angles
            cache["speeds"] = speeds
            cache["star_flags"] = star_flags
            cache["star_phases"] = star_phases
            cache["bh"] = bh
            cache["bw"] = bw
            cache["rng"] = rng  # чтобы при необходимости можно было генерить случайности
            '''
Сохраняем всё это добро в объект, чтоб использовать потом.
            '''
            self._pf_cache = cache
        else:
            cache = self._pf_cache

        bh = cache["bh"]
        bw = cache["bw"]
        angles = cache["angles"]
        speeds = cache["speeds"]
        star_flags = cache["star_flags"]
        star_phases = cache["star_phases"]
        rng = cache["rng"]

        # создаём карту источников для remap (map_x, map_y) — тип float32
        # grid координаты (x,y) для каждого пикселя (map expects map_x for cols)
        grid_x, grid_y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))

        # для каждого блока вычисляем смещение (в пикселях) и заполняем массив смещений
        disp_x = np.zeros((h, w), dtype=np.float32)
        disp_y = np.zeros((h, w), dtype=np.float32)
        #Дальше идёт блок с циклами, где пиксели реально разлетаются:
        '''
Тут для каждого блока считаем смещение (dx, dy) по углу и скорости.
То есть в какую сторону и насколько он улетит.
И заносим это в карты смещений.
        '''
        for by in range(bh):
            y0 = by * pixel_size
            y1 = min(h, y0 + pixel_size)
            for bx in range(bw):
                x0 = bx * pixel_size
                x1 = min(w, x0 + pixel_size)
                ang = angles[by, bx]
                spd = speeds[by, bx]
                # истинное смещение зависит от eased прогресса
                dx = math.cos(ang) * spd * eased
                dy = math.sin(ang) * spd * eased
                disp_y[y0:y1, x0:x1] = float(dy)
                disp_x[y0:y1, x0:x1] = float(dx)

        # Для remap: для каждой точки назначения (u,v) берем источник (u - dx, v - dy)
        '''
remap делает магию: берёт пиксели из исходного кадра,
сдвигает по нашим смещениям, и получается эффект разлетающихся пикселей.
        '''
        map_x = (grid_x - disp_x).astype(np.float32)
        map_y = (grid_y - disp_y).astype(np.float32)

        # Ремапим изображение (интерполяция делает движение гладким)
        # Преобразуем во float32 для аккуратного сложения со звёздами
        frame_f = frame.astype(np.float32)
        remapped = cv2.remap(frame_f, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)

        # Создаём слой звёздочек
        '''
Пустой слой под звёзды.
        '''
        star_layer = np.zeros_like(frame_f)
        # вероятность появления звезды растёт с прогрессом
        cur_star_prob = star_chance * progress
        # добавляем звёзды в центр блоков (направление и фаза дают мерцание)
        for by in range(bh):
            y0 = by * pixel_size
            y1 = min(h, y0 + pixel_size)
            cy = (y0 + y1) / 2.0
            for bx in range(bw):
                if not star_flags[by, bx]:
                    continue
                '''
Тут звезда появляется не всегда — по вероятности.
Типа "по фарту повезёт — будет звезда, нет — так нет".
                '''
                if rng.rand() > cur_star_prob:
                    continue
                x0 = bx * pixel_size
                x1 = min(w, x0 + pixel_size)
                cx = (x0 + x1) / 2.0
                # вычисляем текущую позицию звезды (та же логика, что и для пикселей)
                ang = angles[by, bx]
                spd = speeds[by, bx]
                dx = math.cos(ang) * spd * eased
                dy = math.sin(ang) * spd * eased
                dst_x = int(np.clip(cx + dx, 0, w - 1))
                dst_y = int(np.clip(cy + dy, 0, h - 1))
                # яркость и радиус звезды зависят от фазы и прогресса
                phase = star_phases[by, bx]
                br = float(180.0 * min(1.0, 0.6 + 0.6 * progress) * phase)
                radius = max(1, int(pixel_size * (0.6 + 0.8 * progress)))
                # рисуем белую звезду (additive)
                '''
Рисуем белую звезду кружочком на отдельном слое.
Яркость и радиус зависят от прогресса.
                '''
                cv2.circle(star_layer, (dst_x, dst_y), radius, (br, br, br), -1, lineType=cv2.LINE_AA)

        # Мягко размываем слой звёзд, чтобы получить свечения
        if progress > 0.02:
            glow_sigma = max(1.0, 2.0 + 8.0 * progress)
            '''
Размываем звёзды, чтобы светились, а не просто точки были.
            '''
            star_layer = cv2.GaussianBlur(star_layer, ksize=(0, 0), sigmaX=glow_sigma, sigmaY=glow_sigma)

        # Лёгкий шлейф / подсветка: смешиваем размытую версию исходного кадра
        '''
Делаем "шлейф" — размытую копию кадра, смешиваем её с основным эффектом и звёздами.
Выходит красиво: разлёт + сияние + движение.
        '''
        trail = cv2.GaussianBlur(frame_f, ksize=(0, 0), sigmaX=3.0 + 12.0 * progress)
        trail_alpha = 0.08 + 0.4 * eased  # чем дальше прогресс — тем заметнее шлейф
        # комбинируем: remapped + star_layer (аддитивно) + trail (слабая наложенная смесь)
        combined = remapped * (1.0 - 0.15 * eased) + trail * (0.15 * eased) + star_layer

        # По мере завершения эффекта немного затемняем оставшиеся области (плавное исчезание)
        '''
На финале эффект затухает, типа пиксели исчезают,
а исходное изображение чуть проступает.
        '''
        fade_out = 1.0 - 0.8 * eased
        combined = combined * fade_out + frame_f * (1.0 - fade_out) * 0.6

        # Клип и приведение к uint8
        '''
Обрезаем значения, чтобы картинка не вышла за пределы 0–255,
и возвращаем результат.
        '''
        combined = np.clip(combined, 0, 255).astype(np.uint8)
        return combined

    def hologram_flicker(self, frame, t, duration):
        '''
Забираем у кадра высоту и ширину, типа размеры нашей малявы.
        '''
        h, w = frame.shape[:2]
        '''
Считаем прогресс эффекта: делим прошедшее время t на всё время duration.
max(duration, 1e-6) — чтоб не делить на ноль.
np.clip(..., 0.0, 1.0) — фиксируем прогресс, чтоб он был строго от 0 до 1.
Короче, получаем: 0 = начало, 1 = конец.
        '''
        progress = float(np.clip(t / float(max(duration, 1e-6)), 0.0, 1.0))

        # Копируем кадр в float для безопасных операций
        '''
Делаем копию кадра, переводим в тип float32 и нормализуем в диапазон [0..1].
Это чтоб дальше математикой жонглировать без потерь.
        '''
        f = frame.astype(np.float32) / 255.0

        # ------------------------
        # 1) Динамический синий/циановый тинт
        # ------------------------
        # BGR: делаем сильнее синий и чуть пурпурный для эффекта голограммы
        tint_color = np.array([0.95, 0.35, 0.9], dtype=np.float32)  # B, G, R (0..1)
        '''
Альфа-прозрачность — чем дальше по времени, тем сильнее цветовой фильтр.
        '''
        base_alpha = 0.12 + 0.25 * progress  # усиление по прогрессу
        # небольшой фликер в альфе
        '''
Сюда добавили фликер (мигание).
Берём синус от времени, плюс рандом, чтоб дрожало по-настоящему, как будто помехи.
        '''
        alpha = base_alpha * (1.0 + 0.06 * math.sin(t * 12.0 + random.random() * 6.28))
        '''
Создаём поверхностный слой — весь закрашен в выбранный цвет.
        '''
        overlay = np.ones_like(f) * tint_color
        '''
Смешиваем оригинал и цветной слой. Чем выше alpha, тем больше синевы на экране.
        '''
        f = cv2.addWeighted(f, 1.0 - alpha, overlay, alpha, 0.0)

        # ------------------------
        # 2) Лёгкий хроматический сдвиг (cheap chromatic aberration)
        # ------------------------
        # Сдвиг каждой канала по x немного: зелёный/красный влево/вправо
        '''
Чем дальше эффект — тем сильнее двигаем каналы (хроматическая аберрация, типа цветные полосы).
        '''
        max_shift = int(6 * progress)  # максимальный сдвиг пикселей
        '''
Рассчитываем, насколько красный и синий каналы смещаются по горизонтали.
Зелёный остаётся на месте, чтоб картинка не съезжала совсем.
        '''
        if max_shift > 0:
            shift_r = int((max_shift) * (0.5 + 0.5 * math.sin(t * 7.0)))
            shift_b = -int((max_shift) * (0.5 + 0.5 * math.cos(t * 6.0)))
            # создаём копии каналов и смещаем
            '''
Берём каждый цветовой канал, сдвигаем, и потом собираем обратно.
И вуаля — картинка как будто бьётся цветными тенями по краям.
            '''
            b_ch = np.roll(f[:, :, 0], shift_b, axis=1)
            g_ch = np.roll(f[:, :, 1], 0, axis=1)
            r_ch = np.roll(f[:, :, 2], shift_r, axis=1)
            f = np.stack([b_ch, g_ch, r_ch], axis=2)

        # ------------------------
        # 3) Сканлайны (cheap)
        # ------------------------
        '''
Создаём массив координат по вертикали — будем по ним накладывать "сканлайны".
        '''
        y = np.arange(h, dtype=np.float32)[:, None]
        '''
Настраиваем силу, частоту и фазу полос — они будут мигать по вертикали, как на старых теликах.
        '''
        scan_strength = 0.04 + 0.08 * progress
        scan_freq = 1.5 + 2.5 * progress
        scan_phase = t * 40.0
        '''
Считаем паттерн полосочек.
        '''
        scan = 1.0 - scan_strength * (0.5 + 0.5 * np.sin(y * scan_freq + scan_phase))
        # Broadcasting по ширине и каналам
        '''
Умножаем картинку на эти полоски — вот тебе и сканлайны.
        '''
        f *= scan[:, :, None]

        # ------------------------
        # 4) Лёгкий шум / «помехи»
        # ------------------------
        '''
Добавляем шум, как будто помехи по экрану бегают.
Шум одинаковый для всех каналов, чтоб не рябило дико.
        '''
        noise_strength = 0.02 + 0.06 * progress
        noise = (np.random.randn(h, w, 1).astype(np.float32)) * noise_strength
        f += noise  # шум одинаковый для всех каналов (можно разнести, но дороже)

        # ------------------------
        # 5) Призрачный сдвиг (ghosting) — делает слоистость голограммы
        # ------------------------
        '''
Сила "призрачного сдвига". Чем дольше эффект, тем больше призрак заметен.
        '''
        ghost_alpha = 0.10 * progress
        '''
Создаём копию кадра, чуть смещаем и накладываем поверх с прозрачностью.
Выглядит как будто двойное изображение, прям голограммный стиль.
        '''
        if ghost_alpha > 0.003:
            ghost_shift = int(10 * progress * (0.5 + 0.5 * math.sin(t * 3.3)))
            ghost = np.roll(f, ghost_shift, axis=1)
            f = cv2.addWeighted(f, 1.0, ghost, ghost_alpha, 0.0)

        # ------------------------
        # 6) Разрезы/сдвиги по полосам (векторизовано с редким шагом)
        # ------------------------
        '''
Шаг и амплитуда для полосовых сдвигов. Типа рябь, которая ломает картинку кусками.
        '''
        step = 8  # шаг полос в пикселях — можно поднять, чтобы было ещё легче
        amp = max(1, int(12 * progress))
        # перебор полос, но шаг увеличен — дешёвая операция
        '''
Двигаем картинку кусками (по полосам).
Каждая полоса гуляет сама по себе, создавая эффект разрыва сигнала.
        '''
        for y0 in range(0, h, step):
            # небольшая вариативность для каждой полосы
            local_shift = int(amp * math.sin(t * 6.0 + y0 * 0.08 + random.random() * 2.0))
            if local_shift != 0:
                f[y0:y0 + step, :, :] = np.roll(f[y0:y0 + step, :, :], local_shift, axis=1)

        # ------------------------
        # 7) Умеренная пикселизация при сильном прогрессе (опционально и недорого)
        # ------------------------
        '''
Если эффект уже далеко зашёл (60%+), начинаем пикселизовать кадр.
factor — насколько сильно сжимаем картинку.
        '''
        if progress > 0.6:
            # фактор масштабирования 0.6..0.3
            factor = 1.0 - 0.5 * ((progress - 0.6) / 0.4)
            factor = float(np.clip(factor, 0.3, 1.0))
            '''
Сжали картинку и обратно растянули — получилась пикселизация, как будто сигнал совсем сыпется.
            '''
            if factor < 0.99:
                small_w = max(2, int(w * factor))
                small_h = max(2, int(h * factor))
                small = cv2.resize((f * 255.0).astype(np.uint8), (small_w, small_h), interpolation=cv2.INTER_LINEAR)
                f = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST).astype(np.float32) / 255.0

        # ------------------------
        # 8) Финальные корректировки яркости/фликер
        # ------------------------
        '''
Финальный фликер: иногда яркость падает/поднимается, как будто лампа моросит.
        '''
        flicker = 1.0
        if random.random() < 0.5 + 0.5 * progress:
            flicker *= 0.9 + 0.2 * random.random()
        # небольшой пульс
        '''
Добавляем пульсацию яркости через синус.
        '''
        flicker *= 1.0 + 0.03 * math.sin(t * 18.0)
        '''
Применяем этот фликер к картинке, но зажимаем всё в диапазон [0..1].
        '''
        f = np.clip(f * flicker, 0.0, 1.0)

        '''
Финалочка: возвращаем картинку обратно в стандартный uint8 (0..255).
👊 Всё, братан, разобрали функцию по косточкам.
        '''
        return (f * 255.0).astype(np.uint8)

    def fireworks_overlay(self, frame, t, duration):
        h, w = frame.shape[:2]
        progress = float(np.clip(t / float(max(duration, 1e-6)), 0.0, 1.0))

        base = frame.astype(np.float32) / 255.0
        '''
Создали пустой слой — сюда будем рисовать фейерверки.
        '''
        overlay = np.zeros_like(base, dtype=np.float32)

        # --- параметры фейерверков (легко настроить) ---
        '''
Чем дальше идём, тем больше фейерверков. Максимум — 8.
        '''
        max_fireworks = min(8, 1 + int(progress * 6))
        '''
База искр у каждой ракеты.
        '''
        sparks_base = 8
        '''
Радиус взрыва растёт со временем.
        '''
        radius_scale = 0.08 + 0.20 * progress

        '''
Цикл — для каждого фейерверка.
        '''
        for i in range(max_fireworks):
            '''
Шанс появления фейерверка: чем больше прогресс, тем выше шанс.
В начале мало, ближе к концу — почти всегда бахает.
            '''
            if random.random() > 0.25 + 0.75 * progress:
                continue
            '''
Рассчитываем радиус фейерверка.
Если слишком маленький (<6 пикселей) — скипаем, он будет невидим.
            '''
            radius = int(min(w, h) * radius_scale * (0.8 + 0.8 * random.random()))
            if radius < 6:
                continue
            '''
Случайные координаты центра (чтоб фейерверк был где-то сверху, не у земли).
            '''
            cx = random.randint(radius, w - radius - 1)
            cy = random.randint(int(h * 0.05), max(radius, int(h * 0.55)))
            '''
Случайный цвет. Нормализуем, чтоб не был слишком тёмный или слишком яркий.
Домножаем на 0.6 — приглушаем чуток.
            '''
            col = np.array([random.random(), random.random(), random.random()], dtype=np.float32)
            col = 0.6 * col / (col.max() + 1e-6)
            '''
Интенсивность свечения, зависит от прогресса.
            '''
            intensity = 0.6 + 1.4 * random.random() * progress

            '''
Зона квадрата, где будем рисовать круг взрыва.
            '''
            x0, x1 = max(0, cx - radius), min(w, cx + radius + 1)
            y0, y1 = max(0, cy - radius), min(h, cy + radius + 1)
            '''
Массив координат внутри квадрата.
            '''
            ys = np.arange(y0, y1, dtype=np.float32)[:, None]
            xs = np.arange(x0, x1, dtype=np.float32)[None, :]
            '''
Считаем расстояние от центра (радиальная маска).
            '''
            dist = np.sqrt((xs - float(cx)) ** 2 + (ys - float(cy)) ** 2)
            '''
Создаём маску для круглого градиента: в центре ярко, к краю — темнеет.
Степень 1.8 делает края мягче.
            '''
            mask = np.clip(1.0 - dist / float(radius), 0.0, 1.0)
            mask = mask ** 1.8
            '''
Красим область под фейерверк в нужный цвет.
            '''
            for ch in range(3):
                overlay[y0:y1, x0:x1, ch] += (col[ch] * intensity) * mask

            '''
Количество искр = базовое + зависит от прогресса.
            '''
            n_sparks = int(sparks_base + 10 * progress)
            '''
Начальный угол для искр — рандом.
            '''
            base_angle = random.random() * 2.0 * math.pi
            '''
Цикл для каждой искры.
            '''
            for s in range(n_sparks):
                '''
Каждой искре свой угол + случайное смещение.
                '''
                ang = base_angle + (s / float(n_sparks)) * 2.0 * math.pi + (random.random() - 0.5) * 0.3
                '''
Длина искры — от половины до почти полного радиуса.
                '''
                length = radius * (0.5 + 0.6 * random.random())
                '''
Координаты конца искры.
                '''
                x2 = int(cx + math.cos(ang) * length)
                y2 = int(cy + math.sin(ang) * length)
                '''
Сила свечения искры.
                '''
                spark_strength = 0.6 * (0.8 + 0.6 * random.random()) * progress
                '''
Цвет искры = цвет взрыва, умноженный на коэффициенты.
                '''
                color_float = (col * (1.0 + 0.6 * random.random()) * spark_strength).tolist()
                '''
Рисуем линию от центра до конца искры.
                '''
                cv2.line(overlay, (cx, cy), (x2, y2),
                         color=(float(color_float[0]), float(color_float[1]), float(color_float[2])),
                         thickness=1, lineType=cv2.LINE_AA)
                '''
На конце искры ставим яркую точку-блик.
                '''
                rr = max(1, int(radius * 0.06))
                cv2.circle(overlay, (x2, y2), rr,
                           color=(float(color_float[0]), float(color_float[1]), float(color_float[2])),
                           thickness=-1, lineType=cv2.LINE_AA)

        '''
Размазываем всё, чтоб сияло мягко, как настоящий фейерверк.
        '''
        sigma = 1.0 + 2.0 * progress
        overlay = cv2.GaussianBlur(overlay, ksize=(0, 0), sigmaX=sigma, sigmaY=sigma)

        '''
Смешиваем фон и фейерверки.
Обрезаем яркость (clip).
Делим на (1+0.2*out), чтобы картинка не была пересвеченной.
        '''
        out = base + overlay
        out = np.clip(out, 0.0, 1.2)
        out = out / (1.0 + 0.2 * out)

        # --- переработанные разрезы/сдвиги: теперь полосы могут покрывать всю ширину ---
        '''
После середины добавляем эффект "разрезов".
        '''
        if progress > 0.45:
            # Если хотим более драматично — полностью покрывать уже при прогрессе > 0.75
            '''
Иногда разрез идёт на всю ширину кадра (при прогрессе > 0.75 почти всегда).
            '''
            full_width_threshold = 0.75
            use_full_width = progress >= full_width_threshold or (random.random() < 0.35 * progress)
            # параметры полос
            '''
Параметры полос:
— step: высота полосы (чем дальше — тем тоньше).
— max_shift: насколько сильно двигаем полосу.
— edge_highlight: яркость подсветки краёв.
            '''
            step = max(6, int(6 + 18 * (1.0 - progress)))   # при прогрессе полосы тоньше
            max_shift = int(40 * progress)                  # максимальный пиксельный сдвиг
            edge_highlight = 0.35 + 0.65 * progress         # яркость подсветки края разреза

            '''
Бежим по картинке полосами.
            '''
            for y0 in range(0, h, step):
                # немного вариативности, иногда сильный разрез, иногда почти нет
                '''
Редко пропускаем полосу на маленьком прогрессе.
                '''
                local_rand = random.random()
                if local_rand > 0.95 and progress < 0.6:
                    continue  # редкие пропуски на низком прогрессе
                # направление и величина сдвига
                '''
Сдвиг полосы зависит от времени и случайности.
                '''
                shift = int(max_shift * math.sin(t * 3.0 + y0 * 0.08 + random.random()))
                # сдвиг без лишних копирований: работаем по полоске
                '''
Верхняя граница полосы.
                '''
                y1 = min(h, y0 + step)
                '''
Если выбрали "полный разрез".
                '''
                if use_full_width:
                    # сдвигаем всю строку целиком (полное перекрытие)
                    if shift != 0:
                        out[y0:y1, :, :] = np.roll(out[y0:y1, :, :], shift, axis=1)
                    # подсветка границы разреза — добавляем тонкую светящуюся линию
                    # для эффекта "реза" подсветим вертикальную границу посредине полосы
                    '''
Посередине полосы делаем яркую вертикальную подсветку — типа "разрез".
Ширина линии уменьшается со временем.
                    '''
                    mid_x = w // 2
                    bw = max(1, int(2 * (1.0 - progress)))  # ширина подсветки (уменьшается с прогрессом)
                    lx = max(0, mid_x - bw)
                    rx = min(w, mid_x + bw)
                    # простой добавочный слой в полосе (бережно)
                    out[y0:y1, lx:rx, :] += edge_highlight * (0.5 + 0.5 * random.random())
                    '''
Иначе сдвигаем только часть кадра.
                    '''
                else:
                    # ранее применялось только к части; теперь даём возможность выбрать
                    #центрную или левую часть
                    '''
Ширина блока, который двигаем.
                    '''
                    slice_w = int(w * (0.25 + 0.6 * progress))  # расширенная доля
                    # делаем иногда левую, иногда правую, иногда центральную
                    mode = random.choice(['left', 'right', 'center'])
                    if mode == 'left':
                        x0s, x1s = 0, slice_w
                    elif mode == 'right':
                        x0s, x1s = max(0, w - slice_w), w
                    else:
                        x0s = max(0, (w - slice_w) // 2)
                        x1s = x0s + slice_w
                    '''
Сдвигаем выбранный кусок кадра.
                    '''
                    if x1s - x0s > 2 and shift != 0:
                        block = out[y0:y1, x0s:x1s, :].copy()
                        out[y0:y1, x0s:x1s, :] = np.roll(block, shift, axis=1)
                        # подсветка по краю сдвига (тёмно/светло градиент)
                        '''
Иногда добавляем подсветку на краю сдвига.
Типа шрам на картинке — светится, чтобы эффект был жёстче.
                        '''
                        if random.random() < 0.6:
                            # подсветка на границе справа/слева блока
                            if shift > 0:
                                # левый край подсвечиваем
                                lx = x0s
                                rx = min(w, x0s + 2 + int(2 * progress))
                            else:
                                lx = max(0, x1s - (2 + int(2 * progress)))
                                rx = x1s
                            out[y0:y1, lx:rx, :] += 0.25 * edge_highlight

        # --- редкие белые точки (блики) ---
        '''
Иногда добавляем "звёзды" (белые точки блика).
        '''
        if random.random() < 0.25 * progress:
            stars = 6 + int(10 * progress)
            '''
Рисуем белые точки-блики случайно по верхней части экрана.
            '''
            for _ in range(stars):
                sx = random.randint(0, w - 1)
                sy = random.randint(0, int(h * 0.6))
                rr = max(1, int(1 + 2 * progress))
                out[sy:sy + rr + 1, sx:sx + rr + 1, :] += 0.6

        out = np.clip(out, 0.0, 1.0)
        '''
👊 Всё, братуха.
Эта функция делает мощный эффект фейерверков с искрами, вспышками и разрезами,
как будто картинка ломается под напором салюта.
        '''
        return (out * 255.0).astype(np.uint8)



    '''
Оформляем движуху: функция, которая будет плавить картинку, типа как мороженое тает.
    '''
    def liquid_melt(self, frame, t, duration):
        h, w = frame.shape[:2]
        progress = float(np.clip(t / float(max(duration, 1e-6)), 0.0, 1.0))
        '''
Если прогресс почти нулевой — возвращаем оригинал, типа ничего не произошло.
        '''
        if progress <= 1e-6:
            return frame

        # Параметры эффекта (легко настраиваются)
        '''
Максимум, насколько пиксели будут съезжать.
Чем выше картинка, тем сильнее тает, но не более 80 пикселей.
        '''
        max_amp = max(8, int(min(h * 0.20, 80)))   # максимальный сдвиг в пикселях
        '''
Считаем фактический сдвиг: чем дальше по времени, тем сильнее тает.
        '''
        amp = int(max_amp * progress)
        '''
Частота волн, как сильно картинка «пульсирует» по ширине.
        '''
        freq = 2.0 * math.pi / max(40.0, w * 0.06)  # пространственная частота по ширине
        '''
Скорость плавления — чем больше времени прошло, тем быстрее капает.
        '''
        speed = 1.6 + 1.4 * progress                 # скорость анимации
        '''
Сила шума: добавляем случайные микро-колебания для реалистичности.
        '''
        noise_strength = 0.08 * amp                  # малый шум по столбцам

        # Пересчёт смещений по столбцам (векторно)
        '''
Создаём массив координат по ширине.
        '''
        xs = np.arange(w, dtype=np.float32)
        '''
Основной сдвиг: синусоидальная волна, типа волны по картинке идут.
        '''
        base_shift = amp * np.sin(xs * freq + t * speed).astype(np.float32)
        '''
Случайный шум, чтоб не всё было одинаково.
        '''
        noise = (np.random.randn(w).astype(np.float32)) * noise_strength
        '''
Общий сдвиг: волна + шум.
        '''
        disp = base_shift + noise  # смещение (может быть положительным/отрицательным)

        # Координатные карты для remap: для каждого dst (y,x) берем src_y = y - disp[x] * weight(y)
        '''
Массив координат по высоте, в столбик.
        '''
        ys = np.arange(h, dtype=np.float32)[:, None]  # форма (h,1)
        # Вес смещения по вертикали: больше эффекта у верхних пикселей (как будто стекает вниз)
        '''
Вес эффекта: сверху тает сильнее, снизу почти не двигается (имитация стекания).
        '''
        power = 1.2
        weight = (1.0 - ys / float(max(1, h - 1))) ** power  # (h,1)
        '''
Двигаем пиксели вниз по массе.
        '''
        map_y = ys - (disp[None, :] * weight)                # (h,w)
        '''
Горизонталь не меняется, копируем массив по высоте.
        '''
        map_x = np.tile(xs[None, :], (h, 1)).astype(np.float32)

        # Ограничиваем map_y в допустимой области
        '''
Ограничиваем, чтобы пиксели не улетели за пределы кадра.
        '''
        map_y = np.clip(map_y, 0.0, float(h - 1)).astype(np.float32)

        # Быстрое ремаппинг (C-реализация)
        '''
Перерисовываем кадр с учётом наших смещений. Получаем «растаявшую» картинку.
        '''
        melted = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        # Небольшая вертикальная размазка для эффекта вязкости (дешевая)
        '''
Если эффект уже видимый, добавляем вертикальный блур, типа капля вязко тянется вниз.
        '''
        if amp > 2:
            blur_k = 1 + int(2 * progress)  # 1..3
            # blur только по вертикали: (1, k)
            melted = cv2.blur(melted, (1, blur_k))

        # Создаём overlay для капель/блеска (uint8, чтобы рисование было корректным)
        '''
Пустая картинка под капли.
        '''
        overlay = np.zeros_like(frame, dtype=np.uint8)

        # Рисуем редкие капли/вылеты (малое число — дешёво)
        '''
Кол-во капель: чем дальше эффект, тем больше их падает.
        '''
        max_drops = min(14, int(12 * progress) + 1)
        '''
Иногда капля вообще не рисуется, чтоб было случайно.
        '''
        for i in range(max_drops):
            if random.random() > 0.8 + 0.2 * progress:
                continue
            '''
Координаты старта капли (в верхней части картинки).
            '''
            sx = random.randint(0, w - 1)
            sy = random.randint(0, max(1, int(h * 0.6)))
            '''
Длина капли: чем дальше по времени, тем длиннее.
            '''
            drop_len = int(min(h * 0.18, 6 + 36 * progress * random.random()))
            '''
Конец капли: вниз по Y.
            '''
            ex = sx
            ey = min(h - 1, sy + drop_len)

            # Берём цвет из оригинала (корректно в tuple int)
            '''
Берём цвет из исходного кадра в точке старта, чтобы капля была «цветная».
            '''
            src_y = min(max(0, sy), h - 1)
            src_x = min(max(0, sx), w - 1)
            c = frame[src_y, src_x]
            color = (int(c[0]), int(c[1]), int(c[2]))  # BGR tuple ints

            '''
Толщина линии капли.
            '''
            thickness = 1 if w < 1000 else 2
            '''
Рисуем каплю линией.
            '''
            cv2.line(overlay, (sx, sy), (ex, ey), color, thickness=thickness, lineType=cv2.LINE_AA)
            # В конце капли — маленькая белая блик-точка
            '''
На кончике капли ставим белый блик — типа свет отражается.
            '''
            tip_r = max(1, int(1 + 2 * progress))
            cv2.circle(overlay, (ex, ey), tip_r, (255, 255, 255), -1, lineType=cv2.LINE_AA)
            # Наложение overlay'а на растаявшее изображение (мягко)
        '''
Переводим в float для удобства при наложении.
        '''
        melted_f = melted.astype(np.float32)
        overlay_f = overlay.astype(np.float32)
        '''
Смешиваем кадр с каплями (капли становятся виднее по мере прогресса).
        '''
        alpha = 0.45 * progress  # сила видимости капель
        out_f = melted_f + overlay_f * alpha

        # Лёгкая тональная компрессия + клип
        '''
Ограничиваем цвета в диапазоне 0–255.
        '''
        out = np.clip(out_f, 0.0, 255.0).astype(np.uint8)

        return out


    '''
Функция мутит эффект "неонового свечения" с глитчами.
    '''
    def neon_glow2(self, frame, t, duration):
        
        # Параметры
        progress = max(0.0, min(1.0, t / float(duration)))
        h, w = frame.shape[:2]
        '''
Делаем уменьшенную копию (в 2 раза меньше), чтоб не нагружать проц, типа экономим ресурсы.
        '''
        scale = 0.5  # обрабатываем уменьшенную копию для производительности
        small_w, small_h = max(1, int(w * scale)), max(1, int(h * scale))

        # уменьшить
        '''
Сжали картинку до малого размера.
        '''
        small = cv2.resize(frame, (small_w, small_h), interpolation=cv2.INTER_LINEAR)

        # Мультяшный базовый слой:
        #несколько проходов bilateral для сохранения краев и сглаживания цветов
        '''
Два раза прогнали фильтр bilateral: он сглаживает цвета, но оставляет края.
Получается мультяшный стиль.
        '''
        filtered = small.copy()
        for _ in range(2):
            filtered = cv2.bilateralFilter(filtered, d=9, sigmaColor=75, sigmaSpace=75)

        # Края (тонкие контуры) для рисунка
        '''
Делаем чёрно-белую картинку.
        '''
        gray = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
        '''
Чутка замылили, чтоб шум прибить.
        '''
        gray = cv2.medianBlur(gray, 5)
        '''
Находим границы — как будто обвели фломастером.
        '''
        edges = cv2.Canny(gray, 50, 150)
        # Утолщаем контур, чтобы он выглядел более мультяшно
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        edges = cv2.dilate(edges, kernel, iterations=1)  # 0/255

        # Неоновый цвет (плавно меняется со временем)
        colorA = np.array([200, 40, 220], dtype=np.uint8)   # розово-фиолетовый
        colorB = np.array([60, 220, 240], dtype=np.uint8)   # бирюзовый
        '''
Двигаем туда-сюда по синусу, чтоб цвет пульсировал.
        '''
        mix = 0.5 * (1.0 + math.sin(t * 1.5))
        '''
Смешиваем цвета, получается живой перелив.
        '''
        neon_color = (colorA.astype(np.float32) * (1 - mix) + colorB.astype(np.float32) * mix).astype(np.uint8)

        # Создаем цветную маску краев (на уменьшенной копии)
        '''
Берём маску контуров и красим их в неоновые цвета.
        '''
        colored_edges_small = np.zeros_like(filtered)
        mask = edges == 255
        colored_edges_small[mask] = neon_color

        # Размытые ореолы (глоу) — несколько проходов с разными ядрами
        '''
Размываем контуры несколько раз, чтоб вокруг появился ореол (свечение).
        '''
        glow_small = colored_edges_small.copy()
        glow_small = cv2.GaussianBlur(glow_small, (7, 7), 0)
        glow_small = cv2.addWeighted(glow_small, 1.0, cv2.GaussianBlur(glow_small, (13, 13), 0), 0.8, 0)

        # Пульсация интенсивности свечения
        '''
Свечение дышит, пульсирует.
        '''
        pulse = 0.6 * (0.6 + 0.4 * math.sin(t * 5))  # в диапазоне примерно [0.36,0.96]

        # Смешиваем мультяшный слой и глоу на уменьшенной копии
        combined_small = cv2.addWeighted(filtered, 1.0, glow_small, pulse, 0)

        # Маска тонких ярких контуров (чтобы линии были яркими поверх)
        '''
Добавляем тонкие яркие линии поверх свечения.
        '''
        bright_edges_small = np.zeros_like(filtered)
        bright_edges_small[mask] = (neon_color.astype(np.float32) * 1.2).clip(0, 255).astype(np.uint8)

        '''
Накладываем их на результат.
        '''
        combined_small = cv2.addWeighted(combined_small, 1.0, bright_edges_small, 0.9 * pulse, 0)

        # Вернуть к исходному размеру
        combined = cv2.resize(combined_small, (w, h), interpolation=cv2.INTER_LINEAR)

        # Для глитч-срезов работаем на полном размере
        result = combined.copy()

        # Несколько горизонтальных срезов-глитчей (не тяжело: малые шаги)
        slice_h = max(4, int(h * 0.01))  # высота блока
        max_shift = max(4, int(w * 0.04))  # максимальное смещение по x
        # вероятность появления глитча растет с прогрессом
        glitch_chance = 0.02 + 0.45 * progress

        '''
Пробегаем по картинке полосами, иногда выбираем полосу для глитча.
        '''
        for y in range(0, h, slice_h):
            if random.random() < glitch_chance:
                '''
Границы полосы.
                '''
                dy = slice_h
                y2 = min(h, y + dy)
                # смещение зависит от времени и вертикальной позиции для разнообразия
                '''
Считаем, насколько полосу сдвинуть. Немного случайности для хаоса.
                '''
                dx = int(max_shift * math.sin(t * 6.0 + y * 0.1))
                dx = dx + int((random.random() - 0.5) * max_shift * 0.6)
                # Сдвигаем блок
                '''
Берём блок и сдвигаем его вбок.
                '''
                block = result[y:y2].copy()
                block = np.roll(block, dx, axis=1)
                # Хроматическая аберрация: слегка сдвинуть каналы внутри блока
                '''
Хроматическая аберрация: каналы немного разъезжаются, как в глитчах на VHS.
                '''
                if dx != 0:
                    b, g, r = cv2.split(block)
                    shift_small = int(max(1, abs(dx) * 0.15))
                    b = np.roll(b, -shift_small, axis=1)
                    r = np.roll(r, shift_small, axis=1)
                    block = cv2.merge([b, g, r])
                '''
Возвращаем изменённый блок обратно.
                '''
                result[y:y2] = block

        # Немного усилить контраст/насыщенность для "неонового" вида (легкий LUT через HSV)
        '''
Немного поднимаем насыщенность и яркость, чтоб было «как в клубе» — чистый неон.
        '''
        hsv = cv2.cvtColor(result, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] = (hsv[..., 1] * 1.05).clip(0, 255)  # насыщенность
        hsv[..., 2] = (hsv[..., 2] * 1.03).clip(0, 255)  # яркость
        result = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        return result

    def time_warp(self, frame, t, duration):
        h, w = frame.shape[:2]
        progress = float(np.clip(t / duration, 0.0, 1.0))
        # масштабирование (центральное, плавное)
        warp = 1.0 + 0.6 * (progress ** 1.2)
        '''
Увеличиваем кадр. Типа картинку раздули, чтоб по кайфу смотрелось.
        '''
        scaled = cv2.resize(frame, None, fx=warp, fy=warp, interpolation=cv2.INTER_LINEAR)
        '''
Центр увеличенной картинки. Без центра — никуда, всё крутится вокруг него.
        '''
        cy, cx = scaled.shape[0] // 2, scaled.shape[1] // 2
        '''
Высчитываем сдвиг, чтоб вырезать кусок по размеру оригинала из увеличенной картинки.
        '''
        y0 = max(0, cy - h // 2); x0 = max(0, cx - w // 2)
        '''
Вырезаем центр обратно в размер оригинала. Получаем ровный кадр после зума
        '''
        new_frame = scaled[y0:y0 + h, x0:x0 + w].copy()

        # слоёвое смещение: аккумулируем в float32, чтобы избежать лишних копий
        '''
Количество слоёв для смещения — будем дублировать кадр и двигать по бокам.
        '''
        layers = 4
        '''
Копим результат в формате float32, чтоб не потерять качество при смешивании.
        '''
        acc = new_frame.astype(np.float32)
        '''
Пробегаем по всем слоям.
        '''
        for i in range(1, layers + 1):
            '''
Каждый слой двигаем по-разному. Чем дальше слой, тем сильнее сдвиг.
            '''
            shift = int((4 + 10 * i) * progress)  # горизонтальный сдвиг
            '''
Если слой чётный — двигаем вправо, если нечётный — влево. Типа волны.
            '''
            layer = np.roll(new_frame, shift if (i % 2 == 0) else -shift, axis=1)
            '''
Прозрачность слоя. Чем ближе к концу эффекта, тем меньше его видно.
            '''
            alpha = (i / (layers + 1)) * (0.55 * (1.0 - 0.45 * progress))
            # accumulateWeighted достаточно быстрый и экономит память
            '''
Складываем слой с общим результатом. Грамотно миксуем, чтобы красиво было.
            '''
            cv2.accumulateWeighted(layer.astype(np.float32), acc, alpha)

        # хроматическая аберрация (легкое смещение каналов для "супер" вида)
        '''
Переводим накопленный результат обратно в 8-бит (нормальная картинка).
        '''
        acc_u8 = np.clip(acc, 0, 255).astype(np.uint8)
        '''
Разделяем каналы BGR.
        '''
        b, g, r = cv2.split(acc_u8)
        '''
Сколько сдвигать каналы для аберрации. Чем дальше, тем сильнее.
        '''
        ch_shift = max(1, int(3 * progress))
        '''
Сдвигаем синий влево, красный вправо. Получается такой кислотный эффект, типа глаза ломает.
        '''
        b = np.roll(b, -ch_shift, axis=1)
        r = np.roll(r, ch_shift, axis=1)
        '''
Склеиваем обратно каналы. Теперь с красивым хроматическим глюком.
        '''
        merged = cv2.merge([b, g, r]).astype(np.float32)

        # генерируем и кэшируем звёзды один раз (самые ресурсоёмкие операции не выполнять каждый кадр)
        '''
Проверяем, есть ли уже готовые "звёзды".
Если нет — создаём и храним в объекте (чтоб не пересоздавать каждый кадр).
        '''
        if not hasattr(self, '_tw_stars') or self._tw_stars.shape[0] < 1:
            '''
Создаём генератор случайных чисел.
С фиксированным сидом, чтоб результат был одинаковый при каждом запуске.
            '''
            rng = np.random.default_rng(12345)  # фиксированный сид для стабильности
            '''
Количество звёзд. Чем больше экран — тем больше звёзд.
            '''
            N = max(50, (w * h) // 20000)  # разумное число звёзд в зависимости от разрешения
            '''
Генерим координаты и радиусы для каждой звезды.
            '''
            xs = rng.integers(0, w, size=N)
            ys = rng.integers(0, h, size=N)
            rs = rng.integers(1, 3, size=N)
            '''
Складываем всё в одну матрицу и сохраняем.
            '''
            self._tw_stars = np.column_stack((xs, ys, rs))
        # отображаем долю звёзд пропорционально progress (и немного случайного мерцания по времени)
        '''
Количество звёзд, которое показываем в кадре. Чем ближе к концу — тем больше.
        '''
        star_count = int(len(self._tw_stars) * (0.2 + 0.8 * progress))
        '''
Создаём пустую картинку для звёзд.
        '''
        overlay = np.zeros((h, w, 3), dtype=np.uint8)
        '''
Берём только часть звёзд, которая нужна сейчас.
        '''
        for (x, y, r) in self._tw_stars[:star_count]:
            '''
Звёзды чуть увеличиваются по мере прогресса.
            '''
            radius = int(r + progress * 2)
            '''
Цвет звезды — бело-жёлтый, с оттенком ярче к концу.
            '''
            color = (255, 255, int(200 + 55 * progress))
            '''
Рисуем звезду кружочком.
            '''
            cv2.circle(overlay, (int(x), int(y)), radius, color, -1, lineType=cv2.LINE_AA)
        # добавляем звёзды в виде лёгкого свечения (умножаем интенсивность на progress)
        '''
Добавляем звёзды к картинке. Чем дальше — тем они ярче.
        '''
        merged += overlay.astype(np.float32) * (0.6 * progress)

        
        # простая виньетка (быстро считается через расстояние)
        '''
Координаты всех точек кадра (сетка).
        '''
        ys, xs = np.indices((h, w))
        '''
Центр картинки (с плавающей точкой).
        '''
        cx_f, cy_f = w / 2.0, h / 2.0
        '''
Считаем расстояние от центра для каждой точки.
        '''
        dist = np.sqrt((xs - cx_f) ** 2 + (ys - cy_f) ** 2)
        '''
Максимальное расстояние до углов. Нормировка.
        '''
        maxd = np.sqrt(cx_f ** 2 + cy_f ** 2)
        '''
Создаём виньетку: края затемняются сильнее, центр остаётся ярким.
        '''
        vign = 1.0 - 0.6 * (dist / maxd) ** 1.5 * progress
        '''
Применяем виньетку к картинке.
        '''
        merged *= vign[:, :, None]

        '''
💡 Короче, брат, этот эффект работает так:
Сначала зум, потом несколько слоёв смещения → добавляем хроматический глюк,
вешаем звёзды, и сверху — виньетка.
В итоге выходит космический "варп-эффект", как будто в гиперпространство влетаешь.
        '''
        return np.clip(merged, 0, 255).astype(frame.dtype)


    '''
👉 Определяем функцию, которая будет рвать картинку на куски
и отбрасывать их назад, типа они уменьшаются и улетают.
grid_size — сколько кусочков будет по сетке.
    '''
    def explosion_shatter_backward(self, frame, t, duration, grid_size=10):
        """Фрагменты улетают НАЗАД (уменьшаются)"""
        progress = t / duration
        h, w = frame.shape[:2]
        '''
Создаём пустой чёрный кадр, на него будем собирать всю движуху.
        '''
        new_frame = np.zeros_like(frame)

        '''
Делаем сетку из grid_size на grid_size фрагментов. Типа делим картинку на квадратики.
        '''
        gh, gw = grid_size, grid_size
        '''
Бегаем по всей сетке: строка за строкой, кусок за куском.
        '''
        for i in range(gh):
            for j in range(gw):
                '''
Считаем координаты углов текущего куска (левый верх и правый низ).
Так определяем область для этого квадратика.
                '''
                x1, y1 = j * w // gw, i * h // gh
                x2, y2 = (j+1) * w // gw, (i+1) * h // gh
                '''
Вырезаем кусок из оригинального кадра. Это и есть фрагмент для анимации.
                '''
                frag = frame[y1:y2, x1:x2]
                '''
Берём высоту и ширину этого фрагмента. Нужно для ресайза.
                '''
                fh, fw = frag.shape[:2]

                # Уменьшение (улетает назад)
                '''
Чем дальше идём по времени,
тем сильнее уменьшаем кусок.
В начале scale ≈ 1 (оригинал), в конце почти 0.1 (очень маленький).
Ниже 0.1 не даём, чтоб фрагменты совсем не исчезли.
                '''
                scale = max(0.1, 1 - progress * 0.9)
                '''
Уменьшаем кусок по масштабу. Минимум 1 пиксель, чтобы OpenCV не упал.
                '''
                frag_resized = cv2.resize(frag, (max(1, int(fw*scale)), max(1, int(fh*scale))))
                '''
Получаем новые размеры уменьшенного фрагмента.
                '''
                rh, rw = frag_resized.shape[:2]

                # Центрируем
                '''
Вычисляем новые координаты фрагмента так,
чтобы он оставался по центру своего квадратика.
Иначе он бы съезжал куда-то в сторону.
                '''
                fx = (x1 + x2)//2 - rw//2
                fy = (y1 + y2)//2 - rh//2

                '''
Проверяем, что фрагмент не вылез за границы кадра. А то будет ошибка.
                '''
                if 0 <= fx < w and 0 <= fy < h:
                    '''
Ограничиваем нижний правый угол, чтоб точно влезло в картинку.
                    '''
                    x_end, y_end = min(w, fx+rw), min(h, fy+rh)
                    '''
Если кусок торчит, подрезаем его, чтоб не вышел за кадр.
                    '''
                    frag_crop = frag_resized[:y_end-fy, :x_end-fx]
                    '''
Берём регион в новом кадре, куда будем вставлять кусок.
                    '''
                    roi = new_frame[fy:y_end, fx:x_end]
                    '''
Прозрачность: в начале куски яркие (alpha ≈ 1), ближе к концу почти исчезают.
Берём прогресс в степени 1.5, чтоб плавнее уходило.
                    '''
                    alpha = max(0, 1 - progress**1.5)
                    '''
Смешиваем кусок с фоном. Чем дальше — тем куски прозрачнее.
                    '''
                    blended = cv2.addWeighted(frag_crop, alpha, roi, 1 - alpha, 0)
                    '''
Вставляем смешанный кусок обратно в новый кадр.
                    '''
                    new_frame[fy:y_end, fx:x_end] = blended
        '''
💡 В итоге получаем эффект: вся картинка разбивается на квадраты,
и они как будто улетают в глубину,
уменьшаясь и растворяясь. Типа "взорвалось, но в обратку".
        '''
        return new_frame

    def explosion_shatter_sides(self, frame, t, duration, grid_size=10):
        """Фрагменты: левые улетают вправо, правые — влево"""
        progress = t / duration
        h, w = frame.shape[:2]
        new_frame = np.zeros_like(frame)

        gh, gw = grid_size, grid_size
        '''
mid_x — середина кадра по горизонтали. По этой линии решаем: кусок левый или правый.
        '''
        mid_x = w // 2

        for i in range(gh):
            for j in range(gw):
                x1, y1 = j * w // gw, i * h // gh
                x2, y2 = (j+1) * w // gw, (i+1) * h // gh
                '''
Вырезаем кусок из исходного кадра. Это наш фрагмент.
                '''
                frag = frame[y1:y2, x1:x2]
                '''
Запоминаем его размеры.
                '''
                fh, fw = frag.shape[:2]

                '''
Вот тут движуха:

Если кусок слева от центра (x1 < mid_x) → тащим вправо (dx положительный).

Если справа → тащим влево (dx отрицательный).
👉 Сила сдвига зависит от progress
(чем дальше во времени, тем сильнее улетает),
и масштабаем на 1.2*ширина, чтоб точно улетели за экран.
                '''
                dx = int(progress * w * 1.2) if x1 < mid_x else -int(progress * w * 1.2)


                '''
Новые координаты верхнего угла для вставки фрагмента:

fx — куда по горизонтали сдвинем,

fy — вертикаль остаётся как была.
                '''
                fx = x1 + dx
                fy = y1


                '''
Проверяем, не вылетел ли кусок совсем за кадр. Если в пределах — вставляем.
                '''
                if 0 <= fx < w and 0 <= fy < h:
                    '''
Считаем правый нижний угол, ограничиваем рамками кадра.
                    '''
                    x_end, y_end = min(w, fx+fw), min(h, fy+fh)
                    '''
Если фрагмент выходит за границу — подрезаем его, чтобы аккуратно вставить.
                    '''
                    frag_crop = frag[:y_end-fy, :x_end-fx]
                    '''
Берём область на новом кадре, куда этот кусок встанет.
                    '''
                    roi = new_frame[fy:y_end, fx:x_end]
                    '''
Прозрачность: в начале кусок яркий (alpha≈1), под конец растворяется (alpha→0).
                    '''
                    alpha = max(0, 1 - progress**1.5)
                    '''
Смешиваем кусок с текущим содержимым новой картинки, плавно делая его прозрачным.
                    '''
                    blended = cv2.addWeighted(frag_crop, alpha, roi, 1 - alpha, 0)
                    new_frame[fy:y_end, fx:x_end] = blended
        return new_frame

    def cartoonify2(self, frame, t, duration):
        progress = t / duration

        # --- 1. Уменьшаем для скорости ---
        '''
Делаем картинку меньше в два раза. Так быстрее считать и меньше напрягать процессор.
        '''
        small = cv2.pyrDown(frame)

        # --- 2. Повышаем яркость и контраст для мультяшного вида ---
        '''
Переводим картинку в цветовую систему HSV
(где отдельные каналы: оттенок, насыщенность и яркость). Удобнее крутить цвета.
        '''
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        '''
Разделили картинку на три канала: h — цвет, s — насыщенность, v — яркость.
        '''
        h, s, v = cv2.split(hsv)
        '''
Подкрутили насыщенность (чтоб цвета были ярче) и яркость (чтоб всё сияло).
        '''
        s = cv2.add(s, 30)   # насыщенность
        v = cv2.add(v, 20)   # яркость
        '''
Собрали каналы обратно.
        '''
        hsv = cv2.merge((h, s, v))
        '''
Вернули картинку обратно в обычный BGR (стандартный цвет в OpenCV).
        '''
        small = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

        # --- 3. Квантование цветов через K-means ---
        '''
Делаем из картинки массив точек
(каждая точка — это один пиксель с 3 числами: синий, зелёный, красный).
        '''
        data = np.float32(small).reshape((-1, 3))
        '''
Говорим: "Оставим только 9 цветов". Будет как рисованное, без плавных переходов.
        '''
        K = 9  # количество цветов
        '''
Запускаем кластеризацию K-means:

data — все пиксели.

K — число цветов.

Критерии — либо 20 итераций, либо точность 1.0.

10 раз пробуем, чтобы выбрать лучший результат.

PP_CENTERS — умно выбираем стартовые точки.
        '''
        _, labels, centers = cv2.kmeans(
            data, K, None,
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0),
            10, cv2.KMEANS_PP_CENTERS
        )
        '''
Заменяем каждый пиксель на ближайший из 9 цветов.
Получаем картинку, как будто художник нарисовал заливками.
        '''
        centers = np.uint8(centers)
        quantized = centers[labels.flatten()].reshape(small.shape)

        # --- 4. Обводка контуров ---
        '''
Переводим в чёрно-белое, чтобы найти границы.
        '''
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        '''
Алгоритм Канни ищет чёткие линии на картинке.
        '''
        edges = cv2.Canny(gray, 100, 200)
        '''
Делаем линии толще, чтоб больше походило на мультяшку.
        '''
        edges = cv2.dilate(edges, None)   # утолщаем линии
        '''
Инвертируем: линии стали чёрные, фон белый.
        '''
        edges = cv2.bitwise_not(edges)    # чёрные линии на белом
        '''
Переводим линии обратно в трёхканальный цвет, чтобы их можно было совмещать с цветной картинкой.
        '''
        edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # --- 5. Соединяем заливки и линии ---
        '''
Накладываем чёткие линии на заливку цветов. Получается эффект рисованного комикса.
        '''
        cartoon_small = cv2.bitwise_and(quantized, edges_colored)

        # --- 6. Лёгкое сглаживание, чтобы убрать “шум” ---
        '''
Пропускаем через фильтр, который сглаживает цвета, но сохраняет края. Так картинка смотрится аккуратнее.
        '''
        cartoon_small = cv2.bilateralFilter(cartoon_small, d=5, sigmaColor=50, sigmaSpace=50)

        # --- 7. Возвращаем размер ---
        '''
Увеличиваем обратно до исходного размера кадра.
        '''
        cartoon = cv2.pyrUp(cartoon_small)

        # --- 8. Плавный переход (обычное → мультяшное) ---
        '''
Делаем плавное смешивание:

В начале (progress=0) видим обычное видео.

В конце (progress=1) видим мультяшный вариант.
        '''
        cartoon = cv2.addWeighted(frame, 1 - progress, cartoon, progress, 0)

        '''
⚡ В итоге: картинка ярче, цвета ограничены, контуры жирные,
всё плавно переходит от реала в "мульт". Выглядит как будто нарисовали.
        '''
        return cartoon

    def infinity_spiral2(self, frame, t, duration, twist=3.0, pull=0.5, spins=2.0):
        """
    Плавная насыщенная бесконечная спираль.
    - twist: сила закручивания (больше = более густая спираль)
    - pull: затягивание в центр
    - spins: количество оборотов за анимацию
        """
        # Нормализованный прогресс
        progress = t / duration
        # Плавная кривая (ease-in-out, синусоида)
        '''
Чтобы картинка крутилась не дёргано, а плавно,
делаем «синусовую» плавность:
медленно стартанула, разогналась и аккуратно затормозила.
        '''
        smooth_progress = 0.5 * (1 - np.cos(progress * np.pi))

        '''
Берём высоту и ширину кадра.
Находим центр, потому что именно туда будем тянуть и вокруг него крутить.
        '''
        h, w = frame.shape[:2]
        center_x, center_y = w / 2, h / 2

        # Координатная сетка
        '''
Строим сетку координат: x и y — это матрицы,
где для каждой точки указано её место. Без этого никак не закрутишь картинку.
        '''
        y, x = np.indices((h, w))
        '''
Считаем смещения: насколько каждая точка удалена от центра по горизонтали и вертикали.
        '''
        dx = x - center_x
        dy = y - center_y

        # Полярные координаты
        '''
Переводим картинку в полярку:

r — это расстояние до центра (радиус).

theta — угол от центра.
        '''
        r = np.sqrt(dx**2 + dy**2)
        theta = np.arctan2(dy, dx)

        # Спиральное закручивание
        '''
Вот тут самое мясо:

крутим картинку на угол,
зависящий от прогресса (smooth_progress * spins * 2π = сколько раз повернётся).

плюс добавляем «twist» — чем дальше от центра, тем сильнее поворачивает (густая спираль).
        '''
        theta += smooth_progress * spins * 2 * np.pi + twist * (r / max(w, h))

        # Затягивание в центр
        '''
Радиус уменьшаем — как будто пиксели засасывает в центр. Чем дальше прогресс, тем сильнее тянет.
        '''
        r = r * (1 - pull * smooth_progress)

        # Новые координаты
        '''
Находим новые координаты пикселей после кручения.

cos и sin переводят полярные координаты обратно в обычные.

% w и % h не дают картинке вывалиться за границы — типа замыкаем её бесконечно.
        '''
        src_x = (center_x + r * np.cos(theta)).astype(np.int32) % w
        src_y = (center_y + r * np.sin(theta)).astype(np.int32) % h

        '''
Собираем новый кадр: берём пиксели из старого по новому маршруту.
Всё перемешалось — получилась кручёная спираль.
        '''
        new_frame = frame[src_y, src_x]

        '''
👉 Отдаём готовый кадр. Всё,
видос закрутился как воронка, будто в параллельный мир затягивает. 🌪️
        '''
        return new_frame

    
    def mirror_maze2(self, frame, t, duration):
        # Нормализуем прогресс
        progress = max(0.0, min(1.0, t / duration))
        '''
Если времени ноль — возвращаем картинку без всяких фокусов. Нечего дергаться.
        '''
        if progress == 0.0:
            return frame.copy()

        h, w = frame.shape[:2]
        out = frame.copy()

        # Параметры, можно подстроить
        '''
Решаем, сколько зеркал будет.

базово 2.

добавляем ещё, по мере прогресса (максимум до 5).
        '''
        base_mirrors = 2
        extra_max = 3             # всего до 5 зеркал
        num_mirrors = base_mirrors + int(progress * extra_max)
        '''
Настройки для красоты:

offset — отступ зеркал от центра.

scale — насколько уменьшаются дальние зеркала.

rotation_max — насколько сильно могут поворачиваться.

shear_max — наклон вбок.

alpha — базовая прозрачность ближних слоёв.
        '''
        base_offset = int(20 + 10 * progress)
        max_depth_scale = 0.7     # насколько глубже зеркало может сжимать
        rotation_max = 8.0        # градусы
        shear_max = 0.15          # небольшая горизонтальная деформация
        base_alpha = 0.85         # базовая непрозрачность ближних зеркал

        '''
Погнали делать все зеркала по очереди.
        '''
        for i in range(1, num_mirrors + 1):
            '''
Глубина зеркала: чем дальше, тем больше номер → тем прозрачнее и меньше.
            '''
            depth = i / float(num_mirrors)                 # [0..1]
            # масштаб: глубже -> меньше (параболический эффект чуть заметнее)
            '''
Чем глубже зеркало, тем оно меньше. Если стало совсем микроскопическим — скипаем.
            '''
            scale = 1.0 - (max_depth_scale * (depth ** 1.2) * progress)
            if scale <= 0.05:
                continue

            # перспективное сжатие: ширина уменьшаем сильнее
            '''
Уменьшаем размеры картинки в зависимости от глубины.
По ширине режем сильнее — чтоб эффект перспективы.
            '''
            small_w = max(2, int(w * scale * (1.0 - 0.25 * depth * progress)))
            small_h = max(2, int(h * scale))

            # resize (быстрое уменьшение — INTER_AREA)
            '''
Сжимаем картинку до этих размеров.
            '''
            small = cv2.resize(frame, (small_w, small_h), interpolation=cv2.INTER_AREA)

            # лёгкое вращение (попеременно влево/вправо)
            '''
Каждое зеркало чутка поворачиваем то влево, то вправо (зависит от номера).
            '''
            angle = ((-1) ** i) * rotation_max * depth * progress
            '''
Собственно, крутим изображение, при этом края зеркалим, чтоб дыр не было.
            '''
            Mrot = cv2.getRotationMatrix2D((small_w / 2.0, small_h / 2.0), angle, 1.0)
            small = cv2.warpAffine(small, Mrot, (small_w, small_h), flags=cv2.INTER_LINEAR,
                                   borderMode=cv2.BORDER_REFLECT)

            # лёгкая "сдвиг-наклон" (shear) по X для перспективы
            '''
Добавляем наклон влево/вправо для реализма.
            '''
            shear = ((-1) ** (i + 1)) * shear_max * depth * progress
            # affine matrix: [1, shear, 0; 0,1,0]
            '''
Шифтуем по оси X (типа «shear»). Чтобы влезло — расширяем ширину.
            '''
            A = np.float32([[1.0, shear, 0.0], [0.0, 1.0, 0.0]])
            # расширим ширину на запас, если shear положительный/отрицательный
            add_w = int(abs(shear) * small_h) + 2
            small = cv2.warpAffine(small, A, (small_w + add_w, small_h), flags=cv2.INTER_LINEAR,
                                   borderMode=cv2.BORDER_REFLECT)
            '''
Обновляем новую ширину после наклона.
            '''
            small_w = small.shape[1]  # обновлённая ширина

            # лёгкое размытие для глубины (только для i>1)
            '''
Дальние зеркала слегка размываем — чтоб ощущение глубины.
            '''
            if i > 1:
                small = cv2.GaussianBlur(small, (3, 3), 0)

            # зеркальный фрагмент для правой стороны
            '''
Делаем зеркальную копию (правую сторону).
            '''
            flipped = cv2.flip(small, 1)

            # позиционирование: постепенно от смещения к центру и вниз (параллакс)
            '''
Смещаем зеркала: чем дальше, тем сильнее вбок и вниз уходит.
            '''
            offset_x = int(i * base_offset * progress + depth * 8)
            offset_y = int(depth * 18 * progress)

            # альфа: ближние более яркие, дальние более прозрачны
            '''
Чем дальше зеркало, тем более прозрачное.
            '''
            alpha_global = base_alpha * (1.0 - 0.6 * depth * progress)
            alpha_global = float(np.clip(alpha_global, 0.08, 0.95))

            # цветовая тонировка: ближе — нейтрально, дальше — холод/тёпло переменная
            # создаём матрицу однотонного цвета и смешиваем
            '''
Дальним зеркалам подмешиваем цвет — то холодный, то тёплый, чтоб был эффект разноцветных отражений.
            '''
            tint_strength = 0.12 * depth * progress  # 0..~0.12
            # example: чередуем теплую и холодную тонировки
            if i % 2 == 0:
                tint_color = np.full_like(small, (12, 0, 0))      # лёгкий тёплый (BGR)
            else:
                tint_color = np.full_like(small, (0, 8, 16))      # лёгкий холодный
            small = cv2.addWeighted(small, 1.0 - tint_strength, tint_color, tint_strength, 0)

            # prepare alpha mask: плавное затухание по горизонтали (по краям)
            '''
Делаем градиент (маску для прозрачности).
            '''
            w_s = small_w
            ramp = np.linspace(1.0, 0.0, w_s).astype(np.float32)
            # создаём двухстороннюю маску (центр прозрачнее, края — более прозрачные)
            # лучше создать центральный пиковый профиль:
            '''
Маска делается так, чтобы по краям прозрачнее, а в центре плотнее. Это даёт эффект настоящего зеркала.
            '''
            center = w_s // 2
            left = np.linspace(0.0, 1.0, center, endpoint=False)
            right = left[::-1]
            if w_s % 2 == 1:
                profile = np.concatenate([left, [1.0], right])
            else:
                profile = np.concatenate([left, right])
            profile = profile * alpha_global  # масштабируем по глобальной альфе
            alpha_mask = np.tile(profile[np.newaxis, :], (small.shape[0], 1))  # H x W
            alpha_mask = np.expand_dims(alpha_mask, axis=2)  # H x W x 1

            # Функция наложения блока с маской на выходное изображение (без выделения объектов)
            '''
Тут мини-функция: накладываем зеркало на основное изображение, смешивая по альфа-маске.
            '''
            def blend_to(dst, src, top, left):
                h_s, w_s = src.shape[:2]
                y1 = max(0, top)
                y2 = min(h, top + h_s)
                x1 = max(0, left)
                x2 = min(w, left + w_s)
                if y1 >= y2 or x1 >= x2:
                    return
                sy1 = y1 - top
                sy2 = sy1 + (y2 - y1)
                sx1 = x1 - left
                sx2 = sx1 + (x2 - x1)
                src_part = src[sy1:sy2, sx1:sx2].astype(np.float32)
                dst_part = dst[y1:y2, x1:x2].astype(np.float32)

                am = alpha_mask[sy1:sy2, sx1:sx2]
                # 3-channel alpha
                am3 = np.repeat(am, 3, axis=2)
                blended = src_part * am3 + dst_part * (1.0 - am3)
                dst[y1:y2, x1:x2] = np.clip(blended, 0, 255).astype(np.uint8)

            # Наложение левого зеркала
            blend_to(out, small, offset_y, offset_x)

            # Наложение правого зеркала (с учётом правой границы)
            right_x = w - offset_x - small_w
            blend_to(out, flipped, offset_y, right_x)

        '''
🔥 Братан, эффект реально солидный, как будто в «Дом смеха» попал.
        '''
        return out



    '''
Функция мутит эффект глитча.
Берёт кадр frame, время t, сколько длится эффект duration,
ну и параметры:
насколько по вертикали дёргать картинку (max_vshift)
и сколько уровней цвета оставлять (posterize_max_levels).
    '''
    def glitch_art2(self, frame, t, duration, max_vshift=24, posterize_max_levels=16):
        # прогресс 0..1
        progress = float(np.clip(t / float(duration), 0.0, 1.0))

        h, w = frame.shape[:2]
        new_frame = frame.copy()

        # 1) Постеризация (уменьшаем количество уровней цвета по мере прогресса)
        # levels: от posterize_max_levels (малый глитч) до 2 (сильный глитч)
        '''
Считаем сколько цветов оставим.
В начале много (почти без глитча),
к концу всё скатывается до 2 уровней (жёсткий глитч, всё в кислотных пятнах).
        '''
        levels = max(2, int(posterize_max_levels - (posterize_max_levels - 2) * progress))
        '''
Рассчитываем шаг квантизации. Чем меньше уровней — тем больше шаг.
        '''
        quant = max(1, 256 // levels)
        # integer posterize: убрать дробную часть цветов
        '''
Жёстко округляем цвета к ближайшему "уровню". Это и есть постеризация.
Добавляем quant//2, чтоб картинка не выглядела чересчур тухлой.
        '''
        new_frame = (new_frame // quant) * quant + quant // 2
        '''
Обрезаем значения, чтоб не вылезали за границы допустимого 0–255. Приводим к целому типу пикселей.
        '''
        new_frame = np.clip(new_frame, 0, 255).astype(np.uint8)

        # 2) Вертикальные полосы: создаём несколько блоков столбцов и сдвигаем их по Y
        '''
Количество полос (вертикальных кусков). Чем дальше прогресс, тем больше этих полос.
        '''
        bands = 2 + int(progress * 6)  # от 2 до ~8
        '''
Насколько сильно можно дёргать полосы вверх-вниз. В начале чуть-чуть, потом всё сильнее.
        '''
        max_shift = max(0, int(max_vshift * (0.15 + 0.85 * progress)))
        '''
Будем гонять каждую полосу.
        '''
        for _ in range(bands):
            '''
Ширина полосы случайная: от маленькой до довольно широкой.
            '''
            bw = random.randint(max(1, int(w * 0.03)), max(2, int(w * 0.18)))
            '''
Выбираем случайно, где именно эта полоса начинается по горизонтали.
            '''
            x = random.randint(0, max(0, w - bw))
            '''
Решаем, насколько её сдвинуть по вертикали (вверх или вниз).
            '''
            shift_y = random.randint(-max_shift, max_shift)
            '''
Если есть сдвиг — берём эту полосу и прокручиваем вверх/вниз (как телек без антенны).
            '''
            if shift_y != 0:
                # np.roll быстро делает вертикальный сдвиг
                new_frame[:, x:x + bw] = np.roll(new_frame[:, x:x + bw], shift_y, axis=0)

        # 3) Короткие яркие линийки (scan streaks), иногда горизонтальные, иногда вертикальные
        '''
С шансом (зависящим от прогресса) добавляем яркие линии.
        '''
        if random.random() < 0.9 * (0.3 + 0.7 * progress):
            '''
Чем дальше по прогрессу — тем больше линий.
            '''
            lines = 1 + int(progress * 8)
            '''
Насколько сильно эти линии светятся (амплитуда яркости).
            '''
            amp = int(80 * progress) + 10  # яркость добавления
            '''
Рисуем каждую линию.
            '''
            for _ in range(lines):
                '''
С 60% вероятностью — делаем горизонтальную линию. Иначе вертикальную.
                '''
                if random.random() < 0.6:
                    # горизонтальная линия
                    '''
Берём случайное место по высоте, задаём толщину линии (1–4 пикселя).
                    '''
                    y = random.randint(0, max(0, h - 1))
                    th = random.randint(1, min(4, max(1, int(h * 0.02))))
                    '''
Создаём полоску такого же размера, заполняем ярким цветом.
                    '''
                    tmp = np.zeros((th, w, 3), dtype=np.uint8) + random.randint(amp//2, amp)
                    '''
Накладываем полоску поверх кадра. Она как вспышка.
                    '''
                    y1 = np.clip(y, 0, h - th)
                    new_frame[y1:y1 + th] = cv2.add(new_frame[y1:y1 + th], tmp)
                    '''
Это аналогично, только для вертикальной линии.
                    '''
                else:
                    # вертикальная линия
                    x = random.randint(0, max(0, w - 1))
                    tw = random.randint(1, min(6, max(1, int(w * 0.02))))
                    tmp = np.zeros((h, tw, 3), dtype=np.uint8) + random.randint(amp//2, amp)
                    x1 = np.clip(x, 0, w - tw)
                    new_frame[:, x1:x1 + tw] = cv2.add(new_frame[:, x1:x1 + tw], tmp)

        # 4) Направленное лёгкое размытие (имитация motion smear)
        '''
Чуть позже в процессе (когда уже >5% эффекта) начинаем мутить размытость.
        '''
        if progress > 0.05:
            '''
Размер фильтра размытия. Должен быть нечётным. Чем дальше прогресс — тем сильнее размывает.
            '''
            k = 1 + int(progress * 8)  # kernel length
            if k % 2 == 0:
                k += 1
            # иногда вертикальное, иногда горизонтальное
            '''
Случайно выбираем: размытие вертикальное или горизонтальное.
Эффект "смаза", как будто картинку дёрнули.
            '''
            if random.random() < 0.5:
                # вертикальное размытие: kernel (k,1)
                new_frame = cv2.blur(new_frame, (1, k))
            else:
                # горизонтальное: kernel (1,k)
                new_frame = cv2.blur(new_frame, (k, 1))

        # 5) Лёгкая хрома-смесь: сдвигаем каналы немного и смешиваем
        '''
Разделяем картинку на три канала: синий, зелёный, красный.
        '''
        b, g, r = cv2.split(new_frame)
        '''
Считаем, насколько сдвигать красный и синий каналы влево/вправо.
        '''
        rx = int((2 + int(6 * progress)) * random.choice([-1, 1]))
        bx = -int((1 + int(4 * progress)) * random.choice([-1, 1]))
        '''
Сдвигаем каналы, получается эффект цветного раздвоения.
        '''
        r = np.roll(r, rx, axis=1)
        b = np.roll(b, bx, axis=1)
        # смешиваем каналы обратно с небольшой прозрачностью, чтобы не терять контраст
        merged = cv2.merge([b, g, r])
        '''
Смешиваем оригинал и сдвинутую версию с разной прозрачностью. Это даёт глитчевый колорит.
        '''
        alpha = 0.75 + 0.25 * random.random() * (1.0 - progress)
        new_frame = cv2.addWeighted(new_frame, alpha, merged, 1.0 - alpha, 0)

        # 6) Небольшой аддитивный шум (только если прогресс > 0)
        '''
Сила шума. Чем дальше по прогрессу, тем больше.
        '''
        noise_amp = int(18 * progress)
        '''
Генерим рандомный шум (зерно),
размножаем на три канала (RGB) и накладываем на картинку.
Это усиливает грязь и глитч.
        '''
        if noise_amp > 0:
            noise = np.random.randint(0, noise_amp, (h, w, 1), dtype=np.uint8)
            noise = np.repeat(noise, 3, axis=2)
            new_frame = cv2.add(new_frame, noise)

        return new_frame.astype(np.uint8)

    def glitch_art3(self, frame, t, duration, max_pixel_size=12, max_wave=18):
        # прогресс 0..1
        progress = float(np.clip(t / float(duration), 0.0, 1.0))

        h, w = frame.shape[:2]
        new_frame = frame.copy()

        # 1) Пикселизация / мозайка (чем больше прогресс — тем крупнее пиксели)
        '''
Размер квадратиков для мозайки растёт по мере прогресса.
В начале почти гладко, потом всё квадратами.
        '''
        pixel_size = 1 + int((max_pixel_size - 1) * progress)
        '''
Сжимаем картинку в маленький размер: чем крупнее пиксель, тем меньше итоговое изображение.
        '''
        if pixel_size > 1:
            small_w = max(1, w // pixel_size)
            small_h = max(1, h // pixel_size)
            # downscale + upscale (INTER_NEAREST даёт четкие блоки)
            '''
Короче, сначала жмём картинку, чтоб она стала мелкой и потеряла детали, потом растягиваем обратно,
но не сглаживая, а квадратиками. Получается эффект мозайки — всё как будто в Майнкрафте.
            '''
            small = cv2.resize(new_frame, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
            new_frame = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)

        # 2) Волновые локальные полосы — синусные сдвиги строк внутри небольших полос
        '''
Тут мутим "волну": по кадру выбираем полоски и двигаем пиксели туда-сюда синусом.
— bands: сколько таких полос будет, чем дальше эффект, тем их больше.
— max_band_h: максимальная высота полосы, чтоб не всё полотно двигать.
— wave_amp: сила смещения (амплитуда), растёт по мере прогресса.
        '''
        bands = 1 + int(progress * 5)  # количество полос
        max_band_h = max(2, int(h * 0.12))
        wave_amp = max(1, int(max_wave * (0.1 + 0.9 * progress)))
        '''
Выбираем случайную полосу по высоте band_h,
где она начинается y0, задаём частоту и фазу для синуса.
        '''
        for _ in range(bands):
            band_h = random.randint(2, max_band_h)
            y0 = random.randint(0, max(0, h - band_h))
            freq = random.uniform(0.02, 0.25)
            phase = random.uniform(0, 2 * np.pi)
            # генерим смещения для каждой строки в полосе (меньше работы, чем по всему кадру)
            ys = np.arange(band_h)
            '''
Для каждой строки в этой полосе считаем смещение offs по X.
            '''
            offs = (np.sin(ys * freq + phase) * wave_amp * random.uniform(0.4, 1.0)).astype(int)
            # применяем построчно — band_h обычно невелик
            '''
Берём каждую строчку в полосе, и если смещение dx не ноль, двигаем её вбок.
Типа у картинки живот ходуном ходит — глич волной.
            '''
            for i, row in enumerate(range(y0, y0 + band_h)):
                dx = int(offs[i])
                if dx:
                    # сдвигаем по X (колонки)
                    new_frame[row] = np.roll(new_frame[row], dx, axis=0)

        # 3) Инвертирующие / «вспышка» прямоугольники — с небольшой прозрачностью
        '''
Иногда бахаем прямоугольники, где цвета инвертируются (типа вспышка).
Чем дальше эффект, тем больше прямоугольников.
        '''
        if random.random() < 0.6 * progress:
            rects = 1 + int(progress * 3)
            '''
Размер и позиция прямоугольника случайные.
            '''
            for _ in range(rects):
                rw = random.randint(max(4, int(w * 0.04)), max(8, int(w * 0.25)))
                rh = random.randint(max(2, int(h * 0.03)), max(6, int(h * 0.2)))
                x = random.randint(0, max(0, w - rw))
                y = random.randint(0, max(0, h - rh))
                '''
Вырезаем кусок, делаем его инверсией (чёрное-белое меняется местами),
и мешаем с оригиналом через addWeighted, чтоб выглядело полупрозрачно, как блик.
                '''
                region = new_frame[y:y + rh, x:x + rw]
                inv = cv2.bitwise_not(region)
                alpha = 0.35 + 0.5 * random.random() * progress
                new_frame[y:y + rh, x:x + rw] = cv2.addWeighted(region, 1.0 - alpha, inv, alpha, 0)

        # 4) Редкие перестановки каналов (RGB shuffle) для цветовых артефактов
        '''
Иногда глючим цвета: берём каналы картинки по отдельности (синий, зелёный, красный).
        '''
        if random.random() < 0.45 * progress:
            b, g, r = cv2.split(new_frame)
            '''
Мешаем каналы местами и собираем обратно, чтоб цвета съезжали и багали.
            '''
            perms = [
                (r, g, b),
                (g, r, b),
                (b, r, g),
                (r, b, g)
            ]
            pb, pg, pr = random.choice(perms)
            new_frame = cv2.merge([pb, pg, pr])

        # 5) Призрачный сдвиг (ghost) — небольшое прозрачное наложение смещённой копии
        '''
Создаём "призрак": копия кадра чуть сдвинутая вправо или влево. Чем дальше, тем сильнее сдвиг.
        '''
        ghost_shift = int((3 + int(10 * progress)) * random.choice([-1, 1]))
        '''
Берём копию сдвинутую, накладываем полупрозрачно на оригинал.
Выходит как будто двойное изображение, дрожит по экрану.
        '''
        if ghost_shift != 0:
            ghost = np.roll(new_frame, ghost_shift, axis=1)
            alpha = 0.12 + 0.18 * progress
            new_frame = cv2.addWeighted(new_frame, 1.0 - alpha, ghost, alpha, 0)

        # 6) Спорадический "salt & pepper" шум (сделан разреженным, чтобы экономить ресурсы)
        '''
Вероятность, что пиксель станет белым или чёрным "шумом", увеличивается с прогрессом.
        '''
        sp_prob = 0.0008 + 0.006 * progress  # вероятность на пиксель
        '''
Короче, наугад берём пиксели, половину делаем белыми, половину чёрными.
Получается шум "соль и перец", как на старом телеканале без сигнала.
        '''
        if sp_prob > 0:
            mask = np.random.rand(h, w) < sp_prob
            if mask.any():
                ys, xs = np.nonzero(mask)
                # для каждого выбранного пикселя выбираем черный или белый
                choices = np.random.rand(len(ys)) < 0.5
                new_frame[ys[choices], xs[choices]] = 255  # белые
                new_frame[ys[~choices], xs[~choices]] = 0   # черные

        return new_frame.astype(np.uint8)

    def glitch_art4(self, frame, t, duration, prev_frame=None, intensity=1.0):
        """
        VHS-подобный эффект.
        - frame: входной BGR uint8
        - t, duration: текущее время и длительность (для прогресса 0..1)
        - prev_frame: предыдущий кадр (опционально) для temporal ghost
        - intensity: 0..1 контроль силы эффекта
        """
        progress = float(np.clip(t / float(duration), 0.0, 1.0))
        '''
Считаем прогресс от 0 до 1, чтобы знать, на каком этапе фокусов мы щас.
clip — это чтоб не вылезло за границы, типа «не больше единицы, не меньше нуля».
        '''
        strength = float(np.clip(intensity, 0.0, 1.0)) * (0.4 + 0.6 * progress)
        '''
Берём силу эффекта (intensity) и усиливаем её в зависимости от прогресса.
То есть чем дальше во времени, тем сильнее VHS-разъеб идёт.
        '''

        h, w = frame.shape[:2]
        new_frame = frame.copy()

        # 1) Лёгкий хроматический сдвиг (chroma bleed)
        # сдвигаем R и B по X/Y на небольшое количество пикселей
        '''
Это как старые кассеты: цвета поехали, красный и синий уползли.

bx и ry — случайные сдвиги.

split — делим картинку на каналы (B, G, R).

roll — сдвигаем синий вбок, красный вверх/вниз.

merge — собираем всё обратно. Получается такой «цветовой расплыв».
        '''
        max_chroma = max(1, int(8 * strength))
        bx = random.randint(-max_chroma, max_chroma)
        ry = random.randint(-max_chroma, max_chroma)
        b, g, r = cv2.split(new_frame)
        b = np.roll(b, bx, axis=1)
        r = np.roll(r, ry, axis=0)
        new_frame = cv2.merge([b, g, r])

        # 2) Хабинговые (tracking) горизонтальные «рывки» — несколько полос с большим сдвигом
        # (выбираем небольшое число полос, чтобы не нагружать)
        '''
Делаем те самые глюки, когда картинка полосами скачет вбок.

Выбираем несколько горизонтальных полос.

Случайно решаем, куда и насколько их сдвинуть.

Иногда делаем жёсткий разрыв (в 2 раза сильнее).
        '''
        if random.random() < 0.9 * strength:
            bands = 1 + int(3 * strength)  # число полос
            max_band_h = max(2, int(0.06 * h))
            for _ in range(bands):
                bh = random.randint(1, max_band_h)
                y = random.randint(0, max(0, h - bh))
                shift_x = int((0.15 + 0.85 * random.random()) * w * (0.03 + 0.07 * strength))  # доля ширины
                shift_x *= random.choice([-1, 1])
                # сильные разрывы реже
                if random.random() < 0.25:
                    shift_x *= 2
                new_frame[y:y + bh] = np.roll(new_frame[y:y + bh], shift_x, axis=1)

        # 3) Вертикальные «dropout» полосы (частичное затемнение сигнала)
        '''
Иногда по вертикали появляются такие тёмные полоски (будто сигнал сдох).

dw — ширина полосы.

x — где она будет.

val — насколько затемним.
        '''
        if random.random() < 0.35 * strength:
            drops = 1 + int(2 * strength)
            for _ in range(drops):
                dw = random.randint(max(2, int(w * 0.02)), max(4, int(w * 0.12)))
                x = random.randint(0, max(0, w - dw))
                # глубина затемнения зависит от случайности и прогресса
                val = random.randint(int(40 * strength), int(160 * strength))
                new_frame[:, x:x + dw] = np.clip(new_frame[:, x:x + dw].astype(np.int16) - val, 0, 255).astype(np.uint8)

        # 4) Симуляция низкого разрешения хромы: downsample по ширине/цветовой компоненте
        '''
Чтобы имитировать старое видео, уменьшаем ширину (особенно цвета),
а потом растягиваем обратно.
Получается «замыленный» цвет.
        '''
        if strength > 0.05:
            # уменьшение по ширине хромы и повторное растягивание — цветовый «размыв»
            chroma_scale = 1 + int(4 * (1.0 - strength))  # при малой силе — сильнее субсамплинг
            small_w = max(1, w // chroma_scale)
            tiny = cv2.resize(new_frame, (small_w, h), interpolation=cv2.INTER_LINEAR)
            new_frame = cv2.resize(tiny, (w, h), interpolation=cv2.INTER_LINEAR)

        # 5) Сканлайны — затемнение каждой второй строки и тонкая модуляция яркости
        '''
Короче, добавляем полосочки — затемняем каждую вторую строку.
Плюс ещё картинка как будто «дрожит» синусом — типичный VHS вайб.
        '''
        scan_strength = int(28 * strength)
        if scan_strength > 0:
            # затемняем каждую вторую строку
            tmp = new_frame[::2].astype(np.int16) - int(scan_strength * 0.6)
            new_frame[::2] = np.clip(tmp, 0, 255).astype(np.uint8)
            # небольшая синусная модуляция по Y для VHS vibe (вертикальная нестабильность)
            freq = 2.0 * (0.5 + 0.5 * random.random())  # циклы на высоту
            amp = int(6 * strength)
            if amp > 0:
                ys = np.arange(h)
                offs = (np.sin(ys / h * 2 * np.pi * freq + random.random() * 6.28) * amp).astype(int)
                # применяем по невысоким блокам, чтобы не было тяжело
                band_h = max(4, int(h * 0.02))
                for y0 in range(0, h, band_h):
                    y1 = min(h, y0 + band_h)
                    dy = int(offs[y0])
                    if dy:
                        new_frame[y0:y1] = np.roll(new_frame[y0:y1], dy, axis=1)

        # 6) Tape grain / noise (аддитивный шум, тональный и хрома)
        '''
Добавляем шум, как будто плёнка сыпется.
Каждый пиксель чуть-чуть дергается по цвету.
        '''
        noise_amp = int(14 * strength)
        if noise_amp > 0:
            # делаем источник шума одинарной канал и затем расширяем
            noise = np.random.randint(-noise_amp, noise_amp + 1, (h, w, 1), dtype=np.int16)
            noise = np.repeat(noise, 3, axis=2).astype(np.int16)
            tmp = new_frame.astype(np.int16) + noise
            new_frame = np.clip(tmp, 0, 255).astype(np.uint8)

        # 7) Цветовая деградация / контраст VHS: лёгкое смещение цветовой гаммы и уменьшение насыщенности
        '''
Цвета тухнут, насыщенность падает,
и иногда случайные квадратики уезжают в другой оттенок.
Типа плёнка выцвела.
        '''
        if strength > 0.02:
            hsv = cv2.cvtColor(new_frame, cv2.COLOR_BGR2HSV).astype(np.int16)
            # уменьшение насыщенности и небольшая нелинейность в тональности
            sat_delta = int(30 * strength * (random.random() - 0.3))
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] - sat_delta, 0, 255)
            # случайные глитчи в тональном канале (локальные сдвиги hue)
            if random.random() < 0.45 * strength:
                rects = 1 + int(2 * strength)
                for _ in range(rects):
                    rw = random.randint(6, max(6, int(w * 0.12)))
                    rh = random.randint(4, max(4, int(h * 0.12)))
                    x = random.randint(0, max(0, w - rw))
                    y = random.randint(0, max(0, h - rh))
                    add_h = int(10 * (random.random() - 0.5) * strength)
                    hsv[y:y + rh, x:x + rw, 0] = (hsv[y:y + rh, x:x + rw, 0] + add_h) % 180
            new_frame = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # 8) Temporal ghost / tracking smear: смешиваем с предыдущим кадром с небольшим смещением
        '''
Смешиваем текущий кадр с предыдущим, но чуть смещённым.
Получается «призрак», будто картинка за собой тянется.
        '''
        if prev_frame is not None and strength > 0.02 and random.random() < 0.9:
            pf = prev_frame
            if pf.shape[:2] != (h, w):
                pf = cv2.resize(pf, (w, h), interpolation=cv2.INTER_LINEAR)
            ghost_shift = int(w * 0.02 * (0.5 + 0.5 * random.random()) * strength)
            ghost_shift *= random.choice([-1, 1])
            ghost = np.roll(pf, ghost_shift, axis=1)
            alpha = 0.04 + 0.18 * strength
            new_frame = cv2.addWeighted(new_frame, 1.0 - alpha, ghost, alpha, 0)

        # 9) Финальные «скрипы» (короткие сильные сдвиги — редкие)
        '''
Иногда добавляем редкий, мощный сдвиг — типа кадр дёрнуло жёстко.
        '''
        if random.random() < 0.08 * strength:
            # случайный крупный рывок на небольшой полосе
            th = random.randint(2, max(2, int(h * 0.08)))
            y = random.randint(0, max(0, h - th))
            shift_x = int(w * (0.05 + 0.2 * random.random()) * strength)
            shift_x *= random.choice([-1, 1])
            new_frame[y:y + th] = np.roll(new_frame[y:y + th], shift_x, axis=1)

        '''
👊 Вот так, брат. Теперь ты шаришь, как этот VHS-глитч работает.
        '''
        return new_frame.astype(np.uint8)

    def kaleidoscope2(self, frame, t, duration):
        '''
Считаем, где мы щас по времени, от 0 до 1. Типа прогресс бара.
Если duration ноль — чтоб не глючило, ставим 0.
        '''
        progress = (t % duration) / float(duration) if duration else 0.0
        '''
угол в градусах. Типа полный круг (360), но берём кусок в зависимости от прогресса.
        '''
        angle = 360.0 * progress

        '''
Берём размеры кадра: высоту (h) и ширину (w).
Потом делим пополам, чтоб знать половинки (h2, w2). Это будет наша рабочая зона.
        '''
        h, w = frame.shape[:2]
        h2, w2 = h // 2, w // 2

        # Подготовка float-копии кадра
        '''
проверяем, кадр у нас в плавающем формате (типа с точками) или тупо в целых числах (0–255).
        '''
        is_float = np.issubdtype(frame.dtype, np.floating)
        '''
Если картинка чёрно-белая (2D), то у неё каналов 1. Переводим в float32, чтоб удобнее считать.
Если цветная, то берём кол-во каналов (обычно 3 — RGB) и тоже переводим в float32.
        '''
        if frame.ndim == 2:
            channels = 1
            frame_f = frame.astype(np.float32).reshape(h, w, 1)
        else:
            channels = frame.shape[2]
            frame_f = frame.astype(np.float32)

        # Движение / масштаб
        '''
Тут замутим пульсацию — типа дышит картинка.
Амплитуда 0.05. Берём синус — и размер кадра чуть подрастает или уменьшается.
        '''
        pulse_amp = 0.05
        pulse = 1.0 + pulse_amp * np.sin(2.0 * np.pi * progress * 2.0)
        '''
Сдвигаем центр по синусу и косинусу, чтоб картинка немного гуляла туда-сюда.
        '''
        cx_off = int(0.02 * w * np.sin(2.0 * np.pi * progress))
        cy_off = int(0.02 * h * np.cos(2.0 * np.pi * progress))

        '''
Считаем границы вырезаемого квадрата. Типа берем кусок кадра (середину).
pad — это запас, чтоб не резало по-жёсткому.
        '''
        pad = max(0, int(min(w2, h2) * 0.08))
        x0 = max(0, w // 4 - pad + cx_off)
        y0 = max(0, h // 4 - pad + cy_off)
        x1 = min(w, x0 + w2 + 2 * pad)
        y1 = min(h, y0 + h2 + 2 * pad)
        '''
страховка: если отрезал криво (кусок пустой), то ставим дефолтные координаты.
        '''
        if x1 <= x0 or y1 <= y0:
            x0 = max(0, w // 4 - pad); y0 = max(0, h // 4 - pad)
            x1 = min(w, x0 + w2 + 2 * pad); y1 = min(h, y0 + h2 + 2 * pad)

        '''
Вырезаем кусок кадра. Если там пусто (высота или ширина ноль) — возвращаем оригинал.
        '''
        segment = frame_f[y0:y1, x0:x1].astype(np.uint8).copy()
        seg_h, seg_w = segment.shape[:2]
        if seg_h == 0 or seg_w == 0:
            return frame

        '''
Создаём матрицу поворота + масштабирования (M).
Вращаем кусок картинки и отражаем границы, чтобы не было дыр.
        '''
        M = cv2.getRotationMatrix2D((seg_w / 2.0, seg_h / 2.0), angle, pulse)
        rotated_full = cv2.warpAffine(segment, M, (seg_w, seg_h),
                                      flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        '''
Выравниваем и центрируем обрезанный кусок.
Если вылезли за границы — достраиваем рамку.
Потом берём центрированную часть.
        '''
        sx = max(0, (seg_w - w2) // 2); sy = max(0, (seg_h - h2) // 2)
        if sy + h2 > rotated_full.shape[0] or sx + w2 > rotated_full.shape[1]:
            pad_h = max(0, sy + h2 - rotated_full.shape[0])
            pad_w = max(0, sx + w2 - rotated_full.shape[1])
            rotated_full = cv2.copyMakeBorder(rotated_full, 0, pad_h, 0, pad_w,
                                          borderType=cv2.BORDER_REFLECT)
        rotated = rotated_full[sy:sy + h2, sx:sx + w2].astype(np.float32)

        # Кэш маски
        '''
проверка, есть ли у нас закэшированные маски под размеры (h2, w2).
        '''
        if not hasattr(self, '_kaleido_masks'):
            self._kaleido_masks = {}
        mask_key = (h2, w2)
        '''
Тут мутим маску (затухание к краям),
чтоб красиво выглядело. Если уже считали — берём готовую.
Если нет — считаем: расстояния от центра, нормируем и делаем плавный спад яркости.
        '''
        if mask_key in self._kaleido_masks:
            base_mask = self._kaleido_masks[mask_key]
        else:
            yy = np.linspace(0, h2 - 1, h2) - (h2 - 1) / 2.0
            xx = np.linspace(0, w2 - 1, w2) - (w2 - 1) / 2.0
            xxg, yyg = np.meshgrid(xx, yy)
            dist = np.sqrt(xxg + yyg)
            maxr = np.sqrt(((w2 - 1) / 2.0)**2 + ((h2 - 1) / 2.0)**2) + 1e-9
            base_mask = 1.0 - np.clip(dist / maxr, 0.0, 1.0)
            base_mask = np.power(base_mask, 1.2)
            self._kaleido_masks[mask_key] = base_mask.astype(np.float32)
        base_mask = base_mask.astype(np.float32)

        '''
пустые матрицы для накопления картинки и весов масок.
        '''
        accum = np.zeros((h, w, channels), dtype=np.float32)
        weight = np.zeros((h, w), dtype=np.float32)

        '''
Делаем четыре куска (как квадранты калейдоскопа):
оригинал, отражённый по горизонтали, по вертикали и оба вместе.
У каждого — своя маска и фазовый сдвиг.
        '''
        q = rotated.astype(np.float32)
        quads = [
            (q, 0, 0, base_mask, 0.0),
            (cv2.flip(q, 1), 0, w2, np.fliplr(base_mask), 0.25),
            (cv2.flip(q, 0), h2, 0, np.flipud(base_mask), 0.5),
            (cv2.flip(q, -1), h2, w2, np.flipud(np.fliplr(base_mask)), 0.75),
        ]

        '''
Цикл по четырём кускам:
— считаем яркость (чуть пульсирует)
— применяем маску
— плюсуем результат в общую картину
— и вес добавляем.
        '''
        for img_q, y_off, x_off, mask_q, phase in quads:
            bright = 0.95 + 0.1 * np.sin(2.0 * np.pi * (progress + phase))
            mask3 = mask_q[..., None]
            part = img_q * (mask3 * bright)
            accum[y_off:y_off + h2, x_off:x_off + w2, :channels] += part
            weight[y_off:y_off + h2, x_off:x_off + w2] += (mask_q * bright)

        '''
делим всё накопленное на веса, чтоб усреднить. eps нужен, чтоб не делить на ноль.
        '''
        eps = 1e-6
        out = accum / (weight[..., None] + eps)
        '''
Если где-то вес почти нулевой — значит пустота. Тогда подставляем оригинал кадра.
        '''
        mask_zero = (weight < 1e-3)
        if np.any(mask_zero):
            frame_f_clip = frame_f.astype(np.float32)
            out = np.where(mask_zero[..., None], frame_f_clip, out)

        '''
Возвращаем картинку в нормальный тип: если был float — оставляем.
Если int (0–255) — обрезаем, округляем и переводим назад.
        '''
        if is_float:
            out = out.astype(frame.dtype)
        else:
            out = np.clip(out, 0, 255)
            out = np.rint(out).astype(frame.dtype)
        '''
Если картинка чёрно-белая (1 канал), то убираем лишнее измерение. Возвращаем готовый калейдоскоп.
        '''
        if channels == 1:
            out = out.reshape(h, w)
        return out

    def time_tunnel2(self, frame, t, duration, clip):

        # --- Защита от пустого кадра ---
        '''
Смотрим: если кадр пустой, или вообще его нет (None),
или у него размер ноль — значит, пиздец, надо спасать ситуацию.
        '''
        if frame is None or (hasattr(frame, "size") and frame.size == 0):
            # Попытка вернуть последний валидный кадр
            '''
Если у нас остался предыдущий нормальный кадр, держим его в заначке.
            '''
            if hasattr(self, 'last_frame') and self.last_frame is not None:
                # предупреждение в консоль (можно убрать)
                '''
Орет в консоль: мол, кадр пустой, беру прошлый. Типа предупреждение для пацанов-разработчиков.
                '''
                print(f"warning: empty frame at t={t:.3f}, using last_frame")
                '''
Возвращаем копию старого кадра — не ломаемся.
                '''
                return self.last_frame.copy()
            # если нет last_frame — пробуем размеры из clip, иначе возвращаем маленький чёрный кадр
            if clip is not None and hasattr(clip, "size") and clip.size is not None:
                w, h = clip.size  # MoviePy: (w,h)
                '''
Делаем пустой чёрный кадр с теми же размерами.
                '''
                fallback = np.zeros((int(h), int(w), 3), dtype=np.uint8)
                '''
Снова предупреждение: мол, вернули чёрный кадр размером как у клипа.
                '''
                print(f"warning: empty frame at t={t:.3f}, returning black frame of clip.size {clip.size}")
                '''
Сохранили чёрный кадр как последний и вернули.
                '''
                self.last_frame = fallback
                return fallback
            # окончательный fallback
            '''
Последний шанс: делаем дефолтный чёрный кадр 640x480, как у старых теликов.
            '''
            fallback = np.zeros((480, 640, 3), dtype=np.uint8)
            '''
Выводим предупреждение, сохраняем и возвращаем этот чёрный квадрат.
            '''
            print(f"warning: empty frame at t={t:.3f}, returning default black 640x480")
            self.last_frame = fallback
            return fallback

        # Убедимся, что кадр — numpy array с 3 каналами и uint8
        '''
Превращаем кадр в numpy массив, чтоб точно был нужный тип.
        '''
        frame = np.asarray(frame)
        '''
Если картинка чёрно-белая (2D).
        '''
        if frame.ndim == 2:
            '''
Переводим в цветную (BGR), чтоб было три канала.
            '''
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            '''
Если картинка 4-канальная (с альфой, типа PNG).
            '''
        elif frame.ndim == 3 and frame.shape[2] == 4:
            # если есть альфа — отбросим или премультипликативно применим (здесь просто откидываем)
            '''
Отбрасываем альфу, переводим в обычную 3-канальную.
Тут без заморочек, просто нахрен убираем прозрачность.
            '''
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            '''
Если тип данных не стандартный (не 8-бит), приводим к нормальному виду.
            '''
        if frame.dtype != np.uint8:
            # нормализуем к 0..255
            '''
Короче, если у нас значения какие-то левые (например float), нормализуем их в диапазон 0–255.
Иначе просто приводим к uint8.
            '''
            fmin, fmax = frame.min(), frame.max()
            if fmax > fmin:
                frame = ((frame - fmin) / (fmax - fmin) * 255.0).astype(np.uint8)
            else:
                frame = frame.astype(np.uint8)

        # Сохраняем как последний валидный кадр
        self.last_frame = frame.copy()

        # --- Параметры эффекта (можно регулировать) ---
        progress = np.clip(t / max(1e-6, duration), 0.0, 1.0)
        ease = 1.0 - (1.0 - progress) ** 3

        '''
Это параметры эффекта:

max_cache — сколько прошлых кадров хранить.

downscale — уменьшение кадра для скорости.

alpha, scale_step, rotation_step — как сильно прозрачность, масштаб и поворот меняются.

chroma_shift — цветовое смещение (глитч).

vignette_strength — затемнение по краям.

glow_strength — свечение.

color_boost — усиление цвета.

min_side — минимальный размер кадра после уменьшения.
        '''
        max_cache = 6
        downscale = 0.45
        base_alpha = 0.9
        scale_step = 0.12
        rotation_step = 6.0
        chroma_shift = 3
        vignette_strength = 0.75
        glow_strength = 0.30
        color_boost = 0.18
        min_side = 64

        '''
Высота и ширина кадра. Делаем уменьшенную версию, но не меньше минимума.
        '''
        h, w = frame.shape[:2]
        small_w = max(min_side, int(w * downscale))
        small_h = max(min_side, int(h * downscale))

        # --- кеш уменьшенных кадров ---
        '''
Если нет хранилища уменьшенных кадров — создаём.
        '''
        if not hasattr(self, '_cache_small'):
            self._cache_small = []
        '''
Делаем уменьшенный кадр.
        '''
        cur_small = cv2.resize(frame, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        '''
Запоминаем уменьшенный кадр в кеш. Если кадров стало больше лимита — выкидываем самый старый.
        '''
        self._cache_small.append(cur_small.copy())
        if len(self._cache_small) > max_cache:
            self._cache_small.pop(0)

        '''
Начинаем композицию с текущего уменьшенного кадра.
        '''
        comp = cur_small.astype(np.float32)
        # предвычисление виньетки при необходимости
        '''
Проверяем, есть ли виньеточная маска подходящего размера.
        '''
        if not hasattr(self, '_vignette_mask') or self._vignette_mask.shape[:2] != (small_h, small_w):
            '''
Короче, делаем маску для виньетки:
— Считаем расстояние до центра,
— Обрезаем значения,
— Размываем для мягкости,
— Сохраняем.
            '''
            yy, xx = np.mgrid[0:small_h, 0:small_w]
            cy, cx = small_h / 2.0, small_w / 2.0
            dist = np.sqrt(((yy - cy) / cy) ** 2 + ((xx - cx) / cx) ** 2)
            mask = np.clip(1.0 - dist, 0.0, 1.0)
            mask = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), sigmaX=max(small_w, small_h) * 0.03)
            self._vignette_mask = mask.astype(np.float32)


        '''
Берём прошлые кадры (кроме текущего).
        '''
        layers = list(self._cache_small[:-1])
        '''
Дальше цикл — там вся движуха:
масштабируем, крутим, накладываем цветовые глитчи,
усиливаем центр, добавляем слои. Это и создаёт иллюзию туннеля.
        '''
        for i, prev in enumerate(layers):
            layer_index = i
            rel = (layer_index + 1) / max(1, len(layers))
            '''
Считаем прозрачность (alpha):
— Чем слой глубже, тем он прозрачнее.
— Зависит от плавности (ease) и прогресса анимации.
— В начале (progress≈0) альфа почти нулевая, к концу становится сильнее.
            '''
            alpha = base_alpha * (1.0 - rel * 0.9) * (0.25 + 0.75 * ease)
            alpha *= (1.0 - np.exp(-2.5 * progress))
            '''
Если слой слишком прозрачный — нахер его, не рисуем.
            '''
            if alpha <= 0.01:
                continue

            '''
Чем глубже слой, тем он меньше. Это даёт эффект туннеля.
            '''
            scale = 1.0 - scale_step * layer_index * (0.5 + 0.8 * ease)
            '''
Каждый слой чуть-чуть поворачиваем.
— Чем дальше слой, тем сильнее угол.
— Добавляем ещё динамический угол в зависимости от ease и позиции.
            '''
            angle = rotation_step * layer_index * (0.6 + 0.4 * ease)
            angle += 4.0 * ease * (1.0 - rel)

            '''
Считаем смещения по X и Y — чтоб кадры при масштабировании двигались и создавали эффект глубины.
            '''
            tx = (small_w - small_w * scale) / 2.0 * (0.5 + 0.5 * ease) * (0.6 + 0.4 * rel)
            ty = (small_h - small_h * scale) / 2.0 * (0.5 + 0.5 * ease) * (0.6 + 0.4 * rel)

            '''
Делаем матрицу трансформации (масштаб + поворот + смещение).
Это, типа, как Photoshop’овский "Free Transform".
            '''
            center = (small_w / 2.0, small_h / 2.0)
            M = cv2.getRotationMatrix2D(center, angle, scale)
            M[0, 2] += tx
            M[1, 2] += ty

            '''
Применяем трансформацию к кадру.
Если выходим за границы — отражаем края (чтоб не было дырок).
            '''
            warped = cv2.warpAffine(prev, M, (small_w, small_h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

            '''
Цветовой глитч:
— Берём каналы BGR.
— Сдвигаем синий вправо, красный вниз, оставляем зелёный.
— Получаем эффект "хроматической аберрации".
            '''
            if chroma_shift > 0:
                shift = int(np.round(chroma_shift * rel * ease * 1.6))
                if shift != 0:
                    b, g, r = cv2.split(warped)
                    b = np.roll(b, shift, axis=1)
                    r = np.roll(r, -shift, axis=0)
                    warped = cv2.merge((b, g, r))


            '''
Делаем радиальную карту: чем ближе пиксель к центру, тем значение больше.
Эта штука усиливает центр кадра.
            '''
            yy, xx = np.mgrid[0:small_h, 0:small_w]
            dy = (yy - small_h / 2.0) / (small_h / 2.0)
            dx = (xx - small_w / 2.0) / (small_w / 2.0)
            radial = np.clip(1.0 - (dx * dx + dy * dy), 0.0, 1.0)
            '''
Размываем радиальную маску, чтоб плавно, и считаем коэффициент усиления центра.
            '''
            radial = cv2.GaussianBlur(radial.astype(np.float32), (0, 0), sigmaX=min(small_w, small_h) * 0.05)
            center_boost = 1.0 + 0.6 * (1.0 - rel) * ease
            '''
Добавляем яркость в центре, типа светящийся тоннель.
            '''
            warped_f = warped.astype(np.float32)
            warped_f += (radial[..., None] * center_boost * 25.0)

            '''
Накладываем слой поверх композиции с прозрачностью alpha.
            '''
            comp = comp * (1.0 - alpha) + warped_f * alpha


        '''
Добавляем виньетку: затемняем края кадра, центр оставляем ярким.
        '''
        vmask = (1.0 - vignette_strength * ease) + (self._vignette_mask * vignette_strength * ease)
        comp *= vmask[..., None]

        '''
Делаем буст цвета:
— В HSV увеличиваем насыщенность (S) и яркость (V).
— Потом переводим обратно в BGR.
        '''
        if color_boost > 0.001:
            hsv = cv2.cvtColor(np.clip(comp, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
            hsv[..., 1] = np.clip(hsv[..., 1] * (1.0 + color_boost * ease), 0, 255)
            hsv[..., 2] = np.clip(hsv[..., 2] * (1.0 + 0.08 * ease), 0, 255)
            comp = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)

        '''
Делаем мягкое свечение (glow):
— Размываем картинку,
— Смешиваем с оригиналом.
        '''
        blur_sigma = max(1.0, (small_w + small_h) * 0.003 * (0.5 + ease))
        blur = cv2.GaussianBlur(comp.astype(np.uint8), (0, 0), sigmaX=blur_sigma)
        comp = comp * (1.0 - glow_strength * ease) + blur.astype(np.float32) * (glow_strength * ease)

        '''
Масштабируем обратно к размеру оригинала.
        '''
        up = cv2.resize(np.clip(comp, 0, 255).astype(np.uint8), (w, h), interpolation=cv2.INTER_LINEAR)

        '''
Смешиваем оригинальный кадр с эффектом.
— Чем дальше прогресс, тем больше вес у эффекта.
        '''
        overlay_alpha = 0.85 * ease
        new_frame = cv2.addWeighted(frame.astype(np.uint8), 1.0 - overlay_alpha, up, overlay_alpha, 0)

        '''
Возвращаем готовый кадр с туннелем. 🎥
        '''
        return new_frame

    def neon_glow3(self, frame, t, duration):

        # ---- Защита от пустого кадра и нормализация ----
        '''
Если кадр пустой – проверяем, есть ли у нас прошлый.
Если был, отдаем его копию, типа «держи старое кино».
Если даже этого нет – создаем черный экран 480х640.
Так мы не умираем от пустого входа.
        '''
        if frame is None:
            if hasattr(self, 'last_frame') and self.last_frame is not None:
                return self.last_frame.copy()
            return np.zeros((480, 640, 3), dtype=np.uint8)

        '''
переводим кадр в numpy-массив, чтоб удобно с ним химичить.
        '''
        frame = np.asarray(frame)
        '''
Если кадр черно-белый (2D) – красим в 3 канала (BGR), чтоб цветной был.
Если кадр с альфой (4 канала) – убираем прозрачность, оставляем тупо BGR.
Короче, нормализуем формат, чтоб не было кривых данных.
        '''
        if frame.ndim == 2:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif frame.ndim == 3 and frame.shape[2] == 4:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        '''
–– если пиксели не в типе uint8, подгоняем: обрезаем до 0..255
и делаем нормальные байты. Видеоформат требует этого.
        '''
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)
        '''
сохраняем копию как «последний кадр» на черный день.
        '''
        self.last_frame = frame.copy()

        # ---- Параметры (настройки производительности/вида) ----
        '''
Считаем прогресс от 0 до 1.
Потом делаем его «плавным» через функцию ease – типа в начале и в конце медленно,
а в середине бодро. Это чтоб эффекты красиво разгонялись.
        '''
        progress = float(t) / max(1e-6, float(duration))
        progress = np.clip(progress, 0.0, 1.0)
        ease = 1.0 - (1.0 - progress) ** 2.2


        '''
Тут короче целая пачка настроек:

уменьшаем кадр до 44% ради скорости.

glow_layers – три уровня размытия для свечения.

edge_low / edge_high – пороги для поиска краев.

primary_hue_offset / secondary_hue_offset – сдвиги цвета для основного и вторичного свечения.

sat_base – базовая насыщенность.

mix_strength – сила смешивания свечения с кадром.

temporal_smooth – сглаживание по времени.

vignette_strength – затемнение по краям.

chroma_max_shift – хроматическая аберрация (цветные сдвиги пикселей).

grain_strength – зернистость (шум), сильнее в начале.
        '''
        downscale = 0.44                      # уменьшение для производительности
        glow_layers = [(2.0, 0.62), (7.0, 0.28), (18.0, 0.10)]
        edge_low = 28
        edge_high = 120
        primary_hue_offset = 0                # базовый тон смещения
        secondary_hue_offset = 70             # вторичный тон (контрастный)
        sat_base = 200
        mix_strength = 0.74 * ease
        temporal_smooth = 0.72
        vignette_strength = 0.45 * ease
        chroma_max_shift = int(2 + 4 * ease)  # пикселей хроматической аберрации
        grain_strength = 0.02 + 0.05 * (1.0 - ease)  # сильнее в начале

        '''
берем размеры кадра, делаем уменьшенный вариант (но не меньше 64 пикселей).
        '''
        h, w = frame.shape[:2]
        small_w = max(64, int(w * downscale))
        small_h = max(64, int(h * downscale))

        # ---- Предвычисления виньетки (на small) ----
        '''
Тут заранее считаем виньетку (затемнение по краям).
Берем сетку координат, считаем расстояние до центра,
делаем маску от 1 в центре до 0 по краям.
Размываем – и всё, красивая плавная виньетка готова.
        '''
        if not hasattr(self, '_vignette_small') or self._vignette_small.shape[:2] != (small_h, small_w):
            yy, xx = np.mgrid[0:small_h, 0:small_w]
            cy, cx = small_h / 2.0, small_w / 2.0
            dist = np.sqrt(((yy - cy) / cy) ** 2 + ((xx - cx) / cx) ** 2)
            mask = np.clip(1.0 - dist, 0.0, 1.0)
            mask = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), sigmaX=max(small_w, small_h) * 0.03)
            self._vignette_small = mask.astype(np.float32)

        # ---- Маска краёв на уменьшенной копии ----
        '''
уменьшаем кадр, переводим в серый и слегка блюрим, чтоб шум не мешал при поиске краёв
        '''
        small = cv2.resize(frame, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        '''
Считаем границы через Canny.
Пороги подстраиваем от прогресса. На выходе получаем карту краев от 0 до 1.
        '''
        low_thr = max(1, int(edge_low * (0.6 + 0.8 * ease)))
        high_thr = max(low_thr + 1, int(edge_high * (0.9 + 0.6 * ease)))
        edges = cv2.Canny(blurred, low_thr, high_thr).astype(np.float32) / 255.0

        '''
расширяем края (делаем их жирнее), чтоб эффект был заметнее.
        '''
        kernel_sz = max(3, int(1 + ease * 6))
        kern = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_sz, kernel_sz))
        edges_dil = cv2.dilate((edges * 255).astype(np.uint8), kern, iterations=1).astype(np.float32) / 255.0

        # ---- Разделение маски на primary (сильные края) и secondary (мягкий ореол) ----
        # threshold зависит от progress: при маленьком progress secondary более выражена
        '''
Делим маску краёв на две:

strong – яркие, мощные линии.

soft – мягкий ореол вокруг.
Это даст нам primary и secondary свечение.
        '''
        thresh = 0.42 * (0.7 + 0.6 * ease)
        strong = np.clip((edges_dil - thresh) / (1.0 - thresh + 1e-6), 0.0, 1.0)  # 0..1 strong mask
        soft = np.clip(edges_dil, 0.0, 1.0) - strong * (1.0 - 0.05 * ease)
        soft = np.clip(soft, 0.0, 1.0)

        # ---- Multi-layer glow: два тона (primary + secondary) ----
        # базовые тона пульсируют во времени
        '''
базовый цвет постоянно меняется по синусу, так что оттенки пульсируют со временем.
        '''
        hue_base = int((90 + 140.0 * math.sin(t * 2.1)) % 180)
        primary_hue = (hue_base + primary_hue_offset) % 180
        secondary_hue = int((hue_base + secondary_hue_offset + 10.0 * math.sin(t * 1.7)) % 180)

        '''
создаём пустую копилку под свечение, всё пока чёрное.
        '''
        glow_acc = np.zeros_like(small, dtype=np.float32)
        # Primary: сильные края -> яркий насыщенный цвет
        '''
Тут мутим основное свечение по сильным краям.
– Берём маску сильных линий, блюрим её разными размерами (sigma).
– Создаём HSV картинку: оттенок = основной цвет, насыщенность высокая, яркость = размытые края.
– Конвертим в BGR и плюсуем в общую копилку glow_acc.
Короче, линии загораются ярким неоновым цветом.
        '''
        for sigma, weight in glow_layers:
            m = cv2.GaussianBlur((strong * 255).astype(np.uint8), (0, 0), sigmaX=sigma)
            hsvc = np.zeros((small_h, small_w, 3), dtype=np.uint8)
            hsvc[..., 0] = primary_hue
            hsvc[..., 1] = int(np.clip(sat_base * (0.85 + 0.45 * ease), 0, 255))
            hsvc[..., 2] = m
            col = cv2.cvtColor(hsvc, cv2.COLOR_HSV2BGR).astype(np.float32)
            glow_acc += col * weight * (1.0 + 0.9 * ease)

        # Secondary: мягкий ореол вокруг / контрастный цвет
        '''
Тут второе свечение – мягкий ореол вокруг краёв.
– Цвет другой (контрастный).
– Насыщенность ниже, чтоб не перебивало основной.
– Сильнее видно в начале, потом уходит.
Короче, дополняет основное свечение красивым обводом.
        '''
        for sigma, weight in [(6.0, 0.9), (14.0, 0.4)]:
            m2 = cv2.GaussianBlur((soft * 255).astype(np.uint8), (0, 0), sigmaX=sigma)
            hsvc2 = np.zeros((small_h, small_w, 3), dtype=np.uint8)
            hsvc2[..., 0] = secondary_hue
            hsvc2[..., 1] = int(np.clip(sat_base * 0.6 * (0.8 + 0.4 * (1.0 - ease)), 0, 255))
            hsvc2[..., 2] = m2
            col2 = cv2.cvtColor(hsvc2, cv2.COLOR_HSV2BGR).astype(np.float32)
            glow_acc += col2 * weight * (0.55 + 0.6 * (1.0 - ease))

        '''
подрезаем значения, чтоб не вылезли за пределы цвета.
        '''
        glow_acc = np.clip(glow_acc, 0.0, 255.0)

        # ---- Пульсирующие радиальные кольца (cheap decorative) ----
        # создаём радиальную волновую карту на small, умножаем на мягкий blur и добавляем в glow
        '''
Рисуем пульсирующие круги от центра (как будто волны).
– Считаем радиус от центра.
– Гоним синус, чтобы круги дышали и двигались.
– Оставляем только пики и размываем.
Получается декоративный эффект, как будто энергия по кругам идёт.
        '''
        yy, xx = np.mgrid[0:small_h, 0:small_w]
        dx = (xx - small_w / 2.0) / (small_w / 2.0)
        dy = (yy - small_h / 2.0) / (small_h / 2.0)
        radius = np.sqrt(dx + dy)
        rings = 0.5 + 0.5 * np.sin((radius * 8.0 - t * 3.0) * (1.0 + 2.5 * (1.0 - ease)))
        rings = np.clip((rings - 0.6) * 3.0, 0.0, 1.0)  # выделяем пики
        rings_blur = cv2.GaussianBlur((rings * 255).astype(np.uint8), (0, 0), sigmaX=6.0)
        # тонируем кольца вторичным тоном и добавляем
        '''
красим круги во вторичный цвет и добавляем их в свечение. Получается пульсирующий ореол.
        '''
        hsv_ring = np.zeros((small_h, small_w, 3), dtype=np.uint8)
        hsv_ring[..., 0] = secondary_hue
        hsv_ring[..., 1] = int(np.clip(120 * (0.7 + 0.3 * ease), 0, 255))
        hsv_ring[..., 2] = rings_blur
        ring_col = cv2.cvtColor(hsv_ring, cv2.COLOR_HSV2BGR).astype(np.float32)
        glow_acc += ring_col * (0.18 * (1.0 + 0.8 * (1.0 - ease)))

        # ---- Добавляем центральный подсвет/виньетку на small ----
        '''
добавляем яркость в центре (центральная подсветка), типа «сияние изнутри».
        '''
        glow_acc += (self._vignette_small[..., None] * 30.0 * (1.0 + 0.8 * (1.0 - progress)))

        # ---- Upscale + temporal smoothing ----
        '''
Увеличиваем свечение обратно до исходного размера кадра.
Дальше сглаживаем по времени – берём кусок нового свечения и кусок старого, мешаем.
Это чтоб эффект плавно менялся, а не дёргался.
        '''
        glow_up = cv2.resize(np.clip(glow_acc, 0, 255).astype(np.uint8), (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32)
        if not hasattr(self, '_prev_glow'):
            self._prev_glow = glow_up.copy()
        alpha = 1.0 - temporal_smooth
        self._prev_glow = glow_up * alpha + self._prev_glow * (1.0 - alpha)
        glow_up = self._prev_glow

        # ---- Color dodge composite (float-safe) ----
        '''
Тут делаем крутой приём – color dodge.
Он смешивает картинку с подсветкой так, что края становятся супер яркими, как будто светятся.
Потом смешиваем это с оригиналом, контролируя силу эффектом mix_strength.
        '''
        base_f = frame.astype(np.float32)
        eps = 1e-3
        dodge = base_f * 255.0 / (255.0 - glow_up + eps)
        dodge = np.clip(dodge, 0.0, 255.0)
        out = cv2.addWeighted(base_f, 1.0 - mix_strength, dodge, mix_strength, 0.0)

        # ---- Поднятие насыщенности/яркости ----
        '''
поднимаем насыщенность и яркость (особенно ближе к середине прогресса).
Картинка становится более «кислотной».
        '''
        out_uint = np.clip(out, 0, 255).astype(np.uint8)
        hsv = cv2.cvtColor(out_uint, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] = np.clip(hsv[..., 1] * (1.0 + 0.9 * ease), 0, 255)
        hsv[..., 2] = np.clip(hsv[..., 2] * (1.0 + 0.38 * ease), 0, 255)
        out_uint = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # ---- Лёгкая хроматическая аберрация (на полном размере) ----
        '''
Сдвигаем каналы по-разному (синий вправо, красный вверх).
Получается лёгкий «glitch» эффект, как будто линза хромает.
Это и есть хроматическая аберрация.
        '''
        if chroma_max_shift > 0:
            shift = int(np.clip(chroma_max_shift * (0.5 + 0.5 * math.sin(t * 2.7)), 0, chroma_max_shift))
            b, g, r = cv2.split(out_uint)
            if shift > 0:
                b = np.roll(b, shift, axis=1)
                r = np.roll(r, -shift, axis=0)
            out_uint = cv2.merge((b, g, r))

        # ---- Тонкий film grain / шум ----
        '''
добавляем шум (зерно), чтоб картинка выглядела более «живой», не компьютерной.
        '''
        if grain_strength > 0.0001:
            noise = (np.random.randn(h, w, 1).astype(np.float32) * grain_strength * 255.0)
            out_f = out_uint.astype(np.float32) + noise
            out_uint = np.clip(out_f, 0, 255).astype(np.uint8)

        # ---- Финальная виньетка (на full) ----
        '''
затемняем края (виньетка), чтоб взгляд фокусировался на центре.
        '''
        vign_up = cv2.resize(self._vignette_small, (w, h), interpolation=cv2.INTER_LINEAR)
        vign_mask = (1.0 - vignette_strength) + (vign_up * vignette_strength)
        out_final = np.clip(out_uint.astype(np.float32) * vign_mask[..., None], 0, 255).astype(np.uint8)

        '''
🔥 Короче, брат, это целый «энергетический коктейль» эффектов:
края горят, центр сияет, кольца пульсируют,
всё двигается плавно, ещё и киношный вайб через зерно и виньетку.
        '''
        return out_final

    def glitch_shift2(self, frame, t, duration):
        # frame: HxWx3 uint8, t: текущее время, duration: длительность
        h, w = frame.shape[:2]
        progress = float(np.clip(t / duration, 0.0, 1.0))
        '''
Чем дальше по прогрессу, тем сильнее сдвиги.
Максимум = 60 пикселей. Но минимум хотя бы 1, чтоб эффект всегда был.
        '''
        max_shift = max(1, int(60 * progress))
        '''
— Создаём генератор случайных чисел, но завязываем его на время t.
— Это значит, что каждый кадр всегда даёт одинаковый рандом (чтоб не дёргалось неконтролируемо).
        '''
        rng = np.random.default_rng(int(t * 1000) & 0xffffffff)  # детерминированно на кадр

        # 1) Разрежённый шум (чтобы не нагружать процессор слишком сильно)
        '''
— Вероятность что на пиксель накинем шум. Сначала мало (0.02), потом больше (до 0.1).
        '''
        p_noise = 0.02 + 0.08 * progress  # вероятность для каждого пикселя
        '''
— Делаем маску: где True, туда бахнем шум. Типа случайные пиксели будут "шуметь".
        '''
        mask = rng.random((h, w)) < p_noise
        '''
Если хоть один пиксель выбран, двигаемся дальше.
        '''
        if mask.any():
            '''
Генерим шумовые значения от -20 до +20, для всех выбранных пикселей.
            '''
            noise_vals = rng.integers(-20, 21, size=(mask.sum(), 1), dtype=np.int16)
            '''
Переводим картинку в int16,
чтоб при добавлении не переполнилось
(а то будет как перепиленный барыга — зашкаливать).
            '''
            temp = frame.astype(np.int16)
            # применяем шум только к отмеченным пикселям, ко всем каналам
            '''
Меняем только нужные пиксели (по маске) сразу для всех трёх каналов (BGR).
            '''
            temp.reshape(-1, 3)[mask.ravel()] += noise_vals
            '''
Ограничиваем, чтобы значения оставались от 0 до 255 (иначе картинка поедет нафиг).
            '''
            np.clip(temp, 0, 255, out=temp)
            '''
Возвращаем картинку обратно в нормальный тип байт.
            '''
            frame = temp.astype(np.uint8)

        # 2) Лёгкий RGB-сдвиг (разные сдвиги для каналов)
        '''
Для каждого канала (R, G, B) выбираем свой сдвиг по ширине.
        '''
        shifts = rng.integers(-max_shift, max_shift + 1, size=3)
        # Берём каналы как срезы, чтобы не создавать лишних копий через cv2.split
        '''
— Сдвигаем каналы по горизонтали (axis=1). У каждого свой сдвиг.
— Красный, зелёный, синий теперь поехали в разные стороны.
        '''
        r = np.roll(frame[:, :, 2], shifts[0], axis=1)
        g = np.roll(frame[:, :, 1], shifts[1], axis=1)
        b = np.roll(frame[:, :, 0], shifts[2], axis=1)
        '''
Склеиваем обратно в один кадр (BGR для OpenCV).
        '''
        frame = np.dstack((b, g, r))  # восстанавливаем порядок BGR для OpenCV

        # 3) Полосы (не слишком мелкие, чтобы цикл был короткий)
        '''
Высота полосы. Минимум 8 пикселей, максимум под размер картинки.
        '''
        stripe_h = max(8, h // 20)  # адаптивно по высоте
        '''
Считаем сколько полос будет по высоте.
        '''
        n_stripes = (h + stripe_h - 1) // stripe_h
        # генерируем сдвиги для каждой полосы, часть полос может остаться без сдвига
        '''
Для каждой полосы выбираем случайный сдвиг.
        '''
        stripe_shifts = rng.integers(-max_shift, max_shift + 1, size=n_stripes)
        '''
Решаем, какие полосы реально будут сдвинуты (с прогрессом шанс больше).
        '''
        apply_mask = rng.random(n_stripes) < (0.25 + 0.75 * progress)
        '''
— Бежим по полосам.
— Если полосу надо двигать, то берём её кусок по высоте и сдвигаем по ширине.
        '''
        for i, s in enumerate(stripe_shifts):
            if not apply_mask[i] or s == 0:
                continue
            y0 = i * stripe_h
            y1 = min((i + 1) * stripe_h, h)
            frame[y0:y1] = np.roll(frame[y0:y1], int(s), axis=1)

        # 4) Несколько блочных всплесков (иногда), чтобы эффект стал «супер»
        '''
Иногда (с шансом до 35%) добавляем "всплески".
        '''
        if rng.random() < 0.35 * progress:
            '''
Кол-во блоков, от 1 до 3.
            '''
            n_blocks = int(rng.integers(1, 4))
            '''
— Тут режем картинку на прямоугольные блоки.
— Высота блока случайная, ширина тоже.
— Координаты выбираем случайно.
— Берём этот блок и двигаем его в сторону.
— Выглядит как будто картинку кусками разорвало.
            '''
            for _ in range(n_blocks):
                bh = int(rng.integers(stripe_h, stripe_h * 3))
                bw = int(rng.integers(max(4, w // 15), max(8, w // 3)))
                y = int(rng.integers(0, max(1, h - bh + 1)))
                x = int(rng.integers(0, max(1, w - bw + 1)))
                dx = int(rng.integers(-max_shift, max_shift + 1))
                frame[y:y + bh, x:x + bw] = np.roll(frame[y:y + bh, x:x + bw], dx, axis=1)

        return frame

    def starburst_explosion2(self, frame, t, duration):
        # прогресс 0..1 с плавным easing
        progress = float(t) / max(1e-6, duration)
        progress = max(0.0, min(1.0, progress))
        # лёгкий ease (smooth)
        '''
Тут хитрая формула: делает плавный разгон и замедление.
Типа вместо резкого «вкл/выкл», идёт красивый переход.
        '''
        def smoothstep(x): return x * x * (3 - 2 * x)
        '''
Применяем этот плавный переход, и теперь у нас p – сглаженный прогресс.
        '''
        p = smoothstep(progress)

        h, w = frame.shape[:2]
        '''
Делаем копию кадра, с которой будем работать, и приводим к целым числам для OpenCV.
        '''
        out = frame.copy().astype(np.uint8)

        # === 1) SOFT BLOOM (на уменьшенном слое для экономии) ===
        '''
Решаем, во сколько раз уменьшаем картинку для «свечения».
Если картинка огромная – режем сильнее, чтоб не жрало много ресурсов.
        '''
        ds = 6 if max(h, w) > 1500 else 4  # downscale фактор в зависимости от разрешения
        '''
Считаем размеры уменьшенной копии.
        '''
        sw, sh = max(1, w // ds), max(1, h // ds)
        '''
Создаём чёрное полотно для будущего свечения.
        '''
        glow = np.zeros((sh, sw, 3), dtype=np.uint8)


        '''
Определяем, сколько искр будет. Чем дальше во времени, тем их больше.
Максимум — 250, чтоб не перегрузить систему.
        '''
        max_sparks = 90
        num_sparks = int(max_sparks * (p ** 0.9))
        num_sparks = min(num_sparks, 250)
        '''
Разбрасываем искры случайно по картинке (но на уменьшенной версии).
        '''
        for _ in range(num_sparks):
            gx = random.randint(0, sw - 1)
            gy = random.randint(0, sh - 1)
            # радиус на мелком слое
            '''
Размер искры: чуть больше с прогрессом, плюс немного рандома.
            '''
            r = max(1, int(1 + 6 * p * (0.5 + random.random() * 0.9)))
            # цвет — тёплый с лёгким сдвигом к пурпурно-розовому
            color = (int(160 + random.random() * 95),
                     int(130 + random.random() * 120),
                     int(190 + random.random() * 60))
            '''
Рисуем кружок-искру в слое glow.
            '''
            cv2.circle(glow, (gx, gy), r, color, -1, lineType=cv2.LINE_AA)

        '''
Размываем всё свечение Гауссом, чтоб выглядело мягко.
k – размер фильтра, растёт с прогрессом.
Делаем его нечётным, иначе OpenCV ругнётся.
        '''
        k = max(1, int(3 + 14 * p))
        if k % 2 == 0: k += 1
        glow = cv2.GaussianBlur(glow, (k, k), 0)
        '''
Увеличиваем слой свечения обратно до размеров оригинала.
        '''
        glow_up = cv2.resize(glow, (w, h), interpolation=cv2.INTER_LINEAR)
        # лёгкая хроматическая аберрация на bloom — смещение каналов
        '''
Добавляем эффект «хроматическая аберрация» — сдвигаем цветовые каналы,
чтобы появилось ощущение цифрового блика.
        '''
        shift = max(1, int(1 + 6 * p))
        bloom = glow_up.copy()
        bloom[:,:,0] = np.roll(bloom[:,:,0], shift, axis=1)   # B
        bloom[:,:,2] = np.roll(bloom[:,:,2], -shift//2, axis=1)  # R
        '''
Смешиваем исходный кадр и свечение.
        '''
        out = cv2.addWeighted(out, 1.0, bloom, 0.18 + 0.6 * p, 0)

        # === 2) SOFT LIGHT RAYS (тонкие, от центра или от ярких точек) ===
        '''
Создаём пустой слой для лучей и центр экрана.
        '''
        rays = np.zeros_like(out)
        cx, cy = w // 2, h // 2
        '''
Количество лучей увеличивается с прогрессом.
        '''
        num_rays = int(8 + 12 * p)
        '''
Рисуем луч: угол — равномерно по кругу, но с рандомным сдвигом.
Длина луча зависит от размера картинки и прогресса.
        '''
        for i in range(num_rays):
            angle = random.uniform(-0.25, 0.25) + (2 * math.pi * i / max(1, num_rays))
            length = int(min(w, h) * (0.6 + 0.5 * p) * (0.8 + random.random() * 0.6))
            '''
Конечная точка луча по углу и длине.
            '''
            x2 = int(cx + math.cos(angle) * length)
            y2 = int(cy + math.sin(angle) * length * 0.9)
            '''
Рисуем сам луч: бело-голубой, с толщиной зависящей от прогресса.
            '''
            thickness = max(1, int(1 + 4 * p * (0.5 + random.random())))
            col = (220, 210, 255)
            cv2.line(rays, (cx, cy), (x2, y2), col, thickness, lineType=cv2.LINE_AA)
        '''
Размываем лучи и подмешиваем их в картинку.
        '''
        rays = cv2.GaussianBlur(rays, (15, 15), 0)
        out = cv2.addWeighted(out, 1.0, rays, 0.18 * p, 0)

        # === 3) ELEGANT SHARDS (плавно парящие куски с мягкими краями и лёгкой кинетикой) ===
        '''
Эффект осколков начинается не сразу, а чуть позже прогресса (с 15%).
        '''
        if p > 0.15:
            # адаптивный размер шардов: меньше для мобильных, больше для крупных кадров
            '''
Считаем размер осколков: адаптивно под картинку.
Минимум 48 пикселей, максимум 160 – чтобы маленькие и огромные кадры нормально смотрелись.
            '''
            shard_base = int(min(h, w) / 12)
            shard_size = max(48, min(160, shard_base))
            '''
Насколько сильно осколки будут разлетаться: растёт плавно от 0 до 1 с прогрессом.
            '''
            move_strength = (p - 0.15) / (1.0 - 0.15)
            move_strength = max(0.0, min(1.0, move_strength))
            '''
Вероятность того, что конкретный осколок двинется наружу
            '''
            move_prob = 0.32 + 0.58 * move_strength  # часть шардов движется
            # ограничение на количество дорогих поворотов
            '''
Ограничиваем количество «дорогих» поворотов (чтоб не грузить комп).
            '''
            max_rotates = 10
            rotates_done = 0
            '''
Делим картинку на квадраты (шарды).
С вероятностью move_prob выбираем, какие куски будут лететь.
Берём подкадр с оригинала.
            '''
            for i in range(0, h, shard_size):
                ph = min(shard_size, h - i)
                for j in range(0, w, shard_size):
                    if random.random() > move_prob:
                        continue
                    pw = min(shard_size, w - j)
                    src = frame[i:i+ph, j:j+pw].astype(np.uint8)

                    # направление наружу от центра для естественного разлёта
                    '''
Считаем направление наружу от центра, нормализуем вектор, чтоб осколки летели от центра.
                    '''
                    sx = (j + pw/2.0) - cx
                    sy = (i + ph/2.0) - cy
                    dist = math.hypot(sx, sy) + 1e-6
                    nx, ny = sx / dist, sy / dist

                    # дальность смещения растёт плавно
                    '''
Дальность смещения: растёт с прогрессом и немного рандомная, чтобы выглядело натурально.
                    '''
                    max_shift = int(min(w, h) * 0.45 * (0.25 + 0.75 * move_strength))
                    dx = int(nx * max_shift * (0.5 + 0.5 * random.random()))
                    dy = int(ny * (max_shift*0.55) * (0.4 + 0.6 * random.random()))

                    # небольшой параллакс по глубине: ближние куски смещаются сильнее
                    '''
Параллакс: осколки ближе к центру двигаются сильнее, дальние – слабее.
                    '''
                    depth_bias = 1.0 - (dist / (math.hypot(cx, cy) + 1e-6))
                    dx = int(dx * (0.6 + 0.8 * depth_bias))
                    dy = int(dy * (0.6 + 0.8 * depth_bias))

                    '''
Вычисляем новую позицию осколка и обрезаем, чтобы он не вылез за края.
                    '''
                    new_j = j + int(dx * move_strength)
                    new_i = i + int(dy * move_strength)
                    new_j = max(0, min(w - pw, new_j))
                    new_i = max(0, min(h - ph, new_i))


                    '''
Редкий поворот осколка, чтобы было естественнее.
Не более max_rotates за кадр, угол небольшой, зависит от прогресса.
                    '''
                    dst_patch = src

                    # редкие аккуратные повороты для натуральности
                    if rotates_done < max_rotates and random.random() < 0.12:
                        angle = random.uniform(-6.0, 6.0) * move_strength
                        M = cv2.getRotationMatrix2D((pw / 2.0, ph / 2.0), angle, 1.0)
                        rotated = cv2.warpAffine(src, M, (pw, ph), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                        dst_patch = rotated
                        rotates_done += 1

                    # мягкая маска: используем расстояние до центра фрагмента, даём плавные края
                    '''
Создаём круговую маску для плавных краёв осколка.
                    '''
                    yy, xx = np.ogrid[:ph, :pw]
                    cxr, cyr = pw / 2.0, ph / 2.0
                    radius = math.hypot(cxr, cyr)
                    mask = (( (xx - cxr)**2 + (yy - cyr)**2 ) <= (radius*0.98)**2).astype(np.float32)
                    # размываем маску (маленький гаусс)
                    '''
Размываем маску, делаем мягкий край, повторяем для трёх каналов.
                    '''
                    mk = max(3, int(3 + 5 * (1.0 - move_strength)))
                    if mk % 2 == 0: mk += 1
                    mask = cv2.GaussianBlur((mask*255).astype(np.uint8), (mk, mk), 0).astype(np.float32) / 255.0
                    mask3 = np.repeat(mask[:, :, None], 3, axis=2)

                    # добавляем мягкий trailing (2 шага) для ощущения motion blur — дешёвый приём
                    '''
Делаем дешёвый motion blur: несколько копий осколка с постепенным смещением.
Чем ближе к центру, тем прозрачнее, создаёт ощущение движения.
                    '''
                    trail_steps = 2
                    total = np.zeros_like(dst_patch, dtype=np.float32)
                    alpha_acc = 0.0
                    for s in range(trail_steps + 1):
                        talpha = (1.0 - s / (trail_steps + 1)) * (0.6 + 0.4 * move_strength)
                        shift_x = int(- (dx * move_strength) * (s / (trail_steps + 1)) * 0.6)
                        shift_y = int(- (dy * move_strength) * (s / (trail_steps + 1)) * 0.6)
                        # берём src и сдвигаем в пределах фрагмента: сдвиг через roll, затем обрезка валидной области
                        rolled = np.roll(dst_patch, shift=(shift_y, shift_x), axis=(0,1))
                        total += rolled.astype(np.float32) * talpha
                        alpha_acc += talpha
                    if alpha_acc > 1e-6:
                        total = (total / alpha_acc).astype(np.uint8)
                    else:
                        total = dst_patch

                    # смешивание с фреймом через маску
                    '''
Смешиваем осколок с фреймом по маске: мягко накладываем на картинку.
                    '''
                    dst_roi = out[new_i:new_i+ph, new_j:new_j+pw].astype(np.float32)
                    src_f = total.astype(np.float32)
                    blended = (src_f * mask3 + dst_roi * (1.0 - mask3)).astype(np.uint8)
                    out[new_i:new_i+ph, new_j:new_j+pw] = blended

                    # тонкий подсвет/блик на верхней грани фрагмента
                    '''
Лёгкий блик сверху осколка для объёма и свечения.
                    '''
                    if pw > 6 and ph > 6:
                        light_alpha = 0.18 * (0.4 + move_strength * 0.6)
                        top_line = (230, 225, 255)
                        cv2.line(out, (new_j, new_i), (new_j + pw - 1, new_i), top_line, max(1, int(1 + move_strength)), lineType=cv2.LINE_AA)

        # === 4) SOFT COLOR GRADE & VIGNETTE ===
        # лёгкий тёплый градиент/подтяжка контраста
        '''
Цветокоррекция: лёгкая S-кривая, добавляет контраста и подчёркивает светлые/тёмные области.
        '''
        lut = np.arange(256, dtype=np.uint8)
        # небольшой S-curve: усиливает контраст (кривую можно менять)
        lut = np.clip(255.0 * ( (lut / 255.0) ** (0.95 - 0.12 * p) ), 0, 255).astype(np.uint8)
        for c in range(3):
            out[:,:,c] = cv2.LUT(out[:,:,c], lut)

        # добавить лёгкий тёплый тон: добавить в R небольшую прибавку, в B — небольшое ослабление
        '''
Добавляем тёплый тон: красный чуть ярче, синий чуть тусклее.
        '''
        warm = int(8 + 28 * p)
        out[:,:,2] = np.clip(out[:,:,2].astype(int) + warm, 0, 255).astype(np.uint8)  # R up
        out[:,:,0] = np.clip(out[:,:,0].astype(int) - int(warm * 0.3), 0, 255).astype(np.uint8)  # B down

        # виньетка (мягкая)
        '''
Виньетка: края кадра слегка затемнены, центр ярче.
Сила виньетки растёт с прогрессом.
        '''
        vx = cv2.getGaussianKernel(w, w * 0.9)
        vy = cv2.getGaussianKernel(h, h * 0.9)
        vign = vy @ vx.T
        vign = (vign - vign.min()) / (vign.max() - vign.min() + 1e-9)
        vign_strength = 0.28 * p
        for c in range(3):
            out[:,:,c] = (out[:,:,c].astype(np.float32) * (1.0 - vign_strength * (1.0 - vign))).astype(np.uint8)

        return out

    def mirror_shatter2(self, frame, t, duration):
        # прогресс 0..1 с плавным easing (ease out)
        progress = float(t) / max(1e-6, duration)
        progress = max(0.0, min(1.0, progress))
        def ease_out(x): return 1 - (1 - x) ** 3
        p = ease_out(progress)

        h, w = frame.shape[:2]
        # базовый бленд оригинала и зеркала — зеркальная ось по центру
        '''
Делаем зеркалку по вертикали (flip(frame, 1)) и смешиваем с оригиналом.
0.6/0.4 — чтобы оригинал был ярче. Тип uint8 — стандарт для картинки.
        '''
        mirrored = cv2.flip(frame, 1)
        base = cv2.addWeighted(frame, 0.6, mirrored, 0.4, 0).astype(np.uint8)

        out = base.copy()

        # тонкая подсветка вдоль зеркальной оси (seam glow)
        '''
Чёткая линия по центру зеркала, типа «шов» с лёгким свечением.  
`seam_width` растёт с прогрессом анимации,
`GaussianBlur` делает её мягкой,
а потом смешиваем с кадром через addWeighted.
        '''
        cx = w // 2
        seam = np.zeros_like(base, dtype=np.uint8)
        seam_width = max(2, int(2 + 8 * p))
        cv2.line(seam, (cx, 0), (cx, h - 1), (230, 220, 255), seam_width, lineType=cv2.LINE_AA)
        seam = cv2.GaussianBlur(seam, (1 + 2 * seam_width, 1 + 2 * seam_width), 0)
        out = cv2.addWeighted(out, 1.0, seam, 0.22 * p, 0)

        # когда начинается разлет шардов
        '''
Эффект «разлета shards» стартует после 22% прогресса.
sp — локальный прогресс для этих осколков.
        '''
        shatter_start = 0.22
        if p > shatter_start:
            sp = (p - shatter_start) / (1.0 - shatter_start)
            sp = max(0.0, min(1.0, sp))

            # параметры шардов
            '''
Настраиваем размер осколков и их количество.
С ростом sp осколков становится больше, но не больше max_shards.
            '''
            shard_base = int(min(h, w) / 12)
            shard_size = max(40, min(160, shard_base))
            max_shards = 28
            num_shards = max(4, int(max_shards * (sp ** 0.95)))
            num_shards = min(num_shards, max_shards)

            # ограничение на heavy transforms
            '''
Ограничиваем количество поворотов осколков, чтобы не грузить комп, и сохраняем центральную ось.
            '''
            max_rotates = 6
            rotates_done = 0

            # заранее получаем центр-ось (x=center seam)
            seam_x = float(cx)

            '''
Выбираем случайную точку осколка рядом с осью.
j — горизонталь, i — вертикаль. Гаусс смещает осколок ближе к центру.
            '''
            for s in range(num_shards):
                # выбираем случайную исходную позицию близко к зеркальной оси,
                # чтобы шард выглядел как оторванный от зеркала
                # x в пределах +/- половины ширины шардов от оси
                j = int(np.clip(random.gauss(seam_x, shard_size * 1.2), 0, w - 1))
                i = random.randint(0, max(0, h - 1))

                '''
Корректируем осколок, если он слишком близко к краю, чтобы не вылететь за картинку.
                '''
                pw = min(shard_size, w - j)
                ph = min(shard_size, h - i)
                # если холостой (слишком близко к краю), скорректируем область так, чтобы взять нормальный фрагмент
                if pw <= 4 or ph <= 4:
                    # возьмём безопасный фрагмент внутри кадра
                    j = max(0, min(w - shard_size, j - shard_size // 2))
                    i = max(0, min(h - shard_size, i - shard_size // 2))
                    pw = min(shard_size, w - j)
                    ph = min(shard_size, h - i)

                '''
Вырезаем осколок из оригинала.
                '''
                src = frame[i:i + ph, j:j + pw].astype(np.uint8)

                # направление движения: наружу от seam (если слева — влево, если справа — вправо)
                '''
Определяем направление движения:
влево или вправо от центра, с небольшой вертикальной случайной составляющей.
                '''
                center_x_fragment = j + pw / 2.0
                dir_x = 1.0 if center_x_fragment > seam_x else -1.0
                # вертикальная составляющая небольшая, с рандомом
                dir_y = random.uniform(-0.25, 0.25)

                # глубина/параллакс: фрагменты ближе к центру смещаются сильнее
                '''
Чем ближе осколок к центру — тем сильнее смещаем. Получаем эффект «глубины» или параллакса.
                '''
                dist_from_center = abs(center_x_fragment - seam_x)
                max_dist = w / 2.0
                depth_factor = 1.0 - (dist_from_center / (max_dist + 1e-6))
                depth_factor = 0.5 + 0.5 * depth_factor  # 0.5..1.0
                # величина смещения зависит от sp, depth и рандома
                '''
Вычисляем смещение осколка. dx и dy зависят от направления, прогресса sp, случайности и глубины.
                '''
                max_shift = int(min(w, h) * 0.45 * (0.25 + 0.75 * sp))
                dx = int(dir_x * max_shift * (0.4 + 0.6 * random.random()) * depth_factor)
                dy = int(dir_y * (max_shift * 0.35) * (0.6 + 0.8 * random.random()) * depth_factor)
                new_j = j + int(dx * sp)
                new_i = i + int(dy * sp)

                # корректируем в границы для вставки
                '''
Корректируем осколок, чтобы не вылез за границы кадра.
                '''
                new_j = max(0, min(w - pw, new_j))
                new_i = max(0, min(h - ph, new_i))


                '''
Иногда крутим осколок, но редко, чтобы комп не тормозил. BORDER_REFLECT — чтоб края не уродились.
                '''
                dst_patch = src

                # редко делаем аккуратный поворот (дорогая операция) — ограничиваем общее число
                if rotates_done < max_rotates and random.random() < 0.18:
                    angle = random.uniform(-7.0, 7.0) * sp
                    M = cv2.getRotationMatrix2D((pw / 2.0, ph / 2.0), angle, 1.0)
                    # borderMode REFLECT — без жестких артефактов
                    rotated = cv2.warpAffine(src, M, (pw, ph), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                    dst_patch = rotated
                    rotates_done += 1


                '''
Создаём мягкую маску, чтобы края осколка были плавными. Чем дальше прогресс — тем меньше размытие.
                '''
                # создаём мягкую маску: закруглённый прямоугольник / эллипс
                yy, xx = np.ogrid[:ph, :pw]
                cxr, cyr = pw / 2.0, ph / 2.0
                # эллиптическая маска
                mask = (((xx - cxr) ** 2) / (cxr ** 2 + 1e-6) + ((yy - cyr) ** 2) / (cyr ** 2 + 1e-6)) <= 1.0
                mask = mask.astype(np.float32)
                mk = max(3, int(3 + 5 * (1.0 - sp)))  # меньший blur по мере роста эффекта
                if mk % 2 == 0: mk += 1
                mask = cv2.GaussianBlur((mask * 255).astype(np.uint8), (mk, mk), 0).astype(np.float32) / 255.0
                mask3 = np.repeat(mask[:, :, None], 3, axis=2)

                # лёгкий trailing: 1-2 шага дешёвого смещения для ощущения motion
                '''
Делаем лёгкий «trail», чтобы осколки оставляли след при движении — типа motion blur дешевый.
                '''
                trail_steps = 2
                total = np.zeros_like(dst_patch, dtype=np.float32)
                alpha_acc = 0.0
                for step in range(trail_steps + 1):
                    fac = 1.0 - (step / (trail_steps + 1))
                    talpha = fac * (0.55 + 0.45 * sp)
                    # смещение внутри патча (не глобальное) — создаёт иллюзию размытия движения
                    sx = int(-dx * (step / (trail_steps + 1)) * 0.18)
                    sy = int(-dy * (step / (trail_steps + 1)) * 0.18)
                    rolled = np.roll(dst_patch, shift=(sy, sx), axis=(0, 1))
                    total += rolled.astype(np.float32) * talpha
                    alpha_acc += talpha
                if alpha_acc > 1e-6:
                    total = (total / alpha_acc).astype(np.uint8)
                else:
                    total = dst_patch

                # альфа-блендинг вставляемого фрагмента в выходной кадр
                '''
Вставляем осколок обратно в кадр с плавными краями через маску.
                '''
                dst_roi = out[new_i:new_i + ph, new_j:new_j + pw].astype(np.float32)
                src_f = total.astype(np.float32)
                blended = (src_f * mask3 + dst_roi * (1.0 - mask3)).astype(np.uint8)
                out[new_i:new_i + ph, new_j:new_j + pw] = blended

                # тонкая подсветка сверху фрагмента для ощущения «разреза»
                '''
Добавляем тонкую светящуюся линию сверху осколка, чтобы выглядело как резаное стекло.
                '''
                if pw > 6 and ph > 6:
                    alpha_line = 0.12 + 0.4 * sp
                    line_col = (230, 225, 255)
                    cv2.line(out, (new_j, new_i), (new_j + pw - 1, new_i), line_col, max(1, int(1 + sp * 2)), lineType=cv2.LINE_AA)

        # финальный лёгкий bloom и виньетка для глубины
        # bloom: небольшое размытие копии и смешивание
        '''
Лёгкий bloom: размазываем маленькую версию кадра,
потом возвращаем обратно и смешиваем — красиво блестит.
        '''
        small = cv2.resize(out, (max(1, w // 4), max(1, h // 4)), interpolation=cv2.INTER_LINEAR)
        small = cv2.GaussianBlur(small, (5, 5), 0)
        bloom = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)
        out = cv2.addWeighted(out, 1.0, bloom, 0.12 * p, 0)

        # цветокор: чуть теплее и лёгкий S-curve
        '''
Цветокор: чуть теплее, лёгкий S-curve через LUT, красим красный чуть ярче, синий — чуть тусклее.
        '''
        lut = np.arange(256, dtype=np.uint8)
        gamma = 1.0 - 0.06 * p
        lut = np.clip(255.0 * ((lut / 255.0) ** gamma), 0, 255).astype(np.uint8)
        for c in range(3):
            out[:, :, c] = cv2.LUT(out[:, :, c], lut)
        warm = int(6 * p)
        out[:, :, 2] = np.clip(out[:, :, 2].astype(int) + warm, 0, 255).astype(np.uint8)
        out[:, :, 0] = np.clip(out[:, :, 0].astype(int) - int(warm * 0.25), 0, 255).astype(np.uint8)

        # мягкая виньетка, усиливаем её по мере прогресса
        '''
Делаем виньетку: края чуть темнее, центр ярче, и эффект усиливается с прогрессом.
        '''
        vx = cv2.getGaussianKernel(w, w * 0.9)
        vy = cv2.getGaussianKernel(h, h * 0.9)
        vign = (vy @ vx.T)
        vign = (vign - vign.min()) / (vign.max() - vign.min() + 1e-9)
        vign_strength = 0.22 * p
        for c in range(3):
            out[:, :, c] = (out[:, :, c].astype(np.float32) * (1.0 - vign_strength * (1.0 - vign))).astype(np.uint8)

        return out

    def color_wave_glitch2(self, frame, t, duration):

        # параметры (можно вынести в self)
        '''
«Здесь мы задаём всю химию: сколько крутим оттенки,
как волна двигается, размер полос, сколько блоков рвём,
насколько сдвигаем цвета и добавляем шумы.
Короче, всё для того, чтобы картинка офигенно дергалась.»
        '''
        hue_amp_max = 60
        hue_freq = 1.2
        wave_amp_max = 18
        wave_freq = 0.8
        wave_len = 120.0
        slice_w = 28
        slice_shift_max = 28
        n_blocks = 4
        block_shift_max = 40
        channel_shift_max = 14
        jitter_max = 12
        scanline_strength = 0.12
        noise_amount = 0.035
        noise_intensity = 48


        '''
«Берём размеры картинки,
потом заводим генератор случайных чисел, привязанный к времени,
чтобы глитч был детерминированным, но меняться с течением времени.»
        '''
        progress = float(t) / max(float(duration), 1e-6)
        progress = max(0.0, min(1.0, progress))

        h, w = frame.shape[:2]
        rng = np.random.RandomState(int(t * 1000) ^ 0x9e3779b9)

        # Hue & saturation (работаем в int16/float чтобы не переполнять uint8)
        '''
«Здесь мы крутнем цвета.
Переводим в HSV, чтобы легче было работать с оттенком и насыщенностью.
Потом считаем, как сильно смещать Hue по синусоиде,
добавляем варьирование насыщенности,
ограничиваем значения, и возвращаем обратно в BGR.
В итоге базовая картинка с цветовым сдвигом готова.»
        '''
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.int16)
        hue_shift = int(round(hue_amp_max * progress * math.sin(2 * math.pi * hue_freq * t)))
        hsv[..., 0] = (hsv[..., 0] + hue_shift) % 180
        sat_var = 1.0 + 0.35 * math.sin(t * 3.0 + progress * 6.0)
        hsv[..., 1] = np.clip(hsv[..., 1].astype(np.float32) * sat_var, 0, 255).astype(np.int16)
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        base = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)      # uint8

        # remap: создаём координатные карты в float32
        '''
«Создаём сетку координат, чтобы потом волны по картинке гонять.
Амплитуда волны растёт с прогрессом.
Горизонтальная амплитуда — половина общей, для красоты.»
        '''
        xx, yy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        wave_amp = wave_amp_max * (0.25 + 0.75 * progress)
        horiz_amp = 0.5 * wave_amp

        '''
«Считаем новые координаты пикселей с учётом волн.
yy идёт вверх-вниз, xx — слева-направо.
Синусы и косинусы делают эту картинку как будто дышащей.»
        '''
        map_y = yy + wave_amp * np.sin(2 * math.pi * ((xx / max(1.0, wave_len)) - wave_freq * t))
        map_x = xx + horiz_amp * np.cos(2 * math.pi * ((yy / max(1.0, wave_len * 0.6)) + wave_freq * t * 0.7))

        # jitter (маленькая однотипная добавка) — делаем как float32
        '''
«Добавляем мелкий дерганчик, чтобы не было идеально ровно.
Jitter — типа легкая дрожь, и прогресс увеличивает его силу.»
        '''
        jitter_x = (rng.rand() - 0.5) * 2.0 * (jitter_max * (0.06 + 0.94 * progress))
        map_x = (map_x + float(jitter_x)).astype(np.float32, copy=False)
        map_y = map_y.astype(np.float32, copy=False)

        # remap целиком (будем использовать для базового "warped")
        '''
«Перемапливаем картинку по этим координатам — базовый волновой глитч готов.
Копируем в out, дальше будем допиливать.»
        '''
        warped = cv2.remap(base, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        out = warped.copy()

        # slice-глитч (вертикальные полосы с вертикальным сдвигом)
        '''
«Делаем вертикальные полоски, сдвигаем их вверх-вниз.
Полосы дергаются по синусоиде, с прогрессом глитч становится сильнее.»
        '''
        for x in range(0, w, slice_w):
            xs = min(w, x + slice_w)
            phase = t * 3.0 + x * 0.04
            shift = int(round(slice_shift_max * (0.2 + 0.8 * progress) * math.sin(phase)))
            if shift != 0:
                out[:, x:xs] = np.roll(out[:, x:xs], shift, axis=0)

        # блочные разрывы
        '''
«Режем картинку на случайные блоки и дергаем их по x/y.
Короче, эффект разрыва, как будто кто-то по экрану ударил,
чем больше прогресс, тем сильнее сдвиги.»
        '''
        blocks = max(1, int(n_blocks * (0.6 + 0.8 * progress)))
        for i in range(blocks):
            bw = int(rng.randint(w // 8, max(16, w // 3)))
            bh = int(rng.randint(h // 10, max(12, h // 4)))
            bx = int(rng.randint(0, max(1, w - bw)))
            by = int(rng.randint(0, max(1, h - bh)))
            dx = int(round((rng.randint(-block_shift_max, block_shift_max)) * (0.3 + 0.7 * progress)))
            dy = int(round((rng.randint(-block_shift_max, block_shift_max)) * (0.3 + 0.7 * progress)))
            patch = np.copy(out[by:by + bh, bx:bx + bw])
            if dx != 0 or dy != 0:
                patch = np.roll(patch, dy, axis=0)
                patch = np.roll(patch, dx, axis=1)
            out[by:by + bh, bx:bx + bw] = patch

        # Хроматическое расслоение — создаём карты для B и R и явным образом приводим к float32
        '''
«Хроматическое расслоение: смещаем синий и красный каналы по x/y,
зелёный оставляем как есть. Это даёт эффект старого VHS и искажений цветов.»
        '''
        ch_dx = channel_shift_max * (0.2 + 0.8 * progress) * math.sin(t * 2.9)
        # создаём отдельные карты (в float32) — добавляем небольшие пространственные вариации
        map_x_f = map_x.astype(np.float32, copy=False)
        map_y_f = map_y.astype(np.float32, copy=False)
        map_x_b = (map_x_f + 0.5 * float(ch_dx) * np.sin(t * 2.1 + yy / max(1.0, h) * 6.0)).astype(np.float32, copy=False)
        map_x_r = (map_x_f - 0.5 * float(ch_dx) * np.sin(t * 2.4 + yy / max(1.0, h) * 5.0)).astype(np.float32, copy=False)
        map_y_b = (map_y_f + 0.4 * float(ch_dx) * np.cos(t * 1.7 + xx / max(1.0, w) * 7.0)).astype(np.float32, copy=False)
        map_y_r = (map_y_f - 0.4 * float(ch_dx) * np.cos(t * 1.3 + xx / max(1.0, w) * 6.0)).astype(np.float32, copy=False)

        # remap каналов (SOURCE должен быть uint8 или float32 — у нас uint8)
        '''
«Применяем эти смещения и собираем каналы обратно в картинку.
Готово, цвета дергаются отдельно.»
        '''
        b = cv2.remap(out[..., 0], map_x_b, map_y_b, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        g = cv2.remap(out[..., 1], map_x_f, map_y_f, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        r = cv2.remap(out[..., 2], map_x_r, map_y_r, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        out = cv2.merge([b, g, r])

        # сканлайны
        '''
«Сканлайны: делаем полоски темнее через каждый ряд пикселей, чтобы было похоже на старый экран.»
        '''
        if scanline_strength > 0:
            mask = np.ones((h, 1), dtype=np.float32)
            mask[::2, 0] = 1.0 - scanline_strength
            out = (out.astype(np.float32) * mask[:, :, None]).astype(np.uint8)

        # шум
        '''
«Добавляем случайный шум: кое-где пиксели дергаются случайными значениями.
Красиво режет глаз, как на VHS.»
        '''
        if noise_amount > 0:
            noise_mask = (rng.rand(h, w) < noise_amount)
            if noise_mask.any():
                noise_vals = rng.randint(-noise_intensity, noise_intensity + 1, size=(h, w, 1)).astype(np.int16)
                tmp = out.astype(np.int16)
                tmp += (noise_mask[:, :, None].astype(np.int16) * noise_vals)
                out = np.clip(tmp, 0, 255).astype(np.uint8)

        # небольшой temporal jitter
        '''
«Немного temporal jitter: дергаем всю картинку целиком маленькими шажками. Прогресс усиливает эффект.»
        '''
        if rng.rand() < 0.18 * (0.3 + 0.7 * progress):
            tx = int(round((rng.randint(-6, 7)) * progress * 0.9))
            ty = int(round((rng.randint(-6, 7)) * progress * 0.9))
            if tx != 0 or ty != 0:
                out = np.roll(out, ty, axis=0)
                out = np.roll(out, tx, axis=1)

        return out

    def liquid_melt2(self, frame, t, duration):
        # лёгкий встроенный RNG для детерминированных параметров капель
        import numpy.random as npr

        h, w = frame.shape[:2]
        progress = float(np.clip(t / float(max(duration, 1e-6)), 0.0, 1.0))
        '''
Если ещё только старт, то просто возвращаем исходный кадр, не дергаем его.
        '''
        if progress <= 1e-6:
            return frame

        # копия результата (оставляем видео нетронутым, будем блендить поверх)
        base = frame.astype(np.uint8)
        # overlay цветов и маска прозрачности (float32 для аккуратного смешивания)
        '''
overlay — это сами капли,
а mask — прозрачность,
чтобы можно было аккуратно смешивать с оригиналом.
        '''
        overlay = np.zeros_like(base, dtype=np.uint8)
        mask = np.zeros((h, w), dtype=np.float32)

        # детерминированное распределение капель (одинаково для каждого вызова)
        seed = 424242
        rng = npr.RandomState(seed)

        # количество потенциальных капель (не все появятся сразу)
        '''
Считаем, сколько капель может быть. Сначала мало, потом с прогрессом их больше, максимум 12.
        '''
        max_drops = min(12, 2 + int(8 * progress))

        '''
Перебираем все капли одну за другой.
        '''
        for i in range(max_drops):
            # заранее сгенерированные параметры капли (детерминированно)
            '''
Вот тут мы генерим параметры капли:

start — когда капля появляется;

life_span — сколько живёт;

x и init_y — стартовая позиция;

speed_px — как быстро падает;

width — ширина капли;

color_jitter — чуть-чуть шутим с цветом, чтобы капли не одинаковые.
            '''
            start = float(rng.uniform(-0.6 * duration, duration * 1.1))
            life_span = float(rng.uniform(0.6, 2.6))  # длительность жизни капли в сек
            x = int(rng.randint(int(0.05 * w), int(0.95 * w)))
            init_y = float(rng.uniform(0.0, max(1.0, 0.25 * h)))
            speed_px = float(rng.uniform(0.06 * h, 0.22 * h))
            width = int(1 + rng.randint(0, 2) + (1 if w > 1200 else 0))
            color_jitter = np.array([rng.uniform(0.85, 1.12), rng.uniform(0.85, 1.12), rng.uniform(0.85, 1.12)])

            '''
Считаем, сколько капля живёт. Если ещё не наступило время, или она уже умерла — пропускаем.
            '''
            life = t - start
            if life <= 0.0 or life > life_span:
                continue  # капля ещё не появилась или уже ушла

            # позиция капли (падает вниз)
            '''
Двигаем каплю вниз по экрану. Если дошла до дна — фиксируем на нижней границе.
            '''
            y_pos = init_y + speed_px * life
            if y_pos >= h - 1:
                y_pos = h - 1.0

            # хвост капли — длина растёт по жизни
            '''
Делаем хвост капли, он растёт с движением. y0 — верхняя точка хвоста, y1 — нижняя.
            '''
            tail_len = int(max(2, min(h * 0.22, 2 + speed_px * 0.03 * (0.6 + 0.9 * (life / life_span)))))
            y0 = int(max(0, y_pos - tail_len))
            y1 = int(min(h - 1, y_pos))

            # берём цвет из исходного кадра в верхней точке хвоста, чтобы капля "отрывалась" от кадра
            '''
Берём цвет кадра там, где капля начинается, чтобы выглядело органично.
Подмешиваем чуть шум с color_jitter.
            '''
            sample_y = int(max(0, min(h - 1, y0 + int(tail_len * 0.15))))
            sample_x = int(max(0, min(w - 1, x)))
            base_col = frame[sample_y, sample_x].astype(np.float32) / 255.0
            col = np.clip(base_col * color_jitter, 0.0, 1.0)
            color_bgr = (int(255 * col[0]), int(255 * col[1]), int(255 * col[2]))  # BGR tuple ints

            # непрозрачность капли: появляется, достигает пика, затем чуть гаснет
            '''
Считаем альфу (прозрачность) капли — сначала появляется, потом гаснет, чтобы не было резкого появления.
            '''
            life_norm = float(life / life_span)
            alpha_drop = float(np.clip(0.28 + 0.9 * (1.0 - abs(0.5 - life_norm) * 2.0), 0.10, 1.0) * progress)

            # рисуем хвост: основная линия (цвет), и маску с плавным alpha
            '''
Рисуем саму каплю в виде линии на overlay.
            '''
            cv2.line(overlay, (x, y0), (x, y1), color_bgr, thickness=width, lineType=cv2.LINE_AA)
            # рисуем блик на конце
            tip_r = max(1, int(1 + 2 * progress))
            cv2.circle(overlay, (x, y1), tip_r, (255, 255, 255), -1, lineType=cv2.LINE_AA)

            # на маску рисуем значение alpha (float32), можно рисовать несколько раз — суммируется
            # используем cv2.line на одноканальном изображении float32
            '''
Рисуем прозрачность на маске, чтобы потом аккуратно смешивать с оригиналом.
            '''
            alpha_val = float(alpha_drop)  # 0..1
            # рисуем основную часть хвоста с alpha
            cv2.line(mask, (x, y0), (x, y1), float(alpha_val), thickness=width + 1, lineType=cv2.LINE_AA)
            # добавим более сильный alpha в конце (блик)
            cv2.circle(mask, (x, y1), int(tip_r * 1.2), float(alpha_val * 1.1), -1, lineType=cv2.LINE_AA)

            # небольшой верхний "блик" чуть выше хвоста
            '''
Добавляем ещё один мини-блик чуть выше хвоста для блеска, чтобы капля выглядела живой.
            '''
            blink_y = int(max(0, y1 - max(1, int(tail_len * 0.18))))
            if 0 <= blink_y < h:
                cv2.circle(overlay, (x, blink_y), max(1, int(tip_r / 2)), color_bgr, -1, lineType=cv2.LINE_AA)
                cv2.circle(mask, (x, blink_y), max(1, int(tip_r / 2)), float(alpha_val * 0.6), -1, lineType=cv2.LINE_AA)

        # ограничиваем маску (0..1)
        '''
Убеждаемся, что альфа не больше 1 и не меньше 0.
        '''
        np.clip(mask, 0.0, 1.0, out=mask)

        # смешивание: out = base * (1 - mask) + overlay * mask
        # преобразуем mask в трёхканальный
        '''
Смешиваем оригинал с каплями по маске. Всё аккуратно, чтобы цвета не слетели.
        '''
        mask3 = mask[:, :, None]
        out = (base.astype(np.float32) * (1.0 - mask3) + overlay.astype(np.float32) * mask3)
        out = np.clip(out, 0, 255).astype(np.uint8)

        return out


    def neon_glitch(self, frame, t, duration):
        h, w = frame.shape[:2]
        '''
Здесь мы мутим силу глюка.
Начинаем с 20 и прибавляем ещё от 0 до 40
в зависимости от прогресса (t / duration).
То есть чем дальше по времени идём, тем сильнее эффект разносит картинку.
        '''
        glitch_strength = int(20 + 40 * (t / duration))
        new_frame = frame.copy()
        '''
Цикл. Будем идти по всей высоте картинки, но не по одному ряду, а прыжками.
Шаг прыжка — размер glitch_strength.
Короче, мы берём полосы через определённое расстояние.
        '''
        for i in range(0, h, glitch_strength):
            '''
Для каждой полосы решаем на сколько её сдвинуть влево или вправо.
Берём случайное число от -20 до +20 пикселей.
            '''
            shift = random.randint(-20, 20)
            '''
Вот тут вся магия:
Берём маленькую полоску высотой 5 пикселей (от i до i+5)
и сдвигаем её по горизонтали.
np.roll — это как взять картинку,
отрезать кусок и закинуть его в конец, получается сдвиг без дырок.
axis=1 — значит двигаем по ширине (влево-вправо).
            '''
            new_frame[i:i+5, :] = np.roll(new_frame[i:i+5, :], shift, axis=1)
            '''
Коммент для пацанов — дальше мы будем делать так,
чтоб картинка засияла как неоновые вывески в подвале у барыг.
            '''
        # добавим неон подсветку
        '''
Берём получившийся глючный кадр и прогоняем через цветовую карту COLORMAP_HOT.
Это делает картинку яркой, кислотной, с оранжево-красными неоновыми цветами.
Типа подсветка от ультрафиолета.
        '''
        glow = cv2.applyColorMap(new_frame, cv2.COLORMAP_HOT)
        '''
Финальный замес:
Берём два кадра — глючный (new_frame) и подсвеченный (glow).
Смешиваем их: 70% оригинала + 30% неоновой подсветки.
Последний ноль — это сдвиг яркости (нам тут не нужен).
В итоге получаем глюк с яркой кислотной аурой.
        '''
        return cv2.addWeighted(new_frame, 0.7, glow, 0.3, 0)

    # 2. Hologram flicker
    def hologram_flicker44(self, frame, t, duration,
                       n_stripes=12,
                       swap_interval=0.6,
                       glitch_duration=0.12,
                       glitch_prob=0.35,
                       max_shift_px=18,
                       tint_strength=0.28,
                       seam_blend=2,
                       neon_color=(0.1, 0.9, 1.0),
                       neon_strength=0.22,
                       neon_power=2.0,
                       neon_intensity=1.2,
                       glow_radius_px=18,
                       glow_downscale=0.28,
                       chroma_shift_px=4,
                       chroma_speed=6.0,
                       scanline_strength=0.03,
                       grain_strength=0.04,
                       stutter_chance_per_sec=0.8,
                       stutter_duration=0.08,
                       stutter_blend=0.12,
                       posterize_levels=32
                           ):
        '''
n_stripes=12,
swap_interval=0.6,
glitch_duration=0.12,
glitch_prob=0.35,
max_shift_px=18,
tint_strength=0.28,
seam_blend=2,
Это параметры для полосок и глитчей.
Типа сколько полос, как часто они будут меняться,
с какой вероятностью багнутся и насколько сильно будут смещаться.
neon_color=(0.1, 0.9, 1.0),
neon_strength=0.22,
neon_power=2.0,
neon_intensity=1.2,
glow_radius_px=18,
glow_downscale=0.28,
Настройки неонового свечения: цвет, мощность,
сила свечения, радиус размытия и уменьшение картинки для эффекта.
Короче, чтоб как в киберпанке.
chroma_shift_px=4,
chroma_speed=6.0,
scanline_strength=0.03,
grain_strength=0.04,
stutter_chance_per_sec=0.8,
stutter_duration=0.08,
stutter_blend=0.12,
posterize_levels=32
Тут глобальные настройки: цветовой сдвиг каналов,
сила сканлайнов как на старом телике, плёнка с зерном,
вероятность зависания кадра (stutter),
его длительность и сглаживание, плюс постеризация (уменьшение цветов).
        '''
        # ----- подготовка состояния -----
        h, w = frame.shape[:2]
        '''
Проверка: если у объекта ещё не было сохранённых данных,
то создаём хранилище.
Типа предыдущий кадр,
момент до какого времени мы "зависаем", и кадр,
который надо показывать во время зависона.
        '''
        if not hasattr(self, '_hf44_prev_frame'):
            self._hf44_prev_frame = frame.copy()
            self._hf44_stutter_until = 0.0
            self._hf44_last_stutter_check = 0.0
            self._hf44_stutter_frame = frame.copy()

        '''
Ща делаем эффект лагов:
типа завис кадр на пару миллисекунд, как будто видео тормозит.
        '''
        # Решаем, сгенерировать ли короткий freeze/stutter (детерминированно по времени)
        # Проверяем шанс примерно каждый 1/swap_interval для разумной частоты
        '''
Берём текущее время.
        '''
        now = t
        # если прошло достаточно с последней проверки — потенциально запускаем stutter
        '''
Тут чувак хотел сделать проверку с интервалом,
но по факту — это фиктивная заглушка. Просто чтоб код не упал.
        '''
        check_dt = max(0.01, 1.0 / max(1.0, 1.0))
        # проверяем возможность старта stutter
        '''
Если прошло больше чем 0.05 сек с последней проверки
— пора снова кидать кубик, будет ли зависон.
        '''
        if now - self._hf44_last_stutter_check > 0.05:
            '''
Считаем вероятность зависона за этот промежуток.
Чем дольше прошло — тем больше шанс.
            '''
            prob = 1.0 - math.exp(-stutter_chance_per_sec * (now - self._hf44_last_stutter_check))
            # используем целочисленный индекс интервала как seed (без побочных типов)
            '''
Берём индекс интервала по времени
и используем его как сид для рандома.
Типа, чтоб глюки были детерминированные, а не каждый запуск разные.
            '''
            interval_idx = int(math.floor(now / swap_interval)) if swap_interval > 1e-9 else 0
            seed = interval_idx & 0xffffffff
            rng_check = np.random.RandomState(seed=seed)
            '''
Если повезло (рандом < вероятность),
то запускаем зависон: замораживаем кадр до now + stutter_duration.
            '''
            if rng_check.rand() < prob:
                self._hf44_stutter_until = now + stutter_duration
                self._hf44_stutter_frame = self._hf44_prev_frame.copy()
                '''
Обновляем время последней проверки.
                '''
            self._hf44_last_stutter_check = now

        '''
Если мы ещё в зоне зависона — ставим флаг 1. Иначе 0.
        '''
        if now < self._hf44_stutter_until:
            stutter_t = 1.0
        else:
            stutter_t = 0.0
            '''
Тут делаем плавный вход/выход из зависона. Типа не резкий обруб, а мягко.
            '''
        if stutter_blend > 1e-6:
            start = self._hf44_stutter_until - stutter_duration
            if start < now < start + stutter_blend:
                stutter_t = (start + stutter_blend - now) / stutter_blend
                stutter_t = np.clip(stutter_t, 0.0, 1.0)

        '''
Если зависон активный — берём старый кадр. Если нет — нормальный кадр.
        '''
        if stutter_t > 0.5:
            base = self._hf44_stutter_frame.copy()
        else:
            base = frame.copy()
        '''
Обновляем предыдущий кадр, чтоб в следующий раз было что залипать.
        '''
        self._hf44_prev_frame = frame.copy()

        '''
Переводим картинку в float от 0 до 1, чтоб легче эффекты мутить.
        '''
        base_f = base.astype(np.float32) / 255.0

        '''
дальше идёт "цветовой аберрации" эффект — типа разноцветные ореолы по краям.
Считаем горизонтальный сдвиг каналов.
Берём синус от времени,
умножаем на скорость (chroma_speed)
и на максимальное смещение (chroma_shift_px).
        '''
        csx = int(round(math.sin(t * chroma_speed) * chroma_shift_px))
        '''
А это вертикальный сдвиг, но меньше.
Косинус по времени, скорость поменьше, чтобы не всё одинаково прыгало.
        '''
        csy = int(round(math.cos(t * (chroma_speed * 0.7)) * (chroma_shift_px // 2)))
        '''
сдвигать пиксели с помощью np.roll — это быстрая тема.
Двигаем синий канал ([...,0]) вправо/влево на csx.
        '''
        bch = np.roll(base_f[..., 0], csx, axis=1)
        '''
Зелёный двигаем чуть меньше, чтоб картинка не совсем поехала.
        '''
        gch = np.roll(base_f[..., 1], -csx//2, axis=1)
        '''
Красный двигаем в противоположку синему, чтоб дикая аберрация была.
        '''
        rch = np.roll(base_f[..., 2], -csx, axis=1)
        '''
Складываем каналы обратно в одно изображение.
        '''
        base_f = np.stack([bch, gch, rch], axis=2)

        '''
Теперь добавим мелкий рандом по строкам, чтоб было больше "дрожи".
Определяем номер текущего интервала,
чтоб сид для рандома всегда был одинаков в рамках интервала.
        '''
        interval_idx = int(math.floor(t / swap_interval)) if swap_interval > 1e-9 else 0
        '''
Создаём генератор случайных чисел, привязанный к этому сидy.
        '''
        rng = np.random.RandomState(seed=(interval_idx & 0xffffffff))
        '''
Для каждой строки картинки берём случайный сдвиг от -2 до 2 пикселей.
        '''
        per_row_offsets = (rng.randint(-2, 3, size=(h,))).astype(np.int32)
        '''
Цикл: для каждой строки зелёного канала
двигаем её вверх/вниз на off. Если off=0, оставляем.
        '''
        for row in range(h):
            off = per_row_offsets[row]
            if off != 0:
                gch[row] = np.roll(gch[row], off, axis=0)
                '''
Возвращаем обновлённый зелёный канал в картинку.
                '''
        base_f[...,1] = gch

        '''
Теперь делаем "сканлайны" как на старых телеках и добавляем мигание контраста.
Строим массив от 0 до 1 по высоте кадра, для расчёта полос.
        '''
        rows = np.arange(h, dtype=np.float32)[:, None] / max(1.0, h)
        '''
Формируем паттерн тёмных полос: синус с высокой частотой,
чтобы как на ЭЛТ-экране.
        '''
        scan = 1.0 - scanline_strength * (0.5 + 0.5 * np.sin(rows * 2.0 * math.pi * 240.0 + t * 60.0))
        '''
Умножаем картинку на сканлайны. То есть добавляем вертикальные полосы.
        '''
        base_f = np.clip(base_f * scan[..., None], 0.0, 1.0)

        '''
Делаем лёгкое мигание контраста — синус на 16 Гц.
        '''
        flick = 0.97 + 0.06 * math.sin(t * 16.0)
        '''
Нормализуем картинку вокруг 0.5,
умножаем на коэффициент мигания и возвращаем обратно.
        '''
        base_f = np.clip((base_f - 0.5) * (1.0 + 0.15*(flick-1.0)) + 0.5, 0.0, 1.0)

        '''
Если выбрано количество уровней постеризации больше 2 — включаем эффект.
        '''
        if posterize_levels is not None and posterize_levels > 2:
            '''
Берём число уровней как float.
            '''
            levels = float(posterize_levels)
            '''
Обрезаем значения до дискретных уровней (квантование).
            '''
            base_f = np.floor(base_f * levels) / (levels - 1.0)
            '''
Подрезаем, чтоб значения остались в пределах [0..1].
            '''
            base_f = np.clip(base_f, 0.0, 1.0)

        '''
Если сила шума больше нуля — добавляем плёночное зерно.
        '''
        if grain_strength > 1e-6:
            '''
Создаём генератор случайных чисел,
сидим его временем (каждую миллисекунду разный).
            '''
            noise_rng = np.random.RandomState(seed=int((t*1000) % 2**31))
            '''
Делаем шум с нормальным распределением
для каждой точки кадра, умножаем на силу шума.
            '''
            noise = noise_rng.randn(h, w).astype(np.float32) * grain_strength
            '''
Считаем яркость пикселя как взвешенную сумму каналов (BT.601).
            '''
            lum = base_f[...,0]*0.114 + base_f[...,1]*0.587 + base_f[...,2]*0.299  # (h,w)

            # приведение noise к (h,w,1), затем корректное умножение и прибавление
            '''
Добавляем шум, зависящий от яркости: на светлых местах шум сильнее.
            '''
            base_f += noise[..., None] * (0.5 + lum[..., None])
            '''
Опять ограничиваем всё в [0..1].
            '''
            base_f = np.clip(base_f, 0.0, 1.0)

        '''
Теперь делаем мясо: делим картинку на полоски и перемешиваем их.
Считаем высоту каждой полоски.
        '''
        stripe_h = max(1, h // n_stripes)
        '''
Переводим картинку обратно в uint8, чтоб с ней мутить.
        '''
        out = (base_f * 255.0).astype(np.uint8)

        '''
Фаза внутри интервала: где мы сейчас между заменами полос.
        '''
        phase_in = (t % swap_interval) / swap_interval if swap_interval > 1e-9 else 0.0
        '''
Проверяем: глюк сейчас активен или нет (по времени).
        '''
        is_glitch_active = (phase_in * swap_interval) < glitch_duration

        '''
Создаём список индексов полос (0,1,2,…).
        '''
        src_indices = np.arange(n_stripes, dtype=int)
        '''
Создаём ещё один рандом, тоже сидим его интервалом.
        '''
        rng2 = np.random.RandomState(seed=interval_idx & 0xffffffff)

        '''
Будем хранить тут полосы, которые реально поменялись местами.
        '''
        swapped_set = set()
        '''
Если глюк активен — выбираем случайные полосы,
которые будут участвовать в свапе.
        '''
        if is_glitch_active:
            candidates = [i for i in range(n_stripes) if rng2.rand() < glitch_prob]
            '''
Перемешиваем кандидатов и делаем,
чтоб их было чётное число (иначе одна останется лишней).
            '''
            if len(candidates) >= 2:
                rng2.shuffle(candidates)
                if len(candidates) % 2 == 1:
                    candidates = candidates[:-1]
                    '''
Свапаем полосы попарно.
                    '''
                for k in range(0, len(candidates), 2):
                    a = candidates[k]; b = candidates[k+1]
                    src_indices[a], src_indices[b] = src_indices[b], src_indices[a]
                    '''
Запоминаем, какие полосы были замешаны.
                    '''
                swapped_set = set(candidates)

        '''
Проходимся по каждой полосе: считаем её верх и низ.
        '''
        for i in range(n_stripes):
            y0 = i * stripe_h
            y1 = (i + 1) * stripe_h if i < n_stripes - 1 else h

            '''
Берём источник для этой полосы (вдруг она была свапнута).
            '''
            src_i = src_indices[i]
            sy0 = src_i * stripe_h
            sy1 = (src_i + 1) * stripe_h if src_i < n_stripes - 1 else h

            '''
Вырезаем исходную полоску.
            '''
            stripe = out[sy0:sy1].copy()


            '''
Если полоса была свапнута, начинаем её модифицировать.
            '''
            if i in swapped_set:
                s = stripe.astype(np.float32) / 255.0
                '''
Двигаем полоску вбок случайно.
                '''
                shift = int(rng2.randint(-max_shift_px, max_shift_px + 1))
                if shift != 0:
                    s = np.roll(s, shift, axis=1)
                '''
Красим полоску в другой оттенок (больше синевы).
                '''
                tint = np.array([1.0 - tint_strength * 0.4,
                                 1.0 - tint_strength * 0.1,
                                 1.0 + tint_strength], dtype=np.float32)
                s *= tint
                '''
Ещё по каналам раздвигаем пиксели, чтоб выглядело рвано.
                '''
                b = np.roll(s[..., 0],  int(rng2.randint(-3, 4)), axis=1)
                g = np.roll(s[..., 1],  int(rng2.randint(-2, 3)), axis=1)
                r = np.roll(s[..., 2],  int(rng2.randint(-4, 5)), axis=1)
                '''
Собираем полоску обратно и обрезаем значения.
                '''
                s2 = np.stack([b, g, r], axis=2)
                stripe_out = (np.clip(s2, 0.0, 1.0) * 255.0).astype(np.uint8)
                '''
Если полоса обычная — оставляем как есть.
                '''
            else:
                stripe_out = stripe
                '''
Возвращаем полоску на её место.
                '''
            out[y0:y1] = stripe_out

        '''
Теперь делаем сглаживание границ между полосами.
Если включено сглаживание — берём ширину размытия.
        '''
        if seam_blend and seam_blend >= 1:
            bw = int(seam_blend)
            '''
Для каждой границы между полосами берём кусок вокруг неё.
            '''
            for i in range(1, n_stripes):
                y = i * stripe_h
                y0 = max(0, y - bw)
                y1 = min(h, y + bw)
                if y1 <= y0:
                    continue
                '''
Размываем этот кусок по вертикали.
                '''
                region = out[y0:y1].astype(np.float32)
                kernel_h = max(3, (y1 - y0) | 1)
                blurred = cv2.GaussianBlur(region, (1, kernel_h), 0)
                '''
Создаём градиент от 0 до 1 по высоте.
                '''
                region_h = y1 - y0
                alpha = np.linspace(0.0, 1.0, region_h, dtype=np.float32)[:, None, None]
                '''
Смешиваем оригинал и размытие, получаем плавный переход.
                '''
                blended = region * (1.0 - alpha) + blurred * alpha
                '''
Возвращаем сглаженный кусок обратно.
                '''
                out[y0:y1] = np.clip(blended, 0, 255).astype(np.uint8)

        '''
Включаем неоновое свечение.
Переводим картинку снова в float.
        '''
        if neon_strength > 1e-4:
            out_f = out.astype(np.float32) / 255.0
            '''
Считаем яркость пикселей.
            '''
            lum = out_f[..., 0] * 0.114 + out_f[..., 1] * 0.587 + out_f[..., 2] * 0.299
            '''
Создаём маску свечения: яркие места будут светиться сильнее.
            '''
            mask = np.clip((lum ** neon_power) * neon_intensity, 0.0, 1.0)
            '''
Красим маску в неоновый цвет.
            '''
            neon_col = np.array(neon_color, dtype=np.float32).reshape((1,1,3))
            base_overlay = (mask[..., None] * neon_col)

            '''
Считаем размеры уменьшенной копии кадра, чтоб быстро размывать.
            '''
            ds = float(max(0.08, min(0.6, glow_downscale)))
            small_w = max(2, int(w * ds))
            small_h = max(2, int(h * ds))
            '''
Уменьшаем, размываем и готовим основу для свечения.
            '''
            small = cv2.resize(base_overlay, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
            sigma = max(0.6, glow_radius_px * ds)
            small_blurred = cv2.GaussianBlur(small, (0,0), sigmaX=sigma, sigmaY=sigma)
            '''
Возвращаем размытый свет обратно в исходный размер.
            '''
            glow = cv2.resize(small_blurred, (w, h), interpolation=cv2.INTER_LINEAR)

            '''
Прибавляем свечение к картинке.
            '''
            out_f = np.clip(out.astype(np.float32)/255.0 + glow * neon_strength, 0.0, 1.0)
            '''
Лёгкий общий оттенок неонового цвета поверх.
            '''
            tint_overlay = neon_col * 0.03
            out_f = np.clip(out_f * (1.0 - 0.03) + tint_overlay * 0.03, 0.0, 1.0)
            '''
Возвращаем результат в uint8.
            '''
            out = (out_f * 255.0).astype(np.uint8)
            '''
Отдаём финальную картинку с глюками, шумом, полосами и неоном.
            '''
        return out


    '''
💬 Тут мы мутим метод под эффект «Матрицы». На вход:

frame — картинка (типа кадр видоса),

t — время, сколько прошло,

duration — сколько вся движуха длится,

spacing — через какое расстояние колонки букв падают,

font_scale, base_thickness — чё за размер и толщина текста,

charset — набор символов, если не задали — сами сделаем.
    '''
    def matrix_digital_rain(self, frame, t, duration,
                        spacing=20, font_scale=0.5, base_thickness=1, charset=None):
        """
        Метод класса. Хранит своё состояние в self._matrix_state.
        frame: BGR numpy array
        t: время (сек)
        duration: общее время (сек)
        """
        '''
Подтягиваем модуль string, там всякие буковки и цифры на халяву.
        '''
        import string

        h, w = frame.shape[:2]

        # инициализация состояния в self
        '''
Тут хитро — эффект должен помнить,
какие у него колонки уже есть.
Поэтому если ещё не было self._matrix_state,
мы заводим пустой словарь. А потом юзаем его как state.
        '''
        if not hasattr(self, '_matrix_state'):
            self._matrix_state = {}
        state = self._matrix_state


        
        '''
Если чувак не дал свой набор символов,
мы берём цифры, буковки и пару спецзнаков, чтобы красиво падали, как в фильме.
        '''
        if charset is None:
            charset = list("01" + string.ascii_letters + string.digits + "@#$%&*")

        # (пере)инициализация колонок при изменении размера или spacing
        '''
Проверяем: если колонок ещё не было, или размер кадра поменялся,
или расстояние между колонками другое — значит, надо всё заново нарисовать.
        '''
        if ('cols' not in state) or state.get('size') != (w, h) or state.get('spacing') != spacing:
            '''
Тут мутим сами колонки:

x — где колонка будет по горизонтали,

y — откуда сверху начинает падать (может даже из-за экрана),

speed — скорость падения,

trail — сколько символов в хвосте,

chars — массив случайных символов,

offset — сдвиг, чтоб анимация не одинаковая была.
И всё это складываем в список cols.
            '''
            cols = []
            for x in range(0, w, spacing):
                speed = random.uniform(0.6, 2.0)
                trail = random.randint(6, 20)
                y = random.randint(-h, 0)
                chars = [random.choice(charset) for _ in range(max(30, trail + 10))]
                cols.append({'x': int(x), 'y': float(y), 'speed': speed, 'trail': trail,
                             'chars': chars, 'offset': random.uniform(0, len(chars))})
                '''
Запоминаем колонки и параметры в state, чтоб не пересоздавать каждый раз.
                '''
            state['cols'] = cols
            state['size'] = (w, h)
            state['spacing'] = spacing

            '''
Достаём готовые колонки.
            '''
        cols = state['cols']

        # прогресс и коэффициенты усиления
        '''
Считаем, сколько времени прошло (progress от 0 до 1).
Чем дальше, тем быстрее и ярче всё падает:

speed_boost — ускоряем скорость падения,

trail_boost — хвосты делаем длиннее,

bright_boost — светим ярче.
        '''
        progress = float(np.clip(t / max(1e-6, duration), 0.0, 1.0))
        speed_boost = 1.0 + 3.0 * progress
        trail_boost = 1.0 + 2.0 * progress
        bright_boost = 0.5 + 1.5 * progress

        '''
Создаём пустую чёрную картинку, на ней будем рисовать буквы.
        '''
        overlay = np.zeros_like(frame)

        '''
Определяем шрифт и размер символа.
vstep — вертикальный шаг, через сколько пикселей вниз рисовать следующую букву.
        '''
        font = cv2.FONT_HERSHEY_SIMPLEX
        (tw, th), _ = cv2.getTextSize("0", font, font_scale, base_thickness)
        vstep = max(12, th + 2)

        '''
Проходим по всем колонкам и двигаем их вниз со скоростью
        '''
        for col in cols:
            col['y'] += col['speed'] * speed_boost

            '''
Иногда случайно меняем скорость, чтоб всё не было одинаковое.
            '''
            if random.random() < 0.01:
                col['speed'] = max(0.3, col['speed'] + random.uniform(-0.3, 0.5))

                '''
Если колонка полностью ушла за экран вниз — возрождаем её сверху с новыми параметрами.
                '''
            if col['y'] - col['trail'] * vstep > h:
                col['y'] = random.randint(-h // 2, 0)
                col['speed'] = random.uniform(0.6, 2.0)
                col['trail'] = random.randint(6, 20)
                col['chars'] = [random.choice(charset) for _ in range(max(30, col['trail'] + 10))]
                col['offset'] = random.uniform(0, len(col['chars']))

                '''
Голова колонки (head_y) и сколько символов у неё в хвосте с учётом буста.
                '''
            head_y = int(col['y'])
            trail_len = max(1, int(col['trail'] * trail_boost))

            '''
Перебираем символы в хвосте. Если символ ушёл за экран — пропускаем.
            '''
            for i in range(trail_len):
                y = head_y - i * vstep
                if y < -vstep or y > h + vstep:
                    continue

                '''
Выбираем, какой символ рисовать в этой позиции. Координата x фиксированная для всей колонки.
                '''
                ch_idx = int((i + int(col['offset'])) % len(col['chars']))
                ch = col['chars'][ch_idx]
                x = int(col['x'])

                '''
Считаем прозрачность и яркость: чем дальше от головы, тем бледнее буква.
                '''
                rel = i / max(1, trail_len - 1)
                alpha = (1.0 - rel) ** 1.5
                alpha *= bright_boost
                alpha = float(np.clip(alpha, 0.05, 1.0))

                '''
Цвет символа — зелёный, яркость зависит от alpha.
                '''
                g_val = int(np.clip(60 + 195 * alpha, 0, 255))
                color = (0, g_val, 0)

                '''
Если это голова колонки (i == 0), то рисуем её жирно: чёрная обводка и яркий зелёно-фиолетовый цвет.
Если хвост — просто чёрная тень + зелёная буква.
                '''
                if i == 0:
                    cv2.putText(overlay, ch, (x, y), font, font_scale, (0, 0, 0), 3, cv2.LINE_AA)
                    head_green = int(np.clip(200 + 55 * progress, 0, 255))
                    cv2.putText(overlay, ch, (x, y), font, font_scale, (0, head_green, 200), 1, cv2.LINE_AA)
                else:
                    cv2.putText(overlay, ch, (x, y), font, font_scale, (0, 0, 0), 2, cv2.LINE_AA)
                    cv2.putText(overlay, ch, (x, y), font, font_scale, color, 1, cv2.LINE_AA)

                    '''
Двигаем оффсет, чтоб символы в колонке менялись со временем.
                    '''
            col['offset'] += 0.25 + 0.75 * progress
            if col['offset'] > len(col['chars']):
                col['offset'] -= len(col['chars'])

        out = cv2.addWeighted(frame, 0.65, overlay, 0.95, 0)
        return out


    # 4. CRT wave distortion
    def crt_wave_distortion(self, frame, t, duration):
        h, w = frame.shape[:2]

        # Быстрые координаты как 2D через broadcasting (чтобы не создавать два полноразмерных массива отдельно)
        '''
Это координаты пикселей.
y — вертикаль (от 0 до h-1), столбик.
x — горизонталь (от 0 до w-1), строка.
С [:, None] и [None, :] делаем их двумерными для удобного «броадкаста», чтоб потом красиво складывать.
        '''
        y = np.arange(h, dtype=np.float32)[:, None]   # (h,1)
        x = np.arange(w, dtype=np.float32)[None, :]   # (1,w)

        # Параметры эффектов (регулируй для более/менее выраженного глитча)
        '''
Это настройки «волны»:

amp_main — сила основного искажения,

amp_secondary — слабее доп. колебания,

freq1, freq2 — частоты (как часто волны повторяются по высоте),

time_speed1, time_speed2 — как быстро колбасит по времени.
        '''
        amp_main = 16.0                   # основная амплитуда горизонтального сдвига
        amp_secondary = 8.0               # вторая частота
        freq1 = 0.018                     # частота 1 (по Y)
        freq2 = 0.055                     # частота 2 (по Y)
        time_speed1 = 3.0
        time_speed2 = 6.0

        # Лёгкий периодический шум (коэрс-уровень по высоте, интерполируется) — дешёвая имитация «шумовых полос»
        rng = np.random.RandomState(int(t * 1000) & 0xFFFF)
        '''
Определяем, сколько «шумовых полос» будет сверху вниз.
Берём максимум: либо 4, либо h/20.
        '''
        coarse_n = max(4, h // 20)
        '''
Генерим случайные числа от -1 до 1, столько сколько coarse_n.
Это как «базовые шумовые точки».
        '''
        coarse = rng.uniform(-1.0, 1.0, size=(coarse_n,))
        '''
Создаём координаты X для этих шумов: равномерно от 0 до высоты.
        '''
        xp = np.linspace(0, h - 1, coarse_n)
        '''
Интерполируем шум: растягиваем случайные точки на всю высоту картинки.
Получаем плавный шум по Y.
        '''
        noise_y = np.interp(np.arange(h), xp, coarse).astype(np.float32)[:, None]  # (h,1)
        '''
Коэффициент, насколько сильно этот шум будет влиять.
        '''
        noise_amp = 3.0

        # Горизонтальные (X) смещения: суммируем несколько синусов + шум по Y, небольшой фазовый сдвиг по X для текстуры
        '''
Вот тут начинаем колбасить X-смещения:

первая синусоида — основная волна по Y,

вторая — более мелкая волна, зависящая и от Y, и от X (чтоб текстура живая была),

домножаем кое-где на доп. синус, чтоб волна ещё и «пульсировала».
        '''
        dx = (amp_main * np.sin(2.0 * np.pi * freq1 * y + t * time_speed1) +
              amp_secondary * np.sin(2.0 * np.pi * freq2 * y * 0.6 + t * time_speed2 + x * 0.01) * (1.0 + 0.4 * np.sin(y * 0.12 + t * 1.5)))
        '''
Добавляем сверху наш шум, чтоб волна была грязной, а не ровной.
        '''
        dx += noise_amp * noise_y  # растянуть шум по ширине за счёт broadcast

        # Вертикальные (Y) небольшие искажения для «tear» эффекта
        '''
Тут делаем Y-смещения (вертикальные).
Типа «разрывы» на старых телеках.
vert_amp регулирует силу, синус делает волны по горизонтали, плюс добавляем шум.
        '''
        vert_amp = 2.2
        dy = vert_amp * np.sin(x * 0.02 + t * 2.2) + 0.4 * noise_y

        # Собираем карты remap (OpenCV ожидает float32)
        '''
Готовим карты для cv2.remap.
Они говорят OpenCV, куда каждый пиксель сдвигать.
        '''
        map_x = (x + dx).astype(np.float32)
        map_y = (y + dy).astype(np.float32)

        # Хроматическая аберрация: смещаем цветовые каналы по X/Y чуть по-разному
        # Небольшие значения — «стильно», не разрушает картинку и не нагружает сильно
        '''
Это для хроматической аберрации (разъезжания цветов).
Для каждого канала (синий, зелёный, красный) смещения по X и Y разные.
        '''
        ch_offsets = [
            (0.0, 0.0),    # B
            (1.2, -0.6),   # G
            (-1.6, 0.8)    # R
        ]

        # Разделим каналы, применим remap к каждому и сойдем обратно
        '''
Проверка: если картинка цветная (3 канала), делаем аберрацию.
        '''
        if frame.ndim == 3 and frame.shape[2] == 3:
            '''
Разбиваем картинку на три канала: b, g, r.
Создаём список для новых каналов.
            '''
            b, g, r = cv2.split(frame)
            remapped = []
            '''
Для каждого канала:

сдвигаем карту X и Y на своё смещение,

cv2.remap реально двигает пиксели по этим картам,

добавляем результат в список.
            '''
            for (ox, oy), ch in zip(ch_offsets, (b, g, r)):
                mx = (map_x + ox).astype(np.float32)
                my = (map_y + oy).astype(np.float32)
                rem = cv2.remap(ch, mx, my, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
                remapped.append(rem)
                '''
Склеиваем три канала обратно в цветное изображение.
                '''
            out = cv2.merge(remapped)
            '''
Если картинка чёрно-белая, то делаем ремап один раз, без разделения каналов.
            '''
        else:
            # для серых изображений — один remap
            out = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        # Лёгкие сканлайны/CRT-шумы по строкам
        '''
Делаем «сканлайны» — полоски, как на старом телике.
Это синусоида по высоте, которая колеблет яркость строк.
        '''
        scan_amp = 0.08
        scan = (1.0 - scan_amp * (0.5 + 0.5 * np.sin((np.arange(h, dtype=np.float32)[:, None] / 2.0) + t * 12.0)))
        # Применяем к каждой компоненте (broadcast по ширине и каналам)
        '''
Применяем сканлайны к картинке.

умножаем картинку на коэффициенты,

обрезаем значения в диапазон 0–255,

делаем uint8 (обычные пиксели).
        '''
        out = (out.astype(np.float32) * scan).clip(0, 255).astype(np.uint8)

        '''
Возвращаем готовый кадр с эффектом «старый телик глючит».
        '''
        return out

    # 5. Neon edge glow
    def neon_edge_glow(self, frame, t=0.0, duration=1.0):
        '''
Подсказка: кадр у нас в формате OpenCV — трёхканальный (BGR), и каждый канал 8-битный.
        '''
        # frame: BGR uint8
        h, w = frame.shape[:2]

        # 1) Контуры: Canny + утолщение
        '''
Переводим картинку в ч/б, потому что для контуров цвет нахрен не нужен.
        '''
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        '''
Запускаем детектор контуров Канни:
ищем границы, где резкий перепад яркости.
Пороги — 80 и 180. Чем меньше, тем больше лишнего шума.
        '''
        edges = cv2.Canny(gray, 80, 180)  # можно тонко подбирать пороги
        '''
Создаём ядро-форму 3х3 в виде эллипса — будем им «мазать» контуры.
        '''
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        '''
Берём контур и два раза его «раздуваем». Линии становятся жирнее.
        '''
        edges = cv2.dilate(edges, kernel, iterations=2)  # утолщаем контур
        '''
Переводим картинку с контурами в маску True/False. Где контур — там True.
        '''
        edge_mask = edges.astype(bool)

        # 2) Сглаживание/упрощение цветов (speed-friendly cartoon look)
        # Понижаем разрешение, применяем быстрый фильтр, апскейлим
        '''
Уменьшаем картинку в два раза, чтоб быстрее обрабатывать.
        '''
        small = cv2.resize(frame, (w // 2, h // 2), interpolation=cv2.INTER_LINEAR)
        # Билатеральный фильтр даёт «пластиковую» заливку, но один проход — не слишком дорого
        '''
Пропускаем через билатеральный фильтр: он размывает, но сохраняет края.
В итоге картинка становится «пластиковая» как в мультяшках.
        '''
        small = cv2.bilateralFilter(small, d=7, sigmaColor=60, sigmaSpace=60)
        '''
Возвращаем обратно в нормальный размер. И переводим в float32 с нормализацией (0–1).
        '''
        base = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0

        # 3) Posterize (несколько уровней цвета) — простой и быстрый
        '''
Говорим: у нас будет всего 5 уровней цвета.
        '''
        levels = 5
        '''
Огрубляем цвета — типа постеризация. Больше нет плавных переходов, только ступеньки.
        '''
        base = np.floor(base * levels) / levels

        # 4) Придушение насыщенности и затемнение (мрачный вид)
        # немного смешаем с серым
        '''
Снова делаем ч/б версию из нашей обработанной картинки. В float от 0 до 1.
        '''
        gray_full = cv2.cvtColor((base * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        '''
Смешиваем цвет с серым, чтоб картинка стала более тусклая, мрачная.
        '''
        base = base * 0.65 + gray_full[..., None] * 0.35

        # Контраст/яркость (тонко)
        '''
Чуть добавляем контраст и уменьшаем яркость.
        '''
        contrast = 1.05
        brightness = 0.9
        '''
Вычисляем контраст+яркость. clip режет значения, чтоб не вылезли за 0–1.
        '''
        base = np.clip((base - 0.5) * contrast + 0.5, 0.0, 1.0) * brightness

        # 5) Усиление теней (делаем мрачнее низкие значения)
        '''
Берём готовую яркость из серой версии.
        '''
        luma = gray_full  # уже есть
        '''
Формируем маску: чем темнее пиксель, тем сильнее он попадает в «тень».
        '''
        shadow_mask = np.clip(1.0 - luma * 1.2, 0.0, 1.0)
        '''
Умножаем на коэффициент, тем самым делаем тёмные зоны ещё мрачнее.
        '''
        base = base * (1.0 - 0.28 * shadow_mask[..., None])

        # 6) Виньетка (простая, дешёвая)
        '''
Создаём сетку координат: от -1 до 1 по X и Y. Типа радиальные координаты.
        '''
        yy = np.linspace(-1.0, 1.0, h)[:, None]
        xx = np.linspace(-1.0, 1.0, w)[None, :]
        '''
Считаем круглую маску. Центр яркий, края темнее.
        '''
        vign = 1.0 - np.clip((xx**2 + yy**2), 0.0, 1.0)
        '''
Накладываем виньетку — по краям темнеет почти на 55%.
        '''
        vign_strength = 0.55
        base = base * (1.0 - (1.0 - vign) * vign_strength)[..., None]

        # 7) Наложение чёрных контуров (толстые линии мультяшного стиля)
        '''
Копируем основу, чтобы туда уже рисовать.
        '''
        out = base.copy()
        # делаем контур действительно чёрным (или почти чёрным, чтобы не сжечь детали)
        '''
В местах, где у нас контуры, заливаем их почти чёрным цветом (чуть серым, чтоб не убить мелочи).
        '''
        out[edge_mask] = np.array([0.02, 0.02, 0.02], dtype=np.float32)

        # 8) Лёгкий шум/зерно для атмосферы
        '''
Определяем силу шума. Маленькая, чтоб просто лёгкая зернистость.
        '''
        grain_strength = 0.02
        '''
Генерим шум (нормальное распределение) на всю картинку
        '''
        noise = np.random.randn(h, w, 1).astype(np.float32) * grain_strength
        '''
Добавляем шум к картинке, но режем значения, чтоб не вылезли за 0–1. Атмосферно.
        '''
        out = np.clip(out + noise, 0.0, 1.0)

        # 9) Вернуть BGR uint8
        return (out * 255).astype(np.uint8)

    # 6. Smoke screen dissolve
    def smoke_screen_dissolve(self, frame, t, duration):
        
        # минимальное приведение входа
        '''
Берём frame и превращаем его в массив NumPy,
даже если он изначально был чем-то другим.
Типа: "давай без фокусов, всё в нормальный массив".
        '''
        frame = np.asarray(frame)
        '''
Если картинка не в типе uint8 (а это стандарт для пикселей: 0–255),
то принудительно переводим. Без копий, чтоб память не хавало.
        '''
        if frame.dtype != np.uint8:
            frame = frame.astype(np.uint8, copy=False)

        # безопасно получить скалярные t и duration (поддержка length-1 arrays)
        '''
Короче, берём t и duration, даже если это массивы с одним числом — выковыриваем скаляр.
progress — это сколько процентов эффекта прошло: 0 — начало, 1 — конец.
max(1e-8, d_val) нужен, чтоб деления на ноль не случилось (чисто страховка).
np.clip ограничивает результат в рамках 0.0–1.0, типа не выйдешь за границы.
        '''
        t_val = float(np.ravel(t)[0])
        d_val = float(np.ravel(duration)[0])
        progress = np.clip(t_val / max(1e-8, d_val), 0.0, 1.0)

        '''
Высота и ширина картинки. Потом создаём генератор случайных чисел rng,
инициализируем его хитрым сидом: прогресс * миллион, размер кадра.
Так рандом будет «детерминированный» — один и тот же при одинаковых условиях.
        '''
        h, w = frame.shape[:2]
        rng = np.random.default_rng(int(progress * 1e6) ^ (h<<16) ^ w)

        # случайная маска появления эффекта
        '''
Делаем шум от 0 до 1 размером как картинка.
Потом смотрим: если шум меньше прогресса — пиксель в эффекте.
Чем больше прогресс, тем больше «дыма» проявляется.
        '''
        noise = rng.random((h, w))
        appear_mask = noise < progress   # shape (H, W)

        # рабочая копия в float32
        '''
Берём копию картинки, переводим в float32,
чтоб удобнее считать и эффекты накладывать (иначе всё будет обрезаться).
        '''
        src = frame.astype(np.float32, copy=True)

        # posterize (cartoon) — чем выше progress, тем сильнее упрощение цветов
        '''
Делаем «постеризацию», типа мультяшный стиль.
Чем дальше эффект, тем меньше цветов остаётся (уровни от 4 до 16).
step — размер шага между цветами.
np.floor(...)*step — округляем пиксели вниз к ближайшему «корзинному» цвету.
        '''
        levels = max(3, int(4 + progress * 12))   # 4..16 уровней
        step = 256.0 / levels
        poster = np.floor(src / step) * step

        # edge detection на исходном (uint8 contiguous)
        '''
Делаем картинку в памяти непрерывной, чтоб OpenCV не ругался.
        '''
        src_cv = np.ascontiguousarray(frame)
        '''
Готовим чёрно-белую версию кадра: если RGB — переводим в серый, если уже серый — оставляем.
        '''
        if src_cv.ndim == 3 and src_cv.shape[2] == 3:
            gray = cv2.cvtColor(src_cv, cv2.COLOR_BGR2GRAY)
        else:
            gray = src_cv if src_cv.ndim == 2 else cv2.cvtColor(src_cv, cv2.COLOR_BGR2GRAY)

        # сглаживание перед Canny, параметры зависят от размера и progress
        '''
Перед поиском границ картинку блюрим, чтобы шум не мешал.
Чем меньше прогресс, тем сильнее блюрим (чтобы эффект начинался плавно).
Кернель всегда должен быть нечётный, так что проверяем и прибавляем единичку.
        '''
        blur_k = max(3, int(1 + (1 - progress) * 5))  # при маленьком progress чуть сильнее блюрим
        if blur_k % 2 == 0:
            blur_k += 1
        gray_blur = cv2.medianBlur(gray, blur_k)

        # Canny и расширение линий
        '''
Находим края алгоритмом Canny. Порог чувствительности зависит от прогресса: дальше — жёстче.
        '''
        low = int(30 + progress * 60)
        high = int(90 + progress * 120)
        edges = cv2.Canny(gray_blur, low, high)
        # ширина линий в зависимости от прогресса
        '''
Делаем линии потолще (дилатация). Чем дальше прогресс, тем жирнее линии.
        '''
        dilate_iter = 1 + int(progress * 6)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        edges_dil = cv2.dilate(edges, kernel, iterations=dilate_iter)

        # цвет неона (BGR) — можно менять
        '''
Базовый цвет свечения: в формате BGR, тут он такой фиолетово-синий.
        '''
        base_tint = np.array([40, 10, 240], dtype=np.float32)  # яркий фиолетово-синий
        # усиливаем/меняем оттенок по прогрессу (пульсация)
        '''
Добавляем пульсацию цвета, типа оно дышит. Чем больше прогресс, тем ярче и сочнее.
        '''
        pulse = 0.6 + 0.4 * np.sin(progress * np.pi * 2)
        tint = base_tint * (0.7 + 0.6 * progress) * (0.9 + 0.1 * pulse)

        # создаём цветной налёт краёв
        '''
Создаём слой «свечения» на краях.
Если картинка цветная — красим края цветом tint, если ч/б — средним значением.
        '''
        edges_mask = edges_dil.astype(bool)
        glow = np.zeros_like(src, dtype=np.float32)
        if src.ndim == 2:
            glow[edges_mask] = float(np.mean(tint))
        else:
            # для каждого канала
            glow[edges_mask] = tint

        # мягкое свечение — сильный GaussianBlur; радиус зависит от размера и progress
        '''
Размазываем «свечение» сильным блюром,
радиус растёт с прогрессом.
Ограничиваем максимум, чтобы комп не задохнулся.
        '''
        max_kernel = int(min(max(h, w) * 0.03, 65))  # ограничим ядро
        gk = 3 + int(progress * max_kernel)
        if gk % 2 == 0:
            gk += 1
        glow_blur = cv2.GaussianBlur(glow.astype(np.float32), (gk, gk), 0)

        # Core lines (яркие тонкие линии поверх)
        '''
Делаем «жирные неоновые прожилки» — это центральные яркие линии.
Берём края, чуть сужаем (эрозия) и красим более ярким цветом.
        '''
        core = np.zeros_like(src, dtype=np.float32)
        core_mask_small = cv2.erode(edges_dil, kernel, iterations=max(1, dilate_iter-1)).astype(bool)
        if src.ndim == 2:
            core[core_mask_small] = float(np.mean(tint) * 1.1)
        else:
            core[core_mask_small] = tint * 1.3

        # комбинируем: poster (база) + glow + core
        '''
Начинаем собирать итог: берём мультяшную базу
        '''
        processed = poster.copy()
        # добавляем свечение (аддитивно), чуть сильнее где появился эффект
        '''
К базовой картинке прибавляем свечение, его мощь растёт с прогрессом.
        '''
        glow_strength = 0.9 + 1.2 * progress
        processed += glow_blur * glow_strength

        # накладываем яркие линии
        '''
На места, где «ядро линий», мы кладём смесь из базового и суперяркого неона (почти полностью неон).
        '''
        processed[core_mask_small] = processed[core_mask_small] * 0.15 + core[core_mask_small] * 0.85

        # мягкий bloom (размытие всей картинки и смешивание) для мультяшности
        '''
Делаем эффект bloom: картинка слегка расплывается,
как будто свет рассеивается. Чем дальше, тем сильнее.
        '''
        blur_all_k = 1 + int(progress * 9)
        if blur_all_k % 2 == 0:
            blur_all_k += 1
        bigblur = cv2.GaussianBlur(processed.astype(np.float32), (blur_all_k, blur_all_k), 0)
        processed = cv2.addWeighted(processed.astype(np.float32), 0.85, bigblur.astype(np.float32), 0.45 * progress, 0)

        # финальная тонировка — чуть затемняем неэффектные области и смешиваем
        '''
Берём копию оригинальной картинки для финального микса.
        '''
        out = frame.astype(np.float32).copy()
        # where mask true -> берем processed, else -> mix original and processed by small factor
        '''
Там, где эффект «проявился» по маске — берём уже обработанную версию.
        '''
        out[appear_mask] = processed[appear_mask]
        # вне маски — небольшое влияние эффекта (для плавности)
        '''
Там, где маска не сработала — мы всё равно чуть примешиваем эффект, чтобы переход был плавным.
        '''
        outside = ~appear_mask
        if np.any(outside):
            out[outside] = out[outside] * (1.0 - 0.4 * progress) + processed[outside] * (0.4 * progress)

        # posterize снова чуть-чуть для консистенции
        '''
Ещё разок постеризуем, чтобы картинка не развалилась и была в едином стиле.
        '''
        out = np.floor(out / step) * step

        '''
Ограничиваем все значения от 0 до 255,
и возвращаем итоговый кадр в нормальном формате uint8.
Всё, дымка с неоном готова.
        '''
        np.clip(out, 0, 255, out=out)
        return out.astype(np.uint8)
    

    # 7. Raid flashbang
    def raid_flashbang(self, frame, t, duration):
        '''
Подтягиваем модуль time, чтобы по часикам следить, сколько прошло.
        '''
        import time

        h, w = frame.shape[:2]

        # безопасный переданный прогресс
        '''
Смотри, тут делается так:
Берём текущее время t, делим на длительность duration, и получается прогресс (от 0 до 1).
max(1e-9, duration) – это чтобы на ноль не делилось, хитрый трюк.
np.clip – подрезаем, чтобы не вышло за границы.
Если вдруг какая-то ошибка (ну мало ли, фигня какая в аргументах), то прогресс тупо обнуляем.
        '''
        try:
            prog_passed = float(t) / max(1e-9, float(duration))
            prog_passed = np.clip(prog_passed, 0.0, 1.0)
        except Exception:
            prog_passed = 0.0

            '''
Тут проверяем, есть ли у объекта (self) уже сохранённое состояние, типа память между вызовами.
            '''
        state = getattr(self, '_hack_state', None)
        # (re)инициализация
        '''
Если состояния нет или картинка изменила размер, то надо всё по-новой инициализировать.
        '''
        if (state is None) or (state.get('size') != (w, h)):
            # сетка блоков
            '''
Тут мы делим картинку на блоки.
target_block_pixels = 64 – каждый кусок примерно 64 пикселя в ширину/высоту.
cols и rows – сколько колонок и строк получится. Минимум 4, максимум 36.
            '''
            target_block_pixels = 64
            cols = max(4, min(36, w // target_block_pixels))
            rows = max(4, min(36, h // target_block_pixels))

            # размеры колонок/строк
            '''
Короче, делим ширину и высоту ровно на колонки и строки.
Если не делится без остатка, то лишние пиксели раскидываем по первым кускам.
            '''
            col_widths = [w // cols] * cols
            for i in range(w % cols):
                col_widths[i] += 1
            row_heights = [h // rows] * rows
            for i in range(h % rows):
                row_heights[i] += 1

            # целевые позиции
            '''
Составляем список всех прямоугольников (где каждый блок должен оказаться).
В target_positions хранятся координаты: левый верхний угол (x,y) и размер блока.
            '''
            target_positions = []
            y = 0
            for r in range(rows):
                x = 0
                for c in range(cols):
                    target_positions.append((x, y, col_widths[c], row_heights[r]))
                    x += col_widths[c]
                y += row_heights[r]

                '''
Делаем случайную перестановку блоков. Типа все куски начинают не на своих местах, а где попало.
                '''
            N = len(target_positions)
            perm = np.arange(N)
            np.random.shuffle(perm)
            # стартовые позиции — переставленные цели
            start_positions = [target_positions[int(perm[i])] for i in range(N)]

            # вырезаем блоки один раз (из текущего кадра)
            '''
Вырезаем сами куски из кадра, чтобы потом их двигать.
            '''
            blocks = []
            for (tx, ty, tw, th) in target_positions:
                blocks.append(frame[ty:ty+th, tx:tx+tw].copy())

            # случайные задержки, чтобы движения были видимы
            '''
Каждому блоку даём задержку старта (рандом от 0 до 0.36 секунды).
            '''
            delays = np.random.uniform(0.0, 0.36, size=N)

            '''
Собираем всё это добро в словарь (состояние):
размеры, старт/финиш позиций, блоки, задержки и время начала.
Сохраняем в self._hack_state, чтобы потом не пересоздавать каждый раз.
            '''
            state = {
                'size': (w, h),
                'target_positions': target_positions,
                'start_positions': start_positions,
                'blocks': blocks,
                'delays': delays,
                'init_time': time.time(),
                'last_passed': prog_passed,
                'start_t': t,
            }
            self._hack_state = state

            '''
Достаём всё из состояния, чтобы работать.
            '''
        blocks = state['blocks']
        target_positions = state['target_positions']
        start_positions = state['start_positions']
        delays = state['delays']
        N = len(blocks)

        # выбираем прогресс: используем переданный, но если он "не двигается",
        # переключаемся на реальное время (fallback)
        '''
Тут хитрая схема:
– Если входной прогресс реально меняется → используем его.
– Если нет (застрял), то считаем прогресс сами по часам (elapsed / dur).
Так мы не зависим от глючного входа.
        '''
        last_passed = state.get('last_passed', -1.0)
        if abs(prog_passed - last_passed) > 1e-6:
            progress = prog_passed
        else:
            # fallback по времени
            elapsed = time.time() - state.get('init_time', time.time())
            # если duration слишком маленький или нулевой, ставим 1.5 секунды по умолчанию
            dur = max(0.001, float(duration)) if float(duration) > 0.0 else 1.5
            progress = np.clip(elapsed / dur, 0.0, 1.0)

            '''
Обновляем в памяти последний прогресс.
            '''
        state['last_passed'] = prog_passed

        # завершено
        '''
Если всё уже закончилось (прогресс = 1), убираем состояние и возвращаем кадр как есть.
        '''
        if progress >= 1.0:
            if hasattr(self, '_hack_state'):
                delattr(self, '_hack_state')
            return frame

        # плавная кривая
        '''
Функция сглаживания движения (кривая S-образная, чтобы блоки красиво двига­лись, не дёргались).
        '''
        def smootherstep(x):
            x = np.clip(x, 0.0, 1.0)
            return x * x * x * (x * (x * 6 - 15) + 10)

        '''
Создаём чёрный (почти) фон, на который будем рисовать.
        '''
        out = np.full_like(frame, 6)  # тёмный фон

        # лёгкий шум в начале
        '''
Если прогресс ещё не дошёл до середины,
добавляем немного шума (рандомные пиксели), чтобы экран мерцал.
Альфа постепенно уходит к нулю по мере прогресса.
        '''
        if progress < 0.6:
            noise_alpha = (0.6 - progress) / 0.6 * 0.22
            noise = np.random.randint(0, 256, (h, w, 1), dtype=np.uint8)
            noise = np.repeat(noise, 3, axis=2)
            out = cv2.addWeighted(out, 1.0 - noise_alpha, noise, noise_alpha, 0)

        # рисуем блоки — каждый с собственной локальной прогрессией
        '''
Перебираем блоки: берём стартовую и целевую позицию.
        '''
        for i in range(N):
            block = blocks[i]
            sx, sy, sw, sh = start_positions[i]
            tx, ty, tw, th = target_positions[i]

            '''
Считаем локальный прогресс для блока (учитывая его задержку d).
Если глобальный прогресс ещё меньше задержки → блок не двигается.
Если прошёл → двигаем его по красивой кривой smootherstep.
            '''
            d = float(delays[i])
            if progress <= d:
                bp = 0.0
            else:
                denom = 1.0 - d
                bp = (progress - d) / denom if denom > 1e-6 else 1.0
                bp = np.clip(bp, 0.0, 1.0)
            e = smootherstep(bp)

            # позиция и альфа
            '''
Считаем, где сейчас должен быть блок (cx, cy). Прозрачность тоже растёт с прогрессом.
            '''
            cx = int(round(sx + (tx - sx) * e))
            cy = int(round(sy + (ty - sy) * e))
            alpha = 0.3 + 0.7 * e

            # вставка с учётом выхода за границы
            '''
Проверяем, чтобы блок не вылез за границы кадра.
Если выходит – подрезаем по краям.
Если после обрезки ничего не осталось (ww <= 0 или hh <= 0) – скипаем этот блок.
            '''
            x1, y1 = cx, cy
            x2, y2 = cx + sw, cy + sh
            bx1 = 0
            by1 = 0
            if x1 < 0:
                bx1 = -x1
                x1 = 0
            if y1 < 0:
                by1 = -y1
                y1 = 0
            if x2 > w:
                x2 = w
            if y2 > h:
                y2 = h
            ww = x2 - x1
            hh = y2 - y1
            if ww <= 0 or hh <= 0:
                continue


            '''
Вставляем кусок в картинку out, смешивая с фоном по альфе.
            '''
            src = block[by1:by1+hh, bx1:bx1+ww]
            dst = out[y1:y1+hh, x1:x1+ww]
            cv2.addWeighted(src, float(alpha), dst, 1.0 - float(alpha), 0, dst)
            out[y1:y1+hh, x1:x1+ww] = dst

        # тонкие цифровые полосы поверх, затухают к концу
        '''
Добавляем белые горизонтальные полосы, чтобы напоминало цифровой глитч.
Чем ближе к концу эффекта → тем слабее полосы.
        '''
        if progress < 0.95:
            lines_alpha = (1.0 - progress) * 0.22
            step = max(3, h // 150)
            for yy in range(0, h, step * 5):
                y2 = min(h, yy + step)
                out[yy:y2, :] = cv2.addWeighted(out[yy:y2, :], 1.0 - lines_alpha,
                                                np.full_like(out[yy:y2, :], 255), lines_alpha, 0)

        return out

    # 8. Contraband scan lines
    '''
Определяется метод contraband_scan_lines.
Берёт кадр (frame), время (t), длительность (duration)
и пару приколов — strength (сила эффекта) и quality (качество, детализация).
    '''
    def contraband_scan_lines(self, frame, t, duration, strength=0.95, quality=0.6):
        
        # Параметры управления
        '''
– s: сила эффекта, подрезали чтоб не вылезала за 0..1, как будто наркоту на посту режут.
– q: то же самое, только для качества.
– tt: время. Если t нет, ставим ноль, чтоб не сломалось.
        '''
        s = float(np.clip(strength, 0.0, 1.0))   # общая сила эффекта
        q = float(np.clip(quality, 0.0, 1.0))    # качество/детализация (влияет на несколько операций)
        tt = float(t if t is not None else 0.0)

        '''
– Взяли высоту и ширину кадра.
– Привели кадр в float32 и нормализовали от 0 до 1.
Теперь всё удобно мешать, как порошок в пакетике.
        '''
        h, w = frame.shape[:2]
        img = frame.astype(np.float32) / 255.0

        # 0) лёгкая глобальная дрожь (cheap warp)
        '''
– wobble_x и wobble_y: считаем колебания по синусам — кадр будет слегка дрожать,
будто VHS-кассету перемотали.
– M: матрица смещения.
– warpAffine: двигаем картинку, добавляем дрожь. Границы отражаем, чтоб дырки не было.
        '''
        wobble_x = (0.6 + 3.0 * s * q) * np.sin(2.0 * np.pi * 0.07 * tt)
        wobble_y = (0.25 + 1.0 * s * q) * np.cos(2.0 * np.pi * 0.03 * tt)
        M = np.float32([[1, 0, wobble_x], [0, 1, wobble_y]])
        img = cv2.warpAffine((img * 255).astype(np.uint8), M, (w, h),
                             flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32) / 255.0

        # 1) cheap chroma shift (warp per-channel small offsets) — заметно, но дешево
        '''
– Разбили картинку на каналы: синий, зелёный, красный.
– dx_r и dx_b: сдвигаем красный и синий каналы на пару пикселей.
– Mr, Mb: матрицы сдвига.
– warpAffine: сдвигаем каждый канал отдельно.
– merge: собираем обратно.
Эффект — дешёвый хроматический абер, будто телик без антенны ловит.
        '''
        bch, gch, rch = cv2.split((img * 255).astype(np.uint8))
        dx_r = int(round(1 + 2.5 * s * q * np.sin(tt * 1.9)))
        dx_b = -int(round(1 + 1.8 * s * q * np.cos(tt * 1.3)))
        Mr = np.float32([[1, 0, dx_r], [0, 1, 0.15 * dx_r]])
        Mb = np.float32([[1, 0, dx_b], [0, 1, -0.12 * dx_b]])
        r_w = cv2.warpAffine(rch, Mr, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        b_w = cv2.warpAffine(bch, Mb, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        img = cv2.merge([b_w, gch, r_w]).astype(np.float32) / 255.0

        # 2) posterize / comic palette (чёткая цветовая «плитка»)
        '''
– levels: сколько градаций цвета оставить (от 4 до 16).
– Огрубляем цвета: постеризация, картинка как из комиксов.
        '''
        levels = int(4 + 12 * q * s)  # 4..16
        if levels < 2:
            levels = 2
        img = np.floor(img * levels) / max(1.0, levels - 1)

        # 3) яркие чернильные контуры (Sobel + threshold) — комикс‑стиль
        '''
– Перевели картинку в ч/б.
– Размыли слегка, чтоб шум убрать.
– Sobel: ищем градиенты по x и y.
– grad: длина градиента = сила края.
– edge: выделяем только сильные границы.
– Умножаем картинку на (1 – коеф. края): получаются жирные чёрные линии, будто обведено маркером.
        '''
        gray = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        # немного размытие для устойчивости краев
        blur_g = cv2.GaussianBlur((gray * 255).astype(np.uint8), (3, 3), 0).astype(np.float32) / 255.0
        gx = cv2.Sobel(blur_g, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(blur_g, cv2.CV_32F, 0, 1, ksize=3)
        grad = np.sqrt(gx * gx + gy * gy)
        # адаптивный порог: сильнее при большем s
        edge = np.clip((grad - 0.08 * (1 - q)) * (6.0 * s), 0.0, 1.0)
        # инвертируем, чтобы получить чёрные линии: final_line = edge**gamma
        edge_alpha = np.expand_dims(edge, 2)
        # apply as multiply darkening for комикс-lines
        img = img * (1.0 - 0.9 * edge_alpha)

        # 4) выраженные сканлайны (синус по строкам + colour bias)
        '''
– rows: номера строк.
– scan: синус по строкам — получаем тёмные полосы (scanlines), как на старом мониторе.
– color_bias: лёгкий сдвиг цвета по строкам, даёт эффект неон-комикса.
– Умножили картинку на всё это.
        '''
        rows = np.arange(h, dtype=np.float32)[:, None]
        period = max(2.0, 3.0 - 1.2 * q)   # уменьшение периода делает линии плотнее
        phase = 2.0 * np.sin(2.0 * np.pi * 0.6 * tt)
        scan_strength = 0.55 * s
        scan = 1.0 - scan_strength * (0.5 + 0.5 * np.sin(2.0 * np.pi * (rows / period + phase)))
        scan = np.clip(scan, 0.18, 1.05)[:, :, None]
        # лёгкий цветовой bias на строках — комикс‑неон
        r_bias = 1.02 + 0.06 * s * np.sin(rows * 0.07 + tt * 1.8)
        g_bias = 0.98 + 0.04 * s * np.cos(rows * 0.05 + tt * 1.6)
        b_bias = 0.94 + 0.05 * s * np.sin(rows * 0.08 - tt * 1.2)
        color_bias = np.concatenate([b_bias[:, :, None], g_bias[:, :, None], r_bias[:, :, None]], axis=2)
        img = img * scan * color_bias

        # 5) halftone / dots (cheap sinusoidal dot mask per channel) — даёт комиксовые блики
        # параметры dot
        '''
– Генерим сетку косинусов, как точки в газетной печати (halftone).
– Для каждого канала своя фаза → ощущение CMY печати.
– mask: где применяем точки (по яркости).
– Умножаем каналы → получаются комиксовые блики точками.
        '''
        freq = 2.0 + 6.0 * (1.0 - q)  # больше при низком качестве — крупнее
        xv = (np.linspace(0, 2 * np.pi * freq, w))[None, :].astype(np.float32)
        yv = (np.linspace(0, 2 * np.pi * freq, h))[:, None].astype(np.float32)
        # несколько фаз для каналов — ощущение CMY halftone
        dot_r = 0.5 + 0.5 * np.cos(xv * 1.0 + yv * 0.7 + tt * 4.1)
        dot_g = 0.5 + 0.5 * np.cos(xv * 0.9 + yv * 0.8 + tt * 3.3 + 1.2)
        dot_b = 0.5 + 0.5 * np.cos(xv * 1.1 + yv * 0.6 + tt * 2.7 + 2.3)
        dot_strength = 0.18 * s * (0.6 + 0.4 * q)
        # Blend halftone: darken bright areas more (gives comic dot shading)
        lum = 0.299 * img[:, :, 2] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 0]
        mask = np.clip((lum - 0.25) / 0.6, 0.0, 1.0)  # where halftone visible
        halfr = (1.0 - dot_strength * dot_r * mask)[:, :, None]
        halfg = (1.0 - dot_strength * dot_g * mask)[:, :, None]
        halfb = (1.0 - dot_strength * dot_b * mask)[:, :, None]
        img[:, :, 2] *= halfr[:, :, 0]
        img[:, :, 1] *= halfg[:, :, 0]
        img[:, :, 0] *= halfb[:, :, 0]

        # 6) Ghost / color streak — один резкий сдвиг + blur (быстро: downscale blur)
        '''
– Если сила эффекта норм, делаем «призрак»: размыли картинку, сдвинули, покрасили в оттенок.
– Добавляем к основному изображению.
Получается двойник с цветным шлейфом.
        '''
        ghost_amount = 0.15 * s * q
        if ghost_amount > 0.01:
            small = cv2.resize((img * 255).astype(np.uint8), (max(32, w // 8), max(32, h // 8)), interpolation=cv2.INTER_LINEAR)
            # лёгкое размытие
            small = cv2.GaussianBlur(small, (3, 3), sigmaX=1.5)
            up = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
            dx = int(round((3 + 6 * s) * np.sin(tt * 1.7)))
            dy = int(round((1 + 3 * s) * np.cos(tt * 1.1)))
            Mg = np.float32([[1, 0, dx], [0, 1, dy]])
            shifted = cv2.warpAffine((up * 255).astype(np.uint8), Mg, (w, h),
                                     flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT).astype(np.float32) / 255.0
            tint = np.array([0.95 + 0.08 * np.sin(tt * 1.3), 1.0, 1.02 - 0.06 * np.cos(tt * 0.9)])
            img += shifted * tint[None, None, :] * ghost_amount

        # 7) небольшой bloom для ярких зон (cheap downscale blur)
        '''
– Ищем яркие зоны.
– Если есть, делаем downscale, размываем и растягиваем обратно.
– Добавляем как glow.
Типа ореол у ярких мест.
        '''
        lum = 0.299 * img[:, :, 2] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 0]
        bright_mask = np.clip((lum - 0.65) / 0.35, 0.0, 1.0)
        if bright_mask.mean() > 0.005 and s > 0.05:
            small = cv2.resize((img * 255).astype(np.uint8), (max(16, w // 12), max(16, h // 12)),
                               interpolation=cv2.INTER_LINEAR)
            small = cv2.GaussianBlur(small, (5, 5), sigmaX=2.0)
            up = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR).astype(np.float32) / 255.0
            img += up * (0.35 * s * q) * bright_mask[:, :, None]

        # 8) tape noise / banding: low-res noise upsample + occasional scratches
        '''
– Генерим шум низкого разрешения, растягиваем → получаем VHS шум.
– С шансом scratch_prob кидаем вертикальные царапины.
– Размазываем их по вертикали и накладываем.
        '''
        rng = np.random.RandomState(int((tt * 1000) % (2 ** 31)))
        noise_small = rng.normal(loc=0.0, scale=0.05 * (1.0 - q) + 0.015 * q, size=(max(8, h // 12), max(8, w // 12))).astype(np.float32)
        noise = cv2.resize(noise_small, (w, h), interpolation=cv2.INTER_LINEAR)
        img += noise[:, :, None] * (0.12 * s)
        # редкие вертикальные царапины
        scratch_prob = 0.0009 + 0.0018 * s
        mask = (rng.rand(h, w) < scratch_prob).astype(np.float32)
        if mask.sum() > 0:
            scratch = cv2.blur(mask, (1, max(1, int(30 * s))))
            img += scratch[:, :, None] * (0.6 * s)

        # 9) final color punch + vignette + clamp
        # лёгкое усиление контраста (s-curve approx)
        '''
– Подрезали значения к 0..1.
– Кинул S-образную кривую для контраста.
– Добавили оттенок: красный чуть усилили, синий чуть убавили → VHS вайб.
– Виньетка: затемняем края, центр ярче.
        '''
        img = np.clip(img, 0.0, 1.0)
        img = 0.5 * (np.tanh((img - 0.5) * (1.0 + 1.8 * s * q)) + 1.0)
        # magenta / cyan tint for VHS comic flavor
        img[:, :, 2] = np.clip(img[:, :, 2] * (1.02 + 0.06 * s), 0.0, 1.0)  # R up
        img[:, :, 0] = np.clip(img[:, :, 0] * (0.98 - 0.04 * s), 0.0, 1.0)  # B down
        # vignette
        xv = (np.linspace(-1.0, 1.0, w))[None, :].repeat(h, axis=0)
        yv = (np.linspace(-1.0, 1.0, h))[:, None].repeat(w, axis=1)
        radius = np.sqrt(xv * xv + yv * yv)
        vign = 1.0 - 0.6 * (radius ** (1.2 + 0.8 * (1.0 - q)))  # softer if lower quality
        img *= vign[:, :, None]

        out = (np.clip(img, 0.0, 1.0) * 255.0).astype(np.uint8)
        return out

    # 9. Territory split pan
    '''
Типа будет делать эффект раздвижения картинки
— будто панорама делится на две половины и они уезжают в разные стороны.
    '''
    def territory_split_pan(self, frame, t, duration):
        h, w = frame.shape[:2]
        """
Считаем прогресс эффекта: какое сейчас время (t) делим на общее (duration).
Короче, получаем число от 0 до 1, которое показывает, насколько эффект уже продвинулся.
        """
        progress = t/duration
        """
Берём середину ширины картинки.
// — это целочисленное деление, чтобы не было дробей.
Типа делим картинку на левую и правую половину.
        """
        mid = w//2
        """
Отрезаем левую половину кадра.
: по высоте значит берём все строки, а :mid по ширине — только до середины.
        """
        left = frame[:, :mid]
        """
А это правая половина кадра.
Берём всё после середины и до конца ширины.
        """
        right = frame[:, mid:]
        """
Считаем, насколько нужно сдвинуть половинки.
Чем дальше прогресс (0 → 1), тем сильнее сдвигаем.
w//2 — это половина ширины, значит максимум половинки уедут на полширины кадра.
        """
        shift = int(progress * w//2)
        """
Создаём новый пустой кадр (new_frame), забитый нулями (чёрный фон).
Он такой же формы, как frame.
        """
        new_frame = np.zeros_like(frame)
        """
Берём левую половину и двигаем её влево на shift пикселей (-shift).
axis=1 значит двигаем по горизонтали (по ширине).
После этого пихаем эту сдвинутую левую часть в новую картинку, в левую область.
        """
        new_frame[:, :mid] = np.roll(left, -shift, axis=1)
        """
А теперь правая половина: двигаем её вправо (+shift).
Тоже по горизонтали (axis=1).
И вставляем на место правой части новой картинки.
        """
        new_frame[:, mid:] = np.roll(right, shift, axis=1)
        """
Возвращаем готовый кадр, где левая часть уехала влево, правая вправо.
Получается такой киберпанковый "разрыв территории", будто экран разъезжается по бокам.
        """
        return new_frame

    # 10. Amnesty color shift
    def amnesty_color_shift(self, frame, t, duration):
        progress = t/duration
        '''
А вот тут братан делает хитрую химию:
переводит картинку из обычных цветов (BGR) в HSV.
HSV — это где цвет отдельно, яркость отдельно.
А потом кидает всё это в float32,
чтоб можно было по красоте крутить числа, не теряя точности.
        '''
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        '''
Вот тут вообще мясо:

hsv[:,:,0] — это "оттенок", короче сама краска.

Мы к нему прибавляем progress*90 — значит,
чем дальше по времени, тем сильнее сдвигаем цветовую гамму.

% 180 — это чтобы всё не улетело в закат, а оставалось в диапазоне цветов (0–179).

Представь, брат,
как будто ты красишь стены в хате
и каждый раз чуть меняешь банку краски.
В начале белое, потом зелёное, потом синее,
и так до конца замеса. Вот оно и происходит тут.

        '''
        hsv[:,:,0] = (hsv[:,:,0] + progress*90) % 180
        '''
Теперь обратно: переводим всё из HSV в нормальные человеческие цвета (BGR), чтоб глаз видел.
Перед этим числа ужимаем до uint8, иначе OpenCV начнёт бузить.
        '''
        shifted = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        '''
Ну и на выходе отдаём картинку уже с подкрученными цветами.
Типа фильтр "блатной радуги", понял, да?
        '''
        return shifted

    # 11. Blur pulse
    def blur_pulse(self, frame=None, t: float = 0.0,
                               freq: float = 3.5, max_blur: int = 15,
                               max_sat_mult: float = 3.5,
                               chroma_shift_px: float = 6.0,
                               warp_amp_px: float = 6.0,
                               downscale_base: int = 2,
                               min_effect_thresh: float = 0.02) -> np.ndarray:
        """
        Пульсация с чередованием инверсии <-> гипер-насыщения + хроматическая аберрация и волновая деформация.
        Оптимизации:
        - тяжёлые операции выполняются на уменьшенной копии кадра и затем масштабируются обратно;
        - использую быстрые LUT/bitwise и векторные numpy операции.
        """
        if frame is None:
            return frame
        # далее ваш существующий код, например:
        h, w = frame.shape[:2]
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)

        # базовая фаза и прогресс 0..1, используем abs(sin) для «пульсации»
        phase = t * freq
        progress = abs(math.sin(phase))  # 0..1

        # быстрое раннее возвращение, если эффект минимален
        if progress <= min_effect_thresh:
            return frame

        # выбор уровня уменьшения для тяжёлых операций (чтобы экономить ресурсы)
        # увеличиваем downscale при сильном эффекте, чтобы blur/bloom были дешёвыми
        scale = int(downscale_base + progress * 2)  # 2..4 обычно
        sx = max(1, w // scale)
        sy = max(1, h // scale)

        # уменьшенная копия для тяжёлых операций
        small = cv2.resize(frame, (sx, sy), interpolation=cv2.INTER_LINEAR)

        # размытие (Gaussian на маленькой картинке)
        add = int(progress * max_blur)
        ksize = 1 + add
        if ksize % 2 == 0:
            ksize += 1
        if ksize <= 1:
            blurred_small = small
        else:
            # используем более лёгкий blur при большом scale (чтобы не переусложнять)
            blurred_small = cv2.GaussianBlur(small, (ksize, ksize), 0)

        # bloom: берем яркие области, размываем и добавляем обратно (на маленькой копии)
        hsv_small = cv2.cvtColor(blurred_small, cv2.COLOR_BGR2HSV).astype(np.float32)
        h_s, s_s, v_s = cv2.split(hsv_small)
        # маска ярких пикселей (на маленькой)
        bright_mask = (v_s > 180).astype(np.float32)
        # быстрый bloom: размытие маски и умножение на яркость
        mask_blur = cv2.GaussianBlur((bright_mask * v_s).astype(np.uint8), (ksize|1, ksize|1), 0).astype(np.float32)
        bloom_small = np.clip(blurred_small.astype(np.float32) + (mask_blur[..., None] * 0.25), 0, 255).astype(np.uint8)

        # чередование эффектов по пульсу
        pulse_idx = int(math.floor(phase / math.pi))
        even = (pulse_idx % 2) == 0

        if even:
            # Инверсия + деформация + мягкий bloom
            inv_small = cv2.bitwise_not(bloom_small)

            alpha = float(progress)  # смешивание инвертированного и оригинала
            mixed_small = cv2.addWeighted(bloom_small, 1.0 - alpha, inv_small, alpha, 0)

            # волновая деформация: создаём смещение карты на маленьком разрешении
            yy, xx = np.mgrid[0:sy, 0:sx].astype(np.float32)
            # фазовый сдвиг по координатам, амплитуда зависит от progress
            amp = warp_amp_px * (progress)
            # частота можно варьировать; используем комбинацию синусов
            dx = (np.sin((yy / sy) * 2.0 * math.pi * (1.0 + progress*2.0) + phase) +
                  0.5 * np.sin((xx / sx) * 2.0 * math.pi * (1.0 + progress))) * amp / scale
            dy = (np.cos((xx / sx) * 2.0 * math.pi * (1.0 + progress*1.5) - phase) *
                  0.6) * amp / scale
            map_x = (xx + dx).astype(np.float32)
            map_y = (yy + dy).astype(np.float32)
            warped_small = cv2.remap(mixed_small, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

            result_small = warped_small

        else:
            # Гипер-насыщение + хроматическая аберрация (сдвиг каналов) + лёгкий bloom
            # работаем на small -> hsv -> scale S -> back
            hsv = cv2.cvtColor(bloom_small, cv2.COLOR_BGR2HSV).astype(np.float32)
            hh, ss, vv = cv2.split(hsv)
            factor = 1.0 + progress * (max_sat_mult - 1.0)
            ss *= factor
            np.clip(ss, 0, 255, out=ss)
            hsv = cv2.merge((hh, ss, vv)).astype(np.uint8)
            sat_small = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

            # хроматическая аберрация: сдвигаем каналы в разные стороны
            shift = (chroma_shift_px * progress) / scale  # уменьшаем смещение на малой версии
            # смещения для B,G,R
            M_b = np.float32([[1, 0, -shift], [0, 1, 0]])
            M_r = np.float32([[1, 0, shift], [0, 1, 0]])
            b, g, r = cv2.split(sat_small)
            b_s = cv2.warpAffine(b, M_b, (sx, sy), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            r_s = cv2.warpAffine(r, M_r, (sx, sy), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            merged = cv2.merge((b_s, g, r_s))

            # мягкое добавление bloom (чтобы выглядело сочно)
            result_small = cv2.addWeighted(merged, 1.0, blurred_small, 0.25 * progress, 0)

        # апскейлим обратно на полный размер
        result = cv2.resize(result_small, (w, h), interpolation=cv2.INTER_LINEAR)

        # финальный микс с оригиналом — даём немного исходного кадра, чтобы не терять контент
        final_alpha = 0.85 * progress  # 0..0.85
        out = cv2.addWeighted(frame, 1.0 - final_alpha, result, final_alpha, 0)

        return out

    # 12. Pixelation
    '''
Объявляем такую мутку под названием pixelation.
Это типа эффект — делает картинку пиксельной,
как будто смотришь через старую "Денди".
    '''
    def pixelation(self, frame, t, duration):
        '''
Короче, узнаём габариты картинки, как ширину и высоту плазмы у барыги.
        '''
        h,w = frame.shape[:2]
        """
        Тут считаем, насколько картинка будет "квадратной".
Сначала всегда минимум 10,
а потом добавляется ещё до 20,
в зависимости от того, сколько времени прошло (t/duration).
Короче, чем дальше по времени
— тем сильнее пикселя становятся жирными, как после качалки.
        """
        scale = int(10 + 20*(t/duration))
        """
        Уменьшаем картинку до мелких размеров, делим ширину и высоту на этот scale.
Типа берём картинку, сжимаем её как "скриншот на Нокии 3310",
и она такая мутная и мелкая.
interpolation=cv2.INTER_LINEAR — это как способ сжатия,
чтоб было аккуратненько, но всё равно маленькое.
        """
        temp = cv2.resize(frame, (w//scale, h//scale), interpolation=cv2.INTER_LINEAR)
        """
        — Потом берём эту уменьшенную муть и растягиваем обратно на весь экран.
И вот из-за этого растягивания получаются здоровенные пиксели,
прям такие квадратные кирпичи, как плитка в подвале.
interpolation=cv2.INTER_NEAREST — этот способ тупо копирует квадраты без сглаживания.
В итоге получается эффект пиксель-арта, как будто у тебя графика на районе 90-х.
        """
        return cv2.resize(temp,(w,h), interpolation=cv2.INTER_NEAREST)

    # 13. Heat haze
    """
Это параметры под эффект: размер плитки (tile_size),
базовая скорость смены (base_change_rate),
ускорение в начале (early_speed_mul).
Потом идут проценты на разные приколы: инверсия цветов (prob_inv),
дикая насыщенность (prob_sat), гипер-цвета (prob_hyper), шум (prob_noise).

seed — рандом фиксируем, чтоб каша не менялась каждый раз.
max_sat_mult — насколько можно задрать насыщенность.
hyper_hue_shift — насколько сдвигаем цвет по кругу.
lock_blend_window — плавность перехода при "фиксации".
soften_edges и edge_blur_ksize — чтобы сгладить края плиток, если включено.
    """
    def heat_haze(self, frame, t, duration=None,
                                    tile_size: int = 24,
                                    base_change_rate: float = 80.0,
                                    early_speed_mul: float = 1.8,
                                    prob_inv: float = 0.25,
                                    prob_sat: float = 0.25,
                                    prob_hyper: float = 0.2,
                                    prob_noise: float = 0.15,
                                    seed: int = 1337,
                                    max_sat_mult: float = 3.5,
                                    hyper_hue_shift: int = 40,
                                    lock_blend_window: float = 0.07,
                                    soften_edges: bool = False,
                                    edge_blur_ksize: int = 5) -> np.ndarray:
        """
        Быстрая «расшифровка» плитками, привязка к прогрессу (t/duration).
        Когда duration задан — p = clamp(t/duration, 0, 1).
        При p->1 плитки по порядку фиксируются в оригинал.
        """
        '''
Если кадра нет — ну и пошёл он, возвращаем пустяк.
        '''
        if frame is None:
            return frame
        '''
Проверка на дурака: если это не массив (нет .shape) — шлём ошибку.
        '''
        if not hasattr(frame, "shape"):
            raise TypeError("rapid_decode_tiles_progress: ожидался кадр (np.ndarray).")

        h, w = frame.shape[:2]
        """
Если картинка не в формате uint8 (0..255 на канал),
то обрезаем лишнее и переводим, чтоб OpenCV не сдох.
        """
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)

        # прогресс 0..1: если duration задан, используем t/duration,
        #иначе используем циклический вариант
        '''
Считаем прогресс от 0 до 1.
Если есть длительность — всё чинно-благородно: делим время на общую длину.
Если нет — делаем синусоиду, типа колбасится туда-сюда бесконечно.

        '''
        if duration is not None and duration > 0:
            raw_p = float(t) / float(duration)
            p = max(0.0, min(1.0, raw_p))
        else:
            # циклический fallback — но сборки в единый кадр не будет, если duration не указан
            p = abs(math.sin(t * 1.3))

        # easing для финала (smoothstep)
        '''
Функция сглаживания,
чтоб переходы были не как по бордюру, а мягенько, плавно.
        '''
        def smoothstep(x):
            x = np.clip(x, 0.0, 1.0)
            return x * x * (3.0 - 2.0 * x)
        '''
Сколько плиток уже зафиксировалось — от 0 до 1.
        '''
        reveal_frac = float(smoothstep(p))  # 0..1 — доля уже «раскодированных» плиток

        # динамическая скорость смены: в начале быстрее, под конец медленнее
        change_rate = base_change_rate * (1.0 + (1.0 - reveal_frac) * (early_speed_mul - 1.0))

        # вероятности дополнительных эффектов — нормализуем
        '''
Собираем вероятности эффектов в массив.
        '''
        probs = np.array([max(0.0, prob_inv), max(0.0, prob_sat), max(0.0, prob_hyper), max(0.0, prob_noise)], dtype=np.float32)
        '''
Если слишком много нахапали процентов (сумма больше единицы) — нормализуем,
чтоб суммарно меньше единицы было.
        '''
        total = probs.sum()
        if total >= 1.0:
            probs = probs / total * 0.95
            '''
Раздаём шансы: инверсия, насыщенность, гипер, шум и остаток — оригинал.
            '''
        p_inv, p_sat, p_hyper, p_noise = probs
        p_orig = 1.0 - (p_inv + p_sat + p_hyper + p_noise)

        # варианты кадра — вычисляем заранее
        '''
Делаем версию "наизнанку" — цвета перевёрнутые.
        '''
        inverted = cv2.bitwise_not(frame)

        # насыщенный вариант
        '''
Гоним картинку в HSV, чтоб рулить насыщенностью (ss) и яркостью (vv).
        '''
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV).astype(np.float32)
        hh, ss, vv = cv2.split(hsv)
        '''
Чем меньше плиток зафиксировано, тем сильнее выкручиваем насыщенность.
        '''
        sat_factor = 1.0 + (max_sat_mult - 1.0) * (1.0 - reveal_frac)  # насыщенность сильнее в начале, слабее ближе к концу
        '''
Подкручиваем насыщенность и яркость, но следим, чтоб не вывалились за пределы 0–255.
        '''
        ss2 = ss * sat_factor
        vv2 = vv * (1.0 + 0.15 * (1.0 - reveal_frac))
        np.clip(ss2, 0, 255, out=ss2)
        np.clip(vv2, 0, 255, out=vv2)
        '''
Собрали обратно цветную картинку с диким цветом.
        '''
        sat_frame = cv2.cvtColor(cv2.merge((hh, ss2, vv2)).astype(np.uint8), cv2.COLOR_HSV2BGR)

        # гипер-цвет (hue shift в обе стороны) — создадим два варианта
        '''
Гипер-режим: делаем два варианта,
один со сдвигом тона вправо, другой влево. Чем раньше, тем сильнее двигаем.
        '''
        hsv_h1 = hsv.copy()
        hsv_h2 = hsv.copy()
        # применяем смещение H (OpenCV: H in [0..179])
        shift = int(hyper_hue_shift * (1.0 - reveal_frac))  # сильнее в начале
        '''
Насыщенность в гипере тупо в пол и ещё газу сверху.
        '''
        hsv_h1[..., 0] = (hsv_h1[..., 0] + shift) % 180.0
        hsv_h2[..., 0] = (hsv_h2[..., 0] - shift) % 180.0
        # усиление насыщенности для гиперактивного вида
        hsv_h1[..., 1] = np.clip(hsv_h1[..., 1] * (1.6 + 1.4 * (1.0 - reveal_frac)), 0, 255)
        hsv_h2[..., 1] = np.clip(hsv_h2[..., 1] * (1.6 + 1.4 * (1.0 - reveal_frac)), 0, 255)
        '''
Собрали обратно картинки — получились два бешеных гипер-варианта.
        '''
        hyper1 = cv2.cvtColor(hsv_h1.astype(np.uint8), cv2.COLOR_HSV2BGR)
        hyper2 = cv2.cvtColor(hsv_h2.astype(np.uint8), cv2.COLOR_HSV2BGR)

        # шумовой вариант (белый/цветной шум, малый вклад)
        # создаём один шумовой кадр на весь размер
        '''
Тут генерим шум — как будто телек без антенны шипит.
        '''
        rng = np.random.RandomState((seed ^ int(t * 1000)) & 0xFFFFFFFF)
        noise = (rng.randint(0, 256, (h, w, 1), dtype=np.uint8))
        # несколько каналов для цветного шума
        """
Делаем цветной шум, сдвигаем каналы.
Потом мешаем его с картинкой. Получается грязный трэш.
        """
        noise_color = np.concatenate([noise, np.roll(noise, 7, axis=1), np.roll(noise, 13, axis=0)], axis=2)
        noise_mix = cv2.addWeighted(frame, 0.25, noise_color, 0.75, 0)

        # параметры плиточной сетки
        '''
Считаем, сколько плиток по вертикали и горизонтали.
        '''
        Ty = (h + tile_size - 1) // tile_size
        Tx = (w + tile_size - 1) // tile_size

        # номера плиток
        '''
Делаем сетку координат для плиток.
        '''
        ty = np.arange(Ty, dtype=np.int64)
        tx = np.arange(Tx, dtype=np.int64)
        tile_y, tile_x = np.meshgrid(ty, tx, indexing='ij')  # shape Ty x Tx

        # для фиксации плиток: детерминированный ранж/порядок фиксации
        '''
Считаем уникальный хэш для каждой плитки,
чтоб порядок фиксации был не рандомный, а стабильный.
        '''
        lock_hash = (tile_x * 73856093) ^ (tile_y * 19349663) ^ np.int64(seed * 16777619)
        lock_hash = (lock_hash & 0xFFFFFFFF).astype(np.uint32)
        # нормируем в 0..1 — порядок фиксации
        lock_order = (lock_hash.astype(np.float32) / 4294967295.0)  # Ty x Tx, 0..1

        # вычисляем вес фиксации для каждой плитки: 0..1
        # плитка начинает фиксироваться, когда reveal_frac >= lock_order
        # используем небольшое окно плавной фиксации lock_blend_window
        lbw = max(1e-4, lock_blend_window)
        w_lock_tile = np.clip((reveal_frac - lock_order) / lbw, 0.0, 1.0)  # Ty x Tx

        # discrete time step (для смены состояния у незафиксированных плиток)
        time_step = int(math.floor(t * change_rate))

        # Хэш для выбора состояния плитки в текущий time_step
        '''
Для каждой плитки генерим "жребий" 0–100,
по которому выбираем, какой эффект на ней.
        '''
        state_hash = ((tile_x * 2166136261) ^ (tile_y * 16777619) ^ (np.int64(time_step) * 2246822519) ^ np.int64(seed)) & 0xFFFFFFFF
        r100 = (state_hash % 100).astype(np.int32)

        thr_inv = int(np.clip(p_inv * 100.0, 0, 100))
        thr_sat = int(np.clip((p_inv + p_sat) * 100.0, 0, 100))
        thr_hyper = int(np.clip((p_inv + p_sat + p_hyper) * 100.0, 0, 100))
        # остальные -> noise / orig

        # маски плиток для состояний (Ty x Tx)
        mask_inv_tile = (r100 < thr_inv)
        mask_sat_tile = (r100 >= thr_inv) & (r100 < thr_sat)
        mask_hyper_tile = (r100 >= thr_sat) & (r100 < thr_hyper)
        mask_noise_tile = (r100 >= thr_hyper) & (r100 < int((p_inv + p_sat + p_hyper + p_noise) * 100.0))
        mask_orig_tile = ~(mask_inv_tile | mask_sat_tile | mask_hyper_tile | mask_noise_tile)

        # разворачиваем плиточную маску на пиксели
        tiles_y = (np.arange(h) // tile_size).astype(np.int32)  # (h,)
        tiles_x = (np.arange(w) // tile_size).astype(np.int32)  # (w,)
        ty_idx = tiles_y[:, None]
        tx_idx = tiles_x[None, :]

        mask_inv = mask_inv_tile[ty_idx, tx_idx]
        mask_sat = mask_sat_tile[ty_idx, tx_idx]
        mask_hyper = mask_hyper_tile[ty_idx, tx_idx]
        mask_noise = mask_noise_tile[ty_idx, tx_idx]
        mask_orig_dynamic = mask_orig_tile[ty_idx, tx_idx]  # orig by state (before locking)

        '''
Для каждого пикселя берём вес фиксации его плитки.
        '''
        w_lock = w_lock_tile[ty_idx, tx_idx]
        w_lock_3 = w_lock[:, :, None]

        '''
Начинаем с обычного кадра.
        '''
        effect_mix = frame.astype(np.float32)

        # step 1: invert
        '''
Если плитка в инверсии — подменяем на инверт.
        '''
        effect_mix = np.where(mask_inv[:, :, None], inverted.astype(np.float32), effect_mix)
        # step 2: sat
        effect_mix = np.where(mask_sat[:, :, None], sat_frame.astype(np.float32), effect_mix)
        # step 3: hyper choose between hyper1 and hyper2 using another bit from state_hash
        '''
Если плитка в гипер-режиме — выбираем один из двух вариантов (сдвиг вправо или влево).
        '''
        hyper_choice = ((state_hash >> 16) & 1).astype(np.bool_)
        hyper_tile = np.where(hyper_choice[ty_idx, tx_idx][:, :, None], hyper1.astype(np.float32), hyper2.astype(np.float32))
        effect_mix = np.where(mask_hyper[:, :, None], hyper_tile, effect_mix)
        # step 4: noise
        '''
Шумные плитки заменяем на шум.
        '''
        effect_mix = np.where(mask_noise[:, :, None], noise_mix.astype(np.float32), effect_mix)
        # step 5: dynamic orig
        '''
А плитки, оставленные оригиналом, просто возвращаем без приколов
        '''
        effect_mix = np.where(mask_orig_dynamic[:, :, None], frame.astype(np.float32), effect_mix)

        '''
Смешиваем оригинал и эффект в зависимости от степени фиксации:
закреплённое = оригинал, остальное = эффекты.
        '''
        out_f = frame.astype(np.float32) * w_lock_3 + effect_mix * (1.0 - w_lock_3)

        # optional: if soften_edges True, немного размываем маски перед финальным миксом
        '''
Если включена опция сглаживания — размываем карту фиксации,
и плитки плавно перетекают в оригинал, без рубленых краёв.
        '''
        if soften_edges:
            k = edge_blur_ksize if (edge_blur_ksize % 2 == 1) else (edge_blur_ksize + 1)
            # размываем w_lock чтобы сгладить края фиксации плиток
            w_lock_blur = cv2.GaussianBlur(w_lock.astype(np.float32), (k, k), 0)
            w_lock_blur_3 = w_lock_blur[:, :, None]
            out_f = frame.astype(np.float32) * w_lock_blur_3 + effect_mix * (1.0 - w_lock_blur_3)

            '''
В конце ограничиваем пиксели в нормальные 0–255 и отдаём готовый кадр с эффектом.
            '''
        out = np.clip(out_f, 0, 255).astype(np.uint8)
        return out

    # 14. Edge sketch
    '''
Это, братуха, параметры с настройками. Типа как ручки на магнитофоне.

downscale=2 → уменьшаем картинку, чтоб быстрее считать.

bilateral_iters=1 → сглаживание для красоты.

color_levels=20 → количество цветов, меньше = более мультяшно.

edge_th1=50, edge_th2=140 → параметры для поиска границ (типа контуры).

edge_dilate=2 → делаем края жирнее.

edge_glow_strength=0.9 → насколько сильно сияют неоновые линии.

edge_color=(0, 255, 255) → цвет контура, тут жёлто-зелёный неон.

pink_tint_strength=0.35 → розовый налёт поверх всего, чтоб по-киберпанковски.

chroma_shift_px=6 → смещение цветов по каналам, типа глюк.

glitch_slices=6 → сколько полосок-глюков будет прыгать.

glitch_max_shift=40 → насколько далеко полосы будут прыгать.

scanline_strength=0.08 → полосы, как на старом телевизоре.

noise_strength=0.03 → шум, типа плёнка грязная.

sharpen_amount=0.15 → резкость добавить, чтоб всё кололось глазами.
    '''
    def edge_sketch(self, frame, t, duration,
                           downscale=2,
                           bilateral_iters=1,
                           color_levels=20,
                           edge_th1=50, edge_th2=140,
                           edge_dilate=2,
                           edge_glow_strength=0.9,
                           edge_color=(0, 255, 255),   # neon yellow in BGR
                           pink_tint_strength=0.35,
                           chroma_shift_px=6,         # max pixels for chromatic aberration
                           glitch_slices=6,
                           glitch_max_shift=40,
                           scanline_strength=0.08,
                           noise_strength=0.03,
                           sharpen_amount=0.15):
        
        img = frame.copy()
        h, w = img.shape[:2]

        # ---- downscale for heavy ops ----
        '''
Тут тема такая: мы берём картинку img и называем её small.
Если параметр downscale больше единицы, то мы хотим уменьшить картинку,
чтобы быстрее работать с ней — потому что эффекты жрут процессор как семки в подъезде.

steps = ... → тут считаем, сколько раз можно сжать картинку пополам (каждый раз уменьшаем в 2 раза).

for _ in range(steps): → крутим цикл столько раз.

if small.shape[0] // 2 < 1 ... → если при уменьшении высота или ширина уйдут в ноль, тормозим.

small = cv2.pyrDown(small) → OpenCV-шная магия: уменьшает картинку в 2 раза, но красиво, не как paint.

Итог: получаем уменьшенную копию картинки, чтобы все тяжёлые эффекты делать быстрее.
        '''
        small = img
        if downscale > 1:
            steps = max(1, int(np.round(np.log2(max(1, downscale)))))
            for _ in range(steps):
                if small.shape[0] // 2 < 1 or small.shape[1] // 2 < 1:
                    break
                small = cv2.pyrDown(small)

        # ---- fast smoothing (cheap substitute for many bilateral passes) ----
        """
Короче, тут мы делаем картинку гладкой, как лоб после зоны 😆

for _ in range(max(1, bilateral_iters)):
крутим фильтр несколько раз, сколько задано в bilateral_iters
(если вдруг 0 поставили, всё равно хоть раз прогонит).

cv2.bilateralFilter(small, 7, 50, 50)
это специальный фильтр из OpenCV. Он сглаживает шум, но края оставляет чёткими.
Типа делает картинку более мультяшной, чтоб линии не поплыли, а фон стал мягким.

По факту — это как будто картинку прогнали через бьюти-фильтр из инсты, только для видео.
        """
        for _ in range(max(1, bilateral_iters)):
            small = cv2.bilateralFilter(small, 7, 50, 50)

        # ---- color quantization (cartoon-ish base) ----
        '''
Тут мы рубим количество цветов, чтоб картинка выглядела как комикс.
Берём диапазон от 0 до 255 и режем на color_levels частей.
Итог: цвета крупными блоками, как будто фотку нарисовал школьник фломастером.
        '''
        quant = max(1, 256 // max(1, color_levels))
        q = (small // quant) * quant + quant // 2
        q = np.clip(q, 0, 255).astype(np.uint8)

        # ---- upscale back ----
        """
Мы уменьшали картинку, теперь обратно растягиваем до оригинального размера.
Типа взяли пиксель-арт и накинул на весь экран.
        """
        out = q
        while out.shape[0] < h or out.shape[1] < w:
            out = cv2.pyrUp(out)
        out = out[:h, :w]

        # ---- keep some detail from original ----
        """
Берём мультяшку и примешиваем немного настоящей картинки (18%).
Получаем — мультяшка, но с деталями, чтобы было не совсем как у ребёнка в тетради.
        """
        base = cv2.addWeighted(out, 0.82, img, 0.18, 0)

        # ---- edges (for neon outlines) ----
        """
Перевели в Ч/Б, чуть размыли, потом через Canny ищем границы.
Короче — рисуем контур всего, что видно.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray_blur = cv2.medianBlur(gray, 5)
        edges = cv2.Canny(gray_blur, edge_th1, edge_th2)
        """
Если надо — делаем края толще, типа жирный маркер.
mask2 — это карта, где есть линии.
        """
        if edge_dilate and edge_dilate > 0:
            ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            edges = cv2.dilate(edges, ker, iterations=edge_dilate)
        mask2 = edges > 0

        # ---- colored neon edges + glow (halo) ----
        """
Создали пустую картинку и нарисовали на ней неоновые линии цветом edge_color.
        """
        neon = np.zeros_like(img)
        neon[mask2] = edge_color  # BGR

        # glow: blur a dilated version of edges and tint with neon color
        """
Сделали свечение (размазали линии, как светящийся след).
Потом сложили линии и свечение → теперь у нас чёткие неоновые обводки с подсветкой.
        """
        glow = np.zeros_like(img, dtype=np.float32)
        large = cv2.dilate(edges, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)), iterations=1)
        large = (large > 0).astype(np.uint8) * 255
        # color the large mask with edge_color
        for c in range(3):
            glow[..., c] = large.astype(np.float32) * (edge_color[c] / 255.0)
        glow = glow.astype(np.uint8)
        # big gaussian to get soft halo
        glow = cv2.GaussianBlur(glow, (0, 0), sigmaX=9, sigmaY=9)
        # combine neon and halo
        neon_total = cv2.addWeighted(neon, 1.0, glow, edge_glow_strength, 0)

        # ---- apply pink tint / cyberpunk grade ----
        # simple and fast approach: push R and B up, reduce G; then overlay a subtle pink
        '''
Бустим красный и синий, режем зелёный → картинка становится киберпанк-розовой.
        '''
        fbase = base.astype(np.float32) / 255.0
        # per-channel scaling to push to pinkish/cyan-magenta palette
        # B, G, R order
        fbase[..., 0] *= 1.05   # blue slightly up
        fbase[..., 1] *= 0.7    # green down
        fbase[..., 2] *= 1.25   # red up
        fbase = np.clip(fbase, 0, 1.0)

        # pink overlay (BGR) — values chosen for neon/pink
        """
Добавляем розовый налёт поверх. Получается фирменный неоновый стиль «ночь в Токио».
        """
        pink_bgr = np.array([190, 30, 200], dtype=np.float32) / 255.0
        # overlay only partially to preserve details
        fbase = fbase * (1.0 - pink_tint_strength) + pink_bgr * pink_tint_strength
        result = (fbase * 255.0).astype(np.uint8)

        # ---- chromatic aberration (fast using np.roll) ----
        # offsets vary with time for animation
        """
Двигаем каналы RGB в разные стороны → картинка как с кривого телевизора или VR очков.
        """
        phase = np.sin(2.0 * np.pi * (t / max(0.0001, duration))) if duration > 0 else np.sin(t * 2.0)
        max_shift = max(1, int(round(chroma_shift_px)))
        dx_r = int(round(phase * max_shift))
        dx_b = -int(round(phase * max_shift / 2.0))
        dy_g = int(round(phase * (max_shift // 3)))

        b, g, r = cv2.split(result)
        if dx_b != 0:
            b = np.roll(b, dx_b, axis=1)
        if dx_r != 0:
            r = np.roll(r, dx_r, axis=1)
        if dy_g != 0:
            g = np.roll(g, dy_g, axis=0)
        result = cv2.merge([b, g, r])

        # ---- glitch slices (horizontal bands shifted) ----
        rng = np.random.RandomState(int(t * 1000) & 0xffffffff)
        res_copy = result.copy()
        n = max(1, int(glitch_slices))
        """
Берём случайные горизонтальные полосы и двигаем их влево/вправо.
Плюс иногда кидаем на них цветной оттенок.
Получается классический «глюк-эффект».
        """
        for i in range(n):
            h0 = rng.randint(0, max(1, h - 2))
            hh = rng.randint(2, max(3, h // 8))
            y1 = h0
            y2 = min(h, h0 + hh)
            shift = int(rng.randint(-glitch_max_shift, glitch_max_shift + 1) * abs(np.sin(t * (i + 1) * 1.17)))
            if shift == 0:
                continue
            # slice and roll horizontally
            band = res_copy[y1:y2, :, :].copy()
            band = np.roll(band, shift, axis=1)
            # small color distortion inside band: tint band slightly cyan/magenta randomly
            tint = rng.uniform(0.85, 1.25, size=(3,))
            band = np.clip(band.astype(np.float32) * tint.reshape((1, 1, 3)), 0, 255).astype(np.uint8)
            result[y1:y2, :, :] = band

        # ---- scanlines (subtle) ----
        # create alternating dark/light lines
        """
Рисуем горизонтальные линии, как у старого телика.
Очень слабые, чисто для атмосферы.
        """
        yy = np.arange(h, dtype=np.float32)
        scan = (0.5 + 0.5 * np.sin((yy / 2.0) * np.pi)).reshape(h, 1)  # 0..1 pattern
        scan = 1.0 - scan * scanline_strength
        # broadcast and apply per-channel
        result = (result.astype(np.float32) * scan[:, :, None]).astype(np.uint8)

        # ---- add subtle colored noise/grain ----
        """
Подкидываем шум и цветные точки, как будто VHS кассета.
        """
        noise = (rng.randn(h, w, 1) * 255.0 * noise_strength).astype(np.float32)
        chroma_noise = (rng.randn(h, w, 3) * 255.0 * (noise_strength * 0.6)).astype(np.float32)
        noisy = result.astype(np.float32) + noise + chroma_noise
        result = np.clip(noisy, 0, 255).astype(np.uint8)

        # ---- overlay neon edges (only on edge pixels + glow) ----
        # put neon_total only where edges exist, and add glow additively
        # add glow globally but masked by blurred edges to avoid full-frame bloom
        glow_mask_f = cv2.GaussianBlur((edges > 0).astype(np.float32) * 1.0, (0, 0), sigmaX=12)
        glow_mask = np.expand_dims(glow_mask_f, axis=2)
        # normalize glow_mask to 0..1
        glow_mask = np.clip(glow_mask, 0.0, 1.0)
        # add neon_total (uint8) as floating blend
        """
Добавляем сияние только там, где есть контуры.
И оставляем чёткие неоновые линии.
        """
        result_f = result.astype(np.float32)
        neon_f = neon_total.astype(np.float32)
        result_f = result_f * (1.0 - glow_mask * 0.8) + neon_f * (glow_mask * 0.95)
        result = np.clip(result_f, 0, 255).astype(np.uint8)

        # also paint sharp solid neon lines exactly on edges to keep contour readability
        result[mask2] = neon[mask2]

        # ---- optional sharpen to make it more "sharp cyberpunk" ----
        """
Последний штрих: делаем картинку более резкой, чтобы «киберпанк колол глаза».
        """
        if sharpen_amount and sharpen_amount > 0:
            blur = cv2.GaussianBlur(result, (0, 0), sigmaX=1.0)
            result = cv2.addWeighted(result, 1.0 + sharpen_amount, blur, -sharpen_amount, 0)
            result = np.clip(result, 0, 255).astype(np.uint8)

            '''
Возвращаем готовую картинку — по факту это неоновый глючный киберпанковский фильтр.
            '''
        return result

    # 16. Color invert pulse
    '''
Это всё типа "настройки под ключ". Параметры по дефолту, чтобы видос не лагал и красиво выглядел.

downscale_chroma — уменьшаем детализацию цвета, чтоб быстрее обсчитать.

chroma_blur_sigma — чутка замыливаем цвет, типа мультяшности.

pink_strength — сколько розового наваливаем.

neon_color — какой цвет неона юзаем (BGR, а не RGB).

edge_th1, edge_th2 — параметры для Canny, ищем границы.

edge_glow_sigma — радиус размытия для свечения.

chroma_shift_px — сдвиг каналов, типа аберрация как на старом телике.

glitch_slices и glitch_max_shift — сколько "слайсов" глюкнется и насколько.

glitch_prob — шанс, что вообще глюк бахнет.

scan_strength — сила полосочек сканлайнов.

noise_strength — сила шумка, чтоб "грязь киберпанка".
    '''
    def color_invert_pulse44(self, frame, t, duration,
                        downscale_chroma=2,    # ускорение обработки хромы
                        chroma_blur_sigma=1.2, # легкое сглаживание хромы
                        pink_strength=0.35,    # 0..1
                        neon_color=(0, 230, 255), # BGR neon yellow
                        edge_th1=40, edge_th2=120,
                        edge_glow_sigma=8,
                        chroma_shift_px=3,     # небольшая хроматическая аберрация
                        glitch_slices=4,
                        glitch_max_shift=18,
                        glitch_prob=0.6,
                        scan_strength=0.06,
                        noise_strength=0.02):
        
        img = frame.copy()
        h, w = img.shape[:2]

        # 1) luma/chroma separation — YCrCb: сохраним яркость оригинала
        """
Тут переводим картинку из BGR в YCrCb — это такой формат, где отдельно яркость (Y) и цвета (Cr, Cb).
Яркость (Y_orig) оставляем как есть, а цвета будем мутить.
        """
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb).astype(np.float32)
        Y_orig, Cr, Cb = cv2.split(ycrcb)

        # 2) quick smoothing only on chroma (downscale -> blur -> upscale) — легкая мультяшность
        '''
Делаем уменьшенную картинку для цветовых каналов, чтоб быстрее размыть.
        '''
        small_h = max(1, h // downscale_chroma)
        small_w = max(1, w // downscale_chroma)
        '''
Сжимаем цветовые каналы до мелкого размера.
        '''
        Cr_s = cv2.resize(Cr, (small_w, small_h), interpolation=cv2.INTER_LINEAR)
        Cb_s = cv2.resize(Cb, (small_w, small_h), interpolation=cv2.INTER_LINEAR)

        # gaussian on small chroma is fast
        """
Размазываем эти сжатые каналы Гауссом, чтоб цвета были плавные.
ksize — размер ядра размытия, делаем нечётный.
        """
        ksize = max(1, int(round(chroma_blur_sigma * 4)) | 1)
        Cr_s = cv2.GaussianBlur(Cr_s, (ksize, ksize), sigmaX=chroma_blur_sigma)
        Cb_s = cv2.GaussianBlur(Cb_s, (ksize, ksize), sigmaX=chroma_blur_sigma)

        '''
Обратно растягиваем до нормального размера.
        '''
        Cr_proc = cv2.resize(Cr_s, (w, h), interpolation=cv2.INTER_LINEAR)
        Cb_proc = cv2.resize(Cb_s, (w, h), interpolation=cv2.INTER_LINEAR)

        # optional: quantize chroma a bit to get flatish cartoon regions (fast)
        # small number of levels prevents banding; comment out to keep full precision
        """
Тут мы цвета "ступеньками" режем (квантование).
Короче, делаем меньше оттенков, чтоб картинка выглядела мультяшной.
        """
        levels = 24
        step = max(1.0, 256.0 / levels)
        Cr_proc = (np.floor(Cr_proc / step) * step + step * 0.5)
        Cb_proc = (np.floor(Cb_proc / step) * step + step * 0.5)

        # 3) recompose color image from processed chroma and original luma -> preserves detail
        '''
Собираем обратно цветокартинку из яркости и новых цветов. Это база для эффекта.
        '''
        ycrcb_proc = cv2.merge([Y_orig, Cr_proc, Cb_proc]).astype(np.uint8)
        base = cv2.cvtColor(ycrcb_proc, cv2.COLOR_YCrCb2BGR).astype(np.float32) / 255.0

        # 4) apply pink/cyber grade quickly (color scale in BGR space, subtle)
        """
Наваливаем розовый/фиолетовый фильтр.
Берём смесь оригинала и розового оттенка.
        """
        pink_bgr = np.array([190, 30, 200], dtype=np.float32) / 255.0
        base = base * (1.0 - pink_strength) + pink_bgr * pink_strength
        base = np.clip(base, 0.0, 1.0)

        # 5) compute crisp edges on luminance (small blur then Canny); thin edges -> no heavy masks
        '''
Находим края через Canny, чтоб потом подсветить неоном.
        '''
        gray = (Y_orig / 255.0).astype(np.float32)
        gray_blur = cv2.GaussianBlur((gray * 255).astype(np.uint8), (3, 3), 0)
        edges = cv2.Canny(gray_blur, edge_th1, edge_th2)  # uint8 0/255
        edges_f = edges.astype(np.float32) / 255.0

        # 6) neon lines image (only on edges)
        """
Рисуем картинку с неоновыми линиями там, где есть края.
Цвет берём из neon_color.
        """
        neon_img = np.zeros_like(img, dtype=np.float32) / 255.0
        neon_bgr_f = np.array(neon_color, dtype=np.float32) / 255.0
        # draw solid thin lines where edges exist
        mask_edges = edges > 0
        neon_img[mask_edges] = neon_bgr_f

        # 7) glow: blur edges to create soft halo but clamp intensity so background remains clean
        '''
Свечение вокруг этих линий. Чтоб выглядело как неон с ореолом.
        '''
        glow = cv2.GaussianBlur(edges.astype(np.float32), (0, 0), sigmaX=edge_glow_sigma, sigmaY=edge_glow_sigma)
        glow = np.clip(glow / 255.0, 0.0, 1.0)  # 0..1
        # make color glow and attenuate strongly away from edges to avoid full-frame bloom
        glow_colored = (glow[:, :, None] * neon_bgr_f[None, None, :]) * 0.9

        # 8) additive combine base + glow (only near edges)
        # Use soft mask to ensure glow doesn't produce an ugly full-frame mask
        """
Склеиваем свечение с базовой картинкой.
А там, где прям край, ставим чистый неон, чтобы жёстко выделялось.
        """
        result_f = base.copy()
        result_f = np.clip(result_f + glow_colored, 0.0, 1.0)

        # apply sharp neon lines exactly on edges (preserve contrast)
        result_f[mask_edges] = neon_bgr_f  # ensure readability

        # 9) lightweight chromatic aberration: tiny roll per channel depending on time
        '''
Здесь замут с хроматической аберрацией, брат: каждый канал (R, G, B) чуть двигаем по-разному.
Типа как будто старый кинескоп моргает или VHS тупит.
phase зависит от времени t, чтоб движение было плавное, а не просто сдвиг.
        '''
        phase = (t or 0.0) * 2.0 * np.pi / max(0.0001, max(0.1, duration or 1.0))
        dx_r = int(round(np.sin(phase * 1.1) * chroma_shift_px))
        dx_b = -int(round(np.sin(phase * 0.7) * (chroma_shift_px * 0.6)))
        dy_g = int(round(np.cos(phase * 0.9) * (chroma_shift_px * 0.3)))

        # convert to uint8 for rolling and channel math
        '''
Готовим картинку к сдвигу: переводим в uint8 и делим на каналы (синий, зелёный, красный).
        '''
        result_u = (result_f * 255.0).astype(np.uint8)
        b, g, r = cv2.split(result_u)
        """
Тут и есть сам прикол — берём каналы и двигаем:

b (синий) влево/вправо,

r (красный) тоже по горизонтали,

g (зелёный) по вертикали.

Получается разноцветный разъезд по краям.
        """
        if dx_b != 0:
            b = np.roll(b, dx_b, axis=1)
        if dx_r != 0:
            r = np.roll(r, dx_r, axis=1)
        if dy_g != 0:
            g = np.roll(g, dy_g, axis=0)
            '''
Собираем всё назад в картинку и нормализуем в диапазон [0..1].
            '''
        result_u = cv2.merge([b, g, r]).astype(np.float32) / 255.0

        # 10) glitch slices — few, small shifts; preserve most of frame, only local bands modified
        """
Дальше пойдут гличи — как будто картинка лагнула на телике.
rng — свой генератор рандома, чтоб всё выглядело непредсказуемо.
        """
        rng = np.random.RandomState(int((t or 0.0) * 1000) & 0xffffffff)
        res_glitch = result_u.copy()
        n_slices = max(1, int(glitch_slices))
        '''
Каждый слайс может либо глюкнуть, либо нет — по вероятности glitch_prob.
        '''
        for i in range(n_slices):
            if rng.rand() > glitch_prob:
                continue
            # pick band
            """
Выбираем случайный "отрезок" по высоте (y0..y1) и насколько его сдвинуть по горизонтали (shift).
            """
            y0 = int(rng.randint(0, max(1, h - 2)))
            hh = int(rng.randint(2, max(3, h // (2 * n_slices))))
            y1 = min(h, y0 + hh)
            shift = int(rng.randint(-glitch_max_shift, glitch_max_shift + 1))
            # clamp shift to small magnitude so details not destroyed
            '''
Корректируем сдвиг, чтоб не было прям разрыва в пол-экрана.
            '''
            shift = int(np.clip(shift * (0.25 + 0.75 * rng.rand()), -glitch_max_shift, glitch_max_shift))
            if shift == 0:
                continue
            '''
Берём этот кусок и двигаем вбок.
            '''
            band = res_glitch[y0:y1, :, :].copy()
            band = np.roll(band, shift, axis=1)
            # slight color tint inside band (cheap)
            """
Ещё и цветок подкрасили внутри сдвинутого куска,
чтоб выглядело по-киберпанковски, как на битом экране.
            """
            tint = 0.9 + 0.4 * rng.rand()  # 0.9..1.3
            band = np.clip(band * (1.0 + (tint - 1.0) * np.array([1.0, 0.9, 1.1])[None, None, :]), 0.0, 1.0)
            res_glitch[y0:y1, :, :] = band

        result_u = (res_glitch * 255.0).astype(np.uint8)

        # 11) subtle scanlines and noise to add cyberpunk texture (very light)
        """
Наваливаем сканлайны — тёмные полоски, как будто ты смотришь на CRT телек.
scan по высоте создаёт синусоидные полоски.
        """
        result_f = result_u.astype(np.float32) / 255.0
        yy = np.arange(h, dtype=np.float32)
        scan = 1.0 - (0.5 * np.sin((yy * 1.0) * np.pi / 2.0) ** 2) * scan_strength
        result_f = result_f * scan[:, None, None]

        # color noise
        '''
Добавляем лёгкий шумок, как будто помехи на проводе.
        '''
        noise = (rng.randn(h, w, 3) * noise_strength).astype(np.float32)
        result_f = np.clip(result_f + noise, 0.0, 1.0)

        # 12) final: restore original luminance strongly to keep details (blend a bit of processed luminance)
        '''
Переводим снова в YCrCb, чтобы замутить финальную коррекцию яркости.
        '''
        result_u8 = (result_f * 255.0).astype(np.uint8)
        # convert to YCrCb, replace Y with mix of original and processed Y
        ycrcb_fin = cv2.cvtColor(result_u8, cv2.COLOR_BGR2YCrCb).astype(np.float32)
        Y_proc, Cr_fin, Cb_fin = cv2.split(ycrcb_fin)
        # blend Y: mostly original (preserve details), some processed (adds slight glow contrast)
        """
Финт ушами: яркость берём почти оригинальную (85%), но подмешиваем немного новую (15%).
Так сохраняем детали, но даём мягкий контраст и glow.
        """
        blend_y = 0.85 * Y_orig + 0.15 * Y_proc
        ycrcb_fin = cv2.merge([blend_y, Cr_fin, Cb_fin]).astype(np.uint8)
        final = cv2.cvtColor(ycrcb_fin, cv2.COLOR_YCrCb2BGR)

        '''
Возвращаем готовый кадр с эффектом — чистый неон-гопо-киберпанк 🔥
        '''
        return final

    # 17. Zoom shake
    def zoom_shake(self, frame, t, duration,
                               ion_strength=0.9,       # общая сила эффекта (0..1)
                               warp_amp=16.0,          # амплитуда волновой деформации(px)
                               warp_freq=1.8,          # частота волновой деформации
                               radial_pulse_amp=0.12,  # сила радиального пульса (масштаб)
                               pulse_speed=6.0,        # скорость пульса
                               trail_decay=0.82,       # коэффициент убывания следов (0..1)
                               trail_mix=0.28,         # сколько текущего кадра добавляем в трейл
                               rgb_split=2.4,          # макс. смещение RGB каналов(px)
                               bloom_thresh=200,       # порог для bloom
                               bloom_strength=0.8,     # сила bloom добавки
                               scanline_strength=0.08, # сила сканлайнов (0..0.2)
                               grain_amp=4.5):         # сила зерна
        """
        frame: BGR uint8
        t: время в секундах (или кадр_id / fps — важно, чтобы изменялось)
        duration: не обязателен, можно для фазирования
        Возвращает BGR uint8.
        """
        h, w = frame.shape[:2]

        # --- ensure color ---
        gray_in = (frame.ndim == 2 or frame.shape[2] == 1)
        if gray_in:
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

        # --- init caches ---
        if not hasattr(self, "_hpi_cache") or self._hpi_cache.get("shape") != (h, w):
            self._hpi_cache = {
                "shape": (h, w),
                "xs": None,
                "ys": None,
                "map_x": None,
                "map_y": None,
                "trail": np.zeros((h, w, 3), dtype=np.float32)
            }
        cache = self._hpi_cache

        # координатные сетки в нормализованном виде [-1..1]
        if cache["xs"] is None:
            ys = np.linspace(-1.0, 1.0, h, dtype=np.float32)
            xs = np.linspace(-1.0, 1.0, w, dtype=np.float32)
            X, Y = np.meshgrid(xs, ys)
            cache["xs"], cache["ys"] = X, Y

        X, Y = cache["xs"], cache["ys"]

        # --- wave warp: несколько синусоид на X/Y (быстра и медленная) ---
        # создаём смещение в пикселях
        px = float(w)
        py = float(h)
        # базовые фазы зависят от времени — даёт текучесть
        phase1 = t * 1.6
        phase2 = t * 3.9 + 1.7

        # двумерные волны
        wave_x = (np.sin((X * warp_freq * 3.0 + phase1) * 2.0 * math.pi) +
                  0.5 * np.sin((Y * warp_freq * 6.0 + phase2) * 2.0 * math.pi))
        wave_y = (np.cos((Y * warp_freq * 3.3 + phase2) * 2.0 * math.pi) +
                  0.5 * np.cos((X * warp_freq * 5.2 + phase1) * 2.0 * math.pi))

        disp_x = (wave_x * warp_amp * ion_strength).astype(np.float32)
        disp_y = (wave_y * (warp_amp * 0.6) * ion_strength).astype(np.float32)

        # --- radial pulsing / proton core: масштаб + slight pinch ---
        cx = 0.0  # center in normalized coords (X,Y already -1..1 centered)
        cy = 0.0
        R = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2)  # 0..~1.4
        # пульс, бегущий наружу
        pulse = 0.5 * (1.0 + np.sin(pulse_speed * t - R * 10.0))
        pulse = np.clip(pulse, 0.0, 1.0)
        # радиальное смещение (уменьшим в центре, добавим кольца)
        radial = (pulse * radial_pulse_amp * ion_strength) / (R + 0.35)
        # перевод в пиксели: масштабируем дисплей
        radial_x = (X * radial * px).astype(np.float32)
        radial_y = (Y * radial * py).astype(np.float32)

        # --- combine displacements в координаты для remap ---
        # базовые координаты в пикселях
        base_x = (X * (w * 0.5) + (w * 0.5)).astype(np.float32)
        base_y = (Y * (h * 0.5) + (h * 0.5)).astype(np.float32)

        map_x = base_x + disp_x + radial_x
        map_y = base_y + disp_y + radial_y

        # небольшая псевдо-случайная фаза: пер-кадр смещение
        jitter = 0.5 * ion_strength * np.array([math.sin(t * 9.1), math.cos(t * 7.3)], dtype=np.float32)
        map_x += jitter[0]
        map_y += jitter[1]

        # --- resample один раз с remap ---
        warped = cv2.remap(frame, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        # --- RGB split: каждому каналу свой небольшой remap (cheap: just shift) ---
        # сдвиги зависят от фаз
        sR = rgb_split * (0.5 + 0.5 * math.sin(t * 3.1 + 0.2)) * ion_strength
        sB = rgb_split * (0.5 + 0.5 * math.cos(t * 2.3 + 1.4)) * ion_strength
        # создаём такие же карты, сдвинутые по X
        map_x_r = (map_x + sR).astype(np.float32)
        map_y_r = map_y
        map_x_b = (map_x - sB).astype(np.float32)
        map_y_b = map_y

        r = cv2.remap(frame[:, :, 2], map_x_r, map_y_r, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        g = cv2.remap(warped[:, :, 1], map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        b = cv2.remap(frame[:, :, 0], map_x_b, map_y_b, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        merged = cv2.merge([b, g, r])

        # --- bloom / proton flare: яркие области размазываем и добавляем обратно ---
        # bright pass
        gray = cv2.cvtColor(merged, cv2.COLOR_BGR2GRAY).astype(np.float32)
        bright_mask = np.clip((gray - bloom_thresh) / (255.0 - bloom_thresh), 0.0, 1.0)
        bright_mask = cv2.GaussianBlur(bright_mask, (0, 0), sigmaX=6.0)  # размытие маски
        # apply blur on bright parts
        bright = (merged.astype(np.float32) * bright_mask[:, :, None])
        blurred_bright = cv2.GaussianBlur(bright, (0, 0), sigmaX=12.0)
        # color dodge-like add
        merged = np.clip(merged.astype(np.float32) + blurred_bright * bloom_strength, 0, 255).astype(np.uint8)

        # --- temporal trail (cheap feedback) ---
        trail = cache["trail"]
        # смешиваем предыдущий trail с текущим кадром (как накопительный след)
        frame_f = merged.astype(np.float32)
        # decay и добавление текущего
        trail *= trail_decay
        trail += frame_f * trail_mix * ion_strength
        # combine trail and current (weighted)
        combined = np.clip(frame_f + trail * 0.6, 0, 255).astype(np.uint8)

        # --- scanlines и CRT-ish contrast ---
        # вертикальные/горизонтальные тонкие полосы: use sin over rows
        lines = (0.5 + 0.5 * np.sin((np.arange(h, dtype=np.float32)[:, None] / 1.0) * 3.1415 * 2.0 + t * 18.0))
        lines = 1.0 - scanline_strength * (1.0 - lines)  # invert small darkening
        combined = (combined.astype(np.float32) * lines[:, :, None]).astype(np.uint8)

        # --- grain (cheap) ---
        if grain_amp > 0.01:
            gn = np.random.randn(h // 2, w // 2, 1).astype(np.float32)
            gn = cv2.resize(gn, (w, h), interpolation=cv2.INTER_LINEAR)
            # sometimes cv2.resize squeezes the last dim -> force 3D
            if gn.ndim == 2:
                gn = gn[:, :, None]
            # normalize
            gn = (gn - gn.mean()) / (gn.std() + 1e-9)
            noise = (gn * grain_amp).astype(np.float32)
            # expand single channel noise to 3 channels to match image
            if noise.shape[2] == 1:
                noise = np.repeat(noise, 3, axis=2)
            combined = np.clip(combined.astype(np.float32) + noise, 0, 255).astype(np.uint8)
            
        # --- final tint / clamp ---
        # лёгкая синяя/циановая тонировка для "ионного" настроя
        tint = np.array([0.92, 0.96, 1.04], dtype=np.float32)  # BGR multipliers
        out = np.clip(combined.astype(np.float32) * tint[None, None, :], 0, 255).astype(np.uint8)

        # save trail back
        cache["trail"] = trail

        if gray_in:
            out = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)

        return out

    # 18. VHS noise
    def vhs_noise44(self, frame, t, duration):
        
        h, w = frame.shape[:2]
        if not hasattr(self, 'prev_frames'):
            self.prev_frames = []

        # работа в float [0..1]
        f = frame.astype(np.float32) / 255.0

        # детерминированный RNG по времени кадра
        rng = np.random.RandomState(int((t * 1000)) & 0xFFFFFFFF)

        # 1) Мерцание и вертикальная нестабильность
        flicker_base = 0.04 * np.sin(2.0 * np.pi * t * 3.2) + rng.randn() * 0.01
        rows = np.arange(h)
        flicker_rows = 0.02 * np.sin(rows * 0.55 + t * 25.0)
        flicker = (1.0 + flicker_base + flicker_rows).astype(np.float32)  # shape (h,)
        f *= flicker[:, None, None]

        # 2) Сканлайны
        scan_strength = 0.06
        scan = 1.0 - scan_strength * ((rows % 2) == 0).astype(np.float32)
        scan = cv2.GaussianBlur(scan[:, None], (1, 5), 0)  # shape (h,1)
        f *= scan[:, :, None]

        # 3) Горизонтальный построчный дрожащий сдвиг и хроматическая аберрация
        b_ch = f[:, :, 0].copy()
        g_ch = f[:, :, 1].copy()
        r_ch = f[:, :, 2].copy()

        base_shift = int(1 + 2 * (0.5 + 0.5 * np.sin(t * 5.0)))
        row_jitter = (np.sin(rows * 0.12 + t * 30.0) * 2.0 + rng.randn(h) * 0.6).astype(np.float32)
        shift_b = (row_jitter + base_shift).astype(np.int32)
        shift_r = (row_jitter - base_shift).astype(np.int32)
        shift_g = (row_jitter * 0.45).astype(np.int32)

        cols_idx = np.arange(w)[None, :]

        def shift_channel(ch, shifts):
            idx = (cols_idx - shifts[:, None]) % w
            return ch[np.arange(h)[:, None], idx]

        b_ch = shift_channel(b_ch, shift_b)
        g_ch = shift_channel(g_ch, shift_g)
        r_ch = shift_channel(r_ch, shift_r)
        f = np.stack([b_ch, g_ch, r_ch], axis=2)

        # 4) Вертикальные полосы/царапины
        stripe_mask = np.zeros((h, w), dtype=np.float32)
        n_stripes = max(1, w // 70)
        xs = rng.randint(0, w, size=n_stripes)
        for x in xs:
            width = rng.randint(1, 4)
            intensity = rng.uniform(-0.27, 0.27)
            ygrad = (np.linspace(-1.0, 1.0, h) ** 2).astype(np.float32)
            x0 = max(0, x - width)
            x1 = min(w, x + width)
            stripe_mask[:, x0:x1] += intensity * (0.6 + 0.4 * ygrad)[:, None]
        stripe_mask = cv2.GaussianBlur(stripe_mask, (3, 7), 0)
        f += stripe_mask[:, :, None] * 0.6

        # 5) Ионные пиксели / вспышки (яркие отдельные пиксели с bloom)
        ion_mask = np.zeros((h, w), dtype=np.float32)
        n_ions = rng.randint(6, 16)
        for _ in range(n_ions):
            cy = rng.randint(0, h)
            cx = rng.randint(0, w)
            strength = rng.uniform(0.4, 1.2) * (0.6 + 0.4 * abs(np.sin(t * 2.0)))
            size = rng.randint(1, 5)
            y0 = max(0, cy - size * 3)
            y1 = min(h, cy + size * 3 + 1)
            x0 = max(0, cx - size * 3)
            x1 = min(w, cx + size * 3 + 1)
            yy, xx = np.mgrid[y0:y1, x0:x1]
            dy = yy - cy
            dx = xx - cx
            blob = np.exp(-(dx * dx + dy * dy) / (2.0 * (size**2 + 1.0)))
            ion_mask[y0:y1, x0:x1] += blob * strength
        ion_bloom = cv2.GaussianBlur(ion_mask, (0, 0), 6)
        ion_color = np.empty((h, w, 3), dtype=np.float32)
        ion_color[:, :, 0] = 0.6 + 0.4 * np.sin(t * 1.3)
        ion_color[:, :, 1] = 0.2 + 0.3 * np.cos(t * 0.9)
        ion_color[:, :, 2] = 0.7 - 0.4 * np.sin(t * 0.7)
        f += (ion_bloom[:, :, None] * ion_color) * 0.85
        # 6) VHS-зерно / хрома-шум (FIXED: гарантируем 3D-форму grain)
        grain = rng.randn(h, w, 1).astype(np.float32) * 0.055
        # размываем по 2D; результат иногда теряет третью ось -> восстанавливаем
        grain_blur = cv2.GaussianBlur(grain[:, :, 0], (3, 3), 0)
        # FIXED: приведём к (h,w,1)
        grain = grain_blur[:, :, None]
        # теперь можно формировать хрома-шума
        chroma_noise = np.concatenate([
            grain * (1.0 + 0.6 * rng.randn()), 
            grain * 0.6, 
            grain * (1.1 + 0.4 * rng.randn())
        ], axis=2)
        f += chroma_noise * 1.0

        # 7) Глитч-блоки
        n_glitches = rng.randint(1, 4)
        for _ in range(n_glitches):
            gh = rng.randint(max(4, h // 20), max(8, h // 6))
            gw = rng.randint(max(8, w // 20), max(16, w // 6))
            gy = rng.randint(0, max(1, h - gh))
            gx = rng.randint(0, max(1, w - gw))
            shift = rng.randint(-gw // 3, gw // 3)
            block = f[gy:gy+gh, gx:gx+gw, :].copy()
            for ci, s in enumerate([shift, -shift//2, shift//3]):
                block[:, :, ci] = np.roll(block[:, :, ci], s, axis=1)
            block = np.clip((block - 0.2) * 1.15 + 0.2, 0.0, 1.0)
            f[gy:gy+gh, gx:gx+gw, :] = block

        # 8) Местная пикселизация (мозаика) в полосах
        if rng.rand() < 0.8:
            band_h = max(8, h // 10)
            by = rng.randint(0, max(1, h - band_h))
            small_h = max(1, band_h // 4)
            small_w = max(1, w // 20)
            small = cv2.resize(f[by:by+band_h], (small_w, small_h), interpolation=cv2.INTER_LINEAR)
            small_up = cv2.resize(small, (w, band_h), interpolation=cv2.INTER_NEAREST)
            mix = rng.uniform(0.08, 0.28)
            f[by:by+band_h] = f[by:by+band_h] * (1.0 - mix) + small_up * mix

        # 9) Ghost / фантомы предыдущих кадров
        if len(self.prev_frames) > 0:
            if len(self.prev_frames) >= 2:
                prev = np.mean(np.stack(self.prev_frames[-2:], axis=0), axis=0).astype(np.float32) / 255.0
            else:
                prev = self.prev_frames[-1].astype(np.float32) / 255.0
            prev = cv2.GaussianBlur(prev, (9, 9), 6)
            ghost_shift = int(4 * np.sin(t * 3.0))
            if ghost_shift != 0:
                prev = np.roll(prev, ghost_shift, axis=1)
            f = cv2.addWeighted(f, 1.0, prev * 0.6, 0.12, 0.0)

        # 10) Горизонтальная «roll» нестабильность
        if rng.rand() < 0.25:
            roll_off = int(rng.randn() * 6)
            f = np.roll(f, roll_off, axis=1)

        # 11) Кривые / posterize
        f = np.clip(f, 0.0, 1.0)
        f = np.power(f, 1.0 / (1.0 + 0.02 * np.sin(t * 0.9)))

        # 12) CRT-искажение (remap)
        k = 0.06 * (0.7 + 0.6 * np.sin(t * 0.6))
        cx = w / 2.0
        cy = h / 2.0
        xv, yv = np.meshgrid(np.arange(w), np.arange(h))
        nx = (xv - cx) / cx
        ny = (yv - cy) / cy
        rr = np.sqrt(nx * nx + ny * ny)
        factor = 1.0 + k * (rr ** 2)
        map_x = (cx + nx * factor * cx).astype(np.float32)
        map_y = (cy + ny * factor * cy).astype(np.float32)
        f = cv2.remap(f.astype(np.float32), map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        # 13) Финал
        f = cv2.GaussianBlur(f, (3, 3), 0.6)
        f = np.clip(f, 0.0, 1.0)

        # 14) Обновление буфера
        self.prev_frames.append(frame.copy())
        if len(self.prev_frames) > 4:
            self.prev_frames.pop(0)

        out = (f * 255.0).clip(0, 255).astype(np.uint8)
        return out

    # 19. Glow aura
    def glow_aura(self, frame, t, duration):
        h, w = frame.shape[:2]
        dur = max(1e-6, duration)
        phase = (t % dur) / dur
        pi2 = 2.0 * math.pi

        # параметры — можно подрегулировать
        global_shift_rel = 0.06    # доля ширины для основного сдвига (явный, но плавный)
        chroma_rel = 0.035         # доля ширины для RGB разрыва
        flicker_amp = 0.9          # сила цветовых мерцаний (0..1)
        yellow_amp = 1.0
        pink_amp = 0.95
        noise_grid = max(6, min(48, w // 30))  # low-res mask размер
        noise_blur = 3.0
        edge_glow_amt = 0.85
        sat_boost = 1.18           # насыщенность финала
        final_mix = 0.92           # сколько итоговой обработки vs оригинал (читаемость)

        # детерминированный RNG по кадру (плавность по времени)
        seed = int(t * 1000.0) & 0xffffffff
        rng = np.random.RandomState(seed)

        # float32 рабочая копия
        src = frame.astype(np.float32) / 255.0

        # 1) плавный глобальный X-сдвиг (subpixel, без резких прыжков)
        g_shift = (math.sin(pi2 * (phase * 0.95)) * 0.5 + 0.5 * math.sin(pi2 * (phase * 2.7)) * 0.25)
        g_shift_px = float(w) * global_shift_rel * g_shift
        # небольшой детерминированный импульс
        g_shift_px += (rng.rand() - 0.5) * (w * 0.01)
        Mg = np.array([[1.0, 0.0, g_shift_px], [0.0, 1.0, 0.0]], dtype=np.float32)
        shifted = cv2.warpAffine(src, Mg, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        # 2) chroma split — subpixel R/B смещения (плавно связаны с глобальным сдвигом)
        max_chroma = float(w) * chroma_rel
        ch_phase = math.sin(pi2 * (phase * 1.7 + 0.12))
        shift_r = g_shift_px * 0.9 + max_chroma * (0.6 + 0.4 * ch_phase) + (rng.rand() - 0.5) * 2.0
        shift_b = g_shift_px * -0.7 - max_chroma * (0.4 + 0.4 * ch_phase) + (rng.rand() - 0.5) * 2.0

        def warp_chan_f(ch, dx):
            if abs(dx) < 1e-3:
                return ch
            M = np.array([[1.0, 0.0, float(dx)], [0.0, 1.0, 0.0]], dtype=np.float32)
            return cv2.warpAffine(ch, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        b = warp_chan_f(shifted[:, :, 0], shift_b)
        g = warp_chan_f(shifted[:, :, 1], 0.0)
        r = warp_chan_f(shifted[:, :, 2], shift_r)
        chroma = np.stack([b, g, r], axis=2)

        # 3) цветовые мерцания — делаем два разноцветных low-res поля (жёлтое и розовое)
        nx = max(3, noise_grid)
        ny = max(3, noise_grid)
        ny_field = rng.randn(ny, nx).astype(np.float32)
        pm_field = rng.randn(ny, nx).astype(np.float32)

        ny_up = cv2.resize(ny_field, (w, h), interpolation=cv2.INTER_LINEAR)
        pm_up = cv2.resize(pm_field, (w, h), interpolation=cv2.INTER_LINEAR)
        ny_up = cv2.GaussianBlur(ny_up, (0, 0), noise_blur)
        pm_up = cv2.GaussianBlur(pm_up, (0, 0), noise_blur)

        def norm01(x):
            mn = x.min()
            mx = x.max()
            if mx - mn < 1e-6:
                return np.zeros_like(x)
            y = (x - mn) / (mx - mn)
            return np.clip(y, 0.0, 1.0)

        mask_y = norm01(ny_up * (0.7 + 0.6 * math.sin(pi2 * phase * 2.3)))
        mask_p = norm01(pm_up * (0.8 + 0.5 * math.cos(pi2 * phase * 1.6 + 0.9)))

        # яркие BGR-цвета (настроены для насыщенного желтого и насыщенного розового)
        yellow_bgr = np.array([0.12, 0.95, 1.0], dtype=np.float32)  # слегка холодноватый желтый -> сочность
        pink_bgr   = np.array([1.0, 0.30, 0.78], dtype=np.float32)  # яркий розовый

        # создаём цветовые поля (additive — сохраняет насыщенность)
        # плавный синус-импульс для динамики
        amp_y = yellow_amp * (0.6 + 0.4 * math.sin(pi2 * (phase * 3.1 + 0.2)))
        amp_p = pink_amp   * (0.5 + 0.5 * math.cos(pi2 * (phase * 2.0 + 0.7)))
        color_overlay = (mask_y[:, :, None] * yellow_bgr[None, None, :] * amp_y +
                         mask_p[:, :, None] * pink_bgr[None, None, :] * amp_p) * flicker_amp

        # 4) контурный неоновый glow (Sobel на исходнике, затем раскрашиваем)
        gray = cv2.cvtColor((src * 255.0).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
        sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag = np.sqrt(sx * sx + sy * sy)
        mag = cv2.GaussianBlur(mag, (0, 0), 4.0)
        if mag.max() > 1e-6:
            mag = mag / (mag.max() + 1e-9)
        neon_col = np.array([1.0, 0.9, 0.28], dtype=np.float32)  # warm neon tint
        edge_glow = (mag[:, :, None] * neon_col[None, None, :]) * edge_glow_amt

        # 5) сложение: chroma + additive overlays + edge glow, затем мягкий crossfade с оригиналом для читаемости
        additive = chroma + color_overlay * 0.9 + edge_glow * 0.8
        # небольшой local contrast boost to keep colors pop
        boosted = np.clip(additive * 1.0 + (additive - cv2.GaussianBlur(additive, (0, 0), 3.0)) * 0.18, 0.0, 1.0)

        # 6) лёгкое усиление насыщенности (HSV S channel tweak) — в float
        hsv = cv2.cvtColor((boosted * 255.0).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32)
        h_ch, s_ch, v_ch = cv2.split(hsv)
        s_ch = np.clip(s_ch * sat_boost, 0, 255)
        hsv = cv2.merge([h_ch, s_ch, v_ch]).astype(np.uint8)
        saturated = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR).astype(np.float32) / 255.0

        # 7) финальный мягкий глобальный дрейф X (очень плавно) — ещё одно небольшое warp, в float
        final_shift = float(w) * (global_shift_rel * 0.45) * math.cos(pi2 * (phase * 0.9 + 0.37))
        final_shift += (rng.rand() - 0.5) * (w * 0.006)
        Mf = np.array([[1.0, 0.0, final_shift], [0.0, 1.0, 0.0]], dtype=np.float32)
        final_warp = cv2.warpAffine(saturated, Mf, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        # 8) смешиваем с оригиналом для читаемости логотипов/деталей
        out = np.clip(src * (1.0 - final_mix) + final_warp * final_mix, 0.0, 1.0)

        # 9) финальный тонкий шум (low-res) для текстуры без ярких пикселей
        ns_h = max(2, h // 36)
        ns_w = max(2, w // 36)
        small_noise = rng.normal(0.0, 1.0, (ns_h, ns_w)).astype(np.float32)
        noise_up = cv2.resize(small_noise, (w, h), interpolation=cv2.INTER_LINEAR)
        noise_up = cv2.GaussianBlur(noise_up, (0, 0), 1.2)
        out = np.clip(out + (noise_up[:, :, None] * (4.0 / 255.0)), 0.0, 1.0)

        return (out * 255.0).astype(np.uint8)

    # 20. Circle ripple
    def circle_ripple44(self, frame, t, duration,
                      pull=0.85,        # 0..1 — насколько сильно сжимаем наружную область в центр
                      turns=3.0,        # сколько витков (макс) воронки
                      spin_rate=1.5,    # дополнительное вращение во времени
                      falloff=1.0,      # как быстро скручивание убывает к краю (>0)
                      interp=cv2.INTER_LINEAR):
        """
        Закручивает видео в воронку (без "волнового" размазывания).
        frame: BGR numpy array
        t: текущее время (s)
        duration: общая длительность для вычисления прогресса
        параметры можно подбирать.
        """
        h, w = frame.shape[:2]
        cx, cy = w / 2.0, h / 2.0

        key = (w, h)
        cache = getattr(self, '_vortex_cache', None)
        if cache is None or cache.get('key') != key:
            # сетки один раз
            xs, ys = np.meshgrid(np.arange(w, dtype=np.float32),
                                 np.arange(h, dtype=np.float32))
            dx = xs - cx
            dy = ys - cy
            r = np.sqrt(dx * dx + dy * dy)
            r_safe = np.where(r == 0.0, 1.0, r).astype(np.float32)
            theta = np.arctan2(dy, dx).astype(np.float32)
            maxr = np.sqrt(cx * cx + cy * cy).astype(np.float32)
            cache = {
                'key': key, 'xs': xs, 'ys': ys, 'dx': dx, 'dy': dy,
                'r': r.astype(np.float32), 'r_safe': r_safe, 'theta': theta,
                'maxr': np.float32(maxr)
            }
            self._vortex_cache = cache

        xs = cache['xs']; ys = cache['ys']
        dx = cache['dx']; dy = cache['dy']
        r = cache['r']; r_safe = cache['r_safe']
        theta = cache['theta']; maxr = cache['maxr']

        prog = np.clip(t / max(duration, 1e-6), 0.0, 1.0)

        # делаем exponent < 1 для сжатия: чем меньше, тем сильнее сжатие
        # exponent = 1.0 - pull * prog, защита от нуля
        exponent = np.clip(1.0 - pull * prog, 0.08, 1.0)

        # нормированная радиальная координата 0..1
        r_norm = (r / maxr).astype(np.float32)

        # новое радиальное положение (берём степень <1 чтобы взять source дальше от центра)
        r_src = maxr * (r_norm ** exponent)

        # угол: добавляем витки, сильнее у центра (1 - r_norm^falloff)
        twist = turns * 2.0 * np.pi * (1.0 - (r_norm ** np.maximum(0.001, falloff))) * prog
        # динамический спин во времени
        time_spin = t * spin_rate
        theta_src = theta + twist + time_spin

        # обратно в декартовые — координаты источника
        map_x = (cx + r_src * np.cos(theta_src)).astype(np.float32)
        map_y = (cy + r_src * np.sin(theta_src)).astype(np.float32)

        # remap (обратный маппинг — для каждого dst берем src)
        out = cv2.remap(frame, map_x, map_y, interpolation=interp, borderMode=cv2.BORDER_REFLECT)

        return out

    def neon_glitch2(self, frame, t, duration,
                max_band_height=8,       # макс высота полосы глитча
                base_bands=6,            # базовое число полос
                downscale=4):            # фактор уменьшения для подсветки (чем больше — легче)
        """
        frame: BGR uint8
        t: текущее время (сек)
        duration: общая длительность эффекта (сек)
        Возвращает BGR uint8 с эффектом.
        """
        if duration <= 0:
            progress = 1.0
        else:
            progress = float(t) / float(duration)
            progress = max(0.0, min(1.0, progress))

        h, w = frame.shape[:2]

        # Настройка силы и параметров в зависимости от прогресса
        band_count = int(base_bands + progress * 18)          # от base_bands до ~24
        max_shift = int(1 + progress * 20)                   # пиксельный сдвиг для полос
        glow_strength = 0.3 + 0.7 * progress                  # от 0.3 до 1.0 (влияние glow при смешивании)
        chroma_shift = int(1 + progress * 3)                 # сдвиг каналов для хроматической аберрации

        # Клонируем один раз (будем модифицировать)
        out = frame.copy()

        # Генерация детерминированных "случайных" параметров на основе времени,
        # чтобы кадры были согласованы во времени (меньше визуального шума)
        rng = np.random.RandomState(int(t * 1000) & 0xffffffff)

        # Наложение полос-глитчей: берем случайные полосы и np.roll их по X.
        # Количество полос относительно небольшое => цикл OK и быстрый в C.
        for _ in range(band_count):
            y0 = rng.randint(0, max(1, h - 1))
            bh = rng.randint(1, max(1, min(max_band_height, h - y0)))
            shift = rng.randint(-max_shift, max_shift + 1)
            # небольшой вариант: иногда делаем узкие полосы или чуть больше — выглядит живее
            out[y0:y0 + bh, :] = np.roll(out[y0:y0 + bh, :], shift, axis=1)

        # Быстрый неоновый свет: работаем с уменьшенной копией градаций серого,
        # применяем колормэп и возвращаем назад с размытием.
        gray = cv2.cvtColor(out, cv2.COLOR_BGR2GRAY)
        small_w, small_h = max(1, w // downscale), max(1, h // downscale)
        gray_small = cv2.resize(gray, (small_w, small_h), interpolation=cv2.INTER_LINEAR)

        # Колормап на 1-канале — это дешевле, чем на полном BGR
        glow_small = cv2.applyColorMap(gray_small, cv2.COLORMAP_HOT)

        # Размытие и масштабирование назад (размытие делаем на маленьком изображении и затем апскейлим)
        sigma = 1.0 + progress * 3.0
        glow_small = cv2.GaussianBlur(glow_small, (0, 0), sigmaX=sigma, sigmaY=sigma)
        glow = cv2.resize(glow_small, (w, h), interpolation=cv2.INTER_LINEAR)

        # Хроматическая аберрация (сдвиг каналов), но очень лёгкая — дешёвая операция
        if chroma_shift > 0:
            b, g, r = cv2.split(out)
            # Небольшие np.roll по X/Y: делаем копии каналов, но это дешево по сравнению с полным фильтром
            r_shifted = np.roll(r, chroma_shift, axis=1)
            b_shifted = np.roll(b, -chroma_shift, axis=1)
            chroma = cv2.merge([b_shifted, g, r_shifted])
        else:
            chroma = out

        # Финальное смешивание:
        #  - сначала смешиваем глитч-картинку с неоновым glow (glow_strength регулирует его вклад)
        #  - затем слегка миксуем с хрома-версией, чтобы добавить цветовые искажения
        neon_mix = cv2.addWeighted(out, 1.0 - glow_strength, glow, glow_strength, 0)
        result = cv2.addWeighted(neon_mix, 0.85, chroma, 0.15, 0)

        # Небольшой пульс/мерцание по времени для живости (легкий, не нагружает)
        flicker = 0.95 + 0.05 * np.sin(t * 12.0)  # скорость мерцания можно менять
        result = cv2.convertScaleAbs(result * flicker)

        return result

    def raid_flashbang2(self, frame, t, duration):
        '''
Загружаем время, чтобы замеры и всякая хуита с задержкой работала.
        '''
        import time
        
        h, w = frame.shape[:2]

        '''
Считаем прогресс эффекта.
Если вдруг деление на ноль или фигня, просто ставим ноль.
np.clip не даст выйти за пределы 0–1, чтоб не выёбываться.
        '''
        try:
            prog_passed = float(t) / max(1e-9, float(duration))
            prog_passed = np.clip(prog_passed, 0.0, 1.0)
        except Exception:
            prog_passed = 0.0

            '''
Чекаем, есть ли у объекта сохранённое состояние эффекта
            '''
        state = getattr(self, '_hack_state', None)
        '''
Если состояния нет или размер кадра поменялся — будем заново строить блоки и маски.
        '''
        if (state is None) or (state.get('size') != (w, h)):
            '''
Решаем, на сколько колонок и рядов делим кадр.
Блоки примерно 64 пикселя, но не меньше 4 и не больше 36, чтобы всё красиво было.
            '''
            target_block_pixels = 64
            cols = max(4, min(36, w // target_block_pixels))
            rows = max(4, min(36, h // target_block_pixels))

            '''
Делаем равномерные ширины колонок и высоты рядов.
Если деление нецелое, добавляем по пикселю к первым, чтоб сходилось.
            '''
            col_widths = [w // cols] * cols
            for i in range(w % cols):
                col_widths[i] += 1
            row_heights = [h // rows] * rows
            for i in range(h % rows):
                row_heights[i] += 1

                '''
Братан, это создаёт список всех прямоугольных блоков (x, y, width, height), куда будем кидать пиксели.
                '''
            target_positions = []
            y = 0
            for r in range(rows):
                x = 0
                for c in range(cols):
                    target_positions.append((x, y, col_widths[c], row_heights[r]))
                    x += col_widths[c]
                y += row_heights[r]

                '''
Тут хуярим хаос:

perm — случайная перестановка блоков.

delays — каждый блок появляется с разной задержкой.

masks — случайные маски, чтобы эффект был ломанный и пиксельный.
                '''
            N = len(target_positions)
            perm = np.random.permutation(N)
            delays = np.random.uniform(0.0, 0.45, size=N)
            masks = []
            for (tx, ty, tw, th) in target_positions:
                masks.append(np.random.randint(0, 256, (th, tw), dtype=np.uint8))

                '''
Сохраняем всё это безобразие в объект, чтобы при следующем кадре не пересоздавать блоки
                '''
            state = {
                'size': (w, h),
                'rows': rows,
                'cols': cols,
                'target_positions': target_positions,
                'perm': perm,
                'delays': delays,
                'masks': masks,
                'init_time': time.time(),
                'last_passed': prog_passed
            }
            self._hack_state = state

            '''
Достаём обратно всё, что нам понадобится для текущего кадра.
            '''
        target_positions = state['target_positions']
        perm = state['perm']
        delays = state['delays']
        masks = state['masks']
        N = len(target_positions)

        '''
Считаем прогресс эффекта.
Если время реально сдвинулось, берём прям t/duration, иначе считаем по таймеру.
        '''
        last_passed = state.get('last_passed', -1.0)
        if abs(prog_passed - last_passed) > 1e-7:
            progress = prog_passed
        else:
            elapsed = time.time() - state.get('init_time', time.time())
            dur = max(0.001, float(duration)) if float(duration) > 0.0 else 1.5
            progress = np.clip(elapsed / dur, 0.0, 1.0)
        state['last_passed'] = prog_passed

        '''
Если эффект кончился, чистим состояние и возвращаем исходный кадр, без извращений.
        '''
        if progress >= 1.0:
            if hasattr(self, '_hack_state'):
                delattr(self, '_hack_state')
            return frame

        '''
Создаём кадр-заглушку, почти чёрный с мелким светом (6 — темный оттенок).
        '''
        out = np.full_like(frame, 6)

        '''
На старте добавляем шум, чтобы флешбэнг был слепящий. Чем ближе к 0.6 прогресс, тем сильнее шум.
        '''
        if progress < 0.6:
            noise_alpha = (0.6 - progress) / 0.6 * 0.18
            noise = np.random.randint(0, 256, (h, w, 1), dtype=np.uint8)
            noise = np.repeat(noise, 3, axis=2)
            out = cv2.addWeighted(out, 1.0 - noise_alpha, noise, noise_alpha, 0)

        # scrambled живой фон
        '''
Пацанский “scramble”: каждый блок кадра кидаем на случайное место.
        '''
        for i in range(N):
            tx, ty, tw, th = target_positions[i]
            block = frame[ty:ty+th, tx:tx+tw]
            dst_index = int(perm[i])
            dx, dy, dw, dh = target_positions[dst_index]
            out[dy:dy+dh, dx:dx+dw] = block

            '''
Функция плавного прогресса. Без жёстких рывков, всё мягко выгорает и возвращается.
            '''
        def smootherstep(x):
            x = np.clip(x, 0.0, 1.0)
            return x * x * x * (x * (x * 6 - 15) + 10)

        '''
Для каждого блока считаем, насколько он “включился”.
Сначала задержка, потом плавный рост через smootherstep.
        '''
        for i in range(N):
            tx, ty, tw, th = target_positions[i]
            block = frame[ty:ty+th, tx:tx+tw]
            d = float(delays[i])
            if progress <= d:
                bp = 0.0
            else:
                denom = 1.0 - d
                bp = (progress - d) / denom if denom > 1e-6 else 1.0
                bp = np.clip(bp, 0.0, 1.0)
            e = smootherstep(bp)
            if e <= 1e-6:
                continue
            '''
Маска: какие пиксели блока уже видны, а какие ещё нет.
            '''
            thr = int(np.clip(e * 255.0, 0, 255))
            mask8 = (masks[i] <= thr)  # shape (th, tw), bool

            '''
Берём кусок итогового кадра, чтобы модифицировать.
            '''
            out_block_area = out[ty:ty+th, tx:tx+tw]
            orig_out_area = out_block_area.copy()

            # glitch: делаем XOR только на тех пикселях, где mask случайно истинен,
            # используем одно-канальную маску для cv2.bitwise_xor (без несоответствия размеров)
            '''
“Глитчим” блок, делаем XOR на случайных пикселях, чтоб эффект ломки выглядел по-настоящему.
            '''
            if 0.15 < e < 0.85:
                glitch_mask = (np.random.rand(th, tw) < 0.02).astype(np.uint8) * 255  # shape (th,tw), uint8
                xor_val = np.full_like(out_block_area, 0x33, dtype=np.uint8)
                # bitwise_xor применится только там, где glitch_mask != 0
                out_block_area = cv2.bitwise_xor(out_block_area, xor_val, mask=glitch_mask)

            # расширяем маску на 3 канала для прямой индексации
            '''
Применяем маску к трём каналам, открываем пиксели, которые уже должны показать оригинал.
            '''
            mask3 = np.repeat(mask8[:, :, None], 3, axis=2)

            # полностью открываем пиксели по маске
            out_block_area[mask3] = block[mask3]

            # мягкий blend для остальных пикселей
            '''
Для остальных пикселей делаем плавный blend, чтобы не было резкой смены.
            '''
            alpha_soft = 0.15 + 0.75 * e
            if alpha_soft > 1e-6:
                blended = cv2.addWeighted(block, float(alpha_soft), orig_out_area, float(1.0 - alpha_soft), 0)
                inv_mask3 = ~mask3
                if inv_mask3.any():
                    out_block_area[inv_mask3] = blended[inv_mask3]

                    '''
Возвращаем готовый блок в итоговый кадр.
                    '''
            out[ty:ty+th, tx:tx+tw] = out_block_area

            '''
Добавляем белые горизонтальные линии, типа “яркий флеш”, которые постепенно исчезают.
            '''
        if progress < 0.95:
            lines_alpha = (1.0 - progress) * 0.22
            step = max(3, h // 140)
            for yy in range(0, h, step * 5):
                y2 = min(h, yy + step)
                out[yy:y2, :] = cv2.addWeighted(out[yy:y2, :], 1.0 - lines_alpha,
                                                np.full_like(out[yy:y2, :], 255), lines_alpha, 0)

                '''
Отдаём готовый кадр с флешбэнгом и глитч-эффектом.
                '''
        return out


# --- Поток для создания GIF'ов из видео ---
class GifCreatorThread(QThread):
    '''
Эта строчка говорит: «Эй, интерфейс, я буду сигналить прогресс, типа 0-100 процентов».
    '''
    progress = pyqtSignal(int)
    '''
Когда весь движок с GIFами закончит работу — бах, сигнал на интерфейс с сообщением, что всё готово.
    '''
    finished = pyqtSignal(str)
    '''
Если что-то пойдет не так, шеф, этот сигнал сообщит о проблеме.
    '''
    error = pyqtSignal(str)

    '''
Это конструктор, типа «создаем нового пацана для работы с GIFами»
и даём ему параметры: где папка с эффектами,
размер полотна, кадры в секунду и длину анимации.
    '''
    def __init__(self, effects_dir, canvas_size, fps, animation_length, parent=None):
        '''
Класс-родитель QThread тоже нужно заюзать, чтоб поток нормально работал.
        '''
        super().__init__(parent)
        '''
Папку с эффектами запихиваем в объект Path, чтоб с файлами проще работать.
        '''
        self.effects_dir = Path(effects_dir)
        '''
Эти три строчки — просто сохраняем параметры, чтоб потом знать,
какой размер GIFа,
сколько кадров в секунду
и сколько длится анимация.
        '''
        self.canvas_size = canvas_size
        self.fps = fps
        self.animation_length = animation_length
        '''
Флаг, чтоб можно было потом сказать: «Эй, стоп, больше не делаем GIFы».
        '''
        self._is_running = True
        '''
Эта функция — сердце потока. Тут всё реально делается.
        '''
    def run(self):
        '''
Начало блока «ловим ошибки», чтобы если что-то хреново пойдет, мы не упали с ошибкой.
        '''
        try:
            '''
Создаём путь к новой папке, где будут GIFы.
            '''
            gifs_dir = self.effects_dir / "GIFs"
            '''
Если папки нет — делаем, если есть — чё-то не паримся, просто идём дальше.
            '''
            gifs_dir.mkdir(parents=True, exist_ok=True)

            '''
Собираем все видосы в папке эффектов. Фильтруем по расширениям — нам нужны только видео.
            '''
            video_files = [p for p in self.effects_dir.iterdir()
                           if p.is_file() and p.suffix.lower() in {'.mp4', '.avi', '.mov', '.mkv'}]
            '''
Считаем, сколько видео у нас всего.
            '''
            total = len(video_files)
            '''
Если видео нет, сразу говорим «пошли нахер» и сигналим, что всё кончилось
            '''
            if total == 0:
                self.finished.emit("Нет видео в папке 'эффекты' для конвертации в GIF.")
                return

            '''
Цикл по всем видео, с номерами от 1 и выше.
            '''
            for i, vf in enumerate(video_files, start=1):
                '''
Если кто-то сказал «стоп», прерываем цикл и сигналим, что работу завершили
                '''
                if not self._is_running:
                    self.finished.emit("Операция прервана.")
                    return
                '''
Готовим путь для нового GIFа с таким же именем, но с расширением .gif.
                '''
                out_path = gifs_dir / vf.with_suffix('.gif').name
                '''
Тут мы собираем команду для ffmpeg — типа шеф на кухне:
берём видео, ресайзим под размер полотна,
задаем FPS, обрезаем до длины анимации, убираем звук, кладем в выходной GIF.
                '''
                cmd = [
                    "ffmpeg", "-y",
                    "-i", str(vf),
                    "-vf", f"scale={self.canvas_size[0]}:{self.canvas_size[1]},fps={self.fps}",
                    "-t", str(self.animation_length),
                    "-an",
                    str(out_path)
                ]
                '''
Запускаем команду. check=True — если ffmpeg отвалится,
ловим исключение. stdout и stderr в ноль — не засоряем терминал лишней херней.
                '''
                try:
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    '''
Если ffmpeg сдох, сигналим об ошибке и пишем, какой видос не прокатил
                    '''
                except subprocess.CalledProcessError as e:
                    self.error.emit(f"ffmpeg не смог создать GIF из {vf.name}: {e}")
                    '''
Считаем прогресс в процентах и шлём сигнал на интерфейс.
                    '''
                self.progress.emit(int(i / total * 100))
                '''
Когда цикл кончился, сигналим: «Все GIFы готовы, смотрите в папку».
                '''
            self.finished.emit(f"GIF'ы созданы в: {gifs_dir}")
            '''
Если что-то неожиданное взорвало код, поймали и шлём сигнал с ошибкой.
            '''
        except Exception as e:
            self.error.emit(str(e))

            '''
Просто функция, чтоб сказать потоку: «Парень, хватит, больше не работай».
            '''
    def stop(self):
        self._is_running = False

# --- Поток для конвертации GIF -> WEBM и оптимизации ---
'''
Короче, создаём новый поток,
который будет конвертить гифки в WebM,
чтоб не тормозить основное приложение, понял?
QThread — это типа отдельный тред для тяжёлой работы.
'''
class WebmConverterThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, gifs_dir, canvas_size, fps, animation_length, max_size_kb, parent=None):
        super().__init__(parent)
        self.gifs_dir = Path(gifs_dir)
        self.canvas_size = canvas_size
        self.fps = fps
        self.animation_length = animation_length
        self.max_size_kb = max_size_kb
        self._is_running = True

    def convert_gif_to_webm(self, gif_path, output_path):
        '''
Тут мы делаем саму конвертацию гифки в WebM.
        '''
        command = [
            "ffmpeg", "-y",
            "-i", str(gif_path),
            "-vf", f"scale={self.canvas_size[0]}:{self.canvas_size[1]},fps={self.fps}",
            "-t", str(self.animation_length),
            "-an",
            "-c:v", "libvpx-vp9",
            "-b:v", "150k",
            str(output_path)
        ]
        '''
— Составляем команду для ffmpeg:

"-y" — перезаписывать файлы без вопросов;

"-i" — входной файл (где наша гифка);

"-vf" — фильтр видео: масштабируем под наш холст и ставим FPS;

"-t" — режем по длительности анимации;

"-an" — без звука;

"-c:v" — кодек VP9 для WebM;

"-b:v" — битрейт 150 кбит/с;

и путь куда сохранить результат.
        '''
        '''
Запускаем ffmpeg, молча (чтоб консоль не засорять), если ffmpeg фейлится — кидать ошибку.
        '''
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        '''
Этот метод уменьшает размер файла, если он больше лимита.
        '''
    def optimize_file_size(self, output_path):
        '''
Берём размер файла в байтах.
        '''
        try:
            size_bytes = os.path.getsize(output_path)
            '''
Если файл больше, чем разрешено, тогда будем сжимать.
            '''
            if size_bytes > self.max_size_kb * 1024:
                '''
Создаём временный файл, чтобы не потерять оригинал на случай, если что-то пойдёт не так.
                '''
                temp_path = str(output_path) + ".tmp.webm"
                '''
Команда для сжатия: битрейт ниже (100 кбит/с), всё остальное то же самое, сохраняем во временный файл.
                '''
                command = [
                    "ffmpeg", "-y",
                    "-i", str(output_path),
                    "-c:v", "libvpx-vp9",
                    "-b:v", "100k",
                    "-an",
                    temp_path
                ]
                '''
Запускаем сжатие, опять молча.
                '''
                subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                '''
Если всё норм, заменяем оригинальный файл на оптимизированный.
                '''
                os.replace(temp_path, str(output_path))
        except Exception as e:
            # Не прерываем весь процесс из-за ошибки оптимизации
            self.error.emit(f"Ошибка оптимизации {output_path.name}: {e}")
    '''
Главный метод потока, тут всё реально происходит.
    '''
    def run(self):
        '''
Проверяем, есть ли папка с гифками. Нет — сигналим и выходим.
        '''
        try:
            if not self.gifs_dir.exists():
                self.finished.emit(f"Папка {self.gifs_dir} не найдена.")
                return

            '''
Берём все гифки из папки.
            '''
            gifs = [p for p in self.gifs_dir.iterdir() if p.is_file() and p.suffix.lower() == '.gif']
            '''
Если гифок нет, сигналим и выходим.
            '''
            total = len(gifs)
            if total == 0:
                self.finished.emit("Нет GIF файлов для конвертации.")
                return

            '''
Проходим по каждой гифке. Если поток остановили — сигналим и выходим.
            '''
            for i, gif in enumerate(gifs, start=1):
                if not self._is_running:
                    self.finished.emit("Операция прервана.")
                    return
                '''
Задаём имя выходного файла с расширением .webm.
                '''
                out_webm = gif.with_suffix('.webm')
                '''
Конвертим гифку и сразу оптимизируем размер.
                '''
                try:
                    self.convert_gif_to_webm(gif, out_webm)
                    self.optimize_file_size(out_webm)
                    '''
Ловим ошибки ffmpeg или другие и сигналим о них.
                    '''
                except subprocess.CalledProcessError as exc:
                    self.error.emit(f"ffmpeg не смог конвертировать {gif.name}: {exc}")
                except Exception as e:
                    self.error.emit(f"Ошибка при обработке {gif.name}: {e}")
                    '''
Считаем прогресс и сигналим в интерфейс.
                    '''
                self.progress.emit(int(i / total * 100))

            self.finished.emit(f"WEBM файлы созданы в: {self.gifs_dir}")
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self._is_running = False



'''
А это мы делаем новое окошко, братан.
Оно наследует от QDialog,
значит, типа диалоговое окно,
которое можно открывать поверх всего.
'''
class PreviewWindow(QDialog):
    '''
Конструктор, короче.
Когда создаём наше окошко,
сюда можно сунуть parent — это типа кто его родитель, кому принадлежит.
Если не передадут, будет None.
    '''
    def __init__(self, parent=None):
        '''
Это чтобы базовый QDialog тоже нормально прокачался и не ругался.
Типа вызываем родительский конструктор.
        '''
        super().__init__(parent)
        '''
Тут заголовок окна ставим — сверху будет "Превью эффекта".
        '''
        self.setWindowTitle("Превью эффекта")
        '''
Флаги окна, понял?
Тут мы говорим: “делай это настоящее окно, а не просто модалку”.
Берём старые флаги и добавляем Qt.Window.
        '''
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        '''
Лейбл заводим, братан, это место, где будет GIF или текст. Привязываем его к нашему окну.
        '''
        self.label = QLabel(self)
        '''
А это чтобы содержимое лейбла было по центру. Ни влево, ни вправо — прям ровно посередине.
        '''
        self.label.setAlignment(Qt.AlignCenter)
        '''
Базовый стиль лейбла: фон чёрный, типа кинотеатр в подвале, чтобы глаза не резало.
        '''
        self.label.setStyleSheet("background: black;")
        '''
Создаём вертикальный лэйаут — типа стопку виджетов сверху вниз.
        '''
        lay = QVBoxLayout(self)
        '''
Добавляем наш лейбл в этот лэйаут, чтобы он занимал место в окне.
        '''
        lay.addWidget(self.label)
        '''
Здесь мы заводим переменную для GIF. Пока None,
но потом туда кинем QMovie. Важно, чтобы старый не мешал новому.
        '''
        self.movie = None               # <- важно!
        '''
Размер окна задаём, чтобы было
не слишком маленькое и не слишком большое
— примерно 480x360 пикселей.
        '''
        self.resize(480, 360)

        '''
Метод, братан, для установки GIF. Туда ты передаёшь путь к файлу
        '''
    def set_gif(self, path):
        # остановить старый, если он был
        '''
Если уже был какой-то GIF,
мы его гасим,
удаляем, чтобы память не жрала.
Чисто по понятиям: старый в расход, новый заходит.
        '''
        if self.movie is not None:
            self.movie.stop()
            self.movie.deleteLater()
            self.movie = None

            '''
Проверяем, есть ли файл.
Если нет — пишем "Превью не найдено" на лейбле и выходим. Всё просто.
            '''
        if not os.path.exists(path):
            self.label.setText("Превью не найдено:\n" + path)
            return

        '''
Создаём объект GIF из файла. Это типа новый движок для анимации.
        '''
        self.movie = QMovie(path)
        '''
Размер GIF подгоняем под размер лейбла. Чтобы не растягивался криво.
        '''
        self.movie.setScaledSize(self.label.size())
        '''
Привязываем наш GIF к лейблу, чтобы он начал отображаться.
        '''
        self.label.setMovie(self.movie)
        '''
Запускаем GIF. Вжух, анимация пошла.
        '''
        self.movie.start()

        '''
Срабатывает каждый раз, когда окно меняет размер.
        '''
    def resizeEvent(self, event):
        '''
Чтобы базовое поведение окна тоже оставалось
— чё, оно своё делает, мы не мешаем.
        '''
        super().resizeEvent(event)
        '''
И если GIF есть,
пересчитываем его размер под новое окно.
Типа растягиваем нормально, а не в кривом виде.
        '''
        if self.movie is not None:
            self.movie.setScaledSize(self.label.size())
            


# --- Главное окно ---
class VideoEffectsApp(QWidget):
    def __init__(self):
        super().__init__()
        '''
Название окна сверху — чтоб красиво отображалось «PyEffection — Преобразование видео».
        '''
        self.setWindowTitle("PyEffection — Преобразование видео")
        '''
Размер окна, 700 на 380 пикселей. Чтоб не было мелким, но и не во весь экран.
        '''
        self.resize(700, 380)

        # Красивый шрифт и стиль
        '''
Тут мы шрифт делаем нормальный: Segoe UI, размер 10.
        '''
        font = QFont("Segoe UI", 10)
        '''
Присобачили этот шрифт ко всему окну.
        '''
        self.setFont(font)
        """
Тут, брат, CSS для PyQt.
Настраиваем цвета, кнопки, прогресс-бары,
всё чтоб выглядело как будто пацаны из Кремниевой долины рисовали.

QWidget — фон окна градиентный, текст белый.

QGroupBox — рамочки такие с закруглением.

QPushButton — зелёные кнопки, у кнопки danger красный цвет.

QProgressBar — красивый бар с градиентом.
        """
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0 y1:0, x2:1 y2:1,
                              stop:0 #0f2027, stop:1 #2c5364);
                color: #e6f0f0;
            }
            QGroupBox { 
                border: 1px solid rgba(255,255,255,0.15); 
                border-radius: 8px; 
                margin-top: 6px;
                background: rgba(255,255,255,0.03);
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QPushButton {
                background-color: #4caf50;
                color: white;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton#danger {
            background-color: #e53935;
            }
            QPushButton:disabled {
                background-color: rgba(255,255,255,0.12);
                color: rgba(255,255,255,0.4);
            }
            QComboBox, QLabel {
                color: #e6f0f0;
            }
            QProgressBar {
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 6px;
                text-align: center;
                background: rgba(0,0,0,0.2);
                color: #ffffff;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #6dd5ed, stop:1 #2193b0);
                border-radius: 6px;
            }
        """)

        # Layout
        '''
Главный вертикальный контейнер, куда будем пихать все элементы.
        '''
        main_layout = QVBoxLayout(self)
        '''
Между элементами зазор 12 пикселей, чтоб не слиплось.
        '''
        main_layout.setSpacing(12)

        # Header
        '''
Шапка, типа заголовок сверху окна.
        '''
        header = QLabel("PyEffection — наложение эффектов и экспорт")
        '''
Делаем жирный и побольше размер, чтобы сразу бросался в глаза.
        '''
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        '''
Центруем этот текст по горизонтали.
        '''
        header.setAlignment(Qt.AlignCenter)
        '''
Кидаем шапку в главный контейнер.
        '''
        main_layout.addWidget(header)

        # File selection group
        '''
Группа для выбора видеофайла, подписана «Исходное видео».
        '''
        file_group = QGroupBox("Исходное видео")
        '''
Горизонтальная раскладка внутри этой группы.
        '''
        fg_layout = QHBoxLayout()
        '''
Метка, где будет показано имя выбранного файла. Сначала пишет «Не выбрано».
        '''
        self.label = QLabel("Не выбрано")
        '''
Подсказка при наведении — «Выбранное исходное видео».
        '''
        self.label.setToolTip("Выбранное исходное видео")
        '''
Кнопка для выбора видоса.
        '''
        self.select_button = QPushButton("Выбрать видео")
        '''
Подсказка для кнопки.
        '''
        self.select_button.setToolTip("Выберите видео, к которому будут применяться эффекты")
        '''
Когда нажал кнопку — вызови метод select_video.
        '''
        self.select_button.clicked.connect(self.select_video)
        '''
Добавляем метку в строку.
        '''
        fg_layout.addWidget(self.label)
        '''
Ставим «пустышку», чтобы кнопка ушла вправо.
        '''
        fg_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        '''
Кидаем кнопку в строку.
        '''
        fg_layout.addWidget(self.select_button)
        '''
Прикручиваем горизонталку в группу.
        '''
        file_group.setLayout(fg_layout)
        '''
И эту группу суём в главный контейнер.
        '''
        main_layout.addWidget(file_group)



        # Секция выбора эффекта
        '''
Горизонтальная линия под выбор эффекта.
        '''
        effects_layout = QHBoxLayout()
        '''
Дропдаун (выпадающий список), чтоб выбирать эффект.
        '''
        self.effect_combo = QComboBox()
        '''
Цикл: создаём пункты «Эффект 1», «Эффект 2» ... до 62.
        '''
        for i in range(1, 63):
            self.effect_combo.addItem(f"Эффект {i}", i)
            '''
Когда меняем эффект, вызываем метод on_effect_changed.
            '''
        self.effect_combo.currentIndexChanged.connect(self.on_effect_changed)
        '''
Кидаем список эффектов в строку.
        '''
        effects_layout.addWidget(self.effect_combo)
        '''
пять вставляем пустышку для раздвижки.
        '''
        effects_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        '''
Засовываем всё это в главный контейнер.
        '''
        main_layout.addLayout(effects_layout)

        # создаём окно превью заранее
        '''
Создаём окно превью (просмотр эффекта), но не показываем пока.
        '''
        self.preview_window = PreviewWindow(self)



        
        # Effects group
        '''
Отдельная группа для применения конкретного эффекта.
        '''
        effects_group = QGroupBox("Эффект")
        '''
Горизонталка внутри группы.
        '''
        eg_layout = QHBoxLayout()
        '''
Ещё один выпадающий список с названиями эффектов (тут вручную прописанные).
        '''
        self.effect_combo = QComboBox()
        self.effect_combo.addItems([
            "1. Вылет частиц", "2. Разрезание на полосы", "3. Вихрь ротации",
            "4. Взрыв с осколками вперёд", "5. Морфинг волн", "6. Мультяшный стиль",
            "7. Копии матрицы", "8. Зеркальный лабиринт", "9. Глитч-арт",
            "10. TV-шум", "11. Водная рябь", "12. Пиксельный дождь",
            "13. Калейдоскоп", "14. Туннель времени", "15. Неоновый glow",
            "16. Глитч-сдвиг", "17. Звёздный взрыв", "18. Зеркальное разбиение",
            "19. Цветовая волна с глитчем", "20. Пиксельный вылет", "21. Голограммное мерцание",
            "22. Фейерверк наложение", "23. Жидкое таяние", "24. Неоновое свечение 2",
            "25. Временной warp", "26. Сетка с уменьшением", "27. Смещение половин",
            "28. Мультящный стиль 2 [Hard]", "29. Cпираль бесконечности", "30. Зеркальный лабиринт 2",
            "31. Глитч-арт 2", "32. Глитч-арт 3", "33. VHS-арт", "34. Калейдоскоп 2",
            "35. Туннель времени 2", "36. Неоновый glow 3 (Hard)", "37. Глитч-сдвиг 2",
            "38. Звёздный взрыв 2", "39. Зеркальное разбиение 2", "40. Цветовая волна с глитчем 2",
            "41. Таяние капель", "42. Неоновый глитч", "43. Неоновые полосы [Hard]", "44. Матрица",
            "45. Волновой Глитч", "46. Мрачный мультик", "47. Мультяшный Неон",
            "48. Фрагменты", "49. Хоррор [Hard]", "50. Разъезд половин",
            "51. Ядовитый-тусклый цвет", "52. Пульсация цвета", "53. 8-bit",
            "54. Шифр цвета", "55. Глитч-Кибер Мульт [Hard]", "56. Розово-золотой глитч [Hard]",
            "57. Трип в Лас-Вегасе [Hard]", "58. VHS [Hard]", "59. Золотые блики [Hard]", "60. Воронка",
            "61. Неоновый глитч 2", "62. Фрагменты 2",
        ])

        '''
Кнопка, которая реально применяет выбранный эффект.
        '''
        self.apply_button = QPushButton("Применить эффект")
        '''
Связали кнопку с методом apply_effect.
        '''
        self.apply_button.clicked.connect(self.apply_effect)
        '''
Кидаем список и кнопку в строку.
        '''
        eg_layout.addWidget(self.effect_combo)
        eg_layout.addWidget(self.apply_button)
        '''
Устанавливаем раскладку в группу.
        '''
        effects_group.setLayout(eg_layout)
        '''
Добавляем в главный контейнер.
        '''
        main_layout.addWidget(effects_group)

        # Batch actions
        '''
Группа для массовых действий, типа «сделать всё разом».
        '''
        batch_group = QGroupBox("Пакетные операции")
        '''
Горизонталка внутри.
        '''
        bg_layout = QHBoxLayout()
        '''
Кнопка, чтоб сразу сделать гифки со всеми эффектами.
        '''
        self.create_gifs_button = QPushButton("Создать GIF из всех видео эффектов")
        '''
Привязываем к методу create_gifs_from_effects.
        '''
        self.create_gifs_button.clicked.connect(self.create_gifs_from_effects)
        '''
Кнопка, чтоб переделать гифки в webm.
        '''
        self.convert_webm_button = QPushButton("Создать WEBM из всех GIF")
        '''
Привязка кнопки к методу convert_all_gifs_to_webm.
        '''
        self.convert_webm_button.clicked.connect(self.convert_all_gifs_to_webm)
        '''
Ставим id «danger», чтобы по стилям кнопка была красная.
        '''
        self.convert_webm_button.setObjectName("danger")
        '''
Добавляем кнопки в строку.
        '''
        bg_layout.addWidget(self.create_gifs_button)
        bg_layout.addWidget(self.convert_webm_button)
        '''
Присобачиваем раскладку в группу.
        '''
        batch_group.setLayout(bg_layout)
        '''
Группа идёт в главный контейнер.
        '''
        main_layout.addWidget(batch_group)

        # Progress and status
        '''
Прогресс-бар для отображения прогресса работы.
        '''
        self.progress_bar = QProgressBar()
        '''
Сразу на старте значение 0.
        '''
        self.progress_bar.setValue(0)
        '''
Лейбл справа от бара, пишет «Готово»
        '''
        self.status_label = QLabel("Готово")
        '''
Горизонталка для бара и текста.
        '''
        status_layout = QHBoxLayout()
        '''
Закинули бар и текст в строку.
        '''
        status_layout.addWidget(self.progress_bar)
        status_layout.addWidget(self.status_label)
        '''
Добавили строку в главный контейнер.
        '''
        main_layout.addLayout(status_layout)

        # Internal state
        '''
Переменная под выбранное видео. Пока пусто.
        '''
        self.input_video = None
        # Параметры для GIF -> WEBM
        '''
Размер канваса (типа размер картинки для экспорта).
        '''
        self.canvas_size = (512, 512)
        '''
Кадры в секунду.
        '''
        self.fps = 25
        '''
Длина анимации 5 секунд.
        '''
        self.animation_length = 5
        '''
Лимит размера файла — 256 килобайт.
        '''
        self.max_size_kb = 256

        # Потоки
        '''
Переменные для потоков (чтоб прога не висла, когда гифки и webm делает).
        '''
        self._gif_thread = None
        self._webm_thread = None



        '''
Метод, который вызывается, когда меняешь эффект в комбобоксе.
        '''
    def on_effect_changed(self, index):
        '''
Берём номер эффекта. Если данных нет, то прибавляем 1 к индексу (чтоб с 1 начиналось).
        '''
        effect_number = self.effect_combo.itemData(index) or (index + 1)
        '''
Показываем превью выбранного эффекта.
        '''
        self.show_preview_for(effect_number)


        '''
Функция, чтоб показать превью эффекта по его номеру.
        '''
    def show_preview_for(self, number):
        '''
Если окно превью не видно — открываем его.
        '''
        if not self.preview_window.isVisible():
            self.preview_window.show()

        # безопасный путь к папке preview
        '''
Вычисляем, где лежит сам файл. Если __file__ не сработает, то берём текущую рабочую папку.
        '''
        try:
            base = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            base = os.getcwd()
            '''
Если прога собрана в exe-шник через PyInstaller, то база будет из временной папки _MEIPASS.
            '''
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base = sys._MEIPASS

            '''
Складываем путь до гифки превьюшки (например, preview/3.gif).
            '''
        gif_path = os.path.join(base, "preview", f"{number}.gif")
        '''
Загружаем эту гифку в окно превью.
        '''
        self.preview_window.set_gif(gif_path)




        '''
Вспомогательная функция: где хранить результаты эффектов.
        '''
    def _get_effects_dir(self):
        '''
Если видос не выбран — смысла нет, возвращаем None.
        '''
        if not self.input_video:
            return None
        '''
Берём папку, где лежит исходное видео.
        '''
        parent = self.input_video.parent
        '''
Создаём путь в папку «эффекты».
        '''
        effects_dir = parent / "эффекты"
        '''
Если такой папки нет, то создаём.
        '''
        effects_dir.mkdir(parents=True, exist_ok=True)
        '''
Возвращаем путь к этой папке.
        '''
        return effects_dir


    '''
Чистим название эффекта, чтобы из него получилось нормальное имя файла.
    '''
    def _sanitize_effect_name(self, text):
        '''
Убираем в начале цифры и точку, типа «1. » или «23. ».
        '''
        __name__ = re.sub(r'^\d+\.\s*', '', text)
        '''
Выкидываем всякий мусор, кроме букв, цифр, пробелов и дефисов.
        '''
        __name__ = re.sub(r'[^\w\s-]', '', __name__, flags=re.UNICODE)
        '''
Убираем лишние пробелы.
        '''
        __name__ = re.sub(r'\s+', '', __name__.strip())
        '''
Если в итоге пусто, то возвращаем «effect».
        '''
        return __name__ or "effect"

    '''
Метод для выбора исходного видео.
    '''
    def select_video(self):
        '''
Открываем диалог выбора файла. Можно только видео.
        '''
        video_path, _ = QFileDialog.getOpenFileName(self, "Выберите видео", "", "Video Files (*.mp4 *.avi *.mov *.mkv)")
        '''
Eсли что-то выбрали: сохраняем путь, показываем имя файла в интерфейсе и меняем статус
        '''
        if video_path:
            self.input_video = Path(video_path)
            self.label.setText(self.input_video.name)
            self.status_label.setText("Источник выбран")

            '''
Тут начинается мясо: применяем выбранный эффект к видео.
            '''
    def apply_effect(self):
        # Проверка выбранного видео
        '''
Если видео не выбрано, предупреждаем пользователя и выходим.
        '''
        if not self.input_video:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите видео.")
            return

        # Подготовка пути и имени файла
        '''
Берём папку «эффекты», индекс эффекта, его текст и приводим название в порядок.
        '''
        effects_dir = self._get_effects_dir()
        effect_index = self.effect_combo.currentIndex() + 1
        effect_text = self.effect_combo.currentText()
        effect_name = self._sanitize_effect_name(effect_text)

        '''
Формируем имя выходного файла: имя оригинала + название эффекта + расширение.
        '''
        orig_stem = Path(self.input_video).stem
        ext = Path(self.input_video).suffix
        output_name = f"{orig_stem}_{effect_name}{ext}"
        output_path = effects_dir / output_name

        # Отключаем элементы интерфейса на время обработки
        '''
Блокируем кнопку «Применить эффект», чтоб два раза не жали.
        '''
        try:
            self.apply_button.setDisabled(True)
        except Exception:
            pass
        '''
Блокируем остальные кнопки.
        '''
        try:
            self.create_gifs_button.setDisabled(True)
            self.convert_webm_button.setDisabled(True)
        except Exception:
            pass

        '''
Обнуляем прогресс и пишем «Обработка...».
        '''
        self.progress_bar.setValue(0)
        if hasattr(self, "status_label"):
            self.status_label.setText("Обработка...")

        # Создаём экземпляр EffectProcessor.
        # Поддерживаем оба варианта: правильный init или ошибочный init.
        '''
Создаём обработчик эффектов.
Если обычный конструктор не сработал,
пробуем «костыльный» init. Если ничего — ошибка.
        '''
        try:
            # Попытка обычной инициализации
            self.processor = EffectProcessor(str(self.input_video), str(output_path), effect_index)
        except TypeError:
            # Если сигнатура init отсутствует и используется метод init
            self.processor = EffectProcessor()
            if hasattr(self.processor, "init"):
                # Вызов пользовательского init (как в вашем примере)
                self.processor.init(str(self.input_video), str(output_path), effect_index)
            else:
                # Нечего делать — выбрасываем понятную ошибку
                QMessageBox.critical(self, "Ошибка", "Не удалось создать EffectProcessor: неверный конструктор.")
                self._enable_ui_after_processing()
                return

        # Подключаем сигналы
        '''
Если у процессора есть сигнал прогресса, подключаем его к нашему бару.
        '''
        if hasattr(self.processor, "progress"):
            try:
                self.processor.progress.connect(self.progress_bar.setValue)
            except Exception:
                pass

        # finished ожидается с текстовым сообщением
        '''
Когда процесс завершится — вызываем метод _on_effect_finished.
        '''
        self.processor.finished.connect(self._on_effect_finished)

        # Запускаем поток
        '''
Запускаем поток обработки.
        '''
        self.processor.start()

    # Вспомогательный метод для восстановления UI
    '''
Метод, чтобы вернуть кнопки обратно.
    '''
    def _enable_ui_after_processing(self):
        '''
Снимаем блокировку с кнопок и пишем «Готово».
        '''
        try:
            self.apply_button.setDisabled(False)
        except Exception:
            pass
        try:
            self.create_gifs_button.setDisabled(False)
            self.convert_webm_button.setDisabled(False)
        except Exception:
            pass
        if hasattr(self, "status_label"):
            self.status_label.setText("Готово")

    # Обработчик завершения
    '''
Когда обработка эффекта закончена.
    '''
    def _on_effect_finished(self, msg):
        # Включаем UI
        '''
Возвращаем кнопки, ставим прогресс на 100% и показываем результат.
        '''
        self._enable_ui_after_processing()
        self.progress_bar.setValue(100)
        # Отображаем сообщение от EffectProcessor (может быть текст ошибки или успешное сообщение)
        QMessageBox.information(self, "Результат", msg if msg else "Обработка завершена.")

        '''
Генерация GIF для всех эффектов.
        '''
    def create_gifs_from_effects(self):
        '''
Если видео нет — предупреждение.
        '''
        if not self.input_video:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите любое исходное видео.")
            return

        '''
Отключаем кнопки, сбрасываем прогресс и пишем «Создание GIF...».
        '''
        effects_dir = self._get_effects_dir()
        # Отключаем кнопки, запускаем поток
        self.create_gifs_button.setDisabled(True)
        self.convert_webm_button.setDisabled(True)
        self.apply_button.setDisabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Создание GIF...")


        '''
Создаём поток для генерации GIF.
        '''
        self._gif_thread = GifCreatorThread(
            effects_dir, self.canvas_size, self.fps, self.animation_length
        )
        '''
Подключаем прогресс, ошибки, завершение. Запускаем поток.
        '''
        self._gif_thread.progress.connect(self.progress_bar.setValue)
        self._gif_thread.error.connect(lambda msg: QMessageBox.warning(self, "Ошибка", msg))
        self._gif_thread.finished.connect(self._on_gif_finished)
        self._gif_thread.start()


        '''
Когда все гифки готовы.
        '''
    def _on_gif_finished(self, msg):
        '''
Включаем кнопки обратно,
прогресс на 100,
пишем «Готово» и показываем сообщение.
        '''
        self.create_gifs_button.setDisabled(False)
        self.convert_webm_button.setDisabled(False)
        self.apply_button.setDisabled(False)
        self.progress_bar.setValue(100)
        self.status_label.setText("Готово")
        QMessageBox.information(self, "Результат", msg)

        '''
Конвертация всех GIF в WEBM.
        '''
    def convert_all_gifs_to_webm(self):
        if not self.input_video:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите любое исходное видео.")
            return

        '''
Смотрим, есть ли папка с гифками. Если нет — инфа и выходим.
        '''
        effects_dir = self._get_effects_dir()
        gifs_dir = effects_dir / "GIFs"
        if not gifs_dir.exists():
            QMessageBox.information(self, "Инфо", f"Папка {gifs_dir} не найдена.")
            return

        # Отключаем кнопки и запускаем поток
        self.create_gifs_button.setDisabled(True)
        self.convert_webm_button.setDisabled(True)
        self.apply_button.setDisabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Конвертация GIF -> WEBM...")

        '''
Запускаем поток конвертации.
        '''
        self._webm_thread = WebmConverterThread(
            gifs_dir, self.canvas_size, self.fps, self.animation_length, self.max_size_kb
        )
        '''
Подключаем сигналы, запускаем поток.
        '''
        self._webm_thread.progress.connect(self.progress_bar.setValue)
        self._webm_thread.error.connect(lambda msg: QMessageBox.warning(self, "Ошибка", msg))
        self._webm_thread.finished.connect(self._on_webm_finished)
        self._webm_thread.start()

    def _on_webm_finished(self, msg):
        self.create_gifs_button.setDisabled(False)
        self.convert_webm_button.setDisabled(False)
        self.apply_button.setDisabled(False)
        self.progress_bar.setValue(100)
        self.status_label.setText("Готово")
        QMessageBox.information(self, "Результат", msg)
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoEffectsApp()
    window.show()
    sys.exit(app.exec_())

