# NovaCard 离线预览：用软件渲染 offscreen 截图验证外观，不弹窗
import sys
from pathlib import Path

from PySide6.QtCore import QUrl, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

QML = Path(__file__).parent / "DemoCard.qml"

app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()
engine.warnings.connect(lambda ws: [print("QML:", w.toString()) for w in ws])
engine.load(QUrl.fromLocalFile(str(QML)))

if not engine.rootObjects():
    print("QML load failed")
    sys.exit(1)

win = engine.rootObjects()[0]


def grab():
    img = win.grabWindow()
    ok = img.save("card_preview.png")
    print("screenshot saved:", ok, img.width(), "x", img.height())
    app.quit()


QTimer.singleShot(800, grab)
sys.exit(app.exec())
