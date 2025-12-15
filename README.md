# BigTankController

## Installation (Windows)
1. create an anaconda environment (BigTankController) and install required libraries:
   - conda install pyyaml requests urllib3 opencv
   - pip install pause
2. Download rclone, unzip, and place the executable somewhere safe (I used C:\Program Files\Rclone\rclone.exe). 
Add the path the enclosing directory to your Path environment variable so that you can run
"rclone" commands without actually being in the directory.
3. Clone this repo

## Usage Instructions:

1. Connect all ethernet cables and the hub power source. Wait for the connection to stabilize 
2. Launch the e3vision watchtower (double click on the watchtower executable. It should open a terminal window, then a webpage connected to a localhost address). If asked whether to you want to start watchtower with remote web access, respond no. 
3. Perform initial gui-based setup in the watchtower web interface
    - Scan for cameras and bind all cameras in the array
    - Set the sync camera to the camera plugged into port 2 of the hub
    - Set the codec, video settings, and overlay for all cameras
    - Connect all cameras. Sometimes it helps to connect the sync camera first, then the remaining cameras
    - Wait for connection and sync to stabilize
4. start data collection
   - open the anaconda powershell prompt and activate the BigTankController conda environment
   - navigate into the directory containing this README and the main.py script
   - run the command "python main.py project_name", replacing "project_name" with a unique project name
   - You should see indicators that data collection is running in both the e3v-watchtower console and the console where you ran main.py
   - IMPORTANT: lock the computer by pressing WindowsKey+L. This will lock your account without logging you out, which allows the script to keep running in the background
5. Stop Data Collection
   - if the e3v-watchtower web interface has disconnected, simply reload the page
   - Select all cameras and press the "stop recording" button. Wait for recordings to stop
   - Standby all cameras
   - In the powershell window where main.py is running, press ctrl+c to interrupt the script
   - Manually upload the last videos to dropbox, then delete the local copy of the project to free up space

## Notes
1. in the e3v-watchtower console, you may see frequent messages regarding the cache being unusually full, and inquiring about whether your device is fast enough to support all cameras. Despite these messages, the system seems to perform as expected without any dropped frames.
2. log files will automatically generate in the logs directory
3. while recording, the web interface will likely mis-report the save path. This is fine. The actual output can be found in BigTankController/projects/project_name