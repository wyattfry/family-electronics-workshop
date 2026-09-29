"""Save ArUco marker id 0 (DICT_4X4_50) as marker0.png, for printing (runs anywhere with OpenCV)."""
import cv2

d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
draw = getattr(cv2.aruco, "generateImageMarker", None) or cv2.aruco.drawMarker
img = draw(d, 0, 400)
img = cv2.copyMakeBorder(img, 40, 40, 40, 40, cv2.BORDER_CONSTANT, value=255)  # white quiet zone
cv2.imwrite("marker0.png", img)
print("wrote marker0.png: print it ~5 cm wide")
