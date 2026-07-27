books = []
# {'title': '', 'author': '', 'isbns': [], 'only_isbn': False},
# {'title': '', 'author': '', 'isbns': None, 'only_isbn': False},

books_Aizada = [
    {'title': 'Унесённые ветром', 'author': 'Митчелл', 'isbns': ['978-5-04-108998-6'], 'only_isbn': True},

    # {'title': 'Жизнь моя стала фантастическая', 'author': 'Чуковский', 'isbns': ['978-5-389-22573-2'], 'only_isbn': False}, #6500
    # {'title': 'Нужно быть благодарным судьбе', 'author': 'Чуковский', 'isbns': ['978-5-389-22978-5'], 'only_isbn': False},

    # {'title': 'Сияние', 'author': 'Кинг', 'isbns': ['978-5-17-133880-0'], 'only_isbn': True},
    # {'title': 'Доктор Сон', 'author': 'Кинг', 'isbns': ['978-5-17-134431-3'], 'only_isbn': True},
    # {'title': 'Сияние', 'author': 'Кинг', 'isbns': ['978-5-17-133880-0'], 'only_isbn': False},
    # {'title': 'Доктор Сон', 'author': 'Кинг', 'isbns': ['978-5-17-134431-3'], 'only_isbn': False},

    {'title': 'Приговор', 'author': 'Отохико Кага', 'isbns': ['978-5-89332-370-2'], 'only_isbn': True},
    # {'title': 'Приговор', 'author': 'Отохико Кага', 'isbns': ['978-5-89332-370-2'], 'only_isbn': False, 'need_check_author': True},
    ]

books_zero_priority = [
    {'title': 'Восстание безумных богов. Магия крови', 'author': 'Перумов', 'isbns': ['978-5-222-41915-1'], 'only_isbn': False},

    {'title': 'Слимперия', 'author': 'Бабкин', 'isbns': ['5-93556-229-4'], 'only_isbn': False},

    {'title': 'Мы. Бич Божий', 'author': 'Замятин', 'isbns': ['978-5-389-20387-7'], 'only_isbn': True},

    {'title': 'Пожиратель душ. Об ангелах демонах и потусторонних кошмарах', 'author': 'Каттнер Генри', 'isbns': ['978-5-389-22220-5'], 'only_isbn': False},

    {'title': '1984. Скотный двор. Да здравствует фикус!', 'author': 'Оруэлл', 'isbns': ['978-5-17-164053-8'], 'only_isbn': True},

    {'title': 'Занимательная наука. Физика. Механика. Астрономия', 'author': 'Перельман', 'isbns': ['978-5-389-24268-5'], 'only_isbn': False},

    {'title': 'О дивный новый мир. Остров. Возвращение в дивный новый мир', 'author': 'Хаксли', 'isbns': ['978-5-17-160649-7'], 'only_isbn': True},

    {'title': 'Последний мятеж', 'author': 'Щепетов Сергей', 'isbns': ['5-9717-0089-8'], 'only_isbn': False},
    ]

books1_to_complete_series = [
    {'title': 'Закон девяток', 'author': 'Гудкайнд', 'isbns': None, 'only_isbn': False},

    {'title': 'Душа Бога. Том 1', 'author': 'Перумов', 'isbns': ['978-5-04-110924-0'], 'only_isbn': False},
    {'title': 'Душа Бога', 'author': 'Перумов', 'isbns': ['978-5-04-110924-0'], 'only_isbn': False},

    {'title': 'Ночная стража', 'author': 'Пратчетт', 'isbns': ['978-5-699-52239-2'], 'only_isbn': False, 'alt_author': 'Pratchett', 'need_check_author': False},
    {'title': 'Незримые Академики', 'author': 'Пратчетт', 'isbns': ['978-5-699-69984-1'], 'only_isbn': False, 'alt_author': 'Pratchett', 'need_check_author': False},
    {'title': 'Наука Плоского мира. Книга 3. Часы Дарвина', 'author': 'Пратчетт', 'isbns': ['978-5-699-89838-1'], 'only_isbn': False, 'alt_author': 'Pratchett', 'need_check_author': False},

    {'title': 'Ветер и Правда', 'author': 'Сандерсон', 'isbns': ['978-5-389-30822-0'], 'only_isbn': True},
    {'title': 'Ветер и Правда. Том 2', 'author': 'Сандерсон', 'isbns': ['978-5-389-30822-0'], 'only_isbn': False},

    {'title': 'Падение Левиафана', 'author': 'Кори', 'isbns': ['978-5-389-28641-2'], 'only_isbn': False},
    {'title': 'Легион памяти', 'author': 'Кори', 'isbns': ['978-5-389-28642-9'], 'only_isbn': False},

    {'title': 'Кровавая Роза', 'author': 'Имс', 'isbns': ['978-5-389-16829-9'], 'only_isbn': False},

    {'title': 'Золотой сын', 'author': 'Браун', 'isbns': ['978-5-389-08460-5'], 'only_isbn': False},

    {'title': 'Корабль отплывает в полночь', 'author': 'Лейбер', 'isbns': ['978-5-389-17575-4'], 'only_isbn': False},
    {'title': 'Ведьма. Матерь Тьмы', 'author': 'Лейбер', 'isbns': ['978-5-389-32144-1'], 'only_isbn': False},

    {'title': 'Мистические истории. Похищенные сердца', 'author': None, 'isbns': ['978-5-389-27312-2'], 'only_isbn': False},

    {'title': 'Распознавание образов. Страна призраков. Нулевое досье', 'author': 'Гибсон', 'isbns': ['978-5-389-31974-5'], 'only_isbn': False},
    ]

books2_optional_old_authors = [
    # Асприн
    {'title': 'Шуттовская рота', 'author': 'Асприн', 'isbns': ['978-5-17-151818-9'], 'only_isbn': True},
    {'title': 'Вся Шуттовская рать', 'author': 'Асприн', 'isbns': ['978-5-17-151819-6'], 'only_isbn': True},

    # Аберкромби
    {'title': 'Острые края', 'author': 'Аберкромби', 'isbns': ['978-5-04-118152-9'], 'only_isbn': False, 'need_check_author': True},

    
    # Стейвли
    {'title': 'Присягнувшая Черепу', 'author': 'Стейвли', 'isbns': ['978-5-389-21765-2'], 'only_isbn': False},
    {'title': 'На руинах империи', 'author': 'Стейвли', 'isbns': ['978-5-389-23155-9'], 'only_isbn': False},
    ]

books_Duma = [# Дюма
    {'title': 'Три мушкетера', 'author': 'Дюма', 'isbns': ['978-5-389-19881-4'], 'only_isbn': True},
    {'title': 'Двадцать лет спустя', 'author': 'Дюма', 'isbns': ['978-5-389-21145-2'], 'only_isbn': True},
    {'title': 'Виконт де Бражелон, или Еще десять лет спустя', 'author': 'Дюма', 'isbns': ['978-5-389-24464-1'], 'only_isbn': True},
]

books_Sanderson_extended = [# Сандерсон
    {'title': 'Устремленная в небо', 'author': 'Сандерсон', 'isbns': ['978-5-389-16425-3'], 'only_isbn': False},
    {'title': 'Видящая звезды', 'author': 'Сандерсон', 'isbns': ['978-5-389-18074-1'], 'only_isbn': False},
    {'title': 'Цитоник', 'author': 'Сандерсон', 'isbns': ['978-5-389-23598-4'], 'only_isbn': False},
    {'title': 'Звездная Эскадрилья', 'author': 'Сандерсон', 'isbns': ['978-5-389-26184-6'], 'only_isbn': False},
    {'title': 'Непокорные', 'author': 'Сандерсон', 'isbns': ['978-5-389-30469-7'], 'only_isbn': False},
    {'title': 'Талант под прикрытием', 'author': 'Сандерсон', 'isbns': ['978-5-389-27681-9'], 'only_isbn': False},
    {'title': 'Киборги Нотариуса', 'author': 'Сандерсон', 'isbns': ['978-5-389-27682-6'], 'only_isbn': False},
    {'title': 'Рыцари Кристаллии', 'author': 'Сандерсон', 'isbns': ['978-5-389-27683-3'], 'only_isbn': False},
    ]

books_Erikson = [# Эриксон
    {'title': 'Охотники за костями', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},
    {'title': 'Буря Жнеца', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},
    {'title': 'Дань псам', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},
    {'title': 'Пыль грёз', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},
    {'title': 'Пыль Снов', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},
    {'title': 'Увечный бог', 'author': 'Эриксон', 'isbns': [], 'only_isbn': False},
    {'title': 'Кузница тьмы', 'author': 'Эриксон', 'isbns': ['978-5-389-23072-9'], 'only_isbn': False},
    {'title': 'Бог не желает', 'author': 'Эриксон', 'isbns': ['978-5-389-25785-6'], 'only_isbn': False},    
]

books_kamsha = [# Камша
    {'title': 'Кровь заката', 'author': 'Камша', 'isbns': None, 'only_isbn': False},
    {'title': 'Довод королей', 'author': 'Камша', 'isbns': None, 'only_isbn': False},
    {'title': 'Башня ярости. Чёрные маки', 'author': 'Камша', 'isbns': None, 'only_isbn': False},
    {'title': 'Башня ярости. Всходы ветра', 'author': 'Камша', 'isbns': None, 'only_isbn': False},
    ]

books_Pratchett_extended = [# Пратчетт
    {'title': 'Последний герой. Сказание о Плоском мире', 'author': 'Пратчетт', 'isbns': ['5-699-17413-3', '978-5-699-17413-3'], 'only_isbn': False, 'alt_author': 'Pratchett', 'need_check_author': False},
    {'title': 'Страта', 'author': 'Пратчетт', 'isbns': ['978-5-889-23131-8', '978-5-699-23137-9'], 'only_isbn': False, 'alt_author': 'Pratchett', 'need_check_author': False},
    {'title': 'Только ты можешь спасти человечество', 'author': 'Пратчетт', 'isbns': ['978-5-699-33519-0'], 'only_isbn': False},
    {'title': 'Джонни и мертвецы', 'author': 'Пратчетт', 'isbns': ['978-5-699-33898-6'], 'only_isbn': False},
    {'title': 'Джонни и бомба', 'author': 'Пратчетт', 'isbns': ['978-5-699-34451-2'], 'only_isbn': False},
    {'title': 'Угонщики', 'author': 'Пратчетт', 'isbns': ['978-5-699-31259-7'], 'only_isbn': False},
    {'title': 'Землекопы', 'author': 'Пратчетт', 'isbns': ['978-5-699-31257-3'], 'only_isbn': False},
    {'title': 'Крылья', 'author': 'Пратчетт', 'isbns': ['978-5-699-31263-4'], 'only_isbn': False},
    ]

books_McCaffrey = [# Маккефри
    {'title': 'Глаз Дракона', 'author': 'Маккефри', 'isbns': ['5-699-07904-1'], 'only_isbn': False},
    {'title': 'Дельфины Перна', 'author': 'Маккефри', 'isbns': ['5-699-10394-5'], 'only_isbn': False},
    {'title': 'Драконий родич', 'author': 'Маккефри', 'isbns': ['5-699-10083-0'], 'only_isbn': False},
    {'title': 'Драконье пламя', 'author': 'Маккефри', 'isbns': ['978-5-699-30664-0'], 'only_isbn': False},
    {'title': 'Кровь драконов', 'author': 'Маккефри', 'isbns': ['5-699-16054-X'], 'only_isbn': False},
    {'title': 'Мастер-арфист', 'author': 'Маккефри', 'isbns': ['5-699-15085-4'], 'only_isbn': False},
    {'title': 'Небеса Перна', 'author': 'Маккефри', 'isbns': ['5-699-15972-X'], 'only_isbn': False},
    {'title': 'Хроники Перна: Первое падение', 'author': 'Маккефри', 'isbns': ['5-699-13482-4'], 'only_isbn': False},
    ]

books_mcCammon = [# Маккаммон
    {'title': 'Слышащий', 'author': 'Маккаммон', 'isbns': ['978-5-389-16149-8'], 'only_isbn': False},
    {'title': 'Они жаждут', 'author': 'Маккаммон', 'isbns': ['978-5-389-20942-8'], 'only_isbn': False},
    {'title': 'Зов ночной птицы', 'author': 'Маккаммон', 'isbns': ['978-5-389-16150-4'], 'only_isbn': False},
    ]

books_Feist = [# Фэйст
    {'title': 'Дочь Империи', 'author': 'Фэйст', 'isbns': ["5-7684-0556-9"], 'only_isbn': False},
    {'title': 'Пленник Империи', 'author': 'Фэйст', 'isbns': ["5-7684-0565-8"], 'only_isbn': False},
    {'title': 'Слуга Империи', 'author': 'Фэйст', 'isbns': ["5-7684-0561-5"], 'only_isbn': False},
    {'title': 'Воин Империи', 'author': 'Фэйст', 'isbns': ["5-7684-0370-1"], 'only_isbn': False},
    {'title': 'Хозяйка Империи', 'author': 'Фэйст', 'isbns': ["5-7684-0394-9"], 'only_isbn': False},
    ]

books_brast = [# Браст
    {'title': 'Влад Талтош. Том 1', 'author': 'Браст', 'isbns': ["978-5-04-211206-5"], 'only_isbn': False},
    {'title': 'Влад Талтош. Том 2', 'author': 'Браст', 'isbns': ["978-5-04-212675-8"], 'only_isbn': False},
    {'title': 'Влад Талтош. Том 3', 'author': 'Браст', 'isbns': ["978-5-04-212678-9"], 'only_isbn': False},
    {'title': 'Влад Талтош', 'author': 'Браст', 'isbns': ["978-5-04-211206-5"], 'only_isbn': True},
    {'title': 'Влад Талтош', 'author': 'Браст', 'isbns': ["978-5-04-212675-8"], 'only_isbn': True},
    {'title': 'Влад Талтош', 'author': 'Браст', 'isbns': ["978-5-04-212678-9"], 'only_isbn': True},
        ] 

books_pehov = [
    {'title': 'Аутодафе', 'author': 'Пехов', 'isbns': ['978-5-00242-197-8'], 'only_isbn': True},
    {'title': 'Золотые костры', 'author': 'Пехов', 'isbns': ['978-5-00242-243-2'], 'only_isbn': True},
    {'title': 'Проклятый горн', 'author': 'Пехов', 'isbns': [], 'only_isbn': False},
    {'title': 'Крадущийся в тени', 'author': 'Пехов', 'isbns': ['978-5-00242-011-7'], 'only_isbn': True},
    {'title': 'Джанга с тенями', 'author': 'Пехов', 'isbns': ['978-5-00242-027-8'], 'only_isbn': True},
    {'title': 'Вьюга теней', 'author': 'Пехов', 'isbns': ['978-5-00242-090-2'], 'only_isbn': True},
    {'title': 'Искатели ветра', 'author': 'Пехов', 'isbns': ['978-5-00242-105-3'], 'only_isbn': True},
    {'title': 'Ветер Полыни', 'author': 'Пехов', 'isbns': ['978-5-00242-171-8'], 'only_isbn': True},
    ]

books_salvatore = [
    {'title': 'Легенда о Темном эльфе', 'author': 'Сальваторе', 'isbns': 
        ['978-5-91878-101-2', "978-5-91878-210-1", '978-5-91878-284-2', '978-5-91878-365-8', '978-5-91878-462-4', '978-5-91878-463-1', '978-5-91878-464-8'], 
        'only_isbn': False},
    {'title': 'Сальваторе', 'author': 'Сальваторе', 'isbns': 
        ['978-5-91878-101-2', "978-5-91878-210-1", '978-5-91878-284-2', '978-5-91878-365-8', '978-5-91878-462-4', '978-5-91878-463-1', '978-5-91878-464-8'], 
        'only_isbn': True},
    # {'title': 'Легенда о Темном эльфе. Книга 1. Отступник. Изгнанник. Воин', 'author': 'Сальваторе', 'isbns': ['978-5-91878-101-2'], 'only_isbn': False},
    # {'title': 'Легенда о Темном Эльфе. Книга III', 'author': 'Сальваторе', 'isbns': ["978-5-91878-210-1"], 'only_isbn': False},
    # {'title': 'Легенда о Темном Эльфе. Книга 3', 'author': 'Сальваторе', 'isbns': ["978-5-91878-210-1"], 'only_isbn': False},
    # {'title': 'Легенда о Темном Эльфе. Темное наследие', 'author': 'Сальваторе', 'isbns': ["978-5-91878-210-1"], 'only_isbn': False},
    # {'title': 'Легенда о Темном Эльфе. Книга IV', 'author': 'Сальваторе', 'isbns': ['978-5-91878-284-2'], 'only_isbn': False},
    # {'title': 'Легенда о Темном Эльфе. Книга 4', 'author': 'Сальваторе', 'isbns': ['978-5-91878-284-2'], 'only_isbn': False},
    # {'title': 'Легенда о Темном Эльфе. Книга V: Тысяча орков. Одинокий эльф. Два меча', 'author': 'Сальваторе', 'isbns': ['978-5-91878-365-8'], 'only_isbn': False},
    # {'title': 'Легенда о Темном Эльфе. Книга 5: Тысяча орков. Одинокий эльф. Два меча', 'author': 'Сальваторе', 'isbns': ['978-5-91878-365-8'], 'only_isbn': False},
    # {'title': 'Легенда о Темном Эльфе. Король орков. Король пиратов. Король Призраков', 'author': 'Сальваторе', 'isbns': ['978-5-91878-462-4'], 'only_isbn': False},
    # {'title': 'Король орков. Король пиратов. Король Призраков', 'author': 'Сальваторе', 'isbns': ['978-5-91878-462-4'], 'only_isbn': False},
    # {'title': 'Легенда о Темном Эльфе. Невервинтер. Том 1', 'author': 'Сальваторе', 'isbns': ['978-5-91878-463-1'], 'only_isbn': False},
    # {'title': 'Легенда о Темном Эльфе. Невервинтер. Том 2', 'author': 'Сальваторе', 'isbns': ['978-5-91878-464-8'], 'only_isbn': False},
    # {'title': 'Служитель кристалла. Заклятие короля-колдуна. Дорога Патриарха', 'author': 'Сальваторе', 'isbns': ['978-5-91878-465-5'], 'only_isbn': False},
        ]

books_bardugo = [
    # {'title': 'Шестерка воронов', 'author': 'Бардуго', 'isbns': ['978-5-17-108154-6'], 'only_isbn': False},
    {'title': 'Продажное королевство', 'author': 'Бардуго', 'isbns': ['978-5-17-108910-8'], 'only_isbn': True},
    # {'title': 'Тень и кость', 'author': 'Бардуго', 'isbns': ['978-5-17-105260-7'], 'only_isbn': False},
    # {'title': 'Штурм и буря', 'author': 'Бардуго', 'isbns': ['978-5-17-108603-9'], 'only_isbn': False},
    # {'title': 'Крах и восход', 'author': 'Бардуго', 'isbns': ['978-5-17-108822-4'], 'only_isbn': False},
    # {'title': 'Король шрамов', 'author': 'Бардуго', 'isbns': ['978-5-17-114497-5'], 'only_isbn': False},
    # {'title': 'Правление волков', 'author': 'Бардуго', 'isbns': ['978-5-17-138086-1'], 'only_isbn': False},
        ]

book_stasheff = [
    {'title': 'Зачарованный книжник. Здесь водятся чудовища', 'author': 'Сташеф', 'isbns': ['5-17-019151-0', '5-9577-0067-3'], 'only_isbn': False},
    {'title': 'Волшебник на пути. Последний путь чародея', 'author': 'Сташеф', 'isbns': ['5-17-037546-8', '5-9713-2303-2', '5-9578-4448-9'], 'only_isbn': False},
    {'title': 'Волшебник на пути', 'author': 'Сташеф', 'isbns': ['5-17-037546-8', '5-9713-2303-2', '5-9578-4448-9'], 'only_isbn': False},
    {'title': 'Последний путь чародея', 'author': 'Сташеф', 'isbns': ['5-17-037546-8', '5-9713-2303-2', '5-9578-4448-9'], 'only_isbn': False},
        ]

book_simons = [
    {'title': 'Илион. Олимп', 'author': 'Симмонс', 'isbns': ['978-5-17-108341-0', '978-5-389-33081-8'], 'only_isbn': False, 'need_check_author': True},
    {'title': 'Илион', 'author': 'Симмонс', 'isbns': ['978-5-389-21479-8'], 'only_isbn': False, 'need_check_author': True},
    {'title': 'Олимп', 'author': 'Симмонс', 'isbns': ['978-5-389-22285-4'], 'only_isbn': False, 'need_check_author': True},
    {'title': 'Мерзость', 'author': 'Симмонс', 'isbns': ['978-5-17-147158-3'], 'only_isbn': True},
    {'title': 'Неглубокая могила. Лютая зима. Круче некуда', 'author': 'Симмонс', 'isbns': ['978-5-17-175636-9'], 'only_isbn': True},
    {'title': 'Дети Ночи. Песнь Кали', 'author': 'Симмонс', 'isbns': ['978-5-17-187347-9'], 'only_isbn': True},
    {'title': 'Друд, или Человек в чёрном', 'author': 'Симмонс', 'isbns': ['978-5-17-156919-8'], 'only_isbn': True},
    {'title': 'Утеха падали', 'author': 'Симмонс', 'isbns': ['978-5-17-180042-0'], 'only_isbn': True},
        ]

books_stars_new_fantastic = [
    {'title': 'Милость богов', 'author': 'Кори', 'isbns': ['978-5-389-25565-4'], 'only_isbn': False},
    
    {'title': 'Водяной нож', 'author': 'Бачигалупи', 'isbns': ['978-5-389-25173-1'], 'only_isbn': False},
    {'title': 'Дети Морайбе', 'author': 'Бачигалупи', 'isbns': ['978-5-389-24983-7'], 'only_isbn': False},
    {'title': 'Разрушитель кораблей', 'author': 'Бачигалупи', 'isbns': ['978-5-389-24987-5'], 'only_isbn': False},

    {'title': 'Дом солнц', 'author': 'Рейнольдс', 'isbns': ['978-5-389-20484-3'], 'only_isbn': False},

    {'title': 'Империя тишины', 'author': 'Руоккио', 'isbns': ['978-5-389-16258-7'], 'only_isbn': False},
    {'title': 'Ревущая тьма', 'author': 'Руоккио', 'isbns': ['978-5-389-18304-9'], 'only_isbn': False},
    {'title': 'Демон в белом', 'author': 'Руоккио', 'isbns': ['978-5-389-19022-1'], 'only_isbn': False},
    {'title': 'Царства смерти', 'author': 'Руоккио', 'isbns': ['978-5-389-21797-3'], 'only_isbn': False},
    {'title': 'Прах человеческий', 'author': 'Руоккио', 'isbns': ['978-5-389-23874-9'], 'only_isbn': False},

    {'title': 'Берсеркер', 'author': 'Саберхаген', 'isbns': ['978-5-389-28167-7'], 'only_isbn': True},
    {'title': 'Маска Марса. Брат Берсеркер. Планета смерти', 'author': 'Саберхаген', 'isbns': ['978-5-389-28167-7'], 'only_isbn': False},
    {'title': 'Берсеркер', 'author': 'Саберхаген', 'isbns': ['978-5-389-28485-2'], 'only_isbn': True},
    {'title': 'Непобедимый мутант. Заклятый враг. База берсеркеров', 'author': 'Саберхаген', 'isbns': ['978-5-389-28485-2'], 'only_isbn': False},
    {'title': 'Берсеркер', 'author': 'Саберхаген', 'isbns': ['978-5-389-28486-9'], 'only_isbn': True},
    {'title': 'Трон берсеркера. Синяя смерть. Техника обмана', 'author': 'Саберхаген', 'isbns': ['978-5-389-28486-9'], 'only_isbn': False},

    {'title': 'Хроники железных драконов', 'author': 'Суэнвик', 'isbns': ['978-5-389-08947-1'], 'only_isbn': False},
    {'title': 'Мать железного дракона', 'author': 'Суэнвик', 'isbns': ['978-5-389-18574-6'], 'only_isbn': False},
]

books_stars_new_fantasy = [
    {'title': 'Тень среди лета. Предательство среди зимы', 'author': 'Абрахам', 'isbns': ['978-5-389-24960-8'], 'only_isbn': False},
    {'title': 'Война среди осени. Расплата за весну', 'author': 'Абрахам', 'isbns': ['978-5-389-24961-5'], 'only_isbn': False},
    {'title': 'Путь дракона', 'author': 'Абрахам', 'isbns': ['978-5-389-24963-9'], 'only_isbn': True},
    {'title': 'Королевская кровь', 'author': 'Абрахам', 'isbns': ['978-5-389-24964-6'], 'only_isbn': True},
    {'title': 'Закон тирана', 'author': 'Абрахам', 'isbns': ['978-5-389-24965-3'], 'only_isbn': True},

    # Незакончено, дальше нет
    {'title': 'Восхождение Сенлина', 'author': 'Бэнкрофт', 'isbns': ['978-5-389-15010-2'], 'only_isbn': False},
    {'title': 'Рука Сфинкса', 'author': 'Бэнкрофт', 'isbns': ['978-5-389-16115-3'], 'only_isbn': False},
    {'title': 'Король отверженных', 'author': 'Бэнкрофт', 'isbns': ['978-5-389-18526-5'], 'only_isbn': False},

    {'title': 'Тирания Ночи', 'author': 'Кук', 'isbns': ['978-5-389-07266-4'], 'only_isbn': False},
    {'title': 'Властелин Безмолвного Королевства', 'author': 'Кук', 'isbns': ['978-5-389-07265-7'], 'only_isbn': False},
    {'title': 'Покоритесь воле Ночи', 'author': 'Кук', 'isbns': ['978-5-389-10267-5'], 'only_isbn': False},
    {'title': 'Жестокие игры богов', 'author': 'Кук', 'isbns': ['978-5-389-11726-6'], 'only_isbn': False},

    {'title': 'Милость королей', 'author': 'Лю', 'isbns': ['978-5-389-23695-0'], 'only_isbn': False},
    {'title': 'Стена Бурь', 'author': 'Лю', 'isbns': ['978-5-389-24835-'], 'only_isbn': False},
    {'title': 'Пустующий трон', 'author': 'Лю', 'isbns': ['978-5-389-25856-3'], 'only_isbn': False},
    {'title': 'Говорящие кости', 'author': 'Лю', 'isbns': ['978-5-389-27114-2'], 'only_isbn': False},
    
    {'title': 'Кровавый завет', 'author': 'Макклеллан', 'isbns': ['978-5-389-07270-1'], 'only_isbn': False},
    {'title': 'Кровавый поход', 'author': 'Макклеллан', 'isbns': ['978-5-389-07269-5'], 'only_isbn': False},
    {'title': 'Кровавая осень', 'author': 'Макклеллан', 'isbns': ['978-5-389-10393-1'], 'only_isbn': False},

    {'title': 'В тени молнии', 'author': 'Макклеллан', 'isbns': ['978-5-389-25017-8'], 'only_isbn': False},

    {'title': 'Меченый', 'author': 'Бретт', 'isbns': ['978-5-389-07780-5'], 'only_isbn': False},
    {'title': 'Копье пустыни', 'author': 'Бретт', 'isbns': ['978-5-389-08664-7'], 'only_isbn': False},
    {'title': 'Дневная битва', 'author': 'Бретт', 'isbns': ['978-5-389-08361-5'], 'only_isbn': False},
    {'title': 'Трон черепов', 'author': 'Бретт', 'isbns': ['978-5-389-12357-1'], 'only_isbn': False},
    {'title': 'Королева демонов', 'author': 'Бретт', 'isbns': ['978-5-389-13778-3'], 'only_isbn': False},
    ]

books3_optional_new_authors = [
    {'title': 'Украденный трон. Призыв. Маска призрака', 'author': 'Гейдер', 'isbns': ['978-5-389-19770-1'], 'only_isbn': False},

    {'title': 'Повелители DOOM', 'author': None, 'isbns': [], 'only_isbn': False},

    # {'title': 'Восставший из ада', 'author': 'Баркер', 'isbns': [], 'only_isbn': False},
    
    {'title': 'Нефритовый город', 'author': 'Фонда Ли', 'isbns': None, 'only_isbn': False},
    {'title': 'Нефритовая война', 'author': 'Фонда Ли', 'isbns': None, 'only_isbn': False},
    {'title': 'Нефритовое наследие', 'author': 'Фонда Ли', 'isbns': None, 'only_isbn': False},

    # Квантрелл - Вышло только 3 на русском
    # {'title': 'Восхождение рейнджера', 'author': 'Квантрелл', 'isbns': ['978-5-17-168081-7'], 'only_isbn': False},
    # {'title': 'Империя праха', 'author': 'Квантрелл', 'isbns': ['978-5-17-168082-4'], 'only_isbn': False},
    # {'title': 'Сокровище богов', 'author': 'Квантрелл', 'isbns': ['978-5-17-168083-1'], 'only_isbn': False},

    # Уильямс - последний цикл переведен не полностью
    # {'title': 'Трон из костей дракона', 'author': 'Уильямс', 'isbns': ['978-5-04-112361-1', '978-5-04-113968-1'], 'only_isbn': False},
    # {'title': 'Скала Прощания', 'author': 'Уильямс', 'isbns': ['978-5-04-154811-7', '978-5-04-159321-6'], 'only_isbn': False},
    # {'title': 'Башня Зеленого Ангела', 'author': 'Уильямс', 'isbns': ['978-5-04-184848-4', '978-5-04-184847-7'], 'only_isbn': False},
    # # {'title': 'Корона из ведьминого дерева', 'author': 'Уильямс', 'isbns': ['978-5-04-100153-7', '978-5-04-100436-1'], 'only_isbn': False},
    # # {'title': 'Империя травы', 'author': 'Уильямс', 'isbns': ['978-5-04-110814-4', '978-5-04-111320-9'], 'only_isbn': False},
    # # {'title': 'Братья ветра', 'author': 'Уильямс', 'isbns': ['978-5-04-165825-0'], 'only_isbn': False},
    # # {'title': 'Сердце того, что было утеряно', 'author': 'Уильямс', 'isbns': ['978-5-04-160511-7'], 'only_isbn': False},

    # Кастелл
    # {'title': 'Творец Заклинаний', 'author': 'Кастелл', 'isbns': [], 'only_isbn': False},
    # {'title': 'Чёрная Тень', 'author': 'Кастелл', 'isbns': [], 'only_isbn': False},
    # {'title': 'Механическая птица', 'author': 'Кастелл', 'isbns': [], 'only_isbn': False},
    # {'title': 'Аббатство Теней', 'author': 'Кастелл', 'isbns': [], 'only_isbn': False},
    # {'title': 'Последний трюк', 'author': 'Кастелл', 'isbns': [], 'only_isbn': False},
    # {'title': 'Убийца королевы', 'author': 'Кастелл', 'isbns': [], 'only_isbn': False},
    # {'title': 'Путь аргоси', 'author': 'Кастелл', 'isbns': [], 'only_isbn': False},
    # {'title': 'Алый Крик', 'author': 'Кастелл', 'isbns': [], 'only_isbn': False},
    ]

books_mir_fant = [
    # {'title': 'Игра Эндера. Говорящий от Имени Мертвых', 'author': 'Кард', 'isbns': ['978-5-389-17596-9'], 'only_isbn': False},
    # {'title': 'Ксеноцид. Дети разума', 'author': 'Кард', 'isbns': ['978-5-389-17881-6'], 'only_isbn': False},
    
    {'title': 'Пересадочная станция', 'author': 'Саймак', 'isbns': ['978-5-389-18405-3'], 'only_isbn': True},
    {'title': 'Ветер чужого мира', 'author': 'Саймак', 'isbns': ['978-5-389-18403-9'], 'only_isbn': True},
    {'title': 'Прелесть', 'author': 'Саймак', 'isbns': ['978-5-389-18404-6'], 'only_isbn': True},
    {'title': 'Мастодония', 'author': 'Саймак', 'isbns': ['978-5-389-18401-5'], 'only_isbn': True},
    {'title': 'Братство талисмана', 'author': 'Саймак', 'isbns': ['978-5-389-18400-8'], 'only_isbn': True},
    {'title': 'Все ловушки Земли', 'author': 'Саймак', 'isbns': ['978-5-389-18402-2'], 'only_isbn': True},

    {'title': 'Паломничество на Землю', 'author': 'Шекли', 'isbns': ['978-5-389-15837-5'], 'only_isbn': True},
    {'title': 'Координаты чудес', 'author': 'Шекли', 'isbns': ['978-5-389-18047-5'], 'only_isbn': True},
]

book_new_russian = [
    {'title': 'Мистер Вечный Канун', 'author': 'Торин', 'isbns': ['978-5-00214-122-7', '978-5-00195-734-8', '978-5-00195-790-4'], 'only_isbn': False},
    {'title': 'Моё пост-имаго', 'author': 'Торин', 'isbns': ['978-5-00214-483-9'], 'only_isbn': False},

    {'title': 'Заступа: Все оттенки падали', 'author': 'Белов', 'isbns': ['978-5-17-163405-6'], 'only_isbn': False},
    {'title': 'Заступа: Чернее черного', 'author': 'Белов', 'isbns': ['978-5-17-170204-5'], 'only_isbn': False},
    {'title': 'Заступа: Грядущая тьма', 'author': 'Белов', 'isbns': ['978-5-17-177968-9'], 'only_isbn': False},

    {'title': 'Жнецы страданий', 'author': 'Харитонова', 'isbns': ['978-5-517-03107-5'], 'only_isbn': False},
    {'title': 'Наследники скорби', 'author': 'Харитонова', 'isbns': ['978-5-517-03108-2'], 'only_isbn': False},
    {'title': 'Пленники Раздора', 'author': 'Харитонова', 'isbns': ['978-5-517-03109-9'], 'only_isbn': False},

    {'title': 'Канашибари. Пока не погаснет последний фонарь', 'author': 'Шэн', 'isbns': ['978-5-35-310823-8'], 'only_isbn': True},
    {'title': 'Канашибари. Пока не погаснет последний фонарь', 'author': 'Шэн', 'isbns': ['978-5-353-10899-3'], 'only_isbn': True},
    {'title': 'Канашибари. Пока не погаснет последний фонарь', 'author': 'Шэн', 'isbns': ['978-5-353-10986-0'], 'only_isbn': True},
    {'title': 'Канашибари. Пока не погаснет последний фонарь', 'author': 'Шэн', 'isbns': ['978-5-353-11553-3'], 'only_isbn': True},
]

books_kristoff = [
    {'title': 'Империя вампиров', 'author': 'Кристофф', 'isbns': ['978-5-17-118802-3'], 'only_isbn': False},
    {'title': 'Империя проклятых', 'author': 'Кристофф', 'isbns': ['978-5-17-118809-2'], 'only_isbn': False},
    ]


# {'title': '', 'author': '', 'isbns': [], 'only_isbn': False},
# {'title': '', 'author': '', 'isbns': None, 'only_isbn': False},
books.extend(books1_to_complete_series)

# books.extend(books_zero_priority)
# books.extend(books2_optional_old_authors)

# books.extend(books_Duma)
# books.extend(books_Erikson)
# books.extend(books_kamsha)
# books.extend(books_McCaffrey)
# books.extend(books_mcCammon)
# books.extend(books_Feist)

# books.extend(books_Sanderson_extended)
# books.extend(books_Pratchett_extended)
# books.extend(books_brast)
# books.extend(book_simons)

# books.extend(books3_optional_new_authors)
# books.extend(books_stars_new_fantasy)
# books.extend(books_stars_new_fantastic)
# books.extend(books_mir_fant)
# books.extend(book_new_russian)
# books.extend(books_kristoff)

books.extend(books_pehov)
books.extend(book_stasheff)
books.extend(books_Aizada)
books.extend(books_salvatore)
books.extend(books_bardugo)

all_books = books

# all_books = []

# all_books.extend(book_new_russian)
# all_books.extend(books_kristoff)

# all_books.extend(books_stars_new_fantastic)
# all_books.extend(books_stars_new_fantasy)
# all_books.extend(books_mir_fant)
# all_books.extend(books3_optional_new_authors)