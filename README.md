# Studio ni Owen — Image Processing Project

A Python-based **Image Processing Midterm Project** developed using several image processing and computer vision libraries.

The application provides four main image processing features:

*  **Capture Image**
*  **Remove Background**
*  **Extract Text**
*  **Convert to Pixel Art**

The project uses a graphical user interface (GUI) built with **Tkinter**.



##  Features

###  Capture Image

Uses **OpenCV** to access the computer's camera and capture an image.

The captured image is saved as:

text
images/captured.jpg


###  Remove Background

Uses **rembg** and the lightweight **U²-NetP** model to automatically detect and remove the background from an image.

Output:

text
output/no_background.png


The output is saved as a PNG file to support transparency.

###  Extract Text

Uses **EasyOCR** to detect and extract English text from the captured image.

The extracted text is:

* Displayed inside the application
* Saved as a text file

Output:

text
output/extracted_text.txt


###  Convert to Pixel Art

Uses **Pillow (PIL)** to create a pixel-art effect.

The image is first reduced to **64 × 64 pixels** and then resized back to its original dimensions using nearest-neighbor resampling.

Output:

text
output/pixel_art.png




##  Technologies Used

| Technology | Purpose                        |
| ---------- | ------------------------------ |
| Python     | Main programming language      |
| Tkinter    | Graphical User Interface       |
| OpenCV     | Camera and image capture       |
| Pillow     | Image processing and pixel art |
| rembg      | Background removal             |
| EasyOCR    | Text extraction / OCR          |



##  Project Structure

text
ImageProcessingMidterm/
│
├── images/
│   └── captured.jpg
│
├── output/
│   ├── no_background.png
│   ├── extracted_text.txt
│   └── pixel_art.png
│
├── main.py
└── README.md


> The `images` and `output` folders are automatically created by the program if they do not already exist.



##  Requirements

Make sure you have:

* Python 3.11 or later
* A working webcam
* Windows, macOS, or Linux
* Internet connection for the first EasyOCR/model setup



##  Installation

### 1. Clone the repository

bash
git clone YOUR_GITHUB_REPOSITORY_URL


Then enter the project folder:

bash
cd ImageProcessingMidterm


### 2. Install the required libraries

bash
pip install opencv-python pillow rembg easyocr


If you encounter an `onnxruntime` error when using `rembg`, install the CPU version:

bash
pip install "rembg[cpu]"




##  Running the Application

Run:

bash
python main.py


The application will open with the main interface.



##  How to Use

### 1. Capture an Image

Click:

text
 Capture Image


A camera window will open.

Click **Capture** to save the image.



### 2. Remove Background

After capturing an image, click:

text
 Remove Background


The application will process the image and display the result.



### 3. Extract Text

Click:

text
 Extract Text


EasyOCR will analyze the captured image and detect text.

The extracted text will appear in the application and will also be saved to:

text
output/extracted_text.txt




### 4. Convert to Pixel Art

Click:

text
Convert to Pixel Art


The application will convert the captured image into a pixel-art style image.



### 5. Clear Output

Click:

text
Clear Output


This clears the image preview and extracted text from the GUI.

**Note:** It does not delete the files saved in the `output` folder.



##  How the Project Works

The basic workflow of the application is:

text
Capture Image
      │
      ▼
captured.jpg
      │
      ├──────────────► Remove Background
      │                       │
      │                       ▼
      │                no_background.png
      │
      ├──────────────► Extract Text
      │                       │
      │                       ▼
      │                extracted_text.txt
      │
      └──────────────► Pixel Art
                              │
                              ▼
                         pixel_art.png




##  Image Processing Techniques

### Background Removal

The project uses the **U²-NetP** model through `rembg` to separate the foreground from the background.

### Optical Character Recognition

**EasyOCR** is used to detect characters and convert text from an image into editable digital text.

### Pixel Art

The image is reduced to:

text
64 × 64 pixels


and then enlarged using:

python
Image.Resampling.NEAREST


This preserves the hard edges of the pixels and creates the pixel-art effect.



##  Project Information

**Project:** Image Processing Code Python Midterm

**Project Type:** Image Processing / Computer Vision

**Language:** Python

**Interface:** Tkinter GUI

**Author:** Mark Owen Badua



##  Notes

* A webcam is required for the image capture feature.
* EasyOCR may download its required models during the first run.
* Background removal may take some time when the AI model is loaded for the first time.
* Processing speed depends on the computer's hardware.
* The project uses CPU processing for EasyOCR.



##  License

This project was created for **educational purposes** as part of a college image processing midterm project.
