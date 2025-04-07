from PyQt5.QtWidgets import QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit, QWidget, QMessageBox
from Database import scan_pallet, get_all_packages, export_to_excel, generate_pdf, get_expected_pallet_count


class PalletScreen(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.pallet_input = QLineEdit()
        self.pallet_input.setPlaceholderText("Código del Pallet")
        layout.addWidget(self.pallet_input)

        self.scan_button = QPushButton("Escanear Pallet")
        self.scan_button.clicked.connect(self.scan_pallet_ui)
        layout.addWidget(self.scan_button)

        self.pallet_list = QTextEdit()
        self.pallet_list.setReadOnly(True)
        layout.addWidget(self.pallet_list)

        self.refresh_button = QPushButton("Actualizar Lista")
        self.refresh_button.clicked.connect(self.load_pallets_ui)
        layout.addWidget(self.refresh_button)

        self.export_excel_button = QPushButton("Exportar a Excel")
        self.export_excel_button.clicked.connect(self.export_to_excel_ui)
        layout.addWidget(self.export_excel_button)

        self.generate_pdf_button = QPushButton("Generar PDF")
        self.generate_pdf_button.clicked.connect(self.generate_pdf_ui)
        layout.addWidget(self.generate_pdf_button)

        self.back_button = QPushButton("Regresar")
        self.back_button.clicked.connect(self.go_back)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def scan_pallet_ui(self):
        pallet_id = self.pallet_input.text().strip()
        if not pallet_id:
            QMessageBox.warning(self, "Error", "Ingrese el código del Pallet.")
            return

        load = self.parent.main_screen.Load_input.text().strip()
        if not load:
            QMessageBox.warning(self, "Error", "No se ha ingresado un Load.")
            return

        try:
            scan_pallet(load, pallet_id)
            self.load_pallets_ui()
            QMessageBox.information(self, "Éxito", f"Pallet '{pallet_id}' registrado.")

            total_esperado = get_expected_pallet_count(load)
            actuales = len(get_all_packages(load))
            if actuales >= total_esperado:
                QMessageBox.information(self, "Completado", f"Se han escaneado los {actuales} pallets esperados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al escanear: {str(e)}")

    def load_pallets_ui(self):
        load = self.parent.main_screen.Load_input.text().strip()
        if not load:
            QMessageBox.warning(self, "Error", "No hay Load activo.")
            return

        try:
            pallets = get_all_packages(load)
            self.pallet_list.setPlainText("\n".join(pallets) if pallets else "No hay pallets registrados.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los pallets: {str(e)}")

    def export_to_excel_ui(self):
        try:
            export_to_excel()
            QMessageBox.information(self, "Éxito", "Exportado a Excel correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")

    def generate_pdf_ui(self):
        try:
            generate_pdf()
            QMessageBox.information(self, "Éxito", "PDF generado correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar PDF: {str(e)}")

    def go_back(self):
        self.parent.setCurrentIndex(0)