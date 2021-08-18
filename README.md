# Introduction

I write pacman ... because why not?

# Design

The `pmlib` directory is supposed to be a pure backend with virtually no front
end rendering assumptions.  It operates a grid with (presumed) square cells and
places paku and the ghosts with floating point coordinates on that grid.  It is
the responsibility of the front end to render these floating point locations
across cells as needed.

Each character takes a callable for the logic function which must return a
direction in which to travel.  The `pmlib` core moves the character one epsilon
move distance every game iteration.  The logic function takes a `state`
dictionary which allows the developer of the logic function to retain state
across iterations to have a longer term plan.

# Bread-crumb trails

An emerging design element is that each ghost character should be associated
with an immediate plan of the path it will take.  The first plan is how to get
out of the ghost box and is planned directly from the map.  Subsequent plans
are developed by the ghost logic function.  These plans are little more than a
list of adjacent cells on the map and the navigation engine contains the core
logic to advance the ghost through those cells - including around corners.
These list of adjacent cells through which to navigate are called "bread-crumb
trails".

# Front ends

## Console

A proof-of-concept console rendering should be included.  It would be best
viewed in a square font such as https://strlen.com/square/ .

## Qt

QPainter in a QWidget.

## JSON websocket

Every render call sends out a (hopefully small?) updated board and this could
be passed to a JS front-end.  Render to HTML canvas.
