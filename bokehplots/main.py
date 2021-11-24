#!/usr/bin/env python
# coding: utf-8

# ## Make nice interactive plots with Bokeh package

# In[1]:

from os.path import join, dirname
import numpy as np
#from astropy.io import ascii
import pandas as pd
import bokeh
import glob
from bokeh.layouts import row, column
from bokeh.models import Select, CDSView, GroupFilter, BooleanFilter, Whisker, TeeHead
from bokeh.palettes import Spectral11, Blues8, Viridis11, RdBu8
from bokeh.plotting import curdoc, figure, ColumnDataSource
from bokeh.sampledata.autompg import autompg_clean as df
from bokeh.io import output_notebook, show, push_notebook
from bokeh.server.server import Server
#output_notebook()

SIZES = list(range(6, 22, 3))
COLORS = Viridis11
N_SIZES = len(SIZES)
N_COLORS = len(COLORS)


# In[2]:


df = pd.read_pickle(join(dirname(__file__), 'static/REASONS_DataFrame_withsdbinfo'))


# In[3]:


columns = sorted(df.columns)
discrete = [x for x in columns if df[x].dtype == object]
continuous = [x for x in columns if x not in discrete]
#source = ColumnDataSource(data=df)
#df.at['0','Target']='ciao'
#df['Target'][0]
#glob.glob('./bokehplots/static/GJ14*')
#discrete


# In[4]:



def create_figure():
    xs = x.value#.value#df[x.value].values
    ys = y.value#.value#df[y.value].values
    x_title = x.value.title()
    y_title = y.value.title()
    
    kw = dict()
    if x.value in discrete:
        kw['x_range'] = sorted(set(df[x.value].values))
        if x.value == 'Target':
            df.sort_values(y.value,inplace=True)
            kw['x_range'] = df[x.value].values
                       
    if y.value in discrete:
        kw['y_range'] = sorted(set(df[y.value].values))
        if y.value == 'Target':
            df.sort_values(x.value,inplace=True)
            kw['y_range'] = df[y.value].values
    #print(kw['x_range'])
    #print(y.value)
    
    kw['title'] = "%s vs %s" % (x_title, y_title)
    
      
    #Quantities without upper or lower limits
    df['imgs']=[glob.glob('./bokehplots/static/'+x+'_*.png') for x in df['Target']]
    #source.add([glob.glob('./bokehplots/static/'+x+'*.png') for x in source.data['Target']],
               #name='imgs')
    for i in ['Lstar','d','R', 'Fbelt', 'PA']:
        df[i+'_str']=["{:.1f}".format(x) for x in df[i]] 
        df.loc[df[i+'_str']=='nan',i+'_str'] = '-'
        
    for i in ['wavelength']:
        df[i+'_str']=["{:.2f}".format(x) for x in df[i]] 
        df.loc[df[i+'_str']=='nan',i+'_str'] = '-'
        
    for i in ['f']:
        df[i+'_str']=["{:.1e}".format(x) for x in df[i]]
        df.loc[df[i+'_str']=='nan',i+'_str'] = '-'
        
    #Quantities with upper or lower limits
    for i in ['width','inc']:
        df[i+'_str']=["{:.1f}".format(x) for x in df[i]]
        df.loc[df[i+'_lims']=='u',i+'_str'] = '<'+df[i+'_str']
        df.loc[df[i+'_lims']=='l',i+'_str'] = '>'+df[i+'_str']
        df.loc[df[i+'_str']=='nan',i+'_str'] = '-'

    for i in ['h']:
        df[i+'_str']=["{:.2f}".format(x) for x in df[i]]
        df.loc[df[i+'_lims']=='u',i+'_str'] = '<'+df[i+'_str']
        df.loc[df[i+'_lims']=='l',i+'_str'] = '>'+df[i+'_str']
        df.loc[df[i+'_str']=='nan',i+'_str'] = '-'

    
    source = ColumnDataSource(data=df)
 
    TOOLTIPS = """
        <div>
            <div>
                <img
                    src="@imgs" height="212" alt="@imgs" width="212"
                    style="float: left; margin: 0px 0px 0px 0px;"
                    border="2"
                    class="center"
                ></img>
            </div>
            <div>
                <span style="font-size: 15px; font-weight: bold;text-align: center">@Target</span>
                <span style="font-size: 13px; color: #966;text-align: center">[L: @Lstar_str Lsun, d: @d_str pc]<br></span>
                <span style="font-size: 13px;text-align: center">lambda_mm: @wavelength_str mm, Fbelt_mm: @Fbelt_str mJy<br></span>
                <span style="font-size: 13px;text-align: center">R: @R_str au, width: @width_str au<br></span>
                <span style="font-size: 13px;text-align: center">f: @f_str, h: @h_str<br></span>
                <span style="font-size: 13px;text-align: center">inc: @inc_str deg, PA: @PA_str deg</span>
            </div>
        </div>
    """


    #TOOLTIPS = [
    #("system", "@Target"),
    ##("("+x_title+","+y_title+")", "(@"+x.value+", @"+y.value+")"),
    #("Wavelength (mm)", "@wavelength"),
    #("Flux (mJy)", "@Fbelt"),
    #("Radius (au)", "@R"),
    #("Width (au)", "@width"),
    #("PA (deg)", "@PA"),
    #("inc (deg)", "@inc"),
    ##("desc", "@desc"),
    #]
    

    
    
    
    if (xs not in ['Target', 'wavelength', 'PA', 'inc', 'dRA', 'dDec', 'fracwidth', 'h']):
        xaxtype='log'
    else:
        xaxtype='auto'
    if (ys not in ['Target', 'wavelength', 'PA', 'inc', 'dRA', 'dDec', 'fracwidth', 'h']):
        yaxtype='log'
    else:
        yaxtype='auto'
        
    p = figure(plot_height=600, plot_width=800, tools='pan,box_zoom,hover,reset, wheel_zoom', tooltips=TOOLTIPS, **kw, x_axis_type=xaxtype, y_axis_type=yaxtype)
    p.xaxis.axis_label = x_title
    p.yaxis.axis_label = y_title
    if x.value in discrete:
        p.xaxis.major_label_orientation = pd.np.pi / 4

    
        
    sz = 9
    if size.value != 'None':
        if len(set(df[size.value])) > N_SIZES:
            groups = pd.qcut(df[size.value].values, N_SIZES, duplicates='drop')
        else:
            groups = pd.Categorical(df[size.value])
        sz = [SIZES[xx] for xx in groups.codes]
        source.add(sz, name='size')
    else:
        source.add([sz]*len(df[x.value].values), name='size')

        
    c = "#31AADE"
    if color.value != 'None':
        if len(set(df[color.value])) > N_COLORS:
            groups = pd.qcut(df[color.value].values, N_COLORS, duplicates='drop')
        else:
            groups = pd.Categorical(df[color.value])
        c = [COLORS[xx] for xx in groups.codes]
        source.add(c, name='color')
    else:
        source.add([c]*len(df[x.value].values), name='color')
    
    
    if (xs+'_lims' in source.column_names):# and (ys+'_lims' not in source.column_names):
        #to not plot upper and lower limits, simply flag view3 and view1 lines and corresponding triangle lines below
        #view3 = CDSView(source=source, filters=[GroupFilter(column_name=xs+'_lims', group='l')])
        #view1 = CDSView(source=source, filters=[GroupFilter(column_name=xs+'_lims', group='u')])
        view2 = CDSView(source=source, filters=[GroupFilter(column_name=xs+'_lims', group='NaN'),GroupFilter(column_name=ys+'_lims', group='NaN'),
                                                BooleanFilter([False if xx=='NaN' else True for xx in df[xs].values]), 
                                                BooleanFilter([False if xx=='False' else True for xx in df['ScoCen'].values])])
        view4 = CDSView(source=source, filters=[GroupFilter(column_name=xs+'_lims', group='NaN'),GroupFilter(column_name=ys+'_lims', group='NaN'),
                                                BooleanFilter([False if xx=='NaN' else True for xx in df[xs].values]), 
                                                BooleanFilter([True if xx=='False' else False for xx in df['ScoCen'].values])]) 
        p.circle(x=xs, y=ys, source=source, color='color', size='size', line_color="white", alpha=0.6, 
                 hover_color='white', hover_alpha=0.5, view=view2) 
        p.square(x=xs, y=ys, source=source, color='color', size='size', line_color="white", alpha=0.6, 
                 hover_color='white', hover_alpha=0.5, view=view4) 
        #p.triangle(x=xs, y=ys, source=source, color='color', size='size', line_color="white", alpha=0.6, 
        #           hover_color='white', hover_alpha=0.5, view=view1, angle=np.pi/2.0)  
        #p.triangle(x=xs, y=ys, source=source, color='color', size='size', line_color="white", alpha=0.6, 
        #           hover_color='white', hover_alpha=0.5, view=view3, angle=-np.pi/2.0)
        
    if (ys+'_lims' in source.column_names):# and (xs+'_lims' not in source.column_names):
        #view3 = CDSView(source=source, filters=[GroupFilter(column_name=ys+'_lims', group='l')])
        #view1 = CDSView(source=source, filters=[GroupFilter(column_name=ys+'_lims', group='u')])
        view2 = CDSView(source=source, filters=[GroupFilter(column_name=ys+'_lims', group='NaN'),GroupFilter(column_name=xs+'_lims', group='NaN'), 
                                                BooleanFilter([False if xx=='NaN' else True for xx in df[xs].values]), 
                                                BooleanFilter([False if xx=='False' else True for xx in df['ScoCen'].values])])
        view4 = CDSView(source=source, filters=[GroupFilter(column_name=ys+'_lims', group='NaN'),GroupFilter(column_name=xs+'_lims', group='NaN'), 
                                                BooleanFilter([False if xx=='NaN' else True for xx in df[xs].values]), 
                                                BooleanFilter([False if xx=='True' else True for xx in df['ScoCen'].values])])
        p.circle(x=xs, y=ys, source=source, color='color', size='size', line_color="white", alpha=0.6, 
                 hover_color='white', hover_alpha=0.5, view=view2) 
        p.square(x=xs, y=ys, source=source, color='color', size='size', line_color="white", alpha=0.6, 
                 hover_color='white', hover_alpha=0.5, view=view4) 
        #p.inverted_triangle(x=xs, y=ys, source=source, color='color', size='size', line_color="white", alpha=0.6, 
        #           hover_color='white', hover_alpha=0.5, view=view1)
        #p.triangle(x=xs, y=ys, source=source, color='color', size='size', line_color="white", alpha=0.6, 
        #           hover_color='white', hover_alpha=0.5, view=view3)    

 
    if (xs+'_lims' not in source.column_names) and (ys+'_lims' not in source.column_names):
        view2 = CDSView(source=source, filters=[BooleanFilter([False if xx=='False' else True for xx in df['ScoCen'].values])])
        view4 = CDSView(source=source, filters=[BooleanFilter([False if xx=='True' else True for xx in df['ScoCen'].values])])
        p.circle(x=xs, y=ys, source=source, color='color', size='size', line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5, view=view2)    
        p.square(x=xs, y=ys, source=source, color='color', size='size', line_color="white", alpha=0.6, hover_color='white', hover_alpha=0.5, view=view4)    
    
        
        
    if xs+'_1sigup' in source.column_names:
        source.add(source.data[xs]+source.data[xs+'_1sigup'], name=xs+'up')
        source.add(source.data[xs]+source.data[xs+'_1sigdwn'], name=xs+'dwn')
        w = Whisker(source = source, base = ys, upper = xs+'up', lower = xs+'dwn', dimension='width', line_color='color', 
                    line_width=2.0, line_alpha=0.5, upper_head=TeeHead(line_color='red', line_alpha=0.0), lower_head=TeeHead(line_color='red', line_alpha=0.0))
        #w.upper_head.line_color = 'color'
        #w.lower_head.line_color = 'color'
        p.add_layout(w)
    if ys+'_1sigup' in source.column_names:
        source.add(source.data[ys]+source.data[ys+'_1sigup'], name=ys+'up')
        source.add(source.data[ys]+source.data[ys+'_1sigdwn'], name=ys+'dwn')
        w = Whisker(source = source, base = xs, upper = ys+'up', lower = ys+'dwn', dimension='height', line_color='color',
                    line_width=2.0, line_alpha=0.5, upper_head=TeeHead(line_color='red', line_alpha=0.0), lower_head=TeeHead(line_color='red', line_alpha=0.0))
        #w.upper_head.line_color()
        #w.lower_head.line_color()
        p.add_layout(w)
        
        
    return p#, color=c, size=sz


# In[5]:


def update(attr, old, new):
    layout.children[1] = create_figure()
    #push_notebook()
#source = ColumnDataSource(data=df)
#source.data['R']


# In[6]:


x = Select(title='X-Axis', value='Target', options=columns)
x.on_change('value', update)

y = Select(title='Y-Axis', value='R', options=columns)
y.on_change('value', update)

size = Select(title='Size', value='None', options=['None'] + continuous)
size.on_change('value', update)

color = Select(title='Color', value='width', options=['None'] + continuous)
color.on_change('value', update)

controls = column([x, y, color, size], width=200)
layout = row(controls, create_figure())

curdoc().add_root(layout)
curdoc().title = "REASONS"
show(create_figure())
#sorted(set(df['Target'].values))
#df[color.value].values[np.isfinite(df[color.value].values)]
#Now save as python script, then execute start bokeh server with /d1/boudica1/anaconda3/bin/bokeh serve --show make_bokeh_plots.py


# In[7]:


#pl.hist(df['fracwidth'].values[np.where(df['fracwidth_lims'].values=='NaN')[0]], bins=8, alpha=0.7)
#pl.xlabel('dR/R')


# In[ ]:




