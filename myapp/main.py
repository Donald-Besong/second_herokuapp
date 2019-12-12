#AUTHOR: Donald O. Besong

import re
import json
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, DatetimeTickFormatter, Select
from bokeh.layouts import layout
from bokeh.plotting import figure
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from math import radians
from pytz import timezone
from bokeh.models.widgets import PreText


#create text widget
text = """These are live prices of bitcoins. The y-axis shows the price when it was last traded.
   I show only two bitcoins, from https://www.bitmex.com/app/trade/XBTUSD. These are live 
   values. The bitcon can be selected from thr dropdown menu.I aqcuired the data by 
   performing web-scraping, using beautifulsoup. However, my actual project was a price forecast 
   and I got data using the above site's API, rather than web-scraping. My employer, Datw-wide 
   anayltics dies not permit me to publish the forecasting project, so I decided to show-case this 
   web-scraping use-case where I simply show live prices. It is more or less to show the possibilities 
   of Bokeh Server plots. 
                        Author: Dr Donald O. Besong."""
                        
pre = PreText(text=text, width=30, height=100)

#create figure
f=figure(x_axis_type='datetime')

#create webscraping function
bcsite = "http://bitcoincharts.com/markets/btcnCNY.html" # I will later use https://www.bitmex.com/app/trade/XBTUSD instead, "script" instead of "p", s=value_raw[3], s.text
bttrsite = "http://bitcoincharts.com/markets/btctradeCNY.html"
bitmex_site = "https://www.bitmex.com/app/trade/XBTUSD"
def extract_value_not_usedxxx(site=bcsite):
    r=requests.get(site,headers={'User-Agent':'Mozilla/5.0'})
    c=r.content
    soup=BeautifulSoup(c,"html.parser")
    value_raw=soup.find_all("p")
    value_net=float(value_raw[0].span.text)
    return(value_net)

def extract_value(index):
    r=requests.get(bitmex_site,headers={'User-Agent':'Mozilla/5.0'})
    c=r.content
    soup=BeautifulSoup(c,"html.parser")
    value_raw=soup.find_all("script")
    s=value_raw[3]
    txt=s.text
    d=json.loads(txt)
    instruments = d['instruments']
    instr = instruments[index]
    mark_price = instr['lastPrice']
    return(mark_price)
    
#create ColumnDataSource
#site = bcsite
symb0 = ("ETHZ19", '59')
symb1 = ("LTCZ19", '60')
fact = 1e6
dot = "\."
REMOVE_dot = re.compile(dot)
descr0 = REMOVE_dot.sub("", symb0[0]) + " bitcoin"
descr1 = REMOVE_dot.sub("", symb1[0]) + " bitcoin"

index = int(symb0[1])
source=ColumnDataSource(dict(x=[datetime.now(tz=timezone('Europe/Moscow'))],y=[fact*extract_value(index)]))

#create glyphs
f.circle(x='x',y='y',color='olive',line_color='brown',source=source)
f.line(x='x',y='y',source=source)

f.xaxis.major_label_orientation=radians(45)

###begin code for plotting locally**********************************************
#from bokeh.io import output_file, show
#output_file("bitcoins.html")
#show(f)
###begin code for plotting locally**********************************************
#

###begin code for embedding static plot to html*********************************
#from bokeh.embed import components
#from bokeh.resources import CDN
#js,div=components(f)
#cdn_js=CDN.js_files[0]
#cdn_css=CDN.css_files[0]
###end code for embedding static plot to html***********************************



#begin code for dynamic plots***************************************************
#create Select widget
options=[(symb0[1], descr0),(symb1[1], descr1)]
select=Select(title="Market Name",value=symb0[1],options=options)
#create periodic function
def update():
    index = int(select.value)
    new_data=dict(x=[datetime.now(tz=timezone('Europe/Moscow'))],y=[fact*extract_value(index)])
    source.stream(new_data,rollover=20)
    print(source.data)

def update_intermediate(attr, old, site):
    source.data=dict(x=[],y=[])
    update()
    
f.xaxis.formatter=DatetimeTickFormatter(
seconds=["%Y-%m-%d-%H-%m-%S"],
minsec=["%Y-%m-%d-%H-%m-%S"],
minutes=["%Y-%m-%d-%H-%m-%S"],
hourmin=["%Y-%m-%d-%H-%m-%S"],
hours=["%Y-%m-%d-%H-%m-%S"],
days=["%Y-%m-%d-%H-%m-%S"],
months=["%Y-%m-%d-%H-%m-%S"],
years=["%Y-%m-%d-%H-%m-%S"],
)

# configure visual properties on a plot's title attribute
f.title.text = "Streaming financial data - AUTHOR: Dr Donald O. Besong"
f.title.align = "right"
#f.title.text_color = "orange"
f.title.text_font_size = "18px"
f.title.background_fill_color = "yellow"

#configure visual properties on a plot's axes
f.xaxis.axis_label = "Date and time"
f.yaxis.axis_label = "Last Bid"
f.xaxis.axis_label_text_font_size = "10pt"
f.yaxis.axis_label_text_font_size = "10pt"
f.xaxis.axis_label_text_font_style = "bold"
f.yaxis.axis_label_text_font_style = "bold"

select.on_change("value",update_intermediate)

#add figure to curdoc and configure callback
lay_out=layout([[f, pre],[select]])
curdoc().add_root(lay_out)
curdoc().add_periodic_callback(update,2000)
#end code for dynamic plots***************************************************

#4. Displaying the document using (note Microsft edge does not work well. Use Chrome)
#on the command line, run "bokeh serve --show main.py"

