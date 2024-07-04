from PySide6.QtCore import QObject, QPoint, qDebug, Qt, QEvent
from PySide6.QtGui import QPainter, QCursor, QPixmap, QImage
from PySide6.QtQuick import QQuickItem, QQuickPaintedItem
import pathlib

class MousePointer(QQuickPaintedItem):    

    image = QImage()
    
    def __init__(self, parent:QQuickItem = None):        
        QQuickPaintedItem.__init__(self, parent)
        self.setImplicitWidth(32)
        self.setImplicitHeight(41)
        self.setZ(9999999)
        self.image = QImage("{}/images/cursor.png".format(pathlib.Path(__file__).parent.resolve())).scaled(self.width(), self.height(), Qt.KeepAspectRatio)        

    def paint(self, painter: QPainter):     
        painter.setRenderHint(QPainter.Antialiasing)        
        painter.drawImage(0, 0, self.image)

    ###
    # Slots
    #
    def on_nouvelle_position(self, position: QPoint):
        self.setX(position.x())
        self.setY(position.y())
