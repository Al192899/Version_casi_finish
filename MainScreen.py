from PyQt5.QtWidgets import QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QWidget, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from Database import register_load, is_load_unique  # quitamos add_package

class MainScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Logo
        self.logo_label = QLabel(self)
        logo_pixmap = QPixmap("C:/Users/ericksamuel.ramirez/Documents/Routing(Loads)/Proyecto/assets/logo_footer.png")
        if not logo_pixmap or logo_pixmap.isNull():
            self.logo_label.setText("Logo no disponible")
        else:
            self.logo_label.setPixmap(logo_pixmap)
            self.logo_label.setScaledContents(True)
        self.logo_label.setFixedSize(500, 200)
        layout.addWidget(self.logo_label, alignment=Qt.AlignCenter)

        # Load
        self.Load_input = QLineEdit()
        self.Load_input.setPlaceholderText("Número de Load")
        layout.addWidget(self.Load_input)

        # Número de pallets
        pallet_layout = QHBoxLayout()
        self.Pallet_label = QLabel("Número de pallets")
        pallet_layout.addWidget(self.Pallet_label)
        self.Pallet_input = QComboBox()
        self.Pallet_input.addItems(["13", "14", "15", "30"])
        pallet_layout.addWidget(self.Pallet_input)
        layout.addLayout(pallet_layout)

        # Destino
        destino_layout = QHBoxLayout()
        self.destino_label = QLabel("Destino")
        destino_layout.addWidget(self.destino_label)
        self.DESTINO_input = QComboBox()
        self.DESTINO_input.addItems(["Steris I", "Steris II", "Charlotte", "Ontario"])
        destino_layout.addWidget(self.DESTINO_input)
        layout.addLayout(destino_layout)

        # Número de rampa
        rampa_layout = QHBoxLayout()
        self.rampa_label = QLabel("Número de rampa")
        rampa_layout.addWidget(self.rampa_label)
        self.rampa_input = QComboBox()
        self.rampa_input.addItems([f"{i:02}" for i in range(1, 21)])
        rampa_layout.addWidget(self.rampa_input)
        layout.addLayout(rampa_layout)

        # Camión
        self.transport_input = QLineEdit()
        self.transport_input.setPlaceholderText("Número de Camión")
        layout.addWidget(self.transport_input)

        # Botón
        self.start_button = QPushButton('Registrar Load')
        self.start_button.clicked.connect(self.register_load)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def register_load(self):
        load = self.Load_input.text().strip()
        pallets = int(self.Pallet_input.currentText())
        destino = self.DESTINO_input.currentText().strip()
        rampa = self.rampa_input.currentText().strip()
        transporte = self.transport_input.text().strip()

        if not load or not transporte:
            QMessageBox.warning(self, "Error", "Complete todos los campos requeridos.")
            return

        if not is_load_unique(load):
            QMessageBox.warning(self, "Error", f"El Load '{load}' ya existe.")
            return

        try:
            register_load(load, transporte, rampa, destino, pallets)
            QMessageBox.information(self, "Éxito", f"Load '{load}' registrado.")
            self.parent.setCurrentIndex(1)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar Load: {str(e)}")