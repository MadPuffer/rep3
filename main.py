from PyQt5.QtWidgets import QWidget, QApplication, QTableWidgetItem
import sqlite3
import sys
from PyQt5 import uic


class Coffee(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Coffee')
        uic.loadUi('main.ui', self)
        self.fillTable()

    def fillTable(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        rows = cur.execute("""select * from coffee""").fetchall()
        self.table.setRowCount(len(rows))
        for row in range(len(rows)):
            for column in range(7):
                self.table.setItem(row, column, QTableWidgetItem(str(rows[row][column])))
            self.table.resizeColumnsToContents()
        con.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Coffee()
    window.show()
    sys.exit(app.exec_())
