from bs4 import BeautifulSoup, NavigableString, Tag
from urllib import request
import sys
from operator import itemgetter

class Document(object):
    def __init__(self, position):
        self.tables = []
        response = request.urlopen('http://www.footballoutsiders.com/stats/{0}'.format(position))
        html_doc = response.read()
        soup = BeautifulSoup(html_doc, 'html.parser')
        self.headings = soup.findAll("h1")
        self.table_elements = soup.findAll("table", { "class" : "stats" })

        for element in self.table_elements:
            table = Table()
            table.load(element)
            self.tables.append(table)


    def print(self, key):
        for table in self.tables:
            try:
                self.print_headings()
                table.print('EYds')
            except Exception as e:
                print(e)
            print("")

    def print_headings(self):
        for heading in self.headings:
            print(heading.string)

class Table(object):
    def __init__(self):
        self.column_names = []
        self.players = {}
        self.title = ""

    def find_title(self, table):
        siblings = table.previous_siblings
        for lookback in range(5):
            sibling = next(siblings)
            if isinstance(sibling, Tag) and sibling.name == "h3":
                return sibling.text
        return None

    def header_row(self, cells):
        for i in range(0,len(cells)-1):
            if not cells[i].text == self.column_names[i]:
                return False
        return True

    def load(self, table):
        self.title = self.find_title(table)
        for row in table.findAll("tr"):
            cells = row.findAll("td")
            if not self.column_names:
                for cell in cells:
                    self.column_names.append(cell.text)
            elif not self.header_row(cells):
                player=Player(self.column_names, cells)
                self.players[player.name()] = player

    def print(self, field):
        print(self.title)
        for player in sorted(self.players.values(), key=lambda x: x.stat(field), reverse=True):
            print(player.get_stats(field))



class Player(object):
    column_names = []
    players = {}
    title = ""

    def __init__(self, column_names, cells):
        self.stats = {}
        for i in range(0,len(cells)-1):
            self.stats[column_names[i]] = cells[i].text

    def stat(self, key):
        try:
            return float(self.stats[key])
        except Exception:
            return 0.0

    def name(self):
        return self.stats['Player']

    def get_stats(self, key):
        return "{0:<32}: {1:<4}".format(self.name(), self.stats[key])

for position in ["rb", "wr", "te"]:
    document = Document(position)
    document.print("EYds")
