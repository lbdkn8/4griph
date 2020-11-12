# Прогу запускать только через консоль (обычную/в Пайчарме/...)! Не принимает нажатия клавиш в пайчармовском Run
import pymorphy2    # морфанализатор можем заменить; spacy-udpipe у меня отказывается работать вне колаба - решаемо(?)
import string       # для быстрого убирания знаков препинания - не так важно
import re
import os
import cv2          # для воспроизведения видосов; они пока без звука (важно для слышащих) - потом будут
import msvcrt as M  # для считывания нажатий клавиш; только на винде работает (т.к. MicrosoftVisualC... чототам)

# Перечисляю названия для папок, в которых хранятся данные
gdata_f = 'гриф'                    # главная; прога запускается в директории, в которой лежит папка 'гриф'
swords_f = 'обработанные жесты'
sletters_f = 'Алфавит'
snums_f = 'Цифры, числа'
ssylls_f = 'cлоги'
fileform = 'avi'                    # формат файлов (?)
sepfile = 'blacksec.avi'            # видео, появляющееся перед словами, составленными из букв-жестов

nlp = pymorphy2.MorphAnalyzer()


# токенизатор-лемматизатор + убираем знаки препинания
def chewable(s):
    re_pnct = re.compile('[%s]' % re.escape(string.punctuation))
    s_stripped = re_pnct.sub('', s)
    lemmas = [nlp.parse(token)[0].normal_form for token in s_stripped.split()]
    return lemmas


# ищем пути к видео для слов или букв и составляем списки для дальнейшего их воспроизведения
def find_vids(v):
    os.chdir(gdata_p)
    for ws in v:
        os.chdir(rf'{gdata_p}\\{swords_f}\\{ws[0].capitalize()}')
        prepws = os.listdir()
        vfile = f'{ws}.{fileform}'
        if vfile in prepws:
            v[ws] = rf'{os.getcwd()}\\{vfile}'
        else:
            os.chdir(f'{gdata_p}\\{sletters_f}')
            letters = [rf'{os.getcwd()}\\{l}.{fileform}' for l in ws]
            separator = rf'{gdata_p}\\{sepfile}'
            letters.insert(0, separator)
            v[ws] = letters
    return v


# проигрываем видосы
def play_vids(vids):

    def play(vid):
        cap = cv2.VideoCapture(vid)
        if not cap.isOpened():
            print("Ошибка при воспроизведении видеофайла")
        while cap.isOpened():
            ret, frame = cap.read()
            if ret:
                cv2.imshow('Translation result', frame)
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break
            else:
                break
        cap.release()

    for i in vids:
        print(i)
        if type(i) is list:
            for v in i:
                play(v)
        elif type(i) is str:
            play(i)
    cv2.destroyAllWindows()


# определяем домашнюю директорию перед главным циклом
home_p = os.getcwd()
gdata_p = f'{home_p}\\{gdata_f}'

# Первый, главный цикл - рабочее приложение
sw1 = True
while sw1:
    greeting = '''\nДля перевода с РЯ на РЖЯ введите ваше предложение ниже:\n'''
    print(greeting)

    uinput = input('ввод: ')
    words = chewable(uinput)

    wsigns = {w: None for w in words}
    wsigns = find_vids(wsigns)

    # Второй цикл - диалог по конкретному переводу
    sw2 = True
    while sw2:
        play_vids(wsigns.values())
        print('''
              Нажмите на клавишу:
              "Пробел", если хотите увидеть запись снова.  
              "1", если хотите перевести ещё одно предложение.
              "3", если хотите выйти из приложения.
              ''')
        # Третий цикл - принимает ответ до тех пор, пока не примет нужный
        sw3 = True
        while sw3:
            prkey = M.getch()                        # Это всё - издержки консольного интерфейса, потом GUI будет
            if prkey == b'3':                        # Принимает "Пробел" и цифры - из-за смены раскладки всё сложнее
                sw1, sw2, sw3 = False, False, False
            elif prkey == b' ':
                play_vids(wsigns.values())
            elif prkey == b'1':
                sw2, sw3 = False, False
            else:
                print('Пожалуйста, нажимайте только на вышепредложенные кнопки\n')
