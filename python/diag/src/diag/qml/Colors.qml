pragma Singleton

import QtQuick

/*
Ncurses colors:
================
0	COLOR_BLACK	Noir	(0, 0, 0)
1	COLOR_RED	Rouge	(205, 0, 0)
2	COLOR_GREEN	Vert	(0, 205, 0)
3	COLOR_YELLOW	Jaune	(205, 205, 0)
4	COLOR_BLUE	Bleu	(0, 0, 238)
5	COLOR_MAGENTA	Magenta	(205, 0, 205)
6	COLOR_CYAN	Cyan	(0, 205, 205)
7	COLOR_WHITE	Blanc	(229, 229, 229)
  */

QtObject {

    readonly property string black: "#000"
    readonly property string red: "#cd0000"
    readonly property string green: "#00cd00"
    readonly property string yellow: "#cdcd00"
    readonly property string blue: "#0000ee"
    readonly property string cyan: "#00cdcd"
    readonly property string white: "#e5e5e5"

    readonly property string background: blue
    readonly property string title: yellow

}
