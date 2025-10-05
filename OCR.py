import tesserocr
from customtkinter import filedialog

def main():
    # Best PSM modes from right to left: 12 7 6 11 10
    with tesserocr.PyTessBaseAPI("_internal\\Tesseract-OCR 5.5.0\\tessdata",
                                 lang='eng', psm = 10) as TessOCR:
        
        image_addr_v = filedialog.askopenfilename(title ='Image browser')
        TessOCR.SetImageFile(image_addr_v)

        return TessOCR.GetUTF8Text()

if __name__ == "__main__":
    print(main())
