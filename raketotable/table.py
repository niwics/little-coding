#!/usr/bin/env python
# -*- coding: utf-8 -*-

def print_table(players):
    px = 60
    css = "\
<style type=\"text/css\">\
h2 {text-align: center}\
table {margin: auto; border: 2px solid #555555; font-size: big; border-collapse: collapse; text-align: center; vertical-align: center}\
table th {font-size: small; border-bottom: 2px solid #555555}\
td, th {width: %spx; height: %spx; margin: 0; padding: 0; border: 1px solid #AAAAAA}\
th, tr td:first-of-type {background-color: #DDDDDD}\
tr th:first-of-type {background-color: #AAAAAA}\
tr td:first-of-type {border-right: 2px solid #555555}\
.points, .filled {background-color: #EEEEEE}\
.points {border-left: 2px solid #555555;}\
</style>\
    " % (px, px)
    html = "<html><meta charset=\"utf-8\" /> %s<h2>Raketopohár __.__.201_</h2>\
        <table><tr><th><img src=\"raketoimg.jpg\" width=\"%spx\" height=\"%spx\"></th>" % (css, px, px)
    for i in range(players):
        html += "<th></th>"
    html += "<th class=\"points\">Body</th><th class=\"filled\">Pořadí</th></tr>"
    for row in range(players):
        html += "<tr>"
        for col in range(players+3):
            td_class = ''
            td_class = " class=\"points\"" if col ==  players+1 else ""
            if row == col-1 or col == players+2:
                td_class = 'filled'
            elif col == players+1:
                td_class = 'points'
            class_str = ' class="%s"' % td_class if td_class else ''
            html += "<td%s></td>" % class_str
        html += "</tr>"
    html += "<html>"
    with open('raketotable-%splayers.html'%players, 'w') as f:
        f.write(html)

def main():

    for players in range(4, 9):
        print_table(players)

if __name__ == "__main__":
    main()
