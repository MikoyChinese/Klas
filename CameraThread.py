"""
Using QThread to perform the time-consuming task.
If the thread does not stop yet(e.g. staying in the its run) and you call its start(), this call will be ignored;
author = hobin;
email = '627227669@qq.com';
"""
import sys
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
import time
import cv2
import logging

class MyCameraThread1(QThread):
    """
    It returns a QImage object for QLabel displaying it;
    """
    update = pyqtSignal(object)

    def __init__(self, camera_object, parent=None):
        super(MyCameraThread1, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.capture = camera_object
        self.frame = None  # the frame of camera, it is used for the Account thread;


    def run(self):
        self.status = True  # It is for calling of start() again.
        while self.status:
            ret, self.frame = self.capture.read()
            img2 = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)  # Actually, the picture can be read in RBG format;
            height, width, channel = img2.shape  # width=640, height=480
            bytes_per_line = 3 * width
            img3 = QImage(img2.data, width, height, bytes_per_line, QImage.Format_RGB888)
            img4 = img3.mirrored(horizontal=True, vertical=False)
            self.update.emit(img4)
            time.sleep(0.1)


class MyCameraThread1_2(QThread):
    """
    It returns a QImage object for QLabel displaying it;
    Compared with the MyCameraThread1 class, the main difference is the 'try...except' statements are added when using cv2.VideoCapture.read();
    When the exception happens(assuming the self.capture.read() function fails), I just let this thread quit automatically;
    """
    update = pyqtSignal(object)

    def __init__(self, camera_object, parent=None):
        super(MyCameraThread1_2, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.capture = camera_object
        self.frame = None  # the frame of camera, it is used for the Account thread;


    def run(self):
        self.status = True  # It is for calling of start() again.
        while self.status:
            try:
                ret, self.frame = self.capture.read()
                img2 = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)  # Actually, the picture can be read in RBG format;
                height, width, channel = img2.shape  # width=640, height=480
                bytes_per_line = 3 * width
                img3 = QImage(img2.data, width, height, bytes_per_line, QImage.Format_RGB888)
                img4 = img3.mirrored(horizontal=True, vertical=False)
                self.update.emit(img4)
                time.sleep(0.1)
            except BaseException as e:
                self.status = False
                print('-----------------Error happens in MyCameraThread1_2!--------------------')
                print(e)


class MyCameraThread1_3(QThread):
    """
    Broken class, do not use it.
    It is used with MyCameraThread1_2 class to avoid the concurrent execution of cv2.VideoCapture.read();
    Currently, I am doubt that the frame data will not be refreshed;
    """
    update = pyqtSignal(object)

    def __init__(self, cam_thread, parent=None):
        super(MyCameraThread1_3, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.frame = None
        self.cam_thread = cam_thread


    def run(self):
        self.status = True
        while self.status:
            try:
                self.frame = self.cam_thread.frame  # this will not refresh the data about the frame!
                img2 = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)  # Actually, the picture can be read in RBG format;
                height, width, channel = img2.shape
                bytes_per_line = 3 * width
                img3 = QImage(img2.data, width, height, bytes_per_line, QImage.Format_RGB888)
                img4 = img3.mirrored(horizontal=True, vertical=False)
                self.update.emit(img4)
                time.sleep(0.1)
            except BaseException as e:
                self.status = False
                print(e)


class MyCameraThread2(QThread):
    """
    This class has nothing to do with the MyCameraThread1 class.
    It is used to display the image of the item camera.
    But it does not work well in linux with error: 'QPixmap: It is not safe to use pixmaps outside the GUI thread'
    """
    def __init__(self, camera_object):
        super(MyCameraThread2, self).__init__()
        self.capture = camera_object
        self.status = True

    def run(self):
        self.status = True
        while self.status:
            _, image = self.capture.read()
            cv2.imshow('Item Camera in Brindley', image)
            if cv2.waitKey(100) & 0xFF == ord('q'):  # press keyboard Q to quit
                self.status = False
                cv2.destroyAllWindows()


class MyThread2(QThread):
    """
    This is used for detecting the products;
    """
    detected = pyqtSignal()

    def __init__(self, camera_object, rate_detect=0.1, parent=None):
        super(MyThread2, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.capture = camera_object
        self.rate_detect = rate_detect


    def run(self):
        self.status = True
        try:
            while self.status:
                # print('Camera thread for product detection begins')
                ret, img1 = self.capture.read()
                img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                time.sleep(0.3)
                ret, img2 = self.capture.read()
                img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                img3 = cv2.absdiff(img1_gray, img2_gray)
                img3_1 = cv2.GaussianBlur(img3, (3, 3), 0, 0)
                thresh, img3_2 = cv2.threshold(src=img3_1, thresh=34, maxval=255, type=cv2.THRESH_BINARY)
                element1 = cv2.getStructuringElement(0, (3, 3))
                img3_3 = cv2.dilate(img3_2, kernel=element1)
                full_nums = img3_3.size
                nums_detect = img3_3.sum() / 255.0
                rate_detect = nums_detect / full_nums
                if rate_detect > self.rate_detect:
                    self.status = False
                    self.detected.emit()
                # print('Camera thread for product detection ends')
        except BaseException as e:
            self.capture.release()
            print('Error in MyThread2:', e)
            sys.exit()


class MyThread2_1(QThread):
    """
    This is used for detecting the products;
    Compared with the MyThread2 class, the logging module is introduced to this module at first time.
    """
    detected = pyqtSignal()

    def __init__(self, camera_object, rate_detect=0.1, parent=None, logger_name='hobin'):
        super(MyThread2_1, self).__init__(parent)
        self.parent = parent
        self.status = True
        self.capture = camera_object
        self.rate_detect = rate_detect
        self.mylogger2_1 = logging.getLogger(logger_name)


    def run(self):
        self.status = True
        try:
            while self.status:
                # print('Camera thread for product detection begins')
                ret, img1 = self.capture.read()
                img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
                time.sleep(0.3)
                ret, img2 = self.capture.read()
                img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
                img3 = cv2.absdiff(img1_gray, img2_gray)
                img3_1 = cv2.GaussianBlur(img3, (3, 3), 0, 0)
                thresh, img3_2 = cv2.threshold(src=img3_1, thresh=34, maxval=255, type=cv2.THRESH_BINARY)
                element1 = cv2.getStructuringElement(0, (3, 3))
                img3_3 = cv2.dilate(img3_2, kernel=element1)
                full_nums = img3_3.size
                nums_detect = img3_3.sum() / 255.0
                rate_detect = nums_detect / full_nums
                if rate_detect > self.rate_detect:
                    self.status = False
                    self.detected.emit()
                # print('Camera thread for product detection ends')
        except BaseException as e:
            self.capture.release()
            # print('Error in MyThread2_1:', e)
            self.mylogger2_1.error('Error happens in camera thread for item detection:', e)
            sys.exit()


if __name__ == '__main__':
    print(sys.getsizeof(MyCameraThread1))
