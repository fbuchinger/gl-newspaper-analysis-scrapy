# -*- coding: utf-8 -*-
import logging
import time
import sys, os

import pandas as pd

from bokeh.layouts import row
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.plotting import figure, show, output_file, ColumnDataSource
from bokeh.models import HoverTool, TapTool, CustomJS
from bokeh.models.tickers import YearsTicker
from datetime import date

changes_xlsx = r"E:\dev\gl-newspaper-analysis-scrapy\reports\2005-2015\summary-of-changes.xlsx"



dotstyles = {
    "medium": {
        "fill_color": "orange",
        "line_color": "green",
        "size": 10,
    },
    "major": {
        "fill_color": "red",
        "line_color": "brown",
        "size": 12,
    },
    "minor": {
        "fill_color": "#c6dbef",
        "line_color": "#6baed6",
        "size": 7,
    },
}




def timestamp (d):
    return time.mktime(d.timetuple()) /1000

figure_range = (
   timestamp(date(2007,1,1)),
   timestamp(date(2017,12,31))
)


def get_color(impact):
    style = dotstyles.get(impact,'minor')
    return style['fill_color']

def get_size(impact):
    style = dotstyles.get(impact,'minor')
    return style['size']



def create_change_timeline (changes_xlsx_path):
    xl = pd.ExcelFile(changes_xlsx_path)
    np_sheets = [sheet for sheet in xl.sheet_names if sheet == sheet.lower()] #do not process SUMMARY, CHANGE_TIMELINE sheets
    dot = figure(title="Timeline of Layout Changes", tools="pan,wheel_zoom,box_zoom,reset,resize,previewsave,tap",
                 y_range=np_sheets, x_axis_type="datetime", plot_width=1500, plot_height=300, toolbar_location="right",
                 x_minor_ticks=3)



    for sheet in xl.sheet_names:
        if sheet == sheet.lower():
            newspaper = sheet
            np_df = xl.parse(newspaper)

            np_changes =  np_df.loc[np_df['Change?'].str.lower() == "yes"]
            np_changes = np_changes[pd.notnull(np_changes['Impact'])]
            np_changes['newspaper'] = newspaper
            np_changes['snapshotURL'] = np_changes['snapshotURL'].map(lambda url: ''.join(url.partition('https://web.archive.org')[1:]))
            np_changes['color'] = np_changes['Impact'].str.lower().apply(get_color)
            np_changes['size'] = np_changes['Impact'].str.lower().apply(get_size)
            np_changes['change_date'] = np_changes['snapshot_date'].map(lambda snapshot_date: snapshot_date.strftime('%d-%m-%Y'))

            for impact in ['minor','medium', 'major']:
                changes_w_impact = np_changes.loc[np_changes['Impact'].str.lower() == impact]
                source = ColumnDataSource(changes_w_impact)
                dot.circle('snapshot_date','newspaper', source=source, color='color', size = 'size', legend = impact) # TODO: add correct color symbolizing


            # TODO: add quarters to the toolbar formatting
            dot.xaxis.formatter = DatetimeTickFormatter(months = ['%m/%Y', '%Y %m'])
            dot.xaxis.ticker = YearsTicker(desired_num_ticks= 10)
            dot.xgrid.minor_grid_line_alpha = 1
            dot.xgrid.minor_grid_line_color = 'navy'

    dot.add_tools(HoverTool(tooltips= [("Date","@change_date"),
                                        ("Medium","@newspaper"),
                                        ("Impact","@Impact"),
                                        ("Description","@Description"),
                                       ]))

    dot.legend.location = "top_left"
    dot.legend.click_policy="hide"
    addSnapshotOpener(dot)
    html_output = '%s.graph.html' % os.path.splitext(changes_xlsx_path)[0]
    output_file(html_output, title="Layout Changes in 10 international Newspapers")

    show(dot)


def addSnapshotOpener (figure):
    taptool = figure.select(type=TapTool)
    onGlyphSelectCB = CustomJS(code="""
                       console.log(cb_obj,arguments);
                       var snapshotDates = cb_obj.data.snapshot_date;
                       var clickedDate = arguments[1].geometries[0].x;

                       var smallestDiff = (new Date (2038,1,1)).valueOf();
                       var clickedSnapshotURL = null;
                       for (var i = 0; i < snapshotDates.length; i++){
                            var timeDiff = Math.abs (snapshotDates[i] - clickedDate);
                            if (timeDiff < smallestDiff){
                                clickedSnapshotURL = cb_obj.data.snapshotURL[i];
                            }
                       }


                       if (document.getElementById('content-frame') == null){
                           var iframe = document.createElement('iframe');
                           var containerDiv = document.createElement('div');
                           containerDiv.style = "position: absolute; top:300px; width: 1500px; bottom:40px;";
                           iframe.id = "content-frame";
                           iframe.src = clickedSnapshotURL;
                           iframe.style = "height: 100%; width: 100%";
                           containerDiv.appendChild(iframe);
                           document.body.appendChild(containerDiv);
                       }
                       else {
                         document.getElementById('content-frame').src = clickedSnapshotURL;
                       }
                   """)
    taptool.callback = onGlyphSelectCB



if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: %s xlsx file' % sys.argv[0])

    if not os.path.exists(sys.argv[1]):
        sys.exit('ERROR: .xlsx document %s was not found!' % sys.argv[1])

    create_change_timeline(sys.argv[1])

