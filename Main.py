from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QIcon
from MainScreen import MainScreen
from PalletScreen import PalletScreen 
from Database import create_db
import sys

class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()

        # Inicializar la base de datos
        create_db()

        # Crear instancias de las pantallas
        self.main_screen = MainScreen(self)
        self.pallet_screen = PalletScreen(self)

        # Agregar pantallas al QStackedWidget
        self.addWidget(self.main_screen)  # Índice 0
        self.addWidget(self.pallet_screen)  # Índice 1

        # Configurar propiedades de la ventana
        self.setWindowTitle("SystemLoadsCharge")
        self.setWindowIcon(QIcon(r"C:/Users/ericksamuel.ramirez/Documents/Routing(Loads)/Proyecto/assets/Routing.png"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        with open(r"C:/Users/ericksamuel.ramirez/Documents/Routing(Loads)/Proyecto/style.qss", "r") as style_file:
            app.setStyleSheet(style_file.read())
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'style.qss'.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())