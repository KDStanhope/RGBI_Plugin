from PIL import Image, ImageOps
import cv2
import os, sys

class RGBI_model:
    """
    Quick and dirty object class for creating rgbi tiffs from 
    input 24bit orthorectified RGB tiff and 24bit orthorectified IR tiffs
    They can be different sizes too! 
    The program will clip and mask to the smaller area then merge into RGBI
    """
    ir_tfw = None
    rgb_tfw = None

    def __init__(self, rgb_image_fp, ir_image_fp):
        self.ir_image_fp = ir_image_fp
        self.rgb_image_fp = rgb_image_fp
        self.rgb_image = Image.open(rgb_image_fp)
        self.ir_image = Image.open(ir_image_fp)
        self.extract_tfw_coords()
        self.rgbi_image_create()
        pass

    def extract_tfw_coords(self):
        ir_tfw = self.ir_image.filename.replace("tif", "tfw")
        rgb_tfw = self.rgb_image.filename.replace("tif", "tfw")
        with open(rgb_tfw) as f:
            data = f.read().splitlines()
        self.rgb_tfw = (data[0],data[1],data[2],data[3],data[4],data[5])
        with open(ir_tfw) as f:
            data = f.read().splitlines()
        self.ir_tfw = (data[0],data[1],data[2],data[3],data[4],data[5])
        if self.ir_tfw[0] == self.rgb_tfw[0]:
            return True

    def generate_rgbi_model_tfw(self):
        ir_pxn = self.ir_image.width*self.ir_image.height
        rgb_pxn = self.rgb_image.width*self.rgb_image.height
        if ir_pxn > rgb_pxn:
            tfw_fp = self.rgb_image.filename.replace("tif", "tfw")
            tfw_fp = tfw_fp.replace("RGB", "RGBI")
            print(tfw_fp)
            tfw = open(tfw_fp,'w')
            for i in self.rgb_tfw:
                tfw.write(i+"\n")
            tfw.close()
        else:
            tfw_fp = self.ir_image.filename.replace("tif", "tfw")
            tfw_fp = tfw_fp.replace("IR", "RGBI")
            tfw = open(tfw_fp,'x')
            for i in self.rgb_tfw:
                tfw.write(i+"\n")
            tfw.close()
    
    def rgbi_image_create(self):
        # NEED TO IMPLEMENT A SECOND MASK TO ENSURE NO LONELY PIXELS!!! 
        # Require the D850 data though. 
        ir_pxn = self.ir_image.width*self.ir_image.height
        rgb_pxn = self.rgb_image.width*self.rgb_image.height
        self.generate_rgbi_model_tfw()
        if ir_pxn > rgb_pxn:
            print("IR_LARGER")
            fp = self.ir_image.filename.replace("IR", "RGBI")
            self.rgbi_size = (self.rgb_image.width,self.rgb_image.height)
            self.rgbi_image = Image.new("RGB",self.rgbi_size,"white")
            mask = cv2.imread(self.rgb_image.filename)
            low_range = (0,0,0)
            high_range = (254,254,254)
            mask = cv2.inRange(mask, low_range, high_range)
            mask = Image.fromarray(mask)
            mask = mask.convert("1")
            # a bit messy maybe but OpenCV is super quick
            x_0 = abs(float(self.ir_tfw[4])-float(self.rgb_tfw[4]))/float(self.ir_tfw[0])
            y_0 = abs(float(self.ir_tfw[5])-float(self.rgb_tfw[5]))/float(self.ir_tfw[0])
            x_1 = self.rgb_image.width
            y_1 = self.rgb_image.height
            bbox = (x_0, y_0, (x_1+x_0), (y_1+y_0)) #sneaky sneaky
            print(bbox)
            self.ir_image = self.ir_image.crop(bbox)
            self.ir_image = Image.composite(self.ir_image,self.rgbi_image,mask)
            #convert properly to grayscale
            gray_image = ImageOps.grayscale(self.ir_image)
            self.ir_image = gray_image.convert("L")
            self.rgb_image = self.rgb_image.split()
            self.rgbi_image = Image.merge("RGBX",(self.rgb_image[0],self.rgb_image[1],self.rgb_image[2],self.ir_image))
            self.rgbi_image.save(fp)
            mask.close()
            return True
        else:
            print("RGB_LARGER")
            fp = self.ir_image.filename.replace("IR", "RGBI")
            self.rgbi_size = (self.rgb_image.width,self.rgb_image.height)
            self.rgbi_image = Image.new("RGB",self.rgbi_size,"white")
            mask = cv2.imread(self.ir_image.filename)
            low_range = (0,0,0)
            high_range = (254,254,254)
            mask = cv2.inRange(mask, low_range, high_range)
            mask = Image.fromarray(mask)
            mask = mask.convert("1")
            # a bit messy maybe but OpenCV is super quick
            x_0 = abs(float(self.rgb_tfw[1][0]) - float(self.ir_tfw[1][0]))/float(self.rgb_tfw[0])
            y_0 = abs(float(self.rgb_tfw[1][1]) - float(self.ir_tfw[1][1]))/float(self.rgb_tfw[0])
            x_1 = self.ir_image.width
            y_1 = self.ir_image.height
            bbox = (x_0, y_0, (x_1+x_0), (y_1+y_0)) #sneaky sneaky
            self.rgb_image = self.rgb_image.crop(bbox)
            self.rgb_image = Image.composite(self.rgb_image,self.rgbi_image,mask)
            #convert properly to grayscale
            gray_image = ImageOps.grayscale(self.ir_image)
            self.ir_image = gray_image.convert("L")
            self.rgb_image = self.rgb_image.split()
            self.rgbi_image = Image.merge("RGBX",self.rgb_image[0],self.rgb_image[1],self.rgb_image[2],self.ir_image)
            self.rgbi_image.save(fp)
            mask.close()
            return True


    def clean(self):
        for i in self.rgb_image:
            i = i.close()
        self.ir_image = self.ir_image.close()
        self.rgbi_image = self.rgbi_image.close()
        os.remove(self.rgb_image_fp)
        os.remove(self.ir_image_fp)
        #and the tfws
        os.remove(self.rgb_image_fp.replace('.tif','.tfw'))
        os.remove(self.ir_image_fp.replace('.tif','.tfw'))



