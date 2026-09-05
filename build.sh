#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# ultralytics pulls in opencv-python, the GUI build, which needs libGL that a
# Render container does not have. Installing headless last makes it own cv2.
pip uninstall -y opencv-python opencv-contrib-python || true
pip install --force-reinstall --no-deps opencv-python-headless

python manage.py collectstatic --no-input