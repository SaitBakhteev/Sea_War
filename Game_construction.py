import random

class Game_field: #сетка игрового поля
    bot_player = False  # объект, который будет использован в этом классе, если примет объект Bot
    ships=None # переменная, принимающая БД кораблей
    mask_gride=None # специальный параметр, содержащий замаскированный список игрового поля Бота, доступный игроку-Человеку
    def __init__(self):
        self.gride = [['O' for i1 in range(6)] for i in range(6)]  #генерирование игрового поля

    def shooting_by_Human(self): #функция обработки вводимых человеком  данных по простреливаемой ячейке
        acceptable_text = False
        while acceptable_text==False:
            text=input('Пропишите простреливаемую цель в формате "Ряд, Столбец": ')
            if len(text)!=3 or text[1]!=',':
                print('Некорректно прописана цель! Повторите ввод')
                continue
            try:
                shooting_cell =(int(text[0]),int(text[2])) # обстреливаемая ячейка игрового поля игроком-человеком
                print(text)
                row,col=shooting_cell[0]-1,shooting_cell[1]-1
            except ValueError:
                print("Ошибка! Номера рядов и столбцов нужно прописывать цифрами от 1 до 6. Повторите ввод.")
                continue
            return (row,col)

    def _check_cell(self): # проверка ячейки, в котрую производится выстрел
        row, col = self._shooted_cell[0], self._shooted_cell[1]
        add_tab='\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t' if self.bot_player!=False else ''
        try:
            if self.gride[row][col] == '\u2584':
                self.gride[row][col] = 'X'
                Hitting_target = True  # есть попадание в ячейку корабля
                print(f'{add_tab}ЕСТЬ ПОПАДАНИЕ!')
            elif self.gride[row][col] == 'O':
                self.gride[row][col] = "T"
                Hitting_target = False  # мимо
                print(f'{add_tab}Мимо..')
            else:
                print('Эта ячейка ранее уже обстреливалась, повторите ввод.')
                return False
        except IndexError:
            print('Несуществующие ячейки! Повторите ввод')
            return False
        if self.mask_gride != None:
            self.mask_gride[row][col]=self.gride[row][col]
        return (True, Hitting_target)

    def shooting(self):  # выстрел в игровое поле
        acceptable_text = False
        while acceptable_text == False:
            self._shooted_cell=self.bot_player.choose_cell() if type(self.bot_player)==Bot \
                else self.shooting_by_Human() # человек или бот производит выбирает ячейку для выстрела в неё
            text_=self._check_cell()
            if text_!=False:
                acceptable_text = True
                Hitting_target=text_[1]
            else:
                continue
        if type(self.bot_player) == Bot:
            row, col = self._shooted_cell[0]+1, self._shooted_cell[1]+1
            add_tab = '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t'
            print(f'{add_tab}Координаты простреливаемой Ботом ячейки (ряд, столбец): {(row,col)}')
        if Hitting_target == True:
            self._update_shipsDB()
        if type(self.bot_player)==Bot:
            self.bot_player.after_Shoot(Hitting_target)

    def show_gride(self,gride=None): #отображение на экране игрового поля
        add_tab = '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t' if self.bot_player!=False else ''
        text=''  #инициализация строковой переменной для отображения игровой доски с номерами столбцов
        gride = self.gride if gride==None else gride
        for i in range(6):
            text+=add_tab+ f'\t{i + 1}' if i==0 else  f'\t{i + 1}'
        for row_index, row_item in enumerate(gride):
            text += f'\n{add_tab}{row_index + 1}'
            for col in row_item:
                text+= f'\t{col}'
        return text

    def _update_shipsDB(self): #обновление ключа 'position' в БД кораблей при попадании
        add_tab = '\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t' if self.bot_player != False else ''
        if type(self.bot_player)==Bot:
            self.bot_player.Alive_ship=True # в начале всегда условно бот принимает, что кораль живой
        for i, item in enumerate(self.ships):
            if self._shooted_cell in item['position']:
                item['lifes_count']-=1
            if item['lifes_count']==0:
                if type(self.bot_player) == Bot:
                    self.bot_player.Alive_ship = False # Данная переменная возвращается в False после уничтожения корабля
                print(f'{add_tab}Корабль типа "'+ item['ship title']+ '" УНИЧТОЖЕН!!!!')
                if self.mask_gride!=None:
                    for j in item['position']:
                        row,col=j[0],j[1]
                        self.mask_gride[row][col]='\u2583'
                self.ships.pop(i)

class Bot(): #класс, определяющий поведение бота при игре
    _local_Gride=[[],[]] # локальный перечень ячеек, в которых располагаются остальные части корабля,
                            # определяемый ботом после попадания в одну из ячеек корабля
    _shooted_cell=None #простреливаемая ячейка

    def __init__(self):
        self.Alive_ship=False # переменная, показывающая что корабль, еще жив после попадания
        self._Hitting_target=False # переменная, показывающая что ячейка поражена
        self._virtual_Gride=[(row,col) for row in range(6) for col in range(6)] #перечень координат
                                                                            # ячеек игровой сетки, которые
                                                                            #  бот выбирает при выстрелах

    def _update_virtual_Gride(self,cell): #обновление списка оставшихся для прострела компбютером ячеек
        for i, item in enumerate(self._virtual_Gride):
            if item==cell:
                self._virtual_Gride.pop(i)
                break

    def choose_cell(self): # выбор простреливаемой ячейки на игровом поле
        self._shooted_cell = random.choice(self._virtual_Gride) if self.Alive_ship == False else \
            random.choice(self._local_Gride[1])  # простреливаемая ячейка
        return self._shooted_cell

    def after_kill_ship(self): # дальнейшие руководства бота после уничтожения корабля
        cells = self.formation_near_Area(self._shooted_cell)
        for i1 in cells:
            self._update_virtual_Gride(i1)
        self._local_Gride = [[], []]

    def finish_off_ship(self): # вычисление максимум двух оставшихся ячеек 3-клеточного корабля для его полного уничтожения
        rows,cols=(self._local_Gride[0][0][0],self._local_Gride[0][1][0]),\
                  (self._local_Gride[0][0][1], self._local_Gride[0][1][1]) # присвоение перечня рядов и столбцов
                                                                    # подбитых ячеек еще живого корабля
        cells=((rows[0],min(cols)-1),(rows[0],max(cols)+1)) if rows[0]==rows[1] else \
            ((min(rows)-1,cols[0]),(max(rows)+1,cols[0]))
        for i in self._local_Gride[1]:
            if i not in cells:
                self._update_virtual_Gride(i)
        self._local_Gride[1]=[]
        for i in cells:
            if i in self._virtual_Gride:
                self._local_Gride[1].append(i)

    def formation_near_Area(self,cell): #формирование соседних областей, где потенциально могут располоагаться
                                    # остальные ячейки корабля
        row,col=cell[0],cell[1]
        for i in ('row', 'col'):
            for j in (-1, 1):
                row_ = row + j if i == 'row' else row
                col_ = col + j if i == 'col' else col
                if (row_, col_) not in self._local_Gride[1] and\
                        (row_, col_) in self._virtual_Gride:
                    self._local_Gride[1].append((row_, col_))
        return self._local_Gride[1]

    def _edit_local_area(self): #редактирование списка локального простреливаемого участка
        for i, item in enumerate(self._local_Gride[1]): #удаление  простреленных ячеек из той части локального списка,
            if item==self._shooted_cell:            # которой бот руководствуется для выискивания остальных ячеек корабля
                self._local_Gride[1].pop(i)
        if self._Hitting_target==True: #если ячейка корабля поражена,
            self.formation_near_Area(self._shooted_cell) # то формируется список соседних ячеек, в которых потенциально
                                                        # расположены остальные части корабля
            self._local_Gride[0].append(self._shooted_cell) # а эта ячейка добавляется в перечень пораженных ячеек
                                                            # корабля в локальном списке
            if len(self._local_Gride[0])>1: #если поражена вторая ячейка корабля и у него остается еще одна
                self.finish_off_ship()

    def after_Shoot(self, Hitting_target): #общая конструкция дальнейшего обдумывания ботом после выстрела
        self._Hitting_target = Hitting_target #попал или не попал в ячейку корабля
        self._update_virtual_Gride(self._shooted_cell)
        if self._Hitting_target == True and self.Alive_ship==False: # если после попадания в ячейку корабль уничтожен
            self.after_kill_ship()
        if self.Alive_ship==True: #если корабль еще жив после попадания
            self._edit_local_area()

class Check_input: #проверка введенных данных
    _row= _end_row= _col= _end_col= _lifes_count= None #входные данные для проверки предполагаемого размещеения корабля
    _current_ship=None # переменная, принимающая словарь конкретного корабля из БД кораблей

    def __init__(self,Human_player):
        self.correct_elem = (('1', '2', '3', '4', '5', '6'),('h','v')) #перечень допустимых элементов для
                                                                          # ввода данных расположения корабля
        self.Human_player = Human_player  # переменная, указвающая является ли игроком человек
        self.virtual_Gride = [[True for col in range(6)] for row in range(6)] # виртуальный список ячеек игровой
                                            # сетки, которая определяет доступность размещения последующих кораблей

    def _show_messages_of_invalid_set(self,i): #отображение сообщений при неверной установке кораблей
        if self.Human_player==True:
            print(self._messages_on_invalid_inputs[i])

    def _input_conds_polycell_ships(self): #условия ввода многоклеточных кораблей
        try:  # оператор обработки ошибки ввода, если длина строки окажется меньше 5
            input_pos = input('Введите параметры размещения "' + self._current_ship['ship title'] + '" в формате:'
                                  ' ряд (1-6), столбец (1-6); ориентация (h или v): ')  # ввод данных расположения корабля
            if (input_pos[0] in self.correct_elem[0] and input_pos[2] in self.correct_elem[0]
                    and input_pos[1] == ',' and input_pos[3] == ';' and len(input_pos)==5
                    and input_pos[4] in self.correct_elem[1]):
                return input_pos
            else:
                print('Неверный формат, повторите ввод')
                return False
        except IndexError:
            print('Недостаточно данных или некорректный формат')
        return False

    def _input_conds_monocell_ships(self): #условия ввода одноклеточных кораблей
        try:  # оператор обработки ошибки ввода, если длина строки окажется меньше 3
            input_pos = input('Введите параметры размещения "' + self._current_ship['ship title'] + '" в формате:'
                                  ' ряд (1-6), столбец (1-6): ')  # ввод данных расположения корабля
            if (input_pos[0] in self.correct_elem[0] and input_pos[2] in self.correct_elem[0]
                    and input_pos[1] == ',' and len(input_pos) == 3):
                return input_pos
            else:
                print('Неверный формат, повторите ввод')
                return False
        except IndexError:
            print('Недостаточно данных или некорректный формат')
        return False

    def _acceptable_text_input(self): # метод обработки корректного формата ввода установки расположения корабля
            text_=self._input_conds_polycell_ships() if self._current_ship['lifes_count']>1 \
                else self._input_conds_monocell_ships()
            if text_!= False:
                 return text_
            else:
                return False

    def _set_ship_position_values_after_format_cheking(self,input_pos): #установка значений предполагаемого
            # расположения корабля после корректного ввода присвоение параметров предполагаемого размещения корабля:
            # координаты размещения носовой части (row, col); протяженность корабля по числу жизней и координаты
            # остальной части корабля в зависимости от ориентации

        self._row, self._col, self._lifes_count = \
            int(input_pos[0])-1, int(input_pos[2])-1, self._current_ship['lifes_count']

        if self._lifes_count>1:
            self._end_row=self._row +self._lifes_count-1 if input_pos[4]=='v' else self._row
            self._end_col=self._col +self._lifes_count-1 if input_pos[4]=='h' else self._col
        else:
            self._end_row,self._end_col = self._row, self._col

    def _check_empty_cells(self): # проверка доступности ячеек, для размещения корабля

        try:
            for row in range(self._row, self._end_row+1):
                for col in range(self._col,self._end_col+1):
                    if self.virtual_Gride[row][col] == False:
                        if self.Human_player==True:
                            print('Ячейки не свободны, либо близко расположены к другим кораблям')
                        return False
        except IndexError:
            if self.Human_player == True:
                print('Корабль выходит за пределы игрового поля')
            return False
        return True

    def _input_Bot(self): # ввод ячеек расположения корабля ботом
        if self._current_ship['lifes_count']>1:
            row, col, orientation = random.randint(1, 6), random.randint(1, 6), random.choice(('h', 'v'))
            text_ = f'{row},{col};{orientation}'
        else:
            row, col = random.randint(1, 6), random.randint(1, 6)
            text_ = f'{row},{col}'
        return text_

    def input_and_check(self, ship=dict):  # ввод и проверка корректности формата введенных данных расположения кораблей
        self._current_ship=ship #прием данных словаря конкретного текущего корабля из списка БД кораблей
        acceptable_input = False  # переменная корректного ввода размещения кораблей
        while acceptable_input==False:
            if self.Human_player==True:
                text_=self._acceptable_text_input()
                if text_==False:
                    continue
                else:
                    input_pos=text_
            else:
                input_pos=self._input_Bot()


            self._set_ship_position_values_after_format_cheking(input_pos) #передача параметров расположения
                                                                            # корабля на проверку
            return (self._row, self._end_row, self._col, self._end_col) if self._check_empty_cells()==True \
                else False









    # Возможно не нужные методы
    def get_initial_values_for_checking(self, row, end_row, col, end_col,lifes_count): # прием входных данныхдля проверки
                                                                    # корректности# расположения корабля
        self._row, self._end_row, self._col, self._end_col, self._lifes_count=\
            row, end_row, col, end_col, lifes_count
    def General_checking(self): #общая конструкция проверки корректности ввода кораблей
        if self._check_empty_cells() == True:
            return True
        else:
            return False

class Ships_input(): #размещение кораблей перед игрой
    _row= _end_row= _col= _end_col= _lifes_count= None #входные данные для проверки предполагаемого размещения корабля
    _current_ship=None # переменная, принимающая словарь конкретного корабля из БД кораблей

    def __init__(self, current_game_field, Check=Check_input):
        self._current_game_field = current_game_field  # переменная для присвоения текущего состояния игрового поля
        self._Check = Check  # переменная, принимающая объект проверки данных предполагаемого расположения корабля
        self._Human_player = Check.Human_player  # переменная, указвающая является ли игроком человек
        self._ship_names=('3-клеточный корабль','2-клеточный корабль №1', '2-клеточный корабль №2', '1-клеточный корабль №1',
                '1-клеточный корабль №2', '1-клеточный корабль №3', '1-клеточный корабль №4') #кортеж имен кораблей
        self._correct_elem = (('1', '2', '3', '4', '5', '6'),('h','v')) #перечень допустимых элементов для
                                                                          # ввода данных расположения корабля
        self.ship_DB=[{'ship title':i,'lifes_count':int(i[0]),'position':None} for i in (self._ship_names)] #генерирование
                                                                                                    # базы данных кораблей

    def _set_ship_position_values_after_full_cheking(self, full_check): #установка параметров расположения корабля
                                                # после полной проверки
        self._row, self._end_row, self._col, self._end_col = \
            full_check[0], full_check[1], full_check[2],full_check[3]

    def Set_Ship(self, ship=dict):  # ввод и проверка корректности формата введенных данных расположения кораблей
        self._current_ship=ship #прием данных словаря конкретного текущего корабля из списка БД кораблей
        Valid_input=False # перерменная, указавающая на допустимость установки корабля на игровое поле
        while Valid_input==False:
            full_check=self._Check.input_and_check(ship) # переменная, примающая значение полной проверки
                                                            # корректности расположения корабля
            if full_check!=False: # то есть параметры расположения корабля являются допустимыми
                self._set_ship_position_values_after_full_cheking(full_check)
                self._update_ship_DB()
                self._insert_ship_position_to_gride()
                self._formation_restricted_cells()
                break
            else:
                continue

    def _insert_ship_position_to_gride(self): #размещение корабля в списке игровой сетки+
        for row in range(self._row,self._end_row+1):
            for col in range (self._col, self._end_col+1):
                self._current_game_field[row][col]='\u2584'

    def _update_ship_DB(self): #обновление базы данных кораблей после их установки на игровое поле
        position=[] #генерирование списка координат размещения данного корабля для вненсения в БД
        for row in range(self._row,self._end_row+1):
            for col in range(self._col,self._end_col+1):
                row_col=(row,col)
                position.append(row_col)
        self._current_ship['position']=position

    def _restricted_around_every_cell(self,row,col): #формирование запретных зон, вокруг каждой ячейки корабля
        self._Check.virtual_Gride[row][col] = False
        for cells_parameter in ('row', 'col'):
            for i in (-1, 1):
                row_ = row + i if cells_parameter == 'row' else row
                col_ = col + i if cells_parameter == 'col' else col
                txt_row, txt_col = str(row_+1), str(col_+1)
                if txt_row in self._Check.correct_elem[0] and txt_col in self._Check.correct_elem[0]:
                    self._Check.virtual_Gride[row_][col_]=False

    def _formation_restricted_cells(self):  # формирование списка соседних ячеек, где распологать
                                    # последующие корабли уже нельзя
        for row in range(self._row,self._end_row+1):
            for col in range(self._col,self._end_col+1):
                self._restricted_around_every_cell(row,col)








