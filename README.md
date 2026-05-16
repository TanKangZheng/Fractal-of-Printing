# MoxPrinter

A Moxfield export to MakePlayingCards print converter.

## Description

This project aims to be a one-click preperator for converting a Moxfield deck into MakePlayingCards-project ready images, removing the need to manually prepare each individual card. While websites like MPCfill exist, they may not have the printing you desire. Thus, this project uses your selected version of the card in Moxfield, and creates a print-ready version.

## Getting Started

### Dependencies

These dependencies are only required if you are building the project yourself! The standalone executable has been done so that you don't need any other dependencies, installs, or setup.

* Python 3.11.4
    * Run `pip install -r requirements.txt` in the project folder

### Installing

* **Self-Building the Project**
    * Compiled and Tested on Python 3.11.4
    * External Package requirements are listed in [requirements.txt](requirements.txt)
    * Pull the repo, and simply run the main.py file
* **Standalone Executable (exe)**
    * Download the MoxPrinter zip file from Downloads
    * Extract the folder, and run MoxPrinter.exe
    * The exe is not malware, I swear.

## Usage

* **Left Column | Input and Functions**
    * Input Text Field
        * *The large input text field is where you will paste your Moxfield export*
        * *To get the Moxfield export text, simply go to your deck > More > Export > Copy for Moxfield*
    * Load Images
        * *This button will attempt to fetch all cards you've added*
        * *Once loaded, the preview images will show on the right column*
        * *This will also cache all the image links, so downloading will be faster*
        * ***IMPORTANT: For double faced cards, each face will have its image generated.***
    * Download Images
        * *This button will begin downloading card images for all cards added*
        * *Once downloaded, it will apply all features that have been enabled to the images*
        * *Once complete, it will open the file location of the images*
        * ***IMPORTANT: For double faced cards, each face will have its image generated.***
    * Optional Enhancement Features
        * ***Foil:*** *When printing using MakePlayingCard's foil finish, the images tend to be a bit washed. Enabling this feature will boost the saturation and vibrancy of the card.*
        * ***Upscale:*** *Enabling this option will upscale the card images by 2x. Not mandatory since it is almost un-noticeable when printed.*

## Version History

* 0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the [LICENSE.MD](LICENSE.MD) file for details.

## Acknowledgments

This project would have likely not been possible without the Scrython open source package, or at least, a hell of a lot more tedious. Major thanks to the developer.

**NandaScott / Scrython**
* [Scrython](https://github.com/NandaScott/Scrython)

And the slugify function used to ensure that filenames are safe and legal (for your computer to use as a filepath) was taken from another online repo as it was the first thing to pop up.

**Django**
* [Django/django/utils/text.py](https://github.com/django/django/blob/main/django/utils/text.py)
