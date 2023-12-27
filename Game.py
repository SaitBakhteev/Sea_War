from Game_construction import Game_field, Ships_input, Check_input, Bot

instruction='КРАТКАЯ ИНСТРУКЦИЯ!\n' \
            'Многоклеточные корабли нужно устанавливать на игровое поле в формате: ряд, столбец; ориентация.\n' \
            'Для задания ориентации нужно вводить "h" (горизонтальная) или "v" (вертикальная).\n' \
            'Значения параметра "ряд и столбец" - это координаты носовой части корабля.\n' \
            'Например, если требуется установить горизонтально 3-клеточный корабль, начало которого будет находиться\n' \
            'в ячейке (2,3), то ввод должен быть следующий: 2,3;h)'
print(instruction+'\n')
# Формирование объектов, принадлежащих Человеку
human_check=Check_input(True) # объект проверки при установке кораблей
human_gm_Fl=Game_field() # игровое поле
human_Ships=Ships_input(human_gm_Fl.gride,human_check) # объект установкеи кораблей
human_gm_Fl.ships=human_Ships.ship_DB
print(human_gm_Fl.show_gride()) # отображение исходной игровой сетки
for i in human_Ships.ship_DB:
    human_Ships.Set_Ship(i)
    print(human_gm_Fl.show_gride())

# Формирование объектов, принадлежащих Боту
bot_check=Check_input(False) # объект проверки при установке кораблей
bot=Bot() # объект, определяющий поведение бота при игре
bot_gm_Fl=Game_field() # игровое поле
bot_gm_Fl.mask_gride=[['O' for i1 in range(6)] for i in range(6)] # генерирование видимого для пользователя
                                                    # замаскированного игрового поля Бота
bot_ships=Ships_input(bot_gm_Fl.gride,bot_check) # объект установкеи кораблей
human_gm_Fl.bot_player=bot # присвоение, означающее, что Бот будет обстреливать игровое поле Человека
bot_gm_Fl.ships=bot_ships.ship_DB
for i in bot_ships.ship_DB:
    bot_ships.Set_Ship(i)
bot_gm_Fl.ships=bot_ships.ship_DB

# Отображение исходных состтояний игровых полей
add_tab='\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t\t' #доп табуляция для информации по Боту
print()
print(f'Игровое поле Бота для Вас\n{bot_gm_Fl.show_gride(bot_gm_Fl.mask_gride)}')
print(f'{add_tab}Ваше игровое поле для Бота{human_gm_Fl.show_gride()}\n')


# Сама игра

print('Игра началась!')
game_over=False
while game_over==False:
    # Процедуры хода Человека
    print(f'Ваш Ход')
    bot_gm_Fl.shooting() # стрельба Человека в игровое поле Бота
    game_over=True
    print(bot_gm_Fl.show_gride(bot_gm_Fl.mask_gride))
    for i in bot_gm_Fl.gride: #проверка списка ячеек игровой сетки, остались ли там, еще ячейки кораблей
        if '\u2584' in i:
            game_over=False
    if game_over==True:
        print('Игра завершилась Вашей победой! Поздравляем!!!')
        break

    # Процедуры хода Бота
    print(f'{add_tab}Ход Бота')
    human_gm_Fl.shooting() # стрельба Бота в игровое поле Человека
    print(human_gm_Fl.show_gride())
    game_over=True
    for i in human_gm_Fl.gride: #проверка списка ячеек игровой сетки, остались ли там, еще ячейки кораблей
        if '\u2584' in i:
            game_over=False
    if game_over==True:
        print('Игра завершилась победой Бота.')
        break

