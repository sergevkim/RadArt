#!/bin/bash

# URL of the file to download
URL_SCENES="https://www.dropbox.com/scl/fi/we6d27doac5eisq9ws44x/all_features.tar.gz?rlkey=00wcnc61lah7yh10tokjxviaj&st=m4cla2a7&dl=0"
URL_RADAR_POSITIONS="https://www.dropbox.com/scl/fi/wyhrg1sn4aq1f3e9y3o93/radar_positions.json/?rlkey=e2g4hjzki1vv2er7l9cdocjvx&st=2z2i2ve9&dl=0"

# Filename (assuming it's all_features.tar.gz)
FILENAME_SCENES="all_features.tar.gz"
FILENAME_RADAR_POSITIONS="radar_positions.json"

SCENES_FOLDER_NAME_OLD="data"
SCENES_FOLDER_NAME_NEW="scenes"

DATA_FOLDER="data"

mkdir $DATA_FOLDER
cd $DATA_FOLDER

# Download the file
echo "Downloading $FILENAME_RADAR_POSITIONS from $URL_RADAR_POSITIONS..."
wget "$URL_RADAR_POSITIONS" -O "$FILENAME_RADAR_POSITIONS"

# Check if the download was successful
if [ $? -ne 0 ]; then
  echo "Failed to download the file."
  exit 1
fi

# Download the file
echo "Downloading $FILENAME_SCENES from $URL_SCENES..."
wget "$URL_SCENES" -O "$FILENAME_SCENES"

# Check if the download was successful
if [ $? -ne 0 ]; then
  echo "Failed to download the file."
  exit 1
fi

# Unpack the .tar.gz file
echo "Unpacking $FILENAME_SCENES..."
tar -xzf "$FILENAME_SCENES"

# Check if the unpacking was successful
if [ $? -eq 0 ]; then
  echo "Unpacking completed successfully."
else
  echo "Failed to unpack the file."
  exit 1
fi

# Optionally, remove the original archive file
echo "Removing the original archive file..."
rm "$FILENAME_SCENES"

mv $SCENES_FOLDER_NAME_OLD $SCENES_FOLDER_NAME_NEW

exit 0