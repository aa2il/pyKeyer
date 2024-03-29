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

# Installation under Linux:

1) Uses python3 and tkinter
2) Clone gitub pyKeyer, libs and data repositories
    - cd
    - mkdir Python
    - cd Python
    - git clone https://github.com/aa2il/pyKeyer
    - git clone https://github.com/aa2il/libs
    - git clone https://github.com/aa2il/data
3) Install packages needed for pyKeyer:
   - cd ~/Python/pyKeyer
   - pip3 install -r requirements.txt
4) Make sure its executable:
   - chmod +x pyKeyer.py start start_cw
5) Set PYTHON PATH so os can find libraries:
   - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
   - Under bash:      export PYTHONPATH="$HOME/Python/libs"
6) Bombs away:
   - ./pyKeyer.py
   - See also start and start_cw for examples how to run this thing         

# Installation under Mini-conda:

0) Good video:  https://www.youtube.com/watch?v=23aQdrS58e0&t=552s

1) Point browser to https://docs.conda.io/en/latest/miniconda.html
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
           - conda list

   - To blow away a work environment and start over:
       - conda deactivate
       - conda remove -n work --all
           
3) Create a working enviroment for ham radio stuff:
   - Check which python version we have:
       - conda list   
   - conda create --name aa2il python=3.11

   - To activate this environment, use:
       - conda activate aa2il
   - To deactivate an active environment, use:
       - conda deactivate

   - conda env list
   - conda activate aa2il

4) Clone gitub pyKeyer, libs and data repositories:
    - cd
    - mkdir Python
    - cd Python
    - git clone https://github.com/aa2il/pyKeyer
    - git clone https://github.com/aa2il/libs
    - git clone https://github.com/aa2il/data

5) Install packages needed by pyKeyer:
   - cd ~/Python/pyKeyer
   - pip3 install -r requirements.txt

6) Set PYTHON PATH so os can find libraries:
   - Under tcsh:      setenv PYTHONPATH $HOME/Python/libs
   - Under bash:      export PYTHONPATH="$HOME/Python/libs"

7) To run pyKeyer, we need to specify python interpreter so it doesn't run in
   the default system environment:
   - cd ~/Python/pyKeyer
   - conda activate aa2il
   - python pyKeyer.py

8) Fonts look awful - this seems to be a long-known issue with conda.
   - The ugly fix is replace the offending library in conda:
      - cd ~/miniconda3/envs/aa2il/lib/
      - mv libtk8.6.so libtk8.6.sav
      - ln -s usr/lib/x86_64-linux-gnu/libtk8.6.so .
   - This is not a good solution but the best I've found so far
   
9) Known issues using this (as of July 2023):
   - Fonts look awful - need a better fix than step 8 above

# Installation for Windoz:

1) Best bet is to use mini-conda and follow the instructions above.
2) There is an older compiled binary/installer listed on the right panel
   of this screen.  If you want/need a more recent binary, email me
   or follow the steps in windoz.bat to build it from the source.
