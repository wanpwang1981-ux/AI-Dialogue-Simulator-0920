#!/bin/bash
# A script to update and compile language files.

echo "Extracting new strings from source code..."
# Extract new strings from the source code into the template file
pybabel extract -F babel.cfg -o src/locales/messages.pot src/

echo "Updating language files with new strings..."
# Update the individual language .po files with the new strings
pybabel update -i src/locales/messages.pot -d src/locales

echo "Compiling language files..."
# Compile the .po files into .mo files for the application to use
pybabel compile -d src/locales

echo "Translation files updated and compiled successfully."
