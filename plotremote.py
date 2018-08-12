
from flask import Flask, flash, request, redirect, url_for, render_template
import numpy
import pandas
import os, sys, time
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.sources import ColumnDataSource

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

@app.route('/download', methods=['POST'])
def download_url():
    if request.method != 'POST':
        flash ("download called with incorrect method")
        return redirect(url_for("get_url"))
    url = request.form['url']
    df = pandas.read_csv(url)
    df['AAPL_p'] = df['AAPL_x']   # make a column for readable date
    df.AAPL_x = pandas.to_datetime(df.AAPL_x) # datetime to make plottable
    print "df.head:\n",df.head()
    data = ColumnDataSource(df)
    tooltips = [ ("index", "$index"), ("price", "@AAPL_y"), ("date", "@{AAPL_p}") ]
    plot = figure(x_axis_type="datetime", plot_height=400, title='AAPL', tooltips=tooltips)
    # plot.line(df.AAPL_x, df.AAPL_y)
    plot.circle(x='AAPL_x', y='AAPL_y', source=data)
    script, div = components(plot)
    # generate table next to it
    return render_template("plot.html", bars_count=1, the_div=div, the_script=script)

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=True, host='0.0.0.0', port=5010)
