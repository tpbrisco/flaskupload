
from flask import Flask, flash, request, redirect, url_for, render_template
import numpy
import pandas
import os, sys, time
# bokeh general
from bokeh.models.sources import ColumnDataSource
from bokeh.resources import CDN
# bokeh plots
from bokeh.plotting import figure
from bokeh.models import TapTool, OpenURL, CustomJS, HoverTool
from bokeh.embed import components
# bokeh tables
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn

UPLOAD_FOLDER = '/tmp/uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'secretkey'

@app.route('/', methods=['GET', 'POST'])
def get_url():
    print "Method:",request.method
    if request.method == 'POST':
        # we have a URL to upload
        if 'url' not in request.form:
            flash ("No URL provided in request")
            return redirect(request.url)
        url = request.form['url']
        print "URL:",url
        if url == '':
            # empty URL provided
            flash ("Empty URL provided")
            return redirect(request.url)
        if url:
            flash ("Uploading %s" % (request.form['url']))
            return redirect(url_for("download_url"), code=307)
    # we received a GET request, so just show the template
    return render_template('homepage.j2')

CustomJSCode = """
var data = cds.data
var f = cb_obj.data;
// price = data['AAPL_y'];
// date = data['AAPL_x'];
price = "test_price"
date = "test_date"
x = cb_obj.x
y = cb_obj.y
sx = cb_obj.sx
sy = cb_obj.sy
console.log("Price: " + price + " Date: " + date + " x:" + x + " y:" + y + " sx:" + sx + " sy:" + sy);
// for (var propName in cb_obj) {
//  propValue = cb_obj[propName]
//  console.log("name:" + propName + " value:" + propValue)
// }
// var selected = geometry
// for (var propName in selected) {
//  propValue = cb_data[propName]
//  console.log("data_name:" + propName + " value:" + propValue)
// }

"""

def generate_plot(title, cds, x, y, tooltip):
    plot = figure(x_axis_type="datetime", title=title, tooltips=tooltip)
    # callback = CustomJS(args=dict(cds=cds), code=CustomJSCode)
    plot.circle(x=x, y=y, source=cds, size=8)
    # plot.js_on_event('tap', callback)
    plot.add_tools(TapTool(),hover)
    taptool = plot.select(type=TapTool)
    taptool.callback = OpenURL(url='http://www.dilbert.com/strip/@{AAPL_p}')
    script, div = components(plot)
    return {'script': script, 'div': div}

def generate_table(title, cds, tooltip):
    print "cds column_names:",cds.column_names
    columns = [
        TableColumn(field='AAPL_x', title='Date', formatter=DateFormatter()),
        TableColumn(field='AAPL_y', title='Price')]
    data_table = DataTable(source=cds, columns=columns)
    # could use a widgetbox is multiple tables were involved
    script, div = components(data_table)
    return {'script': script, 'div': div}

@app.route('/download', methods=['POST'])
def download_url():
    plots = []
    if request.method != 'POST':
        flash ("download called with incorrect method")
        return redirect(url_for("get_url"))
    url = request.form['url']
    df = pandas.read_csv(url)
    df['AAPL_p'] = df['AAPL_x']   # make a column for readable date
    df.AAPL_x = pandas.to_datetime(df.AAPL_x) # datetime to make plottable

    # generate graph of price/date
    tooltips = [ ("index", "$index"), ("price", "@AAPL_y"), ("date", "@{AAPL_p}") ]
    # generate bokeh data source
    cds = ColumnDataSource(df)
    plots.append(generate_plot('AAPL', cds, 'AAPL_x', 'AAPL_y', tooltips))
    plots.append(generate_table('AAPL', cds , None))

    return render_template("dashboard.html",
                           plots=plots,
                           css=CDN.render_css(),
                           js=CDN.render_js())

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host='0.0.0.0', port=5010)
