import os
import tkinter
from glob import glob
from datetime import datetime
import time
import tempfile
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.image as mpimg
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import cv2
import extcolors
from colormap import rgb2hex
import sys
import re
import struct
import argparse

### Syntax
#           python /Users/zachary.lamplugh/Documents/_Titmouse/Titmouse_Processor_V2.py /Users/zachary.lamplugh/Downloads phrase/Goes/Here
###

### Ok so here's the current problem is I only have hex codes not RGB codes, duh. Line 110ish, but it's not coming out of Analyze Image correctly. I need to see if i can get RGB codes as list

def Find_Current_Adobe_Install():
    flash_name = "Adobe Animate 2023"
    newPATH="/Applications"#/Applications/Adobe Animate 2023/Adobe Animate 2023.app/Contents/MacOS/Adobe Animate 2023
    adobePaths=[]
    versionsArray=[]        
    animateFiles = [y for x in os.walk(newPATH) for y in glob(os.path.join(x[0], "*animate*"))]
    for item in animateFiles:
        if "Adobe Animate " in item:
            adobePaths.append(item)
            versionNum=(item.split("Adobe Animate ")[1]).split("/")[0]
            if versionNum not in versionsArray:
                versionsArray.append(versionNum)
    if "2023" not in versionsArray:
        flash_name=flash_name.replace("2023","2022")
        if "2022" not in versionsArray:
            flash_name=flash_name.replace("2023","2021")
            if "2021" not in versionsArray:
                flash_name=flash_name.replace("2023","2020")
                if "2020" not in versionsArray:
                    flash_name=flash_name.replace("2023","2019")
    return flash_name

def Process_Folder(PATH,phrase="*.fla"):
    allFlash = [y for x in os.walk(PATH) for y in glob(os.path.join(x[0], phrase))]
    print(len(allFlash))
    for idx,FLA_File in enumerate(allFlash):
        basename=os.path.basename(FLA_File).split(".")[0]
        print(f"Now processing {basename}...")
        currentNum=idx+1
        outputPath=(os.path.dirname(FLA_File))+f"/Export_PNG_{basename}"
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        outputPath2=outputPath+"/_"
        jsfl = []    
        jsfl.append("var sourceFile = \"" + createURI(FLA_File) + "\";\n")
        jsfl.append("var outputFile = \"" + createURI(outputPath2) + "\";\n")
        logFilePath = tempfile.mktemp() + ".log"  
        jsfl.append("var logFile = \"" + createURI(logFilePath) + "\";\n");
        jsfl.append("var doc = fl.openDocument(sourceFile);\n");    
        jsfl.append("fl.outputPanel.clear();\n")
        jsfl.append("doc.exportPNG(outputFile, true);\n")
        jsfl.append("fl.outputPanel.save(logFile, true);\n")
        jsfl.append("fl.compilerErrors.save(logFile, true);\n")
        if currentNum==len(allFlash):
            jsfl.append("fl.quit(false);\n")
        try:
            jsflFile = open(tempfile.mktemp() + ".jsfl", "w")  
            jsflFile.writelines(jsfl)
            jsflFile.close()
        except Exception:
            print("Error creating JSFL file.")
            print("Exiting")
            sys.exit(2)
        shellCommand = "osascript -e 'tell application \""+ flash_name +"\" to open posix file \""+ jsflFile.name +"\"'"
        try:
            os.system(shellCommand)
            Log_Text_file(outputPath,basename)
        except:
            print(Exception)

def Log_Text_file(outputPath,basename):
    Hex_Code_Master_List=[]
    RGB_List_Master_List=[]
    allPNG = [y for x in os.walk(outputPath) for y in glob(os.path.join(x[0], "*.png"))]
    # for item in allPNG:
    #     print(item)
    text_file=outputPath+f"/{basename}_HEX_colors.txt"
    outfile=outputPath+f"/{basename}_palette.aco"
    print(f"output file: {outfile}")
    if not os.path.exists(text_file):
        # try:
        Path(text_file).touch()
    for IMG_File in allPNG:
        Hex_list,RGB_codes = Analyze_Image(IMG_File, 900, 12,2.5)          ##### Write te code to analyze the image for HEX codes
        for HexCode in Hex_list:
            # HexCode2=HexCode.append("untitled")
            if HexCode not in Hex_Code_Master_List:
                Hex_Code_Master_List.append(HexCode)
        for RGB in RGB_codes:
            if RGB not in RGB_List_Master_List:
                RGB_List_Master_List.append(RGB)
    # print("hexCodeMasterList = ")
    # print(Hex_Code_Master_List)
    # Hex_Code_Master_List_2=[] 
    # for item in Hex_Code_Master_List:
    #     item.append("untitled")
    #     print(item)
    #     time.sleep(5)
    # RGBCode_To_ACO=[basename,6,RGB_List_Master_List]
    # print(RGBCode_To_ACO)
    try:
        with open(text_file,"r+") as Hex_Code_Log:
            Hex_Code_Log.write(basename+"\n\n")
            for HexCode in Hex_Code_Master_List:
                Hex_Code_Log.write(HexCode+"\n")
    except Exception as e: 
        print(e)
        # print(Exception)
    try:
        aco_bin = create_aco(1, False, RGB_List_Master_List)
        aco_bin += create_aco(2, False, RGB_List_Master_List)           ##### Write the code to send Hex Code Master List to ACT file
        print("Write: %s" % outfile)
        with open(outfile, 'wb') as f:
            f.write(aco_bin)
    except Exception as e: 
        print(e)
        # except:
        #     print(f"Could not log colors from {basename}...")
    allPNG = [y for x in os.walk(outputPath) for y in glob(os.path.join(x[0], "*.png"))]
    for temp_PNG in allPNG:
        os.remove(temp_PNG)
    
def Create_ACT_File(Hex_Code_Master_List):
    pass

def create_aco(vernum, nonull, colors):
    aco_ver = vernum  # 1 or 2
    col_len = len(colors)
    bindata = struct.pack(">2H", aco_ver, col_len)

    cspace = 0  # color ID 0 = RGB
    for c in colors:
        r, g, b, color_name = c

        w = int(65535 * r / 255)
        x = int(65535 * g / 255)
        y = int(65535 * b / 255)
        z = 0

        bindata += struct.pack(">5H", cspace, w, x, y, z)

        if vernum == 2:
            if nonull == False:
                name_len = len(color_name) + 1
                bindata += struct.pack(">L", name_len)
                for s in list(color_name):
                    n = ord(s)
                    bindata += struct.pack(">H", n)

                # add NULL word
                bindata += struct.pack(">H", 0)
            else:
                name_len = len(color_name)
                bindata += struct.pack(">L", name_len)
                for s in list(color_name):
                    n = ord(s)
                    bindata += struct.pack(">H", n)

    return bindata

def color_to_df(input):
    colors_pre_list = str(input).replace('([(','').split(', (')[0:-1]
    df_rgb = [i.split('), ')[0] + ')' for i in colors_pre_list]
    df_percent = [i.split('), ')[1].replace(')','') for i in colors_pre_list]
    
    #convert RGB to HEX code
    df_color_up = [rgb2hex(int(i.split(", ")[0].replace("(","")),
                          int(i.split(", ")[1]),
                          int(i.split(", ")[2].replace(")",""))) for i in df_rgb]
    
    df = pd.DataFrame(zip(df_color_up, df_percent), columns = ['c_code','occurence'])
    return df

def Analyze_Image(input_image, resize, tolerance, zoom):
    # pass
    # background
    bg = 'bg.png'
    fig, ax = plt.subplots(figsize=(192,108),dpi=10)
    fig.set_facecolor('white')
    plt.savefig(bg)
    plt.close(fig)
    
    #resize
    output_width = resize
    img = Image.open(input_image)
    resize_name = os.path.dirname(input_image)+'/resize_'+ os.path.basename(input_image)
    if not os.path.exists(resize_name):
        if img.size[0] >= resize:
            wpercent = (output_width/float(img.size[0]))
            hsize = int((float(img.size[1])*float(wpercent)))
            img = img.resize((output_width,hsize), Image.ANTIALIAS)
            img.save(resize_name)
        else:
            resize_name = input_image
        
    
    #crate dataframe
    img_url = resize_name
    colors_x = extcolors.extract_from_path(img_url, tolerance = tolerance, limit = 13)
    # print(colors_x)
    colors_x_2=[]
    for item in colors_x[0]:
        r=(item[0])[0]
        g=(item[0])[1]
        b=(item[0])[2]
        item2=[r,g,b,"untitled"]
        colors_x_2.append(item2)
    df_color = color_to_df(colors_x)    #This is where it switches from RGB to HEX
    
    #annotate text
    list_color = list(df_color['c_code'])
    list_precent = [int(i) for i in list(df_color['occurence'])]
    text_c = [c + ' ' + str(round(p*100/sum(list_precent),1)) +'%' for c, p in zip(list_color, list_precent)]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(160,120), dpi = 10)
    
    #donut plot
    wedges, text = ax1.pie(list_precent,
                           labels= text_c,
                           labeldistance= 1.05,
                           colors = list_color,
                           textprops={'fontsize': 150, 'color':'black'})
    plt.setp(wedges, width=0.3)

    #add image in the center of donut plot
    img = mpimg.imread(resize_name)
    imagebox = OffsetImage(img, zoom=zoom)
    ab = AnnotationBbox(imagebox, (0, 0))
    ax1.add_artist(ab)
    
    #color palette
    x_posi, y_posi, y_posi2 = 160, -170, -170
    for c in list_color:
        if list_color.index(c) <= 5:
            y_posi += 180
            rect = patches.Rectangle((x_posi, y_posi), 360, 160, facecolor = c)
            ax2.add_patch(rect)
            ax2.text(x = x_posi+400, y = y_posi+100, s = c, fontdict={'fontsize': 190})
        else:
            y_posi2 += 180
            rect = patches.Rectangle((x_posi + 1000, y_posi2), 360, 160, facecolor = c)
            ax2.add_artist(rect)
            ax2.text(x = x_posi+1400, y = y_posi2+100, s = c, fontdict={'fontsize': 190})

    fig.set_facecolor('white')
    ax2.axis('off')
    bg = plt.imread('bg.png')
    plt.imshow(bg)       
    plt.tight_layout()
    return  list_color,colors_x_2
    # return plt.show()

def createURI(path):
    return "file:///" + path 

flash_name=Find_Current_Adobe_Install()
print(flash_name)

print(len(sys.argv))
if len(sys.argv)<1:
    sys.exit("Please enter folder to search...")
elif len(sys.argv)==2:
    FolderToSearch=sys.argv[1]
    print(f"Search folder {FolderToSearch} with no defined phrase...")
    Process_Folder(FolderToSearch)
elif len(sys.argv)==3:
    FolderToSearch=sys.argv[1]
    Phrase=sys.argv[2]
    InputVar=f"*{Phrase}*.fla"
    print(f"Search folder {FolderToSearch} for the phrase {Phrase}...")
    Process_Folder(FolderToSearch,InputVar)



[[255, 255, 255, 'untitled'], [247, 191, 157, 'untitled'], [223, 146, 192, 'untitled'], [181, 87, 161, 'untitled'], [141, 66, 147, 'untitled'], [219, 28, 74, 'untitled'], [97, 44, 132, 'untitled'], [238, 147, 126, 'untitled'], [233, 103, 108, 'untitled'], [253, 189, 66, 'untitled'], [247, 227, 239, 'untitled'], [231, 174, 208, 'untitled'], [194, 118, 178, 'untitled']]
[[255, 170, 170, 'Untitled'], [255, 86, 86, 'Untitled'], [255, 0, 0, 'Untitled'], [191, 0, 0, 'Untitled'], [127, 0, 0, 'Untitled'], [255, 255, 255, 'Untitled'], [255, 212, 170, 'Untitled'], [255, 170, 86, 'Untitled'], [255, 127, 0, 'Untitled'], [191, 95, 0, 'Untitled'], [127, 63, 0, 'Untitled'], [229, 229, 229, 'Untitled'], [255, 255, 170, 'Untitled'], [255, 255, 86, 'Untitled'], [255, 255, 0, 'Untitled'], [191, 191, 0, 'Untitled'], [127, 127, 0, 'Untitled'], [204, 204, 204, 'Untitled'], [212, 255, 170, 'Untitled'], [170, 255, 86, 'Untitled'], [127, 255, 0, 'Untitled'], [95, 191, 0, 'Untitled'], [63, 127, 0, 'Untitled'], [178, 178, 178, 'Untitled'], [170, 255, 170, 'Untitled'], [86, 255, 86, 'Untitled'], [0, 255, 0, 'Untitled'], [0, 191, 0, 'Untitled'], [0, 127, 0, 'Untitled'], [153, 153, 153, 'Untitled'], [170, 255, 212, 'Untitled'], [86, 255, 170, 'Untitled'], [0, 255, 127, 'Untitled'], [0, 191, 95, 'Untitled'], [0, 127, 63, 'Untitled'], [127, 127, 127, 'Untitled'], [170, 255, 255, 'Untitled'], [86, 255, 255, 'Untitled'], [0, 255, 255, 'Untitled'], [0, 191, 191, 'Untitled'], [0, 127, 127, 'Untitled'], [102, 102, 102, 'Untitled'], [170, 212, 255, 'Untitled'], [86, 170, 255, 'Untitled'], [0, 127, 255, 'Untitled'], [0, 95, 191, 'Untitled'], [0, 63, 127, 'Untitled'], [76, 76, 76, 'Untitled'], [170, 170, 255, 'Untitled'], [86, 86, 255, 'Untitled'], [0, 0, 255, 'Untitled'], [0, 0, 191, 'Untitled'], [0, 0, 127, 'Untitled'], [51, 51, 51, 'Untitled'], [212, 170, 255, 'Untitled'], [170, 86, 255, 'Untitled'], [127, 0, 255, 'Untitled'], [95, 0, 191, 'Untitled'], [63, 0, 127, 'Untitled'], [25, 25, 25, 'Untitled'], [255, 170, 255, 'Untitled'], [255, 86, 255, 'Untitled'], [255, 0, 255, 'Untitled'], [191, 0, 191, 'Untitled'], [127, 0, 127, 'Untitled'], [0, 0, 0, 'Untitled'], [255, 170, 212, 'Untitled'], [255, 86, 170, 'Untitled'], [255, 0, 127, 'Untitled'], [191, 0, 95, 'Untitled'], [127, 0, 63, 'Untitled'], [255, 255, 255, 'Transparent'], [255, 86, 86, 'Untitled'], [127, 255, 0, 'Untitled'], [0, 127, 255, 'Untitled'], [255, 255, 86, 'Untitled'], [125, 127, 127, 'Untitled']]


# Analyze_Image('/Users/zachary.lamplugh/Downloads/lipSyncTut/Export_PNG_lipSyncTutorialDownload/_img0001.png',900,12,2.5)

###### Below is a bunch of code I found for converting a .gpl file into a .aco file

## .gpl files are very dopey and look like this:
# GIMP Palette
# Name: Android ICS
# Columns: 5
# https://developer.android.com/design/style/color.html
#  51 181 229	33B5E5
# 170 102 204	AA66CC
# 153 204   0	99CC00
# 255 187  51	FFBB33
# 255  68  68	FF4444
#   0 153 204	0099CC
# 153  51 204	9933CC
# 102 153   0	669900
# 255 136   0	FF8800
# 204   0   0	CC0000

# gpl2aco.py
# Original script by mieki256
# https://gist.github.com/mieki256/b230c5dc678ed3363f15b7ed7a38c935 #### THIS IS THE ORIGINAL SOURCE AND YES THERE IS A REVISION

#!python
# -*- mode: python; Encoding: utf-8; coding: utf-8 -*-
# Last updated: <2021/07/08 04:18:55 +0900>
# """
# Convert GIMP palette (.gpl) to Photoshop color swatch (.aco).
# usage: python gpl2aco.py GPL_FILE ACO_FILE
# Windows10 x64 20H2 + Python 3.9.5 64bit
# """


# def load_and_parse_gpl(lines):
#     name = ""
#     columns = 0
#     colors = []

#     pat1 = re.compile(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s+(.+)$')
#     pat2 = re.compile(r'^\s*(\d+)\s+(\d+)\s+(\d+)\s*$')

#     # with open(filepath) as f:
#     #     lines = f.read()

#     linenum = 0
#     for l in lines.split("\n"):
#         linenum += 1
#         if linenum == 1:
#             if l.find("GIMP Palette") == 0:
#                 print("Found [GIMP Plaette]")
#                 continue
#             else:
#                 return None, None, None
#                 #print("Error: This file is not a GIMP palette.")
#                 #sys.exit()

#         if len(l) == 0 or l[0] == '#':
#             continue

#         if l.find("Name:") == 0:
#             name = l[5:].strip()
#             print("Found Name: [%s]" % name)
#         elif l.find("Columns:") == 0:
#             columns = int(l[8:].strip())
#             print("Found Columns: [%d]" % columns)
#         else:
#             # r g b colorname
#             r = pat1.match(l)
#             if r:
#                 r, g, b, cname = r.groups()
#                 colors.append([int(r), int(g), int(b), cname])
#             else:
#                 r = pat2.match(l)
#                 if r:
#                     r, g, b = r.groups()
#                     colors.append([int(r), int(g), int(b), ""])
#                 else:
#                     print("Error: Syntax [%s] in line %d" % (l, linenum))
#                     sys.exit()

#     return name, columns, colors


# def create_aco(vernum, nonull, colors):
#     aco_ver = vernum  # 1 or 2
#     col_len = len(colors)
#     bindata = struct.pack(">2H", aco_ver, col_len)

#     cspace = 0  # color ID 0 = RGB
#     for c in colors:
#         r, g, b, color_name = c

#         w = int(65535 * r / 255)
#         x = int(65535 * g / 255)
#         y = int(65535 * b / 255)
#         z = 0

#         bindata += struct.pack(">5H", cspace, w, x, y, z)

#         if vernum == 2:
#             if nonull == False:
#                 name_len = len(color_name) + 1
#                 bindata += struct.pack(">L", name_len)
#                 for s in list(color_name):
#                     n = ord(s)
#                     bindata += struct.pack(">H", n)

#                 # add NULL word
#                 bindata += struct.pack(">H", 0)
#             else:
#                 name_len = len(color_name)
#                 bindata += struct.pack(">L", name_len)
#                 for s in list(color_name):
#                     n = ord(s)
#                     bindata += struct.pack(">H", n)

#     return bindata


# def main():
#     # parse argv
#     desc = "Convert GIMP palette (.gpl) to Photoshop color swatch (.aco)"
#     p = argparse.ArgumentParser(description=desc)
#     p.add_argument("gpl_file", help="Input GIMP palette file (.gpl)")
#     p.add_argument("aco_file", help="Output Photoshop swatch file (.aco)")
#     p.add_argument("--nonull", help="Exclude null from color name",
#                    action='store_true', default=False)
#     args = p.parse_args()

#     infile = args.gpl_file
#     outfile = args.aco_file
#     print("input file: %s" % infile)
#     print("output file: %s" % outfile)
#     nonull = args.nonull

#     # load and parse gpl file
#     name, columns, colors = load_and_parse_gpl(infile)

#     # for c in colors:
#     #     print(c)

#     print("Found Color length: %d" % len(colors))

#     # create aco binary ver1 and ver2
#     aco_bin = create_aco(1, nonull, colors)
#     aco_bin += create_aco(2, nonull, colors)

#     # write aco file
#     print("Write: %s" % outfile)
#     with open(outfile, 'wb') as f:
#         f.write(aco_bin)


# if __name__ == '__main__':
#     main()


