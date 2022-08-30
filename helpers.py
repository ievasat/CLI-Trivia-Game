import os
import sqlite3
import curses
import sys


class Curses:
    def __init__(self):
        self.screen = curses.initscr()
        self.cols = 120
        curses.resize_term(26, self.cols)
        self.headers_screen = curses.newwin(3, self.cols, 0, 0)
        self.error_screen = curses.newwin(3, self.cols, 4, 0)
        self.mid_screen = curses.newwin(17, self.cols, 7, 0)
        self.input_screen = curses.newwin(3, self.cols, 23, 0)
        self.input_screen.keypad(True)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        self.error = curses.color_pair(1)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_MAGENTA)
        self.wrong = curses.color_pair(2)
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.text = curses.color_pair(3)
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_GREEN)
        self.label = curses.color_pair(4)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_YELLOW)
        self.headers = curses.color_pair(5)

    @staticmethod
    def clear_refresh(screen):
        screen.clear()
        screen.refresh()

    @staticmethod
    def clear_add_refresh(screen, strings, arg):
        screen.clear()
        for string in strings:
            if string[1]:
                screen.addstr(string[0], arg)
            else:
                screen.addstr(string[0])
        screen.refresh()

    def clear_add_input(self, string, container=None, check=False):
        self.input_screen.clear()
        self.input_screen.addstr(string, curses.A_BOLD)
        choice = self.input_screen.getch()
        if not check:
            return self.quit_check(choice)
        choice = self.invalid_check(choice, container, string)
        return choice

    def invalid_check(self, choice, container, sentence):
        choice = self.quit_check(choice)
        while choice not in container:
            self.clear_add_refresh(self.error_screen, (('\tInvalid input. Try again.', True),), self.error)
            choice = self.clear_add_input(sentence, container)
        self.clear_refresh(self.error_screen)
        return choice

    @staticmethod
    def quit_check(choice):
        if choice == 27:
            quit()
        elif choice == 546 or choice == 3:
            os.system('python main.py')
            sys.exit()
        return chr(choice)


class GameStatic:
    BASE_URL = 'https://opentdb.com/api.php?amount=30&type=multiple'
    DIFFICULTIES = {'1': {'name': 'Easy'},
                    '2': {'name': 'Medium'},
                    '3': {'name': 'Hard'},
                    }
    CATEGORIES = {'1': {'name': 'Computer Science',
                        'code': '18'},
                  '2': {'name': 'Nature',
                        'code': '17'},
                  '3': {'name': 'General Knowledge',
                        'code': '9'},
                  '4': {'name': 'History',
                        'code': '23'},
                  }
    INSTRUCTIONS = ' * Choose 1 out of 4 categories and 1 out of 3 difficulties.\n\n' \
                   ' * You will then get 10 multiple choice questions and answers.\n\n' \
                   ' * You get 10 points for each correct answer answered on a first try,\n' \
                   '\t6 points - second try, 2 points - third try.\n\n' + \
                   " * Press 'Esc' to quit or 'ctrl-C' to restart at any time. \n\n" + \
                   ' *** WARNING - do not resize this windows, doing so will restart the program.\n\n'
    HEADERS = ['ID', 'Timestamp', 'Difficulty', 'Category', 'Score']
    SUMMARY_HEADERS = ['Quizzes Completed', 'Average Score', 'Best at', 'Worst at']
    TABLES = [
        '''Difficulty (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, 
        name TEXT UNIQUE)''',
        '''Category (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, 
        name TEXT UNIQUE)''',
        '''Stats (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, 
        date DATE, difficulty_id INTEGER, category_id INTEGER, score INTEGER)''',
    ]


class Database(GameStatic):
    connection = None
    cursor = None

    def __init__(self):
        if self.connection is None:
            self.connection = sqlite3.connect('stats.sqlite')
            self.cursor = self.connection.cursor()
        for table in GameStatic.TABLES:
            self.cursor.execute(f'''CREATE TABLE if not exists {table}''')
        self.insert_or_ignore(self.DIFFICULTIES, 'Difficulty')
        self.insert_or_ignore(self.CATEGORIES, 'Category')
        self.connection.commit()

    def insert_or_ignore(self, dictionary, name):
        for value in dictionary.values():
            self.cursor.execute(f'INSERT or IGNORE into {name} (name) values (?)', (value['name'],))

    def get_recent_stats(self):
        tuples = self.cursor.execute('''SELECT Stats.id, Stats.date, Difficulty.name, Category.name, Stats.score
         FROM Stats INNER JOIN Difficulty on Stats.difficulty_id = Difficulty.id
         INNER JOIN Category on Stats.category_id = Category.id''').fetchall()[-5:]
        return tuples

    def get_worst_best(self, min_or_max):
        self.cursor.execute(f'''SELECT name FROM Category WHERE id=(
        SELECT category_id FROM (SELECT category_id, {min_or_max}(averages.avg_score) FROM
        (SELECT category_id, AVG(score) as avg_score FROM Stats GROUP BY category_id) averages))''')
        category = self.cursor.fetchone()[0]
        return category

    def insert_stat(self, instance):
        self.cursor.execute(f'''INSERT INTO Stats 
        (date, difficulty_id, category_id, score) VALUES(
        datetime('now', 'localtime'), 
        (SELECT id FROM Difficulty WHERE name='{instance.difficulty}'), 
        (SELECT id FROM Category WHERE name='{instance.category}'), ?)''', (instance.score,))
        self.connection.commit()

    def get_summary_data(self):
        total_quizzes = self.cursor.execute('SELECT COUNT(id) from Stats').fetchone()[0]
        self.cursor.execute('SELECT AVG(score) from Stats')
        average_score = self.cursor.fetchone()[0]
        best_at = self.get_worst_best('MAX')
        worst_at = self.get_worst_best('MIN')
        return [total_quizzes, round(average_score, 2), best_at, worst_at]
