import cv2 as cv2
import numpy as np
from collections import Counter
import math
import matplotlib.pyplot as plt

#test images
# s='add.png'
s='lenna.jpg'
# s='ttt.jpg'

#pixel used for SIFT
pixelX=200
pixelY=200

#functions
def drawContours(img,contours,color):
    contours=np.array(contours)
    for i in range(contours.shape[0]):
        for j in range(contours[i].shape[0]):
            for k in range(contours[i][j].shape[0]):
                img[contours[i][j][k][1]][contours[i][j][k][0]]=color

def getContours(img,seuil=30):
    contours=[]
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h,w=np.shape(img)
    imgContours=np.zeros((h,w),np.double)
    imgContoursX=np.zeros((h,w),np.double)
    imgContoursY=np.zeros((h,w),np.double)
    for i in range(0,h):
        for j in range (0,w):
            if(j==0 or j==w-1 or i==0 or i==h-1):
                imgContoursX[i][j]=0
                imgContoursY[i][j]=0
            else:
                imgContoursX[i][j] = (np.multiply( convX,img[i-1:i+2,j-1:j+2]).sum(axis=1).sum(axis=0))
                imgContoursY[i][j] = (np.multiply( convY,img[i-1:i+2,j-1:j+2]).sum(axis=1).sum(axis=0))
            a=math.sqrt(math.pow(imgContoursX[i][j],2)+math.pow(imgContoursY[i][j],2))
            a=min(a,255)
            a=max(a,0)
            if(a>seuil):
                imgContours[i][j]=a
                contours.append([i,j])
    return imgContours,contours,imgContoursX,imgContoursY

def getOrientation(img,x,y):
    global imgContoursX,imgContoursY
    if(x<0 or x>w-1 or y<0 or y>h-1):
        d=0
    else:
        d=math.atan2(imgContoursY[y][x],imgContoursX[y][x])
    d+=math.pi
    return d

def getBlock(img,x,y):
    a=[]
    block=np.zeros((16,16),np.double)
    for i in range(x-8,x+8):
        for j in range(y-8,y+8):
            angle=roundAngle(getOrientation(img,i,j))
            block[j-y+8][i-x+8]=angle
    # block=np.zeros((4,4),np.double)
    # for i in range(x-8,x+8):
    #     for j in range(y-8,y+8):
    #         xb=(i-x+8)//4
    #         yb=(j-y+8)//4
    #         angle=roundAngle(getOrientation(img,i,j))
    #         block[yb][xb]=max(block[yb][xb],angle)
    #         a.append(angle)
    return block


def anglesArray():
    angles = []
    i=0
    while True:
        angles.append(math.pi*i)
        i+=1/4
        if(i==2):
            break
    return angles

def anglesStringsArray():
    return ["0","π/4","π/2","3π/4","π","5π/4","3π/2","7π/4"]

def roundAngle(angle):
    angles = anglesArray()
    index=np.argmin(np.abs(np.subtract(angles,angle)))
    angles = anglesArray()
    a=angles[index]
    return a

def roundAngleTitle(angle):
    anglesStrings = anglesStringsArray()
    angles = anglesArray()
    a=np.argmin(np.abs(np.subtract(angles,angle)))
    return anglesStrings[a]

def roundAngleIndex(angle):
    angles = anglesArray()
    a=np.argmin(np.abs(np.subtract(angles,angle)))
    return a

def showHist(tempdicArray):
    fig, ax = plt.subplots(4,4,figsize=(14,8))
    for i in range (0,len(tempdicArray)): 
        x=(int)(i/4)
        ax[x][i%4].bar(list(tempdicArray[i].keys()), tempdicArray[i].values(), color='b')
    fig.tight_layout()
    plt.show()


#main
img=cv2.imread(s)
h,w,d = np.shape(img)
# #find contours
# imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#convolution matrix
c=1
convX=np.zeros((3,3),np.double)
convX[0,0]=0;convX[0,1]=0;convX[0,2]=0;convX[1,0]=-c;convX[1,1]=0
convX[1,2]= c;convX[2,0]= -0;convX[2,1]=0;convX[2,2]=0

convY=np.zeros((3,3),np.double)
convY[0,0]=-0;convY[0,1]=-c;convY[0,2]=-0;convY[1,0]=0;convY[1,1]=0
convY[1,2]= 0;convY[2,0]= 0;convY[2,1]=c;convY[2,2]=0

seuil=100
img,contours,imgContoursX,imgContoursY=getContours(img,seuil)
angles=[]
# for i in range(0,np.shape(contours)[0]):
#     a=roundAngle(getOrientation(img,contours[i][1],contours[i][0]))
#     angles.append(a)

for i in range(0,np.shape(contours)[0]):
    pixelX=contours[i][1]
    pixelY=contours[i][0]
    blocks=getBlock(img,pixelX,pixelY)
    dic={}
    histogrammes=[]
    iBlock=0
    maxiAngles=[]
    minSeuil=2
    maxSeuil=5
    for block in blocks:
        #count orientations for histogramme
        array=np.matrix.flatten(block)
        count=Counter(array)
        for c in count:
            dic[roundAngleTitle(c)]=count[c]
        histogrammes.append(dic.copy())
        dic={}
        #get max seen orientaion to find interest point
        xBlock=max(pixelX-8,0)
        yBlock=max(pixelY-8,0)
        #find in most found angle in 4x4 block
        maxi=-1
        maxiAngle=-2*math.pi
        for c in count:
            if count[c]>maxi:
                maxi=count[c]
                maxiAngle=roundAngle(c)
        maxiAngles.append(maxiAngle)
        # print('nb apparitions :'+str(maxi),' , angle:'+str(roundAngleTitle(maxiAngle)))
        iBlock+=1

    countAngles=Counter(maxiAngles)
    maxiGlobal=-2*math.pi
    for c in countAngles:
        if countAngles[c]>maxi:
            maxiGlobal=countAngles[c]
    # print(maxiGlobal)
    if(maxiGlobal>minSeuil and maxiGlobal<maxSeuil):
        # img[pixelY][pixelX]=128
        cv2.rectangle(img, (pixelX, pixelY), (pixelX+10, pixelY+10), (128), 2)

# showHist(histogrammes)


# ret, thresh = cv2.threshold(imgray, 100, 255, 0)
# contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#show result
# img=np.zeros((h,w,3),np.double)
# drawContours(img,contours,255)
# cv2.drawContours(img, contours, -1, (255,255,255), 1)
cv2.imshow('image : '+s,img)
cv2.waitKey(0)