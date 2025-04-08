# SlotMaker for Fusion 360

A Fusion 360 add-in that creates evenly spaced slots along selected lines on a face.

## Features

- Create multiple slots along any line on a face
- Customize slot dimensions (length, width, depth)
- Control the number of slots
- Works with multiple lines simultaneously
- Automatically creates proper slot profiles with rounded ends

## Installation

1. Download the latest release
2. In Fusion 360, go to `Tools > ADD-INS > Add-ins`
3. Click the `+` button and select the downloaded add-in folder
4. Enable the add-in and click "Run on Startup" if desired

## Usage

1. Click the "Create Slots" button in the Solid Create panel
2. Select the face where you want to create slots
3. Select one or more lines along which to create the slots
4. Adjust the slot parameters:
   - Number of slots
   - Slot length
   - Slot width
   - Slot depth
5. Click OK to create the slots

## Parameters

- **Number of Slots**: How many slots to create along each line (1-100)
- **Slot Length**: The length of each slot
- **Slot Width**: The width of each slot
- **Slot Depth**: How deep to cut the slots into the face

## Notes

- The slots are created with rounded ends for a professional finish
- The selected lines are used as construction lines and don't affect the final geometry
- Each slot is created as a proper profile and extruded into the face
- The add-in automatically handles multiple lines and creates slots along each one

## Requirements

- Autodesk Fusion 360
- Python 3.x

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Your Name 