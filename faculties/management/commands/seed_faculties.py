"""
Management command to seed the faculties app with realistic test data.

Usage:
    python manage.py seed_faculties
"""

from django.core.management.base import BaseCommand
from faculties.models import (
    Faculty, FacultyAchievement,
    Department, DepartmentProgram, DepartmentSubject,
    DepartmentStaff, DepartmentPublication,
)


# Realistic Uzbek university faculty data
FACULTIES_DATA = [
    {
        'name_uz': "Kompyuter injiniringi fakulteti",
        'name_ru': "Факультет компьютерной инженерии",
        'name_en': "Faculty of Computer Engineering",
        'faculty_code': 'KI',
        'short_description_uz': "Zamonaviy axborot texnologiyalari va dasturiy ta'minot ishlab chiqish sohasida kadrlar tayyorlash.",
        'short_description_ru': "Подготовка кадров в области современных информационных технологий и разработки программного обеспечения.",
        'short_description_en': "Training specialists in modern information technologies and software development.",
        'description_uz': "<p>Kompyuter injiniringi fakulteti zamonaviy texnologiyalar asosida yuqori malakali mutaxassislar tayyorlaydi.</p>",
        'description_ru': "<p>Факультет компьютерной инженерии готовит высококвалифицированных специалистов на основе современных технологий.</p>",
        'description_en': "<p>The Faculty of Computer Engineering trains highly qualified specialists based on modern technologies.</p>",
        'dean_name_uz': "Abdullayev Sherzod Karimovich",
        'dean_name_ru': "Абдуллаев Шерзод Каримович",
        'dean_name_en': "Abdullayev Sherzod Karimovich",
        'phone': '+998 71 234 56 78',
        'email': 'ki@nuujf.uz',
        'office_location_uz': "A binosi, 3-qavat, 301-xona",
        'office_location_ru': "Здание А, 3 этаж, комната 301",
        'office_location_en': "Building A, 3rd floor, Room 301",
    },
    {
        'name_uz': "Iqtisodiyot fakulteti",
        'name_ru': "Факультет экономики",
        'name_en': "Faculty of Economics",
        'faculty_code': 'IQ',
        'short_description_uz': "Iqtisodiy soha bo'yicha zamonaviy bilim va ko'nikmalarni egallagan mutaxassislar tayyorlash.",
        'short_description_ru': "Подготовка специалистов с современными знаниями и навыками в экономической сфере.",
        'short_description_en': "Training specialists with modern knowledge and skills in the economic field.",
        'description_uz': "<p>Iqtisodiyot fakulteti bozor iqtisodiyoti sharoitida faoliyat yuritish uchun zarur bilimlarni beradi.</p>",
        'description_ru': "<p>Факультет экономики предоставляет необходимые знания для деятельности в условиях рыночной экономики.</p>",
        'description_en': "<p>The Faculty of Economics provides the necessary knowledge for activities in a market economy.</p>",
        'dean_name_uz': "Karimov Botir Rustamovich",
        'dean_name_ru': "Каримов Ботир Рустамович",
        'dean_name_en': "Karimov Botir Rustamovich",
        'phone': '+998 71 234 56 79',
        'email': 'iq@nuujf.uz',
        'office_location_uz': "B binosi, 2-qavat, 201-xona",
        'office_location_ru': "Здание B, 2 этаж, комната 201",
        'office_location_en': "Building B, 2nd floor, Room 201",
    },
    {
        'name_uz': "Huquqshunoslik fakulteti",
        'name_ru': "Юридический факультет",
        'name_en': "Faculty of Law",
        'faculty_code': 'HQ',
        'short_description_uz': "Huquqiy soha bo'yicha malakali kadrlar tayyorlash.",
        'short_description_ru': "Подготовка квалифицированных кадров в правовой сфере.",
        'short_description_en': "Training qualified professionals in the legal field.",
        'description_uz': "<p>Huquqshunoslik fakulteti davlat va jamiyat manfaatlarini himoya qiladigan yuristlarni tayyorlaydi.</p>",
        'description_ru': "<p>Юридический факультет готовит юристов, защищающих интересы государства и общества.</p>",
        'description_en': "<p>The Faculty of Law trains lawyers who protect the interests of the state and society.</p>",
        'dean_name_uz': "Rahimov Javlon Saidovich",
        'dean_name_ru': "Рахимов Жавлон Саидович",
        'dean_name_en': "Rahimov Javlon Saidovich",
        'phone': '+998 71 234 56 80',
        'email': 'hq@nuujf.uz',
        'office_location_uz': "C binosi, 1-qavat, 105-xona",
        'office_location_ru': "Здание C, 1 этаж, комната 105",
        'office_location_en': "Building C, 1st floor, Room 105",
    },
    {
        'name_uz': "Pedagogika fakulteti",
        'name_ru': "Педагогический факультет",
        'name_en': "Faculty of Pedagogy",
        'faculty_code': 'PD',
        'short_description_uz': "Ta'lim sohasida zamonaviy pedagogik kadrlar tayyorlash.",
        'short_description_ru': "Подготовка современных педагогических кадров в сфере образования.",
        'short_description_en': "Training modern pedagogical staff in the field of education.",
        'description_uz': "<p>Pedagogika fakulteti ta'lim tizimini rivojlantirishga hissa qo'shadigan pedagoglarni tayyorlaydi.</p>",
        'description_ru': "<p>Педагогический факультет готовит педагогов, вносящих вклад в развитие системы образования.</p>",
        'description_en': "<p>The Faculty of Pedagogy trains educators who contribute to the development of the education system.</p>",
        'dean_name_uz': "Toshmatov Alisher Bahodirovich",
        'dean_name_ru': "Тошматов Алишер Баходирович",
        'dean_name_en': "Toshmatov Alisher Bakhodirovich",
        'phone': '+998 71 234 56 81',
        'email': 'pd@nuujf.uz',
        'office_location_uz': "D binosi, 2-qavat, 210-xona",
        'office_location_ru': "Здание D, 2 этаж, комната 210",
        'office_location_en': "Building D, 2nd floor, Room 210",
    },
    {
        'name_uz': "Filologiya fakulteti",
        'name_ru': "Филологический факультет",
        'name_en': "Faculty of Philology",
        'faculty_code': 'FL',
        'short_description_uz': "Til va adabiyot sohasida yuqori malakali filologlar tayyorlash.",
        'short_description_ru': "Подготовка высококвалифицированных филологов в области языка и литературы.",
        'short_description_en': "Training highly qualified philologists in the field of language and literature.",
        'description_uz': "<p>Filologiya fakulteti o'zbek va jahon adabiyotini o'rganishga bag'ishlangan.</p>",
        'description_ru': "<p>Филологический факультет посвящен изучению узбекской и мировой литературы.</p>",
        'description_en': "<p>The Faculty of Philology is dedicated to the study of Uzbek and world literature.</p>",
        'dean_name_uz': "Mamatov Dilshod Anvarovich",
        'dean_name_ru': "Маматов Дилшод Анварович",
        'dean_name_en': "Mamatov Dilshod Anvarovich",
        'phone': '+998 71 234 56 82',
        'email': 'fl@nuujf.uz',
        'office_location_uz': "E binosi, 3-qavat, 315-xona",
        'office_location_ru': "Здание E, 3 этаж, комната 315",
        'office_location_en': "Building E, 3rd floor, Room 315",
    },
    {
        'name_uz': "Tabiiy fanlar fakulteti",
        'name_ru': "Факультет естественных наук",
        'name_en': "Faculty of Natural Sciences",
        'faculty_code': 'TF',
        'short_description_uz': "Fizika, kimyo va biologiya sohasida ilmiy kadrlar tayyorlash.",
        'short_description_ru': "Подготовка научных кадров в области физики, химии и биологии.",
        'short_description_en': "Training scientific staff in physics, chemistry and biology.",
        'description_uz': "<p>Tabiiy fanlar fakulteti fundamental fanlar bo'yicha chuqur bilim beradi.</p>",
        'description_ru': "<p>Факультет естественных наук обеспечивает глубокие знания по фундаментальным наукам.</p>",
        'description_en': "<p>The Faculty of Natural Sciences provides in-depth knowledge of fundamental sciences.</p>",
        'dean_name_uz': "Normatov Ulugbek Sobirvich",
        'dean_name_ru': "Норматов Улугбек Собирвич",
        'dean_name_en': "Normatov Ulugbek Sobirovich",
        'phone': '+998 71 234 56 83',
        'email': 'tf@nuujf.uz',
        'office_location_uz': "F binosi, 1-qavat, 110-xona",
        'office_location_ru': "Здание F, 1 этаж, комната 110",
        'office_location_en': "Building F, 1st floor, Room 110",
    },
    {
        'name_uz': "Xalqaro munosabatlar fakulteti",
        'name_ru': "Факультет международных отношений",
        'name_en': "Faculty of International Relations",
        'faculty_code': 'XM',
        'short_description_uz': "Xalqaro siyosat va diplomatiya sohasida kadrlar tayyorlash.",
        'short_description_ru': "Подготовка кадров в области международной политики и дипломатии.",
        'short_description_en': "Training specialists in international politics and diplomacy.",
        'description_uz': "<p>Xalqaro munosabatlar fakulteti diplomatiya va xalqaro huquq bo'yicha mutaxassislar tayyorlaydi.</p>",
        'description_ru': "<p>Факультет международных отношений готовит специалистов по дипломатии и международному праву.</p>",
        'description_en': "<p>The Faculty of International Relations trains specialists in diplomacy and international law.</p>",
        'dean_name_uz': "Yusupov Sardor Ilhomovich",
        'dean_name_ru': "Юсупов Сардор Илхомович",
        'dean_name_en': "Yusupov Sardor Ilkhomovich",
        'phone': '+998 71 234 56 84',
        'email': 'xm@nuujf.uz',
        'office_location_uz': "G binosi, 4-qavat, 401-xona",
        'office_location_ru': "Здание G, 4 этаж, комната 401",
        'office_location_en': "Building G, 4th floor, Room 401",
    },
    {
        'name_uz': "Matematika fakulteti",
        'name_ru': "Факультет математики",
        'name_en': "Faculty of Mathematics",
        'faculty_code': 'MT',
        'short_description_uz': "Amaliy va nazariy matematika sohasida mutaxassislar tayyorlash.",
        'short_description_ru': "Подготовка специалистов в области прикладной и теоретической математики.",
        'short_description_en': "Training specialists in applied and theoretical mathematics.",
        'description_uz': "<p>Matematika fakulteti zamonaviy matematik usullarni qo'llash bo'yicha bilim beradi.</p>",
        'description_ru': "<p>Факультет математики обеспечивает знания по применению современных математических методов.</p>",
        'description_en': "<p>The Faculty of Mathematics provides knowledge on the application of modern mathematical methods.</p>",
        'dean_name_uz': "Xolmatov Firdavs Shuhratovich",
        'dean_name_ru': "Холматов Фирдавс Шухратович",
        'dean_name_en': "Kholmatov Firdavs Shukhratovich",
        'phone': '+998 71 234 56 85',
        'email': 'mt@nuujf.uz',
        'office_location_uz': "H binosi, 2-qavat, 205-xona",
        'office_location_ru': "Здание H, 2 этаж, комната 205",
        'office_location_en': "Building H, 2nd floor, Room 205",
    },
    {
        'name_uz': "Menejment fakulteti",
        'name_ru': "Факультет менеджмента",
        'name_en': "Faculty of Management",
        'faculty_code': 'MN',
        'short_description_uz': "Boshqaruv va biznes sohasida zamonaviy bilim va ko'nikmalar berish.",
        'short_description_ru': "Предоставление современных знаний и навыков в области управления и бизнеса.",
        'short_description_en': "Providing modern knowledge and skills in management and business.",
        'description_uz': "<p>Menejment fakulteti korxona va tashkilotlarni samarali boshqarish bo'yicha kadrlar tayyorlaydi.</p>",
        'description_ru': "<p>Факультет менеджмента готовит кадры для эффективного управления предприятиями и организациями.</p>",
        'description_en': "<p>The Faculty of Management trains personnel for effective management of enterprises and organizations.</p>",
        'dean_name_uz': "Ergashev Nodir Bahromovich",
        'dean_name_ru': "Эргашев Нодир Бахромович",
        'dean_name_en': "Ergashev Nodir Bakhromovich",
        'phone': '+998 71 234 56 86',
        'email': 'mn@nuujf.uz',
        'office_location_uz': "I binosi, 3-qavat, 308-xona",
        'office_location_ru': "Здание I, 3 этаж, комната 308",
        'office_location_en': "Building I, 3rd floor, Room 308",
    },
    {
        'name_uz': "Arxitektura va qurilish fakulteti",
        'name_ru': "Факультет архитектуры и строительства",
        'name_en': "Faculty of Architecture and Construction",
        'faculty_code': 'AQ',
        'short_description_uz': "Arxitektura, shaharsozlik va qurilish sohasida kadrlar tayyorlash.",
        'short_description_ru': "Подготовка кадров в области архитектуры, градостроительства и строительства.",
        'short_description_en': "Training specialists in architecture, urban planning and construction.",
        'description_uz': "<p>Arxitektura va qurilish fakulteti zamonaviy binolarni loyihalash va qurish bo'yicha bilim beradi.</p>",
        'description_ru': "<p>Факультет архитектуры и строительства обеспечивает знания по проектированию и строительству современных зданий.</p>",
        'description_en': "<p>The Faculty of Architecture and Construction provides knowledge in design and construction of modern buildings.</p>",
        'dean_name_uz': "Mirzayev Otabek Zaripovich",
        'dean_name_ru': "Мирзаев Отабек Зарипович",
        'dean_name_en': "Mirzayev Otabek Zaripovich",
        'phone': '+998 71 234 56 87',
        'email': 'aq@nuujf.uz',
        'office_location_uz': "J binosi, 1-qavat, 102-xona",
        'office_location_ru': "Здание J, 1 этаж, комната 102",
        'office_location_en': "Building J, 1st floor, Room 102",
    },
]

# 30 departments — 3 per faculty
DEPARTMENTS_DATA = [
    # Faculty 0: KI - Computer Engineering
    {
        'faculty_code': 'KI',
        'name_uz': "Axborot texnologiyalari va dasturlash kafedrasi",
        'name_ru': "Кафедра информационных технологий и программирования",
        'name_en': "Department of Information Technology and Programming",
        'department_code': 'ATDT',
        'short_description_uz': "Dasturlash tillari va zamonaviy IT texnologiyalari bo'yicha ta'lim.",
        'short_description_ru': "Обучение языкам программирования и современным IT технологиям.",
        'short_description_en': "Education in programming languages and modern IT technologies.",
        'head_name_uz': "Ismoilov Bekzod Tuychiyevich",
        'head_name_ru': "Исмоилов Бекзод Туйчиевич",
        'head_name_en': "Ismoilov Bekzod Tuychiyevich",
    },
    {
        'faculty_code': 'KI',
        'name_uz': "Kompyuter tizimlari kafedrasi",
        'name_ru': "Кафедра компьютерных систем",
        'name_en': "Department of Computer Systems",
        'department_code': 'KT',
        'short_description_uz': "Kompyuter tizimlari va tarmoqlar bo'yicha ta'lim.",
        'short_description_ru': "Обучение компьютерным системам и сетям.",
        'short_description_en': "Education in computer systems and networks.",
        'head_name_uz': "Aliyev Murod Toshpulatovich",
        'head_name_ru': "Алиев Мурод Тошпулатович",
        'head_name_en': "Aliyev Murod Toshpulatovich",
    },
    {
        'faculty_code': 'KI',
        'name_uz': "Sun'iy intellekt va ma'lumotlar fanlari kafedrasi",
        'name_ru': "Кафедра искусственного интеллекта и наук о данных",
        'name_en': "Department of Artificial Intelligence and Data Science",
        'department_code': 'SIMF',
        'short_description_uz': "Sun'iy intellekt, mashina o'rganish va katta ma'lumotlar tahlili.",
        'short_description_ru': "Искусственный интеллект, машинное обучение и анализ больших данных.",
        'short_description_en': "Artificial intelligence, machine learning and big data analysis.",
        'head_name_uz': "Qodirov Jasur Ilhomovich",
        'head_name_ru': "Кодиров Жасур Илхомович",
        'head_name_en': "Qodirov Jasur Ilkhomovich",
    },
    # Faculty 1: IQ - Economics
    {
        'faculty_code': 'IQ',
        'name_uz': "Moliya va bank ishi kafedrasi",
        'name_ru': "Кафедра финансов и банковского дела",
        'name_en': "Department of Finance and Banking",
        'department_code': 'MBI',
        'short_description_uz': "Moliyaviy tahlil va bank tizimi bo'yicha ta'lim.",
        'short_description_ru': "Обучение финансовому анализу и банковской системе.",
        'short_description_en': "Education in financial analysis and banking system.",
        'head_name_uz': "Saidov Ravshan Abdullayevich",
        'head_name_ru': "Саидов Равшан Абдуллаевич",
        'head_name_en': "Saidov Ravshan Abdullayevich",
    },
    {
        'faculty_code': 'IQ',
        'name_uz': "Buxgalteriya hisobi va audit kafedrasi",
        'name_ru': "Кафедра бухгалтерского учёта и аудита",
        'name_en': "Department of Accounting and Audit",
        'department_code': 'BHA',
        'short_description_uz': "Buxgalteriya hisobi, audit va soliq tizimi bo'yicha ta'lim.",
        'short_description_ru': "Обучение бухгалтерскому учёту, аудиту и налоговой системе.",
        'short_description_en': "Education in accounting, audit and tax systems.",
        'head_name_uz': "Tursunov Baxtiyor Karimovich",
        'head_name_ru': "Турсунов Бахтиёр Каримович",
        'head_name_en': "Tursunov Bakhtiyor Karimovich",
    },
    {
        'faculty_code': 'IQ',
        'name_uz': "Iqtisodiy nazariya kafedrasi",
        'name_ru': "Кафедра экономической теории",
        'name_en': "Department of Economic Theory",
        'department_code': 'IN',
        'short_description_uz': "Makroiqtisodiyot va mikroiqtisodiyot nazariyalari bo'yicha ta'lim.",
        'short_description_ru': "Обучение теориям макроэкономики и микроэкономики.",
        'short_description_en': "Education in macroeconomics and microeconomics theories.",
        'head_name_uz': "Hamidov Aziz Shokirovich",
        'head_name_ru': "Хамидов Азиз Шокирович",
        'head_name_en': "Khamidov Aziz Shokirovich",
    },
    # Faculty 2: HQ - Law
    {
        'faculty_code': 'HQ',
        'name_uz': "Fuqarolik huquqi kafedrasi",
        'name_ru': "Кафедра гражданского права",
        'name_en': "Department of Civil Law",
        'department_code': 'FH',
        'short_description_uz': "Fuqarolik huquqi va shartnomalar bo'yicha ta'lim.",
        'short_description_ru': "Обучение гражданскому праву и договорам.",
        'short_description_en': "Education in civil law and contracts.",
        'head_name_uz': "Nazarov Otabek Shuhratovich",
        'head_name_ru': "Назаров Отабек Шухратович",
        'head_name_en': "Nazarov Otabek Shukhratovich",
    },
    {
        'faculty_code': 'HQ',
        'name_uz': "Jinoyat huquqi kafedrasi",
        'name_ru': "Кафедра уголовного права",
        'name_en': "Department of Criminal Law",
        'department_code': 'JH',
        'short_description_uz': "Jinoyat huquqi va kriminologiya bo'yicha ta'lim.",
        'short_description_ru': "Обучение уголовному праву и криминологии.",
        'short_description_en': "Education in criminal law and criminology.",
        'head_name_uz': "Xudoyberganov Timur Anvarovich",
        'head_name_ru': "Худойберганов Тимур Анварович",
        'head_name_en': "Khudoyberganov Timur Anvarovich",
    },
    {
        'faculty_code': 'HQ',
        'name_uz': "Xalqaro huquq kafedrasi",
        'name_ru': "Кафедра международного права",
        'name_en': "Department of International Law",
        'department_code': 'XH',
        'short_description_uz': "Xalqaro huquq va diplomatik huquq bo'yicha ta'lim.",
        'short_description_ru': "Обучение международному и дипломатическому праву.",
        'short_description_en': "Education in international and diplomatic law.",
        'head_name_uz': "Sharipov Eldor Bahodirovich",
        'head_name_ru': "Шарипов Элдор Баходирович",
        'head_name_en': "Sharipov Eldor Bakhodirovich",
    },
    # Faculty 3: PD - Pedagogy
    {
        'faculty_code': 'PD',
        'name_uz': "Boshlang'ich ta'lim metodikasi kafedrasi",
        'name_ru': "Кафедра методики начального образования",
        'name_en': "Department of Primary Education Methods",
        'department_code': 'BTM',
        'short_description_uz': "Boshlang'ich sinf o'qituvchilarini tayyorlash.",
        'short_description_ru': "Подготовка учителей начальных классов.",
        'short_description_en': "Training primary school teachers.",
        'head_name_uz': "Jumayev Sanjar Kamolovich",
        'head_name_ru': "Жумаев Санжар Камолович",
        'head_name_en': "Jumayev Sanjar Kamolovich",
    },
    {
        'faculty_code': 'PD',
        'name_uz': "Psixologiya kafedrasi",
        'name_ru': "Кафедра психологии",
        'name_en': "Department of Psychology",
        'department_code': 'PS',
        'short_description_uz': "Psixologiya va pedagogik psixologiya bo'yicha ta'lim.",
        'short_description_ru': "Обучение психологии и педагогической психологии.",
        'short_description_en': "Education in psychology and pedagogical psychology.",
        'head_name_uz': "Qurbonova Mohira Toxirovna",
        'head_name_ru': "Курбонова Мохира Тохировна",
        'head_name_en': "Qurbonova Mokhira Tokhirovna",
    },
    {
        'faculty_code': 'PD',
        'name_uz': "Ta'lim texnologiyalari kafedrasi",
        'name_ru': "Кафедра образовательных технологий",
        'name_en': "Department of Educational Technologies",
        'department_code': 'TT',
        'short_description_uz': "Zamonaviy ta'lim texnologiyalari va innovatsiyalar.",
        'short_description_ru': "Современные образовательные технологии и инновации.",
        'short_description_en': "Modern educational technologies and innovations.",
        'head_name_uz': "Xasanov Zafar Murodovich",
        'head_name_ru': "Хасанов Зафар Муродович",
        'head_name_en': "Khasanov Zafar Murodovich",
    },
    # Faculty 4: FL - Philology
    {
        'faculty_code': 'FL',
        'name_uz': "O'zbek tili va adabiyoti kafedrasi",
        'name_ru': "Кафедра узбекского языка и литературы",
        'name_en': "Department of Uzbek Language and Literature",
        'department_code': 'OTA',
        'short_description_uz': "O'zbek tili grammatikasi va jahon adabiyoti bo'yicha ta'lim.",
        'short_description_ru': "Обучение грамматике узбекского языка и мировой литературе.",
        'short_description_en': "Education in Uzbek language grammar and world literature.",
        'head_name_uz': "Umarov Shahzod Ibrohimovich",
        'head_name_ru': "Умаров Шахзод Иброхимович",
        'head_name_en': "Umarov Shahzod Ibrokhimovich",
    },
    {
        'faculty_code': 'FL',
        'name_uz': "Ingliz tili kafedrasi",
        'name_ru': "Кафедра английского языка",
        'name_en': "Department of English Language",
        'department_code': 'IT',
        'short_description_uz': "Ingliz tili va tarjima bo'yicha ta'lim.",
        'short_description_ru': "Обучение английскому языку и переводу.",
        'short_description_en': "Education in English language and translation.",
        'head_name_uz': "Mirkomilova Nilufar Baxodirovna",
        'head_name_ru': "Миркомилова Нилуфар Баходировна",
        'head_name_en': "Mirkomilova Nilufar Bakhodirovna",
    },
    {
        'faculty_code': 'FL',
        'name_uz': "Rus tili va adabiyoti kafedrasi",
        'name_ru': "Кафедра русского языка и литературы",
        'name_en': "Department of Russian Language and Literature",
        'department_code': 'RTA',
        'short_description_uz': "Rus tili va adabiyoti bo'yicha ta'lim.",
        'short_description_ru': "Обучение русскому языку и литературе.",
        'short_description_en': "Education in Russian language and literature.",
        'head_name_uz': "Petrov Aleksandr Ivanovich",
        'head_name_ru': "Петров Александр Иванович",
        'head_name_en': "Petrov Aleksandr Ivanovich",
    },
    # Faculty 5: TF - Natural Sciences
    {
        'faculty_code': 'TF',
        'name_uz': "Fizika kafedrasi",
        'name_ru': "Кафедра физики",
        'name_en': "Department of Physics",
        'department_code': 'FZ',
        'short_description_uz': "Nazariy va amaliy fizika bo'yicha ta'lim.",
        'short_description_ru': "Обучение теоретической и прикладной физике.",
        'short_description_en': "Education in theoretical and applied physics.",
        'head_name_uz': "Eshmatov Sardor Rustamovich",
        'head_name_ru': "Эшматов Сардор Рустамович",
        'head_name_en': "Eshmatov Sardor Rustamovich",
    },
    {
        'faculty_code': 'TF',
        'name_uz': "Kimyo kafedrasi",
        'name_ru': "Кафедра химии",
        'name_en': "Department of Chemistry",
        'department_code': 'KM',
        'short_description_uz': "Organik va noorganik kimyo bo'yicha ta'lim.",
        'short_description_ru': "Обучение органической и неорганической химии.",
        'short_description_en': "Education in organic and inorganic chemistry.",
        'head_name_uz': "Tojiboyev Dostonbek Shavkatovich",
        'head_name_ru': "Тожибоев Достонбек Шавкатович",
        'head_name_en': "Tojiboyev Dostonbek Shavkatovich",
    },
    {
        'faculty_code': 'TF',
        'name_uz': "Biologiya kafedrasi",
        'name_ru': "Кафедра биологии",
        'name_en': "Department of Biology",
        'department_code': 'BL',
        'short_description_uz': "Umumiy biologiya va ekologiya bo'yicha ta'lim.",
        'short_description_ru': "Обучение общей биологии и экологии.",
        'short_description_en': "Education in general biology and ecology.",
        'head_name_uz': "Jalolov Shamsiddin Karimovich",
        'head_name_ru': "Жалолов Шамсиддин Каримович",
        'head_name_en': "Jalolov Shamsiddin Karimovich",
    },
    # Faculty 6: XM - International Relations
    {
        'faculty_code': 'XM',
        'name_uz': "Xalqaro siyosat kafedrasi",
        'name_ru': "Кафедра международной политики",
        'name_en': "Department of International Politics",
        'department_code': 'XS',
        'short_description_uz': "Xalqaro munosabatlar va siyosatshunoslik bo'yicha ta'lim.",
        'short_description_ru': "Обучение международным отношениям и политологии.",
        'short_description_en': "Education in international relations and political science.",
        'head_name_uz': "Boboyev Jahongir Anvarovich",
        'head_name_ru': "Бобоев Жахонгир Анварович",
        'head_name_en': "Boboyev Jakhongir Anvarovich",
    },
    {
        'faculty_code': 'XM',
        'name_uz': "Diplomatiya kafedrasi",
        'name_ru': "Кафедра дипломатии",
        'name_en': "Department of Diplomacy",
        'department_code': 'DP',
        'short_description_uz': "Diplomatiya va consulllik ishi bo'yicha ta'lim.",
        'short_description_ru': "Обучение дипломатии и консульскому делу.",
        'short_description_en': "Education in diplomacy and consular affairs.",
        'head_name_uz': "Ibragimov Temur Sodiqovich",
        'head_name_ru': "Ибрагимов Темур Содикович",
        'head_name_en': "Ibragimov Temur Sodiqovich",
    },
    {
        'faculty_code': 'XM',
        'name_uz': "Mintaqashunoslik kafedrasi",
        'name_ru': "Кафедра регионоведения",
        'name_en': "Department of Regional Studies",
        'department_code': 'MS',
        'short_description_uz': "Mintaqaviy tadqiqotlar va geosiyosat bo'yicha ta'lim.",
        'short_description_ru': "Обучение региональным исследованиям и геополитике.",
        'short_description_en': "Education in regional studies and geopolitics.",
        'head_name_uz': "Ahmedov Kamol Umarovich",
        'head_name_ru': "Ахмедов Камол Умарович",
        'head_name_en': "Akhmedov Kamol Umarovich",
    },
    # Faculty 7: MT - Mathematics
    {
        'faculty_code': 'MT',
        'name_uz': "Amaliy matematika kafedrasi",
        'name_ru': "Кафедра прикладной математики",
        'name_en': "Department of Applied Mathematics",
        'department_code': 'AM',
        'short_description_uz': "Matematik modellashtirish va hisoblash usullari.",
        'short_description_ru': "Математическое моделирование и вычислительные методы.",
        'short_description_en': "Mathematical modeling and computational methods.",
        'head_name_uz': "Sodiqov Behruz Anvarovich",
        'head_name_ru': "Содиков Бехруз Анварович",
        'head_name_en': "Sodiqov Behruz Anvarovich",
    },
    {
        'faculty_code': 'MT',
        'name_uz': "Matematik tahlil kafedrasi",
        'name_ru': "Кафедра математического анализа",
        'name_en': "Department of Mathematical Analysis",
        'department_code': 'MTA',
        'short_description_uz': "Matematik tahlil va differensial tenglamalar.",
        'short_description_ru': "Математический анализ и дифференциальные уравнения.",
        'short_description_en': "Mathematical analysis and differential equations.",
        'head_name_uz': "Qoraboyev Dostonbek Ilhomovich",
        'head_name_ru': "Коробоев Достонбек Илхомович",
        'head_name_en': "Qoraboyev Dostonbek Ilkhomovich",
    },
    {
        'faculty_code': 'MT',
        'name_uz': "Statistika kafedrasi",
        'name_ru': "Кафедра статистики",
        'name_en': "Department of Statistics",
        'department_code': 'ST',
        'short_description_uz': "Ehtimollar nazariyasi va matematik statistika.",
        'short_description_ru': "Теория вероятностей и математическая статистика.",
        'short_description_en': "Probability theory and mathematical statistics.",
        'head_name_uz': "Valiyev Doniyor Tohirovich",
        'head_name_ru': "Валиев Дониёр Тохирович",
        'head_name_en': "Valiyev Doniyor Tokhirovich",
    },
    # Faculty 8: MN - Management
    {
        'faculty_code': 'MN',
        'name_uz': "Biznes boshqaruvi kafedrasi",
        'name_ru': "Кафедра бизнес-управления",
        'name_en': "Department of Business Management",
        'department_code': 'BB',
        'short_description_uz': "Strategik boshqaruv va biznes rejalashtirish.",
        'short_description_ru': "Стратегическое управление и бизнес-планирование.",
        'short_description_en': "Strategic management and business planning.",
        'head_name_uz': "Ruziyev Shahboz Baxtiyorovich",
        'head_name_ru': "Рузиев Шахбоз Бахтиёрович",
        'head_name_en': "Ruziyev Shahboz Bakhtiyorovich",
    },
    {
        'faculty_code': 'MN',
        'name_uz': "Marketing kafedrasi",
        'name_ru': "Кафедра маркетинга",
        'name_en': "Department of Marketing",
        'department_code': 'MK',
        'short_description_uz': "Zamonaviy marketing strategiyalari va reklama.",
        'short_description_ru': "Современные маркетинговые стратегии и реклама.",
        'short_description_en': "Modern marketing strategies and advertising.",
        'head_name_uz': "Usmanova Kamola Toxirovna",
        'head_name_ru': "Усманова Камола Тохировна",
        'head_name_en': "Usmanova Kamola Tokhirovna",
    },
    {
        'faculty_code': 'MN',
        'name_uz': "Inson resurslari boshqaruvi kafedrasi",
        'name_ru': "Кафедра управления человеческими ресурсами",
        'name_en': "Department of Human Resources Management",
        'department_code': 'IRB',
        'short_description_uz': "Xodimlar boshqaruvi va tashkiliy xulq-atvor.",
        'short_description_ru': "Управление персоналом и организационное поведение.",
        'short_description_en': "Personnel management and organizational behavior.",
        'head_name_uz': "Jalilova Sevara Abdullayevna",
        'head_name_ru': "Жалилова Севара Абдуллаевна",
        'head_name_en': "Jalilova Sevara Abdullayevna",
    },
    # Faculty 9: AQ - Architecture
    {
        'faculty_code': 'AQ',
        'name_uz': "Arxitektura kafedrasi",
        'name_ru': "Кафедра архитектуры",
        'name_en': "Department of Architecture",
        'department_code': 'AR',
        'short_description_uz': "Binolar loyihalash va arxitektura tarixi.",
        'short_description_ru': "Проектирование зданий и история архитектуры.",
        'short_description_en': "Building design and architecture history.",
        'head_name_uz': "Murodov Farrux Kamolovich",
        'head_name_ru': "Муродов Фаррух Камолович",
        'head_name_en': "Murodov Farrukh Kamolovich",
    },
    {
        'faculty_code': 'AQ',
        'name_uz': "Qurilish texnologiyalari kafedrasi",
        'name_ru': "Кафедра строительных технологий",
        'name_en': "Department of Construction Technologies",
        'department_code': 'QT',
        'short_description_uz': "Zamonaviy qurilish materiallari va texnologiyalari.",
        'short_description_ru': "Современные строительные материалы и технологии.",
        'short_description_en': "Modern construction materials and technologies.",
        'head_name_uz': "Sultanov Oybek Ravshonovich",
        'head_name_ru': "Султанов Ойбек Равшонович",
        'head_name_en': "Sultanov Oybek Ravshonovich",
    },
    {
        'faculty_code': 'AQ',
        'name_uz': "Shaharsozlik kafedrasi",
        'name_ru': "Кафедра градостроительства",
        'name_en': "Department of Urban Planning",
        'department_code': 'SH',
        'short_description_uz': "Shahar rejalashtirish va infrastruktura loyihalash.",
        'short_description_ru': "Городское планирование и проектирование инфраструктуры.",
        'short_description_en': "Urban planning and infrastructure design.",
        'head_name_uz': "Nuriddinov Shaxzod Ulug'bek o'g'li",
        'head_name_ru': "Нуриддинов Шахзод Улугбек угли",
        'head_name_en': "Nuriddinov Shakhzod Ulugbekovich",
    },
]

# Staff templates per department
STAFF_NAMES = [
    ("Abdullayev Komil", "Абдуллаев Комил", "Abdullayev Komil"),
    ("Karimova Nodira", "Каримова Нодира", "Karimova Nodira"),
    ("Toshmatov Sardor", "Тошматов Сардор", "Toshmatov Sardor"),
]

# Program templates
PROGRAM_TEMPLATES = [
    ("Bakalavr dasturi", "Программа бакалавриата", "Bachelor's Program"),
    ("Magistr dasturi", "Магистерская программа", "Master's Program"),
]

# Subject templates (varied per department type)
SUBJECT_TEMPLATES = [
    ("Kirish kursi", "Вводный курс", "Introductory Course"),
    ("Ilg'or mavzular", "Продвинутые темы", "Advanced Topics"),
    ("Amaliy seminar", "Практический семинар", "Practical Seminar"),
]

# Publication templates
PUBLICATION_TEMPLATES = [
    {
        'title_uz': "Zamonaviy yondashuvlar va muammolar",
        'title_ru': "Современные подходы и проблемы",
        'title_en': "Modern Approaches and Challenges",
        'authors': "A. Karimov, B. Toshmatov",
        'year': 2024,
        'journal_or_conference': "Journal of Academic Research",
    },
    {
        'title_uz': "Tadqiqot natijalari va istiqbollar",
        'title_ru': "Результаты исследования и перспективы",
        'title_en': "Research Results and Perspectives",
        'authors': "S. Normatov, D. Ismoilov",
        'year': 2023,
        'journal_or_conference': "International Conference Proceedings",
    },
]

# Achievement templates
ACHIEVEMENT_TEMPLATES = [
    {
        'title_uz': "Xalqaro ilmiy konferensiyada 1-o'rin",
        'title_ru': "1 место на международной научной конференции",
        'title_en': "1st place at International Scientific Conference",
        'description_uz': "Fakultet o'qituvchilari xalqaro konferensiyada birinchi o'rinni qo'lga kiritdi.",
        'description_ru': "Преподаватели факультета заняли первое место на международной конференции.",
        'description_en': "Faculty teachers won first place at an international conference.",
        'year': 2024,
    },
    {
        'title_uz': "Eng yaxshi ilmiy maqola mukofoti",
        'title_ru': "Награда за лучшую научную статью",
        'title_en': "Best Scientific Paper Award",
        'description_uz': "Fakultet professor-o'qituvchilari eng yaxshi maqola mukofotini oldi.",
        'description_ru': "Профессорско-преподавательский состав получил награду за лучшую статью.",
        'description_en': "Faculty professors received the best paper award.",
        'year': 2023,
    },
]


class Command(BaseCommand):
    help = 'Seed realistic test data for faculties app (10 faculties, 30 departments with related data)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            Faculty.objects.all().delete()
            Department.objects.all().delete()

        self.stdout.write(self.style.MIGRATE_HEADING('Seeding faculties app...\n'))

        # Create faculties
        faculty_map = {}
        for i, data in enumerate(FACULTIES_DATA):
            faculty = Faculty.objects.create(order=i, **data)
            faculty_map[data['faculty_code']] = faculty
            self.stdout.write(self.style.SUCCESS(f'  ✅ Faculty: {faculty.name}'))

            # Add achievements
            for ach_data in ACHIEVEMENT_TEMPLATES:
                FacultyAchievement.objects.create(faculty=faculty, **ach_data)

        self.stdout.write(f'\n  Created {len(FACULTIES_DATA)} faculties\n')

        # Create departments
        for i, dept_data in enumerate(DEPARTMENTS_DATA):
            faculty_code = dept_data.pop('faculty_code')
            faculty = faculty_map[faculty_code]
            dept = Department.objects.create(
                faculty=faculty,
                phone=f'+998 71 345 67 {10+i:02d}',
                email=f'{dept_data["department_code"].lower()}@nuujf.uz',
                office_location_uz=f"A binosi, {(i % 4) + 1}-qavat, {100 + i}-xona",
                office_location_ru=f"Здание А, {(i % 4) + 1} этаж, комната {100 + i}",
                office_location_en=f"Building A, floor {(i % 4) + 1}, Room {100 + i}",
                order=i,
                **dept_data,
            )
            self.stdout.write(f'  ✅ Department: {dept.name} → {faculty.name}')

            # Add programs
            for j, (name_uz, name_ru, name_en) in enumerate(PROGRAM_TEMPLATES):
                DepartmentProgram.objects.create(
                    department=dept,
                    code=f'{dept.department_code}-{j+1:02d}',
                    name_uz=f'{dept.name_uz} - {name_uz}',
                    name_ru=f'{dept.name_ru} - {name_ru}',
                    name_en=f'{dept.name_en} - {name_en}',
                    description_uz=f"<p>{dept.short_description_uz}</p>",
                    description_ru=f"<p>{dept.short_description_ru}</p>",
                    description_en=f"<p>{dept.short_description_en}</p>",
                )

            # Add subjects
            for j, (name_uz, name_ru, name_en) in enumerate(SUBJECT_TEMPLATES):
                DepartmentSubject.objects.create(
                    department=dept,
                    name_uz=f'{name_uz} - {dept.name_uz}',
                    name_ru=f'{name_ru} - {dept.name_ru}',
                    name_en=f'{name_en} - {dept.name_en}',
                    description_uz=f"{dept.short_description_uz}",
                    description_ru=f"{dept.short_description_ru}",
                    description_en=f"{dept.short_description_en}",
                )

            # Add staff
            for j, (name_uz, name_ru, name_en) in enumerate(STAFF_NAMES):
                DepartmentStaff.objects.create(
                    department=dept,
                    name_uz=name_uz,
                    name_ru=name_ru,
                    name_en=name_en,
                    email=f'{name_uz.split()[0].lower()}{i}@nuujf.uz',
                )

            # Add publications
            for pub_data in PUBLICATION_TEMPLATES:
                DepartmentPublication.objects.create(
                    department=dept,
                    **pub_data,
                )

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Seeding complete!\n'
            f'   {Faculty.objects.count()} faculties\n'
            f'   {FacultyAchievement.objects.count()} achievements\n'
            f'   {Department.objects.count()} departments\n'
            f'   {DepartmentProgram.objects.count()} programs\n'
            f'   {DepartmentSubject.objects.count()} subjects\n'
            f'   {DepartmentStaff.objects.count()} staff members\n'
            f'   {DepartmentPublication.objects.count()} publications'
        ))
