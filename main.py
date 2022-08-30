import requests
import random
import html
from helpers import Curses, GameStatic, Database
import curses


class QuestionsAnswers(GameStatic):

    def __init__(self, curses_obj):
        self.curse = curses_obj
        category = self.choose(self.CATEGORIES, category='category')
        category_code = self.CATEGORIES[category]['code']
        self.category = self.CATEGORIES[category]['name'].title()
        self.difficulty = self.DIFFICULTIES[self.choose(self.DIFFICULTIES)]['name'].title()
        self.score = 0
        endpoint = f'&category={category_code}&difficulty={self.difficulty.lower()}'
        url = self.BASE_URL + endpoint
        self.data = requests.get(url).json()['results']
        self.run_quiz()

    def choose(self, container, category='difficulty'):
        self.curse.clear_add_refresh(self.curse.headers_screen, ((f'\n\tQuiz Setup: {category.title()}\n', True),),
                                     self.curse.label)
        self.curse.clear_add_refresh(self.curse.mid_screen, [(f'Choose {category}:\n\n', True)] +
                                     [('\t' + key + ' - ' + value['name'] + '\n\n', False)
                                      for key, value in container.items()], curses.A_BOLD)
        choice = self.curse.clear_add_input('Enter a number of your chosen option: ', container, check=True)
        return choice

    def print_label(self, score_type):
        label_text = f'\n\t{score_type} Score: {self.score} | Category: {self.category} | ' \
                     f'Difficulty: {self.difficulty}\t\n'
        self.curse.clear_add_refresh(self.curse.headers_screen, ((label_text, True), ), self.curse.label)

    def print_question_answers(self, all_answers, question):
        self.curse.mid_screen.clear()
        self.curse.clear_add_refresh(self.curse.mid_screen, [(question, True)] +
                                     [('\t' + j + ' - ' + answer + '\n\n', False) for j, answer in all_answers.items()],
                                     curses.A_BOLD)

    def run_quiz(self):
        indexes = random.sample(range(0, 30), 10)
        self.score = 0
        number = 1
        score_type = 'Current'
        for i in indexes:
            guesses = 1
            self.print_label(score_type)
            question_string = str(number) + '. ' + html.unescape(self.data[i]['question']) + '\n\n'
            correct_answer = html.unescape(self.data[i]['correct_answer'])
            incorrect = [html.unescape(answer) for answer in self.data[i]['incorrect_answers']]
            all_answers = incorrect + [correct_answer]
            random.shuffle(all_answers)
            all_answers = {str(i + 1): value for i, value in enumerate(all_answers)}
            self.print_question_answers(all_answers, question_string)
            choice = self.curse.clear_add_input('Your answer: ', all_answers, check=True)
            while all_answers[choice] != correct_answer:
                self.curse.clear_add_refresh(self.curse.error_screen,
                                             (('\tIncorrect answer. Try again.', True),), self.curse.wrong)
                del all_answers[choice]
                guesses += 1
                self.print_question_answers(all_answers, question_string)
                choice = self.curse.clear_add_input('Your answer: ', all_answers, check=True)
            if guesses == 1:
                self.score += 10
            elif guesses == 2:
                self.score += 6
            elif guesses == 3:
                self.score += 2
            else:
                self.score += 0
            number += 1
        score_type = 'Final'
        self.print_label(score_type)


class Game(GameStatic):

    def __init__(self):
        self.db = Database()
        self.curse = Curses()
        self.first = True
        self.headers = self.get_row(self.HEADERS)
        self.summary_headers = self.get_row(self.SUMMARY_HEADERS)

    def play(self):
        self.curse.headers_screen.addstr('\n\tWelcome to Quiz Game!\t\n', self.curse.label | curses.A_BOLD)
        self.curse.headers_screen.refresh()
        self.curse.mid_screen.addstr(self.INSTRUCTIONS, self.curse.text | curses.A_BOLD)
        self.curse.mid_screen.addstr('\n\tGood Luck!\t\n', self.curse.label | curses.A_BOLD)
        self.curse.mid_screen.refresh()
        while True:
            if self.first:
                word = 'Ready'
                self.first = False
            else:
                word = 'Play again'
            self.curse.clear_add_input(f"{word}? Press any key to start: ")
            game = QuestionsAnswers(self.curse)
            self.db.insert_stat(game)
            self.print_stats()

    @staticmethod
    def get_row(lst):
        return ' | '.join(str(s).center(19) for s in lst) + '\n'

    def print_stats(self):
        all_stats = self.db.get_recent_stats()
        stats_string = ''
        for stat in all_stats:
            stats_string += self.get_row(stat)
        summary_strings = self.db.get_summary_data()
        summary_string = self.get_row(summary_strings)
        self.curse.clear_add_refresh(self.curse.mid_screen,
                                     (('\tMost recent stats:\n', False), (self.headers, True),
                                      (stats_string, False), ('\n\tStats summary:\n', False),
                                      (self.summary_headers, True), (summary_string, False)), self.curse.headers)


if __name__ == '__main__':
    m = Game()
    m.play()
