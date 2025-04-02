# PyKeyer

A CW contest keyer and logger in written Python.

![Screen Shot]( Docs/pykeyer.png)

Also can be used as a sending and receiving CW trainer.

![Screen Shot]( Docs/paddling.png)

# Background

Over the years, a number of very good logging programs have been developed.  The most popular of these today is the N1MM logger.  Unfortunately, this is a Windoz-only application and is very difficult to get working under linux.  My experience with the other options available for linux are either not being actively maintained and/or are too bloated and/or lacking to be useful for contesting.  Hence, the development of yet another keying/logging program.

# Features

- Macros and data entry are focused on contest exchanges.
- Basic support for dx, ragchew and satellite contact is also provided.
- Large text used for data entry fields
- Rig can be interface via direct, flrig or hamlib connections
- Rig keying (via DTR) generated either internally or by NanoIO keyer (much more precise)
- Logging uses standard ADIF format
- Optional sidetone generation
- Practice mode for each supported contest 
- Variety of text generation facilities for practicing with keyer paddles.
- ...

# Installation under Linux - Depricated:

0) THIS IS *NOT* THE RECOMMENED PROCEDURE ANYMORE.  As of Linux Mint 22, the system python libraries are heavily guarded.  If you see a message stating that "This environment is externally managed," you will need to use some sort of "virtual" or "container" for your python environment.  I have found that Miniconda is a straight-forward way to do this.  See the next section for the installation instructions under Miniconda.

1) Uses python3 and tkinter
2) Clone gitub pyKeyer, libs and data repositories

      cd
      mkdir Python
      cd Python
      git clone https://github.com/aa2il/pyKeyer
      git clone https://github.com/aa2il/libs
      git clone https://github.com/aa2il/data
      
3) Install packages needed for pyKeyer:

     cd ~/Python/pyKeyer
     pip3 install -r requirements.txt
     
4) Make sure its executable:

     chmod +x pyKeyer.py start start_cw
     
5) Set PYTHON PATH so os can find libraries:

   - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
   - Under bash:      export PYTHONPATH="$HOME/Python/libs"
   
6) Bombs away:

     ./pyKeyer.py
     
   See also start and start_cw for examples how to run this thing         

# Installation under Mini-conda (Linux):

0) There are several ways to achieve a "virtual environment" for python.  Although such "containerized" approaches require a little bit of work up-front, there are several advantages:

   - Protects the system python libraries (required by many recent distro releases)
   - Allows for establishment of different environments with, say, different versions of python
   - App will continue to function as python evolves and functions are depricated or syntx changes.

Here is a good video overview of Miniconda:

     https://www.youtube.com/watch?v=23aQdrS58e0&t=552s

1) Point a browser to
      
   https://docs.conda.io/en/latest/miniconda.html
   
2) Download and install latest & greatest Mini-conda for your particular OS:
   - I used the bash installer for linux
   - As of July 2023: Conda 23.5.2 Python 3.11.3 released July 13, 2023
   - cd ~/Downloads
   - bash Miniconda3-latest-Linux-x86_64.sh
   - Follow the prompts

   - If you'd prefer that conda's base environment not be activated on startup, 
      set the auto_activate_base parameter to false: 

      conda config --set auto_activate_base false

   - To get it to work under tcsh:
       - bash
       - conda init tcsh
       - This creates ~/.tcshrc - move its contents to .cshrc if need be
       - relaunch tcsh and all should be fine!
       - Test with:
       
          conda list

   - To blow away a work environment and start over:
          
         conda deactivate
         conda remove -n work --all
           
3) Create a working enviroment for ham radio stuff:
   - Check which python version we have:
   - conda list

   - !!! By default, conda does not include very many fonts for tk and therefore the
           Tk GUIs look like crap.  Do this when creating the sandbox to avoid this problem:

      bash
      cd ~/miniconda3/envs/
      conda create -y --prefix "aa2il" -c conda-forge "python==3.12.*" "tk[build=xft_*]"
      exit

    - The fonts on an existing sandbox can be upgraded via:

       bash
       conda install --prefix "aa2il" -c conda-forge "tk=*=xft_* "
       exit

   - To activate this environment, use:
       - conda activate aa2il
   - To deactivate an active environment, use:
       - conda deactivate

   - conda env list
   - conda activate aa2il

4) Clone gitub pyKeyer, libs and data repositories:

      cd
      mkdir Python
      cd Python
      git clone https://github.com/aa2il/pyKeyer
      git clone https://github.com/aa2il/libs
      git clone https://github.com/aa2il/data

5) Install packages needed by pyKeyer:

     cd ~/Python/pyKeyer
     pip3 install -r requirements.txt

6) Set PYTHON PATH so os can find libraries:

   - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
   - Under bash:      export PYTHONPATH="$HOME/Python/libs"

7) To run pyKeyer, we need to specify python interpreter so it doesn't run in
   the default system environment:
   
     cd ~/Python/pyKeyer
     conda activate aa2il
     python pyKeyer.py

8) If the fonts look awful, see step 3 above
   
9) Known issues using this (as of March 2025):
   - None

# Installation for Windoz:

0) One option is to use miniconda and follow the directions above.
      
1) I had success installing Python (v3.12 as of Oct 2024) via the Microslop Store
   (or directly from python.org).

2) Clone gitub repositories.  There are several tools available for windows
   for fetching git repositories.  I use the command line version from
   
       https://git-scm.com/downloads/win
       
   Find one you like, open a command prompt and effect the following:
   
        cd %userprofile%
        mkdir Python
        cd Python
        git clone https://github.com/aa2il/pyKeyer
        git clone https://github.com/aa2il/libs
        git clone https://github.com/aa2il/data

   Note - to simply grab the latest changes, use "pull" instead of "clone"
   in these commands.

3) Install dependancies:

        cd pyKeyer
        pip install -r requirements.txt

4a) There are three codes here - the complete keyer, e.g.:
           
        pyKeyer.py -prac -cwt -adjust -wpm 30 -keyer WINKEY

4b) ... a paddle sending practice tool:
            
        paddling.py

4c) ... and a callsign lookup tool:

        qrz.py

5) Under linux, these programs can discover the type of keying device available.
   This doesn't yet work under winblows so only the most popular device,
   Winkeyer, is available.
                               
6) There is an older compiled binary/installer listed on the right panel
   of this screen.  If you want/need a more recent binary, follow the steps
   in windoz.bat to build it from the source.  

7) A note about drivers.  Compared to linux where almost everything works right out of the box, Windoz is awful when dealing with device drivers.  To get the keyer to work, you will probably have to install device drivers for both the keying deivce (e.g. winkeyer via a serial COM port) AND for your rig (e.g. CAT control and rx audio via a pair of USB ports).
                                                                                Most likely, the rig manufacturer has the proper drivers for the rig available on their website.  This may or may not be the case for your keying device.  I do not own a genuine Winkeyer as I "roled my own."

To add further complictions, the Winblows device drivers are often buggy and unstable.  My main keying device is a modified version of the K3NG keyer hosted on an Arduino Nano knock-off.  This device emulates the popular Winkeyer.  The Nano-knockoff uses a CH340 chip for USB I/O and not the venerable FTDI chipset.  The latest driver (v3.8 as of Oct 2024) for the CH340 initially works but then hangs upon program exit.  To get the keyer to work properly, I found I needed to use an older version of the driver (v3.7 from 2022).  A zip file with this driver is included in this repository.

I've also built version of the K3NG keyer which is hosted on an ESP32 board.  This particular board uses a CP2102 USB to UART bridge.  The driver for this one is

https://www.silabs.com/developer-tools/usb-to-uart-bridge-vcp-drivers

One other reminder - MAKE SURE USB CABLE IS A "FULL SERVICE" CABLE, NOT JUST "POWER-ONLY" charging cable.  (I admit that, on mulitple occasions, I have wasted considerable time tracking this down - ugh!)
