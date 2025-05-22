# BigTankController

## Installation (Windows)
1. create an anaconda environment install required libraries:
   - conda install pyyaml requests urllib3
   - pip install pause
2. Download rclone, unzip, and place the executable somewhere safe (I used C:\Program Files\Rclone\rclone.exe). 
Add the path the enclosing directory to your Path environment variable so that you can run
"rclone" commands without actually being in the directory.


## Usage Instructions:

1. Connect all ethernet cables and the hub power source. Wait for the connection to stabilize 
2. Launch the e3vision watchtower
3. Perform initial gui-based setup in the watchtower gui.
    - Scan for cameras and bind all cameras in the array
    - Set the sync camera to the camera plugged into port 2 of the hub
    - Set the codec, video settings, and overlay for all cameras
    - Connect all cameras
    - Wait for connection and sync to stabilize
4. start data collection
   - open the anaconda powershell prompt and activate the  