import sys
import sqlite3
from random import choice, shuffle

from PyQt6.QtGui import (
    QPixmap,
    QPalette,
    QIntValidator
)
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLCDNumber,
    QLabel,
    QInputDialog,
    QFileDialog,
    QLineEdit,
    QWidget,
    QTextBrowser,
    QPlainTextEdit
)


class NewGameError(BaseException):
    pass


class MonopolyHelper(QMainWindow):
    def __init__(self):
        super().__init__()

        connection = sqlite3.connect('db/monopoly.sqlite')
        cursor = connection.cursor()
        research = cursor.execute('''SELECT * FROM cards''').fetchall()

        self.database = []
        for i in research:
            self.database.append(list(i))

        self.setWindowTitle('Monopoly Helper')
        self.setFixedSize(1300, 720)

        self.steps = [1, 2, 3, 4, 5, 6]

        self.chances = open('data/chances.txt', encoding='utf-8', mode='r').readlines()
        self.chances_copy = self.chances

        self.com_chests = open('data/com_chests.txt', encoding='utf-8', mode='r').readlines()
        self.com_chests_copy = self.com_chests

        self.about = ''.join(open('data/about.txt', encoding='utf-8', mode='r').readlines())

        self.players = dict()
        self.budgets = dict()
        self.deeds = dict()

        self.buttons = dict()
        self.pluses = dict()
        self.minuses = dict()

        self.numfields = dict()

        self.initUI()

    def initUI(self):
        self.name = QLabel('<b>Monopoly Helper<b>', self)
        self.name.setGeometry(245, 10, 698, 60)
        self.name.setStyleSheet("QLabel {font-size: 40px; }")

        self.pixmap = QPixmap('data/image.jpg')
        self.image = QLabel(self)
        self.image.move(63, 90)
        self.image.resize(923, 392)
        self.image.setPixmap(self.pixmap)

        self.dice = QPushButton('Dice', self)
        self.dice.setGeometry(1050, 10, 225, 30)
        self.dice.clicked.connect(self.dice_clicked)

        self.dice_result = QLCDNumber(self)
        self.dice_result.setGeometry(1050, 40, 225, 50)
        self.dice_opened = 0

        self.chance = QPushButton('Chance', self)
        self.chance.setGeometry(1050, 125, 70, 90)
        self.chance.clicked.connect(self.chance_clicked)
        self.chance_opened = 0

        self.chance_counter = QLCDNumber(self)
        self.chance_counter.setGeometry(1050, 480, 70, 50)
        self.chance_counter_name = QLabel('Chances\ncounter:', self)
        self.chance_counter_name.setGeometry(1055, 430, 70, 50)
        self.chance_count = 0

        self.community_chest = QPushButton('Comm.\nChest', self)
        self.community_chest.setGeometry(1205, 125, 70, 90)
        self.community_chest.clicked.connect(self.community_chest_clicked)
        self.com_chest_opened = 0

        self.com_chests_counter = QLCDNumber(self)
        self.com_chests_counter.setGeometry(1205, 480, 70, 50)
        self.com_chests_counter_name = QLabel('Comm. chest\ncounter:', self)
        self.com_chests_counter_name.setGeometry(1205, 430, 70, 50)
        self.com_chest_count = 0

        self.card_result = QPlainTextEdit(self)
        self.card_result.setPlainText('...')
        self.card_result.setGeometry(1050, 230, 225, 200)
        self.card_opened = ''

        self.new_button = QPushButton(self)
        self.new_button.setText('New\nGame')
        self.new_button.setGeometry(10, 10, 70, 60)
        self.new_button.clicked.connect(self.new_button_clicked)

        self.isNew = False

        self.open_button = QPushButton(self)
        self.open_button.setText('Open\nGame')
        self.open_button.setGeometry(85, 10, 70, 60)
        self.open_button.clicked.connect(self.open_button_clicked)

        self.isOpen = False

        self.save_button = QPushButton(self)
        self.save_button.setText('Save\nGame')
        self.save_button.setGeometry(160, 10, 70, 60)
        self.save_button.clicked.connect(self.save_button_clicked)

        self.about_button = QPushButton(self)
        self.about_button.setText('About\nprogramme')
        self.about_button.setGeometry(917, 10, 70, 60)
        self.about_button.clicked.connect(self.about_button_clicked)

        self.count = 0

        self.num = None

    def dice_clicked(self):
        self.dice_opened = choice(self.steps) + choice(self.steps)
        self.dice_result.display(self.dice_opened)

    def chance_clicked(self):
        if self.chance_opened >= len(self.chances):
            self.chances = self.chances_copy
            self.chance_opened = 0

        if self.chance_opened == 0:
            shuffle(self.chances)
            self.card_opened = self.chances[self.chance_opened].rstrip()
            self.card_result.setPlainText(self.card_opened)

        else:
            self.card_opened = self.chances[self.chance_opened].rstrip()
            self.card_result.setPlainText(self.card_opened)

        self.chance_opened += 1
        self.chance_count += 1
        self.chance_counter.display(self.chance_count)

    def community_chest_clicked(self):
        if self.com_chest_opened >= len(self.com_chests):
            self.com_chests = self.com_chests_copy
            self.com_chest_opened = 0

        if self.com_chest_opened == 0:
            shuffle(self.com_chests)
            self.card_opened = self.com_chests[self.com_chest_opened].rstrip()
            self.card_result.setPlainText(self.card_opened)

        else:
            self.card_opened = self.com_chests[self.com_chest_opened].rstrip()
            self.card_result.setPlainText(self.card_opened)

        self.com_chest_opened += 1
        self.com_chest_count += 1
        self.com_chests_counter.display(self.com_chest_count)

    def new_button_clicked(self):
        try:
            if self.isOpen:
                self.isNew = True
                self.image.hide()

                self.card_result.setPlainText(self.card_opened)
                self.chance_counter.display(self.chance_count)
                self.com_chests_counter.display(self.com_chest_count)
                self.dice_result.display(self.dice_opened)

                self.isOpen = False

            elif not self.isOpen and not self.isNew:
                num, ok_pressed = QInputDialog.getItem(
                    self, 'Add players', 'Select',
                    ('1', '2', '3', '4', '5', '6', '7', '8'), 1, False)

                if ok_pressed:
                    self.isNew = True
                    self.count = num
                    self.image.hide()

                    for i in range(1, int(num) + 1):
                        self.players[str(i)] = f'Player {i}'
                        self.budgets[str(i)] = '1500'
                        self.deeds[str(i)] = '...'
                        self.buttons[str(i)] = ''

                else:
                    self.isNew = False

            elif self.isNew:
                raise NewGameError

            else:
                self.image.hide()

            x = 80
            y = 120
            for k, v in self.players.items():
                self.players[k] = QLineEdit(self)
                self.players[k].setText(v)
                self.players[k].setStyleSheet('QLineEdit {font-size: 20px}')
                self.players[k].setGeometry(x, y, 250, 35)
                self.players[k].show()

                if x > 380:
                    x = 80
                    y += 180
                else:
                    x += 300

            x = 80
            y = 160
            for k, v in self.budgets.items():
                self.budgets[k] = QLineEdit(self)
                self.budgets[k].setText(v)
                self.budgets[k].setStyleSheet('QLineEdit {font-size: 20px}')
                self.budgets[k].setValidator(QIntValidator())
                self.budgets[k].setGeometry(x, y, 120, 40)
                self.budgets[k].show()

                self.pluses[k] = QPushButton(self)
                self.pluses[k].setText('+')
                self.pluses[k].setGeometry(x + 125, y, 20, 20)
                self.pluses[k].clicked.connect(self.operation)
                self.pluses[k].show()

                self.minuses[k] = QPushButton(self)
                self.minuses[k].setText('-')
                self.minuses[k].setGeometry(x + 125, y + 20, 20, 20)
                self.minuses[k].clicked.connect(self.operation)
                self.minuses[k].show()

                self.numfields[k] = QLineEdit(self)
                self.numfields[k].setStyleSheet('QLineEdit {font-size: 20px}')
                self.numfields[k].setValidator(QIntValidator())
                self.numfields[k].setGeometry(x + 150, y, 100, 40)
                self.numfields[k].show()

                if x > 380:
                    x = 80
                    y += 180
                else:
                    x += 300

            x = 80
            y = 210
            for k, v in self.deeds.items():
                self.deeds[k] = QTextBrowser(self)
                self.deeds[k].setText(v)
                self.deeds[k].setGeometry(x, y, 200, 40)
                self.deeds[k].show()

                self.buttons[k] = QPushButton(self)
                self.buttons[k].setText('+')
                self.buttons[k].setGeometry(x + 210, y, 40, 40)
                self.buttons[k].clicked.connect(self.deeds_button_clicked)
                self.buttons[k].show()

                if x > 380:
                    x = 80
                    y += 180
                else:
                    x += 300

        except NewGameError:
            agreement, ok_pressed = QInputDialog.getItem(
                self, 'New game', 'Do you want to start a new game?',
                ('Yes', 'No'), 1, False)

            if ok_pressed:
                if agreement == 'No':
                    pass

                else:
                    self.image.show()

                    self.dice_result.display(0)
                    self.card_result.setPlainText('...')
                    self.chance_counter.display(0)
                    self.com_chests_counter.display(0)

                    self.chance_count = 0
                    self.com_chest_count = 0

                    for k, v in self.players.items():
                        self.players[k].hide()
                    for k, v in self.budgets.items():
                        self.budgets[k].hide()
                    for k, v in self.deeds.items():
                        self.deeds[k].hide()
                    for k, v in self.buttons.items():
                        self.buttons[k].hide()
                    for k, v in self.numfields.items():
                        self.numfields[k].hide()
                    for k, v in self.pluses.items():
                        self.pluses[k].hide()
                    for k, v in self.minuses.items():
                        self.minuses[k].hide()

                    self.players.clear()
                    self.budgets.clear()
                    self.deeds.clear()
                    self.buttons.clear()
                    self.numfields.clear()
                    self.pluses.clear()
                    self.minuses.clear()

                    self.isNew = False

            else:
                pass

    def open_button_clicked(self):
        try:
            filename = QFileDialog.getOpenFileName(self,
                                                   'Open', '', '*.mon')[0]
            filename = filename.split('/')[-1]

            if filename:
                for k, v in self.players.items():
                    self.players[k].hide()
                for k, v in self.budgets.items():
                    self.budgets[k].hide()
                for k, v in self.deeds.items():
                    self.deeds[k].hide()
                for k, v in self.buttons.items():
                    self.buttons[k].hide()
                for k, v in self.numfields.items():
                    self.numfields[k].hide()
                for k, v in self.pluses.items():
                    self.pluses[k].hide()
                for k, v in self.minuses.items():
                    self.minuses[k].hide()

                self.players.clear()
                self.budgets.clear()
                self.deeds.clear()
                self.buttons.clear()
                self.numfields.clear()
                self.pluses.clear()
                self.minuses.clear()

            else:
                raise FileNotFoundError

            with open(filename, encoding='utf-8', mode='r') as file:
                game = file.readlines()

                self.chances.clear()
                self.com_chests.clear()
                self.card_result.clear()
                self.count = int(game[1])
                self.chances = game[2].split('||')
                self.com_chests = game[3].split('||')
                self.chance_opened = int(game[4])
                self.com_chest_opened = int(game[5])
                self.dice_opened = int(game[6])
                self.chance_count = int(game[7])
                self.com_chest_count = int(game[8])
                self.card_opened = game[9]
                self.chances_copy = game[10].split('||')
                self.com_chests_copy = game[11].split('||')

                v = 13
                for i in range(self.count):
                    self.players[f'{i + 1}'] = game[v].rstrip()
                    self.budgets[f'{i + 1}'] = game[v + 1].rstrip()
                    self.deeds[f'{i + 1}'] = '\n'.join(
                        game[v + 2].split('||')).rstrip()
                    v += 6

                self.isOpen = True

                self.new_button_clicked()

        except FileNotFoundError:
            pass

    def save_button_clicked(self):
        try:
            filename = QFileDialog.getSaveFileName(self,
                                                   'Save', '', '*.mon')[0]

            with open(filename, encoding='utf-8', mode='w') as file:
                file.write('%%%MONOPOLY HELPER%%%\n')
                file.write(f'{self.count}\n')
                file.write(f'{"||".join([i.rstrip() for i in self.chances])}\n')
                file.write(f'{"||".join([i.rstrip() for i in self.com_chests])}\n')
                file.write(f'{self.chance_opened}\n')
                file.write(f'{self.com_chest_opened}\n')
                file.write(f'{self.dice_opened}\n')
                file.write(f'{self.chance_count}\n')
                file.write(f'{self.com_chest_count}\n')
                file.write(f'{self.card_result.toPlainText().rstrip()}\n')
                file.write(f'{"||".join([i.rstrip() for i in self.chances_copy])}\n')
                file.write(f'{"||".join([i.rstrip() for i in self.com_chests_copy])}\n')

                for i in range(1, int(self.count) + 1):
                    file.write('\n')
                    file.write(self.players[str(i)].text() + '\n')
                    file.write(self.budgets[str(i)].text() + '\n')
                    file.write('||'.join(self.deeds[str(i)].toPlainText().split('\n')) + '\n')
                    file.write('\n')
                    file.write('---\n')

        except FileNotFoundError:
            pass

    def operation(self):
        btn = self.sender()

        for k, v in self.buttons.items():
            if self.pluses[k] == btn:
                self.num = k

            if self.minuses[k] == btn:
                self.num = k

        try:
            op = eval(f'{self.budgets[self.num].text()}{self.sender().text()}{self.numfields[self.num].text()}')
            self.budgets[self.num].setText(str(op))
            self.numfields[self.num].setText('')

        except SyntaxError:
            pass

    def about_button_clicked(self):
        self.window = AboutProgramme()
        self.window.show()

    def deeds_button_clicked(self):
        btn = self.sender()

        for k, v in self.buttons.items():
            if self.buttons[k] == btn:
                self.num = k

        self.window = Deeds(self.num, self.deeds)
        self.window.show()


class AboutProgramme(MonopolyHelper, QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('About')
        self.setFixedSize(500, 300)
        self.setStyleSheet('background-color: white')

        self.initUI()

    def initUI(self):
        self.text = QTextBrowser(self)
        self.text.setPlainText(self.about)
        self.text.setGeometry(0, 0, 500, 300)
        self.text.setStyleSheet('QTextBrowser {font-size: 15px}')


class Deeds(MonopolyHelper, QWidget):
    def __init__(self, num, deeds):
        super().__init__()

        self.num = num
        self.deeds = deeds

        self.setFixedSize(700, 450)
        self.setStyleSheet('background-color: black')
        self.image.hide()

        self.line = ''

        x = 10
        y = 10
        for i in self.database:
            self.btn = QPushButton(i[1], self)
            self.btn.setGeometry(x, y, 330, 30)

            if i[3] == 1:
                self.btn.setDisabled(True)
            elif i[0] == 1:
                self.btn.setStyleSheet('QPushButton {background-color: #964b00}')
            elif i[0] == 2:
                self.btn.setStyleSheet('QPushButton {background-color: #afeeee}')
            elif i[0] == 3:
                self.btn.setStyleSheet('QPushButton {background-color: #dd00a5}')
            elif i[0] == 4:
                self.btn.setStyleSheet('QPushButton {background-color: #ff910c}')
            elif i[0] == 5:
                self.btn.setStyleSheet('QPushButton {background-color: #ff0000}')
            elif i[0] == 6:
                self.btn.setStyleSheet('QPushButton {background-color: #ffff00}')
            elif i[0] == 7:
                self.btn.setStyleSheet('QPushButton {background-color: #00ff00}')
            elif i[0] == 8:
                self.btn.setStyleSheet('QPushButton {background-color: #0000ff}')
            elif i[0] == 9:
                self.btn.setStyleSheet('QPushButton {background-color: #a0a0a0}')
            elif i[0] == 10:
                self.btn.setStyleSheet('QPushButton {background-color: #666666}')

            if y > 370:
                y = 10
                x = 360
            else:
                y += 30

            self.btn.clicked.connect(self.chosen)

    def chosen(self):
        if not self.deeds[self.num].toPlainText() == '...':
            self.line = self.deeds[self.num].toPlainText()
            self.deeds[self.num].setPlainText(
                f'{self.line.lstrip()}\n{self.sender().text()}')

        else:
            self.line = ''
            self.deeds[self.num].setPlainText(f'{self.sender().text()}')

        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MonopolyHelper()
    ex.show()
    sys.exit(app.exec())
