import sys
import os
import openai
import pytesseract
from PIL import Image
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QCursor
from PyQt5.QtCore import Qt, QRect
from userInfo import api_key
from database import add_to_database


class ScreenshotWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.begin = None  # Seçim başlangıç noktası
        self.end = None    # Seçim bitiş noktası

        self.setWindowOpacity(0.3)  # Arayüzün saydamlığını ayarla
        self.setWindowState(Qt.WindowFullScreen)  # Tam ekran modunda başlat

        self.screenshot_count = 0  # Screenshot sayacı

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 128))  # Ekranı hafifçe karart

        if self.begin is not None and self.end is not None:
            selection = QRect(self.begin, self.end).normalized()
            painter.fillRect(selection, QColor(255, 255, 255, 128))  # Seçilen alanı hafifçe vurgula

    def mousePressEvent(self, event):
        self.setCursor(Qt.CrossCursor)  # Seçim işlemi sırasında çapraz imleç göster
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.ArrowCursor)  # Seçim işlemi bittiğinde normal imleç göster
        # Seçilen alanın koordinatlarını al
        selected_area = QRect(self.begin, self.end).normalized()

        # Seçilen alanı temizle
        self.begin = None
        self.end = None
        self.update()

        # Ekranı tamamen karart
        self.setWindowOpacity(0.0)

        # Ekran görüntüsünü al ve seçilen alana göre kırp
        screenshot = QApplication.primaryScreen().grabWindow(QApplication.desktop().winId(), 
                                                             selected_area.x(), selected_area.y(),
                                                             selected_area.width(), selected_area.height())
        
        # Klasör kontrolü ve oluşturma
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        # Alınan görüntüyü dosyaya kaydet
        while True:
            self.screenshot_count += 1
            file_name = f"screenshots/screenshot_{self.screenshot_count}.png"
            if not os.path.exists(file_name):
                break
        screenshot.save(file_name)
        print(f"Ekran görüntüsü kaydedildi: {file_name}")

        # Metni tanıma işlemini başlat
        stt = ScreenshotToText()
        text = stt.image_to_text(file_name)
        # print(stt.get_gpt3_response(text))
        add_to_database(file_name, text, "deneme1")

        # Clipboard'e metni kopyala
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

        self.close()  # Seçim yapıldıktan sonra pencereyi kapat
    
    def show_notification(self, title, message):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec_()


class ScreenshotToText:
    def image_to_text(self, image_path):
        path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        pytesseract.pytesseract.tesseract_cmd = path_to_tesseract 
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        print(text)
        return text
    
    # def get_gpt3_response(text):
    #     # API anahtarınızı buraya girin

    #     # API anahtarını ayarla
    #     openai.api_key = api_key

    #     # GPT-3'e sormak için gönderilecek parametreler
    #     model_engine = "gpt-3.5-turbo"

    #     # GPT-3 API'sine isteği gönderme
    #     response = openai.ChatCompletion.create(
    #        model=model_engine,
    #        messages=[{"role": "user", "content": text }]
    #     )

    #     # Cevapları alma
    #     output_text = response['choices'][0]['message']['content']

    #     return output_text

    # Kullanım örneği:
    # text = "Biraz bilgi verir misiniz?"
    # responses = get_gpt3_response(text)
    # for idx, response in enumerate(responses, start=1):
    #     print(f"Cevap {idx}: {response}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ScreenshotWidget()
    widget.show()
    sys.exit(app.exec_())
