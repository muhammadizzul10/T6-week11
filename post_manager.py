# NAMA: MUHAMMAD IZZUL ISLAM
# NIM: F1D02410077
# KELAS: D

# main.py

import sys
import requests

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QLineEdit,
    QTextEdit,
    QMessageBox,
    QComboBox,
    QSplitter,
    QHeaderView,
)


BASE_URL = "https://api.pahrul.my.id/api/posts"


# API WORKER THREAD
class ApiWorker(QThread):
    success = Signal(object)
    error = Signal(str)

    def __init__(self, method, url, data=None):
        super().__init__()
        self.method = method
        self.url = url
        self.data = data

    def run(self):
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            if self.method == "GET":
                response = requests.get(
                    self.url,
                    headers=headers,
                    timeout=5
                )

            elif self.method == "POST":
                response = requests.post(
                    self.url,
                    json=self.data,
                    headers=headers,
                    timeout=5
                )

            elif self.method == "PUT":
                response = requests.put(
                    self.url,
                    json=self.data,
                    headers=headers,
                    timeout=5
                )

            elif self.method == "DELETE":
                response = requests.delete(
                    self.url,
                    headers=headers,
                    timeout=5
                )

            # VALIDASI ERROR
            if response.status_code == 422:
                try:
                    data = response.json()
                    message = data.get("message", "Validation Error")
                except:
                    message = "Validation Error"

                self.error.emit(message)
                return

            response.raise_for_status()

            # DELETE kadang kosong
            if response.text:
                data = response.json()
            else:
                data = {}

            self.success.emit(data)

        except requests.Timeout:
            self.error.emit("Request timeout")

        except requests.ConnectionError:
            self.error.emit("Tidak dapat terhubung ke server")

        except requests.HTTPError as e:
            self.error.emit(f"HTTP Error: {str(e)}")

        except Exception as e:
            self.error.emit(str(e))


# MAIN WINDOW
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Post Manager")
        self.resize(1200, 700)

        self.selected_id = None

        self.setup_ui()
        self.load_posts()

    # UI
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        # BUTTONS
        button_layout = QHBoxLayout()

        self.btn_add = QPushButton("Tambah")
        self.btn_edit = QPushButton("Edit")
        self.btn_delete = QPushButton("Hapus")
        self.btn_refresh = QPushButton("Refresh")

        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

        button_layout.addWidget(self.btn_add)
        button_layout.addWidget(self.btn_edit)
        button_layout.addWidget(self.btn_delete)
        button_layout.addWidget(self.btn_refresh)

        # SPLITTER
        splitter = QSplitter()

        # TABLE
        self.table = QTableWidget()
        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Title",
            "Author",
            "Status"
        ])

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        splitter.addWidget(self.table)

        # DETAIL PANEL
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)

        form = QFormLayout()

        self.input_title = QLineEdit()
        self.input_author = QLineEdit()
        self.input_slug = QLineEdit()

        self.input_status = QComboBox()
        self.input_status.addItems([
            "published",
            "draft"
        ])

        self.input_body = QTextEdit()

        form.addRow("Title", self.input_title)
        form.addRow("Author", self.input_author)
        form.addRow("Slug", self.input_slug)
        form.addRow("Status", self.input_status)
        form.addRow("Body", self.input_body)

        detail_layout.addLayout(form)

        # COMMENTS
        detail_layout.addWidget(QLabel("Comments"))

        self.comments = QTextEdit()
        self.comments.setReadOnly(True)

        detail_layout.addWidget(self.comments)

        splitter.addWidget(detail_widget)

        splitter.setSizes([700, 500])

        # SAVE BUTTON
        self.btn_save = QPushButton("Simpan")
        detail_layout.addWidget(self.btn_save)

        # STATUS LABEL
        self.status_label = QLabel("Ready")

        # ADD TO MAIN
        main_layout.addLayout(button_layout)
        main_layout.addWidget(splitter)
        main_layout.addWidget(self.status_label)

        # SIGNALS
        self.btn_refresh.clicked.connect(self.load_posts)
        self.table.cellClicked.connect(self.select_post)

        self.btn_add.clicked.connect(self.clear_form)
        self.btn_save.clicked.connect(self.save_post)

        self.btn_edit.clicked.connect(self.fill_form)
        self.btn_delete.clicked.connect(self.delete_post)

    # STATE
    def set_loading(self, loading=True):
        self.btn_add.setEnabled(not loading)
        self.btn_edit.setEnabled(
            not loading and self.selected_id is not None
        )
        self.btn_delete.setEnabled(
            not loading and self.selected_id is not None
        )
        self.btn_refresh.setEnabled(not loading)
        self.btn_save.setEnabled(not loading)

        if loading:
            self.status_label.setText("Loading...")
        else:
            self.status_label.setText("Ready")

    # LOAD POSTS
    def load_posts(self):
        self.set_loading(True)

        self.worker = ApiWorker(
            "GET",
            BASE_URL
        )

        self.worker.success.connect(self.show_posts)
        self.worker.error.connect(self.show_error)

        self.worker.start()

    def show_posts(self, data):
        self.set_loading(False)

        posts = data.get("data", data)

        self.table.setRowCount(len(posts))

        for row, post in enumerate(posts):
            self.table.setItem(
                row,
                0,
                QTableWidgetItem(str(post.get("id")))
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(post.get("title", ""))
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(post.get("author", ""))
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(post.get("status", ""))
            )

    # SELECT POST
    def select_post(self, row):
        post_id = self.table.item(row, 0).text()

        self.selected_id = post_id

        self.btn_edit.setEnabled(True)
        self.btn_delete.setEnabled(True)

        self.load_detail(post_id)

    # LOAD DETAIL
    def load_detail(self, post_id):
        self.set_loading(True)

        self.worker = ApiWorker(
            "GET",
            f"{BASE_URL}/{post_id}"
        )

        self.worker.success.connect(self.show_detail)
        self.worker.error.connect(self.show_error)

        self.worker.start()

    def show_detail(self, data):
        self.set_loading(False)

        post = data.get("data", data)

        self.current_post = post

        self.input_title.setText(post.get("title", ""))
        self.input_author.setText(post.get("author", ""))
        self.input_slug.setText(post.get("slug", ""))
        self.input_body.setPlainText(post.get("body", ""))

        status = post.get("status", "draft")

        index = self.input_status.findText(status)

        if index >= 0:
            self.input_status.setCurrentIndex(index)

        # COMMENTS
        comments = post.get("comments", [])

        text = ""

        for c in comments:
            text += f"- {c.get('body', '')}\n"

        self.comments.setPlainText(text)

    # CLEAR FORM
    def clear_form(self):
        self.selected_id = None

        self.input_title.clear()
        self.input_author.clear()
        self.input_slug.clear()
        self.input_body.clear()

        self.comments.clear()

        self.input_status.setCurrentIndex(0)

        self.btn_edit.setEnabled(False)
        self.btn_delete.setEnabled(False)

    # SAVE POST
    def save_post(self):
        title = self.input_title.text().strip()
        author = self.input_author.text().strip()
        slug = self.input_slug.text().strip()
        body = self.input_body.toPlainText().strip()
        status = self.input_status.currentText()

        if not title or not author or not slug or not body:
            QMessageBox.warning(
                self,
                "Warning",
                "Semua field wajib diisi"
            )
            return

        payload = {
            "title": title,
            "author": author,
            "slug": slug,
            "body": body,
            "status": status
        }

        self.set_loading(True)

        # CREATE
        if self.selected_id is None:
            self.worker = ApiWorker(
                "POST",
                BASE_URL,
                payload
            )

            self.worker.success.connect(self.create_success)

        # UPDATE
        else:
            self.worker = ApiWorker(
                "PUT",
                f"{BASE_URL}/{self.selected_id}",
                payload
            )

            self.worker.success.connect(self.update_success)

        self.worker.error.connect(self.show_error)

        self.worker.start()

    # CREATE SUCCESS
    def create_success(self, data):
        self.set_loading(False)

        post = data.get("data", data)

        QMessageBox.information(
            self,
            "Sukses",
            f"Post berhasil ditambahkan\nID: {post.get('id')}"
        )

        self.load_posts()
        self.clear_form()

    # UPDATE SUCCESS
    def update_success(self, data):
        self.set_loading(False)

        QMessageBox.information(
            self,
            "Sukses",
            "Post berhasil diperbarui"
        )

        self.load_posts()

    # FILL FORM
    def fill_form(self):
        if not hasattr(self, "current_post"):
            return

        post = self.current_post

        self.input_title.setText(post.get("title", ""))
        self.input_author.setText(post.get("author", ""))
        self.input_slug.setText(post.get("slug", ""))
        self.input_body.setPlainText(post.get("body", ""))

    # DELETE POST
    def delete_post(self):
        if self.selected_id is None:
            return

        confirm = QMessageBox.question(
            self,
            "Konfirmasi",
            "Yakin ingin menghapus post ini?\n"
            "Semua comments juga akan terhapus."
        )

        if confirm != QMessageBox.Yes:
            return

        self.set_loading(True)

        self.worker = ApiWorker(
            "DELETE",
            f"{BASE_URL}/{self.selected_id}"
        )

        self.worker.success.connect(self.delete_success)
        self.worker.error.connect(self.show_error)

        self.worker.start()

    # DELETE SUCCESS
    def delete_success(self, data):
        self.set_loading(False)

        QMessageBox.information(
            self,
            "Sukses",
            "Post berhasil dihapus"
        )

        self.clear_form()
        self.load_posts()

    # ERROR
    def show_error(self, message):
        self.set_loading(False)

        if "slug" in message.lower():
            message = "Slug sudah digunakan"

        QMessageBox.critical(
            self,
            "Error",
            message
        )


# MAIN
app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())