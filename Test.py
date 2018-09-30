from random import randrange
from time import time
from time import sleep
from tkinter import *
from tkinter.messagebox import *
import _thread


class Ship():
    '''
    Класс Ship - реализация поведения объекта корабль для игры "Морской бой"
    свойство (указывается при создании объекта):палубность (1 - 4)
    свойство (указывается при создании объекта):расположение (0 - горизонтальное, 1 - вертикальное)
    свойство (указывается при создании объекта):ключевая точка (тег в формате: "столбец_строка")
    свойство:массив со статусами точек, который формируется конструктором
    свойство:массив с координатами точек корабля, который формируется конструктором
    свойство:координаты точек вокруг корабля
    свойство:статус гибели корабля
    свойство (указывается при создании объекта):префикс тега (для своих кораблей будет, например, "my", для чужих "nmy"
    метод-конструктор:изменение массива со статусами точек, например [0,0,1,0]
    метод:shoot(координаты точки), возвращает 1 - если попали, 2 - убил, 0 - мимо
    '''

    # свойства объектов, описанные в классе
    # длина
    length = 1
    # массив со статусами точек корабля
    status_map = []
    # массив с координатами точек корабля
    coord_map = []
    # точки вокруг корабля
    around_map = []
    # статус гибели корабля
    death = 0
    # префикс тега
    prefix = ""
    # свойство: корабль был создан и не выходит за рамки поля
    ship_correct = 1

    # метод-конструктор
    def __init__(self, length, rasp, keypoint):
        self.status_map = []
        self.around_map = []
        self.coord_map = []
        self.death = 0
        self.ship_correct = 1
        self.length = length
        # переопределить переменную self.prefix
        self.prefix = keypoint.split("_")[0]
        # создать массивы status_map и coord_map (в зависимости от направления)
        stroka = int(keypoint.split("_")[1])
        stolb = int(keypoint.split("_")[2])
        for i in range(length):
            self.status_map.append(0)
            # в зависимости от направления генерировать новые точки корабля
            # 0 - горизонт (увеличивать столбец), 1 - вертикаль (увеличивать строку)
            if stolb + i > 9 or stroka + i > 9:
                self.ship_correct = 0
            if rasp == 0:
                self.coord_map.append(self.prefix + "_" + str(stroka) + "_" + str(stolb + i))
            else:
                self.coord_map.append(self.prefix + "_" + str(stroka + i) + "_" + str(stolb))
        for point in self.coord_map:
            ti = int(point.split("_")[1])
            tj = int(point.split("_")[2])
            for ri in range(ti - 1, ti + 2):
                for rj in range(tj - 1, tj + 2):
                    if ri >= 0 and ri <= 9 and rj >= 0 and rj <= 9:
                        if not (self.prefix + "_" + str(ri) + "_" + str(rj) in self.around_map) and not (
                                self.prefix + "_" + str(ri) + "_" + str(rj) in self.coord_map):
                            self.around_map.append(self.prefix + "_" + str(ri) + "_" + str(rj))

    # выстрел
    def shoot(self, shootpoint):
        # определить номер точки и изменить её статус
        status = 0
        for point in range(len(self.coord_map)):
            if self.coord_map[point] == shootpoint:
                self.status_map[point] = 1
                status = 1
                break
        if not (0 in self.status_map):
            status = 2
            self.death = 1
        return status


class Application(Frame):
    '''
    Приложение. Наследует класс Frame. Создание окна, холста и всех функций для реализации приложения
    '''
    # ширина рабочего поля
    width = 800
    # высота рабочего поля
    height = 400
    # цвет фона холста
    bg = "lightcyan"
    # отступ между ячейками
    indent = 2
    # размер одной из сторон квадратной ячейки
    gauge = 32
    # смещение по y (отступ сверху)
    offset_y = 40
    # смещение по x пользовательского поля
    offset_x_user = 30
    # смещение по x поля компьютера
    offset_x_comp = 430
    # компьютерный флот
    fleet_comp = []
    # наш флот
    fleet_user = []
    # массив точек, в которые стрелял компьютер
    comp_shoot = []

    # добавление холста на окно
    def createCanvas(self):
        self.canv = Canvas(self)
        self.canv["height"] = self.height
        self.canv["width"] = self.width
        self.canv["bg"] = self.bg
        self.canv.pack()
        # клик по холсту вызывает функцию play
        self.canv.bind("<Button-1>", self.userPlay)

    def new_game(self):
        self.canv.delete('all')
        # добавление игровых полей пользователя и компьютера
        # создание поля для пользователя
        # перебор строк
        for i in range(10):
            # перебор столбцов
            for j in range(10):
                xn = j * self.gauge + (j + 1) * self.indent + self.offset_x_user
                xk = xn + self.gauge
                yn = i * self.gauge + (i + 1) * self.indent + self.offset_y
                yk = yn + self.gauge
                # добавление прямоугольника на холст с тегом в формате:
                # префикс_строка_столбец
                self.canv.create_rectangle(xn, yn, xk, yk, tag="my_" + str(i) + "_" + str(j))

        # создание поля для компьютера
        # перебор строк
        for i in range(10):
            # перебор столбцов
            for j in range(10):
                xn = j * self.gauge + (j + 1) * self.indent + self.offset_x_comp
                xk = xn + self.gauge
                yn = i * self.gauge + (i + 1) * self.indent + self.offset_y
                yk = yn + self.gauge
                # добавление прямоугольника на холст с тегом в формате:
                # префикс_строка_столбец
                self.canv.create_rectangle(xn, yn, xk, yk, tag="nmy_" + str(i) + "_" + str(j), fill="gray")

        # добавление букв и цифр
        for i in reversed(range(10)):
            # цифры пользователя
            xc = self.offset_x_user - 15
            yc = i * self.gauge + (i + 1) * self.indent + self.offset_y + round(self.gauge / 2)
            self.canv.create_text(xc, yc, text=str(i + 1))
            # цифры компьютера
            xc = self.offset_x_comp - 15
            yc = i * self.gauge + (i + 1) * self.indent + self.offset_y + round(self.gauge / 2)
            self.canv.create_text(xc, yc, text=str(i + 1))
        # буквы
        symbols = "АБВГДЕЖЗИК"
        for i in range(10):
            # буквы пользователя
            xc = i * self.gauge + (i + 1) * self.indent + self.offset_x_user + round(self.gauge / 2)
            yc = self.offset_y - 15
            self.canv.create_text(xc, yc, text=symbols[i])

            # буквы компьютера
            xc = i * self.gauge + (i + 1) * self.indent + self.offset_x_comp + round(self.gauge / 2)
            yc = self.offset_y - 15
            self.canv.create_text(xc, yc, text=symbols[i])

        # генерация кораблей противника
        self.createnmyships("nmy")
        # генерация своих кораблей
        self.createmyhips("my")

    def createnmyships(self, prefix="nmy"):
        # функция генерации кораблей на поле
        # количество сгенерированных кораблей
        count_ships = 0
        while count_ships < 10:
            # массив занятых кораблями точек
            fleet_array = []
            # обнулить количество кораблей
            count_ships = 0
            # массив с флотом
            fleet_ships = []
            # генерация кораблей (length - палубность корабля)
            for length in reversed(range(1, 5)):
                # генерация необходимого количества кораблей необходимой длины
                for i in range(5 - length):
                    # генерация точки со случайными координатами, пока туда не установится корабль
                    try_create_ship = 0
                    while 1:
                        try_create_ship += 1
                        # если количество попыток превысило 50, начать всё заново
                        if try_create_ship > 50:
                            break
                        # генерация точки со случайными координатами
                        ship_point = prefix + "_" + str(randrange(10)) + "_" + str(randrange(10))
                        # случайное расположение корабля (либо горизонтальное, либо вертикальное)
                        orientation = randrange(2)
                        # создать экземпляр класса Ship
                        new_ship = Ship(length, orientation, ship_point)
                        # если корабль может быть поставлен корректно и его точки не пересекаются с уже занятыми точками поля
                        # пересечение множества занятых точек поля и точек корабля:
                        intersect_array = list(set(fleet_array) & set(new_ship.around_map + new_ship.coord_map))
                        if new_ship.ship_correct == 1 and len(intersect_array) == 0:
                            # добавить в массив со всеми занятыми точками точки вокруг корабля и точки самого корабля
                            fleet_array += new_ship.around_map + new_ship.coord_map
                            fleet_ships.append(new_ship)
                            count_ships += 1
                            break
        # отрисовка кораблей
        self.fleet_comp = fleet_ships

    def createmyships(self, prefix="my"):
        pass

    # метод для отрисовки кораблей
    def paintShips(self, field):
        # отрисовка кораблей
        self.canv.itemconfig(field, fill="white")

    # метод рисования в ячейке креста на белом фоне
    def paintCross(self, xn, yn, tag):
        xk = xn + self.gauge
        yk = yn + self.gauge
        self.canv.itemconfig(tag, fill="white")
        self.canv.create_line(xn + 2, yn + 2, xk - 2, yk - 2, width="3")
        self.canv.create_line(xk - 2, yn + 2, xn + 2, yk - 2, width="3")
        if self.canv.create_line == TRUE:
            showinfo("", "Эта координата уже раскрыта")

    # метод рисования промаха
    def paintMiss(self, point):
        # найти координаты
        new_str = int(point.split("_")[1])
        new_stlb = int(point.split("_")[2])
        if point.split("_")[0] == "nmy":
            xn = new_stlb * self.gauge + (new_stlb + 1) * self.indent + self.offset_x_comp
        else:
            xn = new_stlb * self.gauge + (new_stlb + 1) * self.indent + self.offset_x_user
        yn = new_str * self.gauge + (new_str + 1) * self.indent + self.offset_y
        # добавить прямоугольник
        # покрасить в белый
        self.canv.itemconfig(point, fill="white")
        self.canv.create_oval(xn + 13, yn + 13, xn + 17, yn + 17, fill="gray")
        if self.canv.create_oval == TRUE:
            showinfo("", "Эта координата уже раскрыта")

    # метод проверки финиша
    def checkFinish(self, type):
        '''type - указание, от чьего имени идёт обращение'''
        status = 0
        if type == "user":
            for ship in self.fleet_comp:
                status += ship.death
        else:
            for ship in self.fleet_user:
                status += ship.death
        return status

    # метод игры компьютера
    # параметр step - шаг, с которым происходит выстрел,
    # если он 0 - значит выстрел является первым после промаха
    # если 1 - значит надо стрелять рядом с последним выстрелом
    def compPlay(self, step=0):
        sleep(1)
        # если step = 0, то генерировать случайные точки
        if step == 0:
            # генерировать случайные точки, пока не будет найдена пара, которой не было в списке выстрелов
            while 1:
                i = randrange(10)
                j = randrange(10)
                if not ("my_" + str(i) + "_" + str(j) in self.comp_shoot):
                    break
        else:
            # взять предпоследнюю точку, выбрать любую точку вокруг (по горизонтали или вертикали)
            # массив точек вокруг
            points_around = []
            i = int(self.comp_shoot[-1].split("_")[1])
            j = int(self.comp_shoot[-1].split("_")[2])
            for ti in range(i - 1, i + 2):
                for tj in range(j - 1, j + 2):
                    if ti >= 0 and ti <= 9 and tj >= 0 and tj <= 9 and ti != tj and (ti == i or tj == j) and not (
                            ti == i and tj == j) and not ("my_" + str(ti) + "_" + str(tj) in self.comp_shoot):
                        points_around.append([ti, tj])
            # cлучайная точка из массива
            select = randrange(len(points_around))
            i = points_around[select][0]
            j = points_around[select][1]
        xn = j * self.gauge + (j + 1) * self.indent + self.offset_x_user
        yn = i * self.gauge + (i + 1) * self.indent + self.offset_y
        hit_status = 0
        for obj in self.fleet_user:
            # если координаты точки совпадают с координатой корабля, то вызвать метод выстрела
            if "my_" + str(i) + "_" + str(j) in obj.coord_map:
                # изменить статус попадания
                hit_status = 1
                # мы попали, поэтому надо нарисовать крест
                self.paintCross(xn, yn, "my_" + str(i) + "_" + str(j))
                # добавить точку в список выстрелов компьютера
                self.comp_shoot.append("my_" + str(i) + "_" + str(j))
                # если метод вернул двойку, значит, корабль убит
                if obj.shoot("my_" + str(i) + "_" + str(j)) == 2:
                    hit_status = 2
                    # изменить статус корабля
                    obj.death = 1
                    # все точки вокруг корабля сделать точками, в которые мы уже стреляли
                    for point in obj.around_map:
                        # нарисовать промахи
                        self.paintMiss(point)
                        # добавить точки вокруг корабля в список выстрелов компьютера
                        self.comp_shoot.append(point)
                    showinfo("", "Убил!")
                else:
                    showinfo("", "Попал!")
                break
        # если статус попадания остался равным нулю - значит, мы промахнулись, передать управление компьютеру
        # иначе дать пользователю стрелять
        if hit_status == 0:
            # добавить точку в список выстрелов
            self.comp_shoot.append("my_" + str(i) + "_" + str(j))
            self.paintMiss("my_" + str(i) + "_" + str(j))
            print("", "Мимо!")
        else:
            # проверить выигрыш, если его нет - передать управление компьютеру
            if self.checkFinish("comp") < 10:
                if hit_status == 1:
                    step += 1
                    if step > 4:
                        self.compPlay()
                    else:
                        self.compPlay(step)
                else:
                    self.compPlay()
            else:
                showinfo("", "Победил компьютер!")

    # метод для игры пользователя
    def userPlay(self, e):
        for i in range(10):
            for j in range(10):
                xn = j * self.gauge + (j + 1) * self.indent + self.offset_x_comp
                yn = i * self.gauge + (i + 1) * self.indent + self.offset_y
                xk = xn + self.gauge
                yk = yn + self.gauge
                if e.x >= xn and e.x <= xk and e.y >= yn and e.y <= yk:
                    # проверить попали ли мы в корабль
                    hit_status = 0
                    for obj in self.fleet_comp:
                        # если координаты точки совпадают с координатой корабля, то вызвать метод выстрела
                        if "nmy_" + str(i) + "_" + str(j) in obj.coord_map:
                            # изменить статус попадания
                            hit_status = 1
                            # мы попали, поэтому надо нарисовать крест
                            self.paintCross(xn, yn, "nmy_" + str(i) + "_" + str(j))
                            # если метод вернул двойку, значит, корабль убит
                            if obj.shoot("nmy_" + str(i) + "_" + str(j)) == 2:
                                # изменить статус корабля
                                obj.death = 1
                                # все точки вокруг корабля сделать точками, в которые мы уже стреляли
                                for point in obj.around_map:
                                    # нарисовать промахи
                                    self.paintMiss(point)
                                print("", "Вы потопили корабль!")
                            else:
                                print("", "Вы попали!")
                            break
                    # если статус попадания остался равным нулю - значит, мы промахнулись, передать управление компьютеру
                    # иначе дать пользователю стрелять
                    if hit_status == 0:
                        self.paintMiss("nmy_" + str(i) + "_" + str(j))
                        print("", "Вы промахнулись!")
                        # проверить выигрыш, если его нет - передать управление компьютеру
                        if self.checkFinish("user") < 10:
                            self.compPlay()
                        else:
                            showinfo("Морской бой", "Победил игрок!")
                    break

    def __init__(self, master=None):
        # инициализация окна
        Frame.__init__(self, master)
        self.pack()

        # инициализация меню
        self.m = Menu(master)
        master.config(menu=self.m)
        self.m_play = Menu(self.m, tearoff=0)
        self.m.add_cascade(label="Игра", menu=self.m_play)
        self.m_play.add_command(label="Новая игра", command=self.new_game)
        # вызов функции создания холста
        self.createCanvas()

    def createmyhips(self, param):
        pass


# инициализация окна
root = Tk()
root.title = "Морской бой"
root.geometry("800x400+100+100")

# инициализация приложения
app = Application(root)
app.mainloop()