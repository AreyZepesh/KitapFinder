from collections import defaultdict
from itertools import combinations
from tqdm import tqdm
import cv2
import numpy as np
from models import ShopCard
import sys

def find_duplicate_via_hash(img_bytes1: bytes, img_bytes2: bytes, **kwargs) -> bool:
    """Сравниваем хеш двух байтмассивов изображение, возвращает True если совпадают"""
    import hashlib
    return hashlib.md5(img_bytes1).hexdigest() == hashlib.md5(img_bytes2).hexdigest()

def _image_from_bytes(img_bytes: bytes):
    """Получаем изображение в формате для OpenCV из байтов"""
    return cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR )

def find_dublicate_via_opencv(img_bytes1: bytes, img_bytes2: bytes, method = "akaze", reference_score = 0.5) -> bool:
    """Сравнение двух изображений, возвращает True если считает их похожими. \n
    Порог (reference_score) можно подобрать экспериментально, для каждого метода эффективны разные: \n
    >0.3 — вероятно, то же изображение \n
    >0.6 — почти точно одно и то же, независимо от поворота или фона\n\n
    method: 'orb' | 'flann' | 'sift' | 'akaze' | 'brisk'\n"""
    
    # Получаем изображение из байтов
    img1 = _image_from_bytes(img_bytes1)
    img2 = _image_from_bytes(img_bytes2)

    # В зависимости от выбранного медота выбираются параметры
    if method == "sift":
        detector = cv2.SIFT.create()
        norm_type = cv2.NORM_L2
    elif method == "akaze":
        detector = cv2.AKAZE.create()
        norm_type = cv2.NORM_HAMMING
    elif method == "brisk":
        detector = cv2.BRISK.create()
        norm_type = cv2.NORM_HAMMING
    else:  # orb / flann по умолчанию
        detector = cv2.ORB.create(nfeatures=1000)
        norm_type = cv2.NORM_HAMMING

    # Отправляет изображения на первичную обработку детектором
    kp1, des1 = detector.detectAndCompute(img1, None)
    kp2, des2 = detector.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        return False

    matches = []
    # Выбор матчера, для каждого метода свой подход
    if method == "flann":
        # FLANN для бинарных дескрипторов (LSH)
        FLANN_INDEX_LSH = 6
        index_params = dict(algorithm=FLANN_INDEX_LSH, table_number=6, key_size=12, multi_probe_level=1)
        search_params = dict(checks=50)
        matcher = cv2.FlannBasedMatcher(index_params, search_params)
        # knnMatch -> список списков
        raw = matcher.knnMatch(des1, des2, k=2)
        # safety: каждый элемент может быть не длины 2 в редких случаях
        for pair in raw:
            if len(pair) < 2:
                continue
            m, n = pair[0], pair[1]
            if m.distance < 0.75 * n.distance:
                matches.append(m)

    elif method == "sift":
        # SIFT -> используем knn + ratio test
        bf = cv2.BFMatcher(norm_type)
        raw = bf.knnMatch(des1, des2, k=2)
        for pair in raw:
            if len(pair) < 2:
                continue
            m, n = pair[0], pair[1]
            if m.distance < 0.75 * n.distance:
                matches.append(m)

    else:
        # BFMatcher with crossCheck for ORB/AKAZE/BRISK (возвращает список DMatch)
        bf = cv2.BFMatcher(norm_type, crossCheck=True)
        raw = bf.match(des1, des2)
        # raw уже список одиночных DMatch, используем их напрямую
        matches = raw

    if not matches:
        return False

    # Нормализуем по количеству ключевых точек
    current_score  = len(matches) / max(len(kp1), len(kp2))
    # Сравниваем с референсным значением, если входит True
    if current_score >= reference_score:
        return True
    else:
        return False

def _connected_indices(items, func, **kwargs) -> list[list]:
    """Функция-обертка, попарно отправляет объекты в функции сравнений. \n
    Возвращает список списков индексов похожих изображений \n
    TODO использовать и возвращать не индексы, а артикли из самих карточек?
    """
    n = len(items)
    connections = {i: set() for i in range(n)}
    detected = set()  # сюда будем записывать все j, для которых уже найдено совпадение

    # проверяем все пары
    # for (i, j) in combinations(range(n), 2):
    for (i, j) in tqdm(combinations(range(n), 2), 
                       ncols=80, 
                       total=n*(n-1)//2, 
                       desc=f"{items[0].store}",
                       leave=False,
                       ):
        # если j уже был в найденных совпадениях — пропускаем
        # if j in detected:
        #     continue

        if items[i].cover_bytes is None or items[j].cover_bytes is None:
            continue
        
        if func(items[i].cover_bytes, items[j].cover_bytes, **kwargs):
            connections[i].add(j)
            connections[j].add(i)
            detected.add(j)  # запоминаем, что j уже нашёл совпадение

    # ищем связанные компоненты (через DFS)
    visited = set()
    groups = []

    for i in range(n):
        if i not in visited:
            stack = [i]
            group = set()
            while stack:
                node = stack.pop()
                if node not in visited:
                    visited.add(node)
                    group.add(node)
                    stack.extend(connections[node])
            if len(group) > 1:
                groups.append(sorted(group))

    return groups

def get_cleaned_list(price_cards: list[ShopCard], duplicates: list[list]) -> list[ShopCard]:
    """Очищаем карточкки цен (первый список) от дубликатов (список списков с индексом). \n
    Возвращает сортированный по цене список \n
    Между поиском дубликатов и этой функцией не должно быть сортировки списка карточек, 
    иначе индексы не будут соответсвовать нужной карточке \n
    TODO"""
    detected = []
    opt_cards = []
    
    for pull in duplicates:
        for index in pull:
            detected.append(index)
        opt_cards.append(price_cards[pull[0]])

    for index, price_card in enumerate(price_cards):
        if index not in detected:
            opt_cards.append(price_card)
            
    return sorted(opt_cards, key=lambda b: b.price)

def optimize_stores_by_cover(data: list[ShopCard]):
    # Разбиваем цены по магазинам
    groups = defaultdict(list)
    for price_card in data:
        groups[f"{price_card.store}_{price_card.type_search}"].append(price_card)
    
    # Прогоняем данные по отдельным магизинам
    # for store, price_cards in groups.items():
    for store, price_cards in tqdm(groups.items(), 
                       ncols=80, 
                       desc=f"Оптимизация",
                       leave=False,
                       ):
        # Сортируем по возрастанию цены,
        price_cards = sorted(price_cards, key=lambda b: b.price) 

        # Прогоняем сравнение по хэшу
        duplicates = _connected_indices(price_cards, find_duplicate_via_hash)
        if duplicates != []:
            # заменяем исходный на очищенный от дубликатов список
            price_cards = get_cleaned_list(price_cards, duplicates)

        # сравнение и оптимизации с высокими требованиями к железу - только на основном компе с виндой
        # TODO не забыть убрать, если будет железо мощнее
        if sys.platform == "win32":
            # Прогоняем сравнение через OpenCV
            duplicates = _connected_indices(price_cards, find_dublicate_via_opencv, 
                                            # **{"method": "akaze", "reference_score": 0.5}
                                            )
            if duplicates != []:
                # заменяем исходный на очищенный от дубликатов список
                price_cards = get_cleaned_list(price_cards, duplicates)
        # Заменяем список в основном словаре 
        groups[store] = price_cards

    # Приводим карточки к исходному виду и возвращаем
    new_data = []
    for price_cards in groups.values():
        new_data.extend( price_cards)

    return new_data

