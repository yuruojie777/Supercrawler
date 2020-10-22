import cv2
import numpy as np
from matplotlib import pyplot as plt

#对目标图片做预处理，去除黑色部分增加匹配精度
def ClearBlack(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    # Now find contours in it. There will be only one object, so find bounding rectangle for it.
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt = contours[0]
    x, y, w, h = cv2.boundingRect(cnt)
    # Now crop the image, and save it into another file.
    crop = img[y:y + h, x:x + w]
    cv2.imwrite('sofwinres.png', crop)
    return crop

#定位目标图片的位置
def Locate(pic,aim):
    img = cv2.imread(pic, 0)
    img2 = img.copy()
    template = cv2.imread(aim)
    ClearBlack(template)
    template = cv2.imread('sofwinres.png', 0)
    cv2.imshow('out', template)
    w, h = template.shape[::-1]

    # All the 6 methods for comparison in a list
    # methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
    #            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    #cv2.TM_CCOEFF准确率80%
    #cv2.TM_CCOEFF_NORMED准确率90%
    #cv2.TM_CCORR为0
    #cv2.TM_CCORR_NORMED准确率90%
    #cv2.TM_SQDIFF60%
    #cv2.TM_SQDIFF_NORMED准确率80%
    methods = ['cv2.TM_SQDIFF_NORMED']

    for meth in methods:
        img = img2.copy()
        method = eval(meth)

        # Apply template Matching
        res = cv2.matchTemplate(img, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        bottom_right = (top_left[0] + w, top_left[1] + h)

        cv2.rectangle(img, top_left, bottom_right, 255, 2)

        plt.subplot(121), plt.imshow(res, cmap='gray')
        plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
        plt.subplot(122), plt.imshow(img, cmap='gray')
        plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
        plt.suptitle(meth)

        plt.show()

if __name__ == "__main__":
    for num in range(1,11):
        pic = './test_code/pic'+str(num)+'.jpg'
        aim = './test_code/aim'+str(num)+'.png'
        Locate(pic,aim)