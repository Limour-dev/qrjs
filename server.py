import cv2
import pyzbar.pyzbar as pyzbar

camera = cv2.VideoCapture(1)  # 0 表示前置
cv2.namedWindow('zbar', cv2.WINDOW_NORMAL)
size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2, int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2)
print(size, cv2.resizeWindow('zbar', size[0], size[1]))

try:
    while True:
        ret, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('zbar', gray)
        barcodes = pyzbar.decode(gray)
        if barcodes:
            for barcode in barcodes:
                data = barcode.data.decode('utf-8')
                print(data)
        c = cv2.waitKey(500)  # ms
        if c == 27:
            break
finally:
    camera.release()
    cv2.destroyAllWindows()

