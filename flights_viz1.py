

import pandas as pd 
import numpy as np 
import bokeh 
from bokeh.plotting import figure, output_file, show
from bokeh.models.tools import HoverTool
from bokeh.core.properties import value
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.plotting import figure
import math
from bokeh.models import Range1d, LabelSet, Label

class Flight_Arrivals():
    def __init__(self):
        pass 
    
    def flights(self):
        avion=pd.read_csv("fly_mia.csv",encoding="latin-1")
        a=avion 
        a['est_arr_time'] = a['est_arr_time'].str.replace('?', '')
        a['est_arr_time']=a['est_arr_time'].str.replace(r"\(.*\)","")
        a=a[a.est_arr_time.str.contains('0')]

        sun1=a[a.est_arr_time.str.contains('Sun')]
        sun1['est_arr_time'] = sun1['est_arr_time'].str.replace('Sun', '2019-08-18')
        sun1['dep_time'] = sun1['dep_time'].str.replace('Sun', '2019-08-18')
        sat1=a[a.est_arr_time.str.contains('Sat')]
        sat1['est_arr_time'] = sat1['est_arr_time'].str.replace('Sat', '2019-08-17')
        sat1['dep_time'] = sat1['dep_time'].str.replace('Sat', '2019-08-17')
        fri1=a[a.est_arr_time.str.contains('Fri')]
        fri1['est_arr_time'] =fri1['est_arr_time'].str.replace('Fri', '2019-08-16')
        fri1['dep_time'] =fri1['dep_time'].str.replace('Fri', '2019-08-16')

        ok2=pd.concat([sun1,sat1,fri1],axis=0)
        ok2['dep_time'] =ok2['dep_time'].str.replace('Fri', '2019-08-16')
        ok2['dep_time'] =ok2['dep_time'].str.replace('Sat', '2019-08-17')

        ok2['dep_time']=pd.to_datetime(ok2['dep_time'])
        ok2['est_arr_time']=pd.to_datetime(ok2['est_arr_time'])

        ok2['flight_time']=ok2['est_arr_time']-ok2['dep_time']
        ok2['flight_time']=ok2['flight_time'].dt.total_seconds()
        ok2['flight_time']=ok2['flight_time']/60 #to minutes

        #airport time zones (departure zones) 
        #1. cest 
        cest=ok2[ok2.origin.str.contains('MAD|ZRH|BRU|MXP|CDG|DUS|FCO|VIE|FRA|Pisa|BCN|ZAZ|WAW|ORY|AMS')]
        cest['flight_time']=cest['flight_time']+360 
        cest['flight_time'] = cest['flight_time'].apply(lambda x: 561 if x < 400 else x)

        #2. +03 south american flights?? 
        sa=ok2[ok2.origin.str.contains("GIG|FOR|COR|EZE|Dois de|BSB|GRU|REC|MVD|BEL|SNU")]
        sa['flight_time']=sa['flight_time']+60
        sa['flight_time']=sa['flight_time'].apply(lambda x: 451.5 if x<350 else x)
        otro=ok2[~ok2.origin.str.contains('MAD|ZRH|BRU|MXP|CDG|DUS|FCO|VIE|FRA|Pisa|BCN|ZAZ|WAW|ORY|AMS|GIG|FOR|COR|EZE|Dois de|BSB|GRU|REC|MVD|BEL|SNU')]
        todos=pd.concat([cest,sa,otro],axis=0)

        # percent less one hour 
        bins=[0,60,120,180,240,300,360,420,480,540,600,660]
        todos['flight_bins']=pd.cut(todos['flight_time'], bins)  

        pct_time=todos['flight_bins'].value_counts()
        pct_time=pd.DataFrame(pct_time)
        pct_time.reset_index(level=0,inplace=True)
        pct_time['pct']=pct_time['flight_bins']/todos.shape[0]

        #ii. variance por origin
        vaR=todos.groupby('origin')['flight_time'].var()
        vaR.sort_values() 

        #iii. arrives part of the day 
        tiempo=todos[["origin","est_arr_time"]]
        t=tiempo 
        t['hours']=t['est_arr_time'].dt.hour
        t['minutes']=t['est_arr_time'].dt.minute 

        mid_six=t[(t.hours>=0) & (t.hours<=6)]
        seven_twelve=t[(t.hours>=7) & (t.hours<=12)]
        one_six=t[(t.hours>=13) & (t.hours<=18)]
        seven_twelve1=t[(t.hours>=19) & (t.hours<=23)]

        #percent arrivals by time of the day 
        mid_sixP=mid_six.shape[0]/t.shape[0]
        seven_twelveP=seven_twelve.shape[0]/t.shape[0]
        one_sixP=one_six.shape[0]/t.shape[0]
        seven_twelveP1=seven_twelve1.shape[0]/t.shape[0]

        #origin counts 
        ori=t['origin'].value_counts()
        ori=pd.DataFrame(ori)
        ori.reset_index(level=0,inplace=True)
        ori.columns=['origin','total']

        #time between flights 
        tX=todos
        tX.sort_values(['origin','dep_time'],inplace=True)
        tX['diff_dep']=tX['dep_time'].diff()
        mask=tX.origin !=tX.origin.shift(1)
        tX['diff_dep'][mask]=np.nan
        tX['diff_dep']=tX['diff_dep'].dt.total_seconds() 
        tX['diff_dep']=tX['diff_dep']/60 #to minutes  
        tX.iloc[0:10]
        tX=tX[~(tX.diff_dep==0)]

        takeoffs=tX.groupby('origin')['diff_dep'].median() 
        takeoffs=takeoffs.sort_values() 
        takeoffs=pd.DataFrame(takeoffs)
        take=takeoffs 
        take=take[take.diff_dep>=1]
        take1=take[take.diff_dep<=80]

        s=t
        s=s.set_index('est_arr_time')
        s=s.loc['2019-08-17 00:00:00':'2019-08-17 23:59:59']

        #VIZ I 
        #east coast time vs. cst,pdt, and mdt (comparing flight times)
        west_cent=tX[tX.origin.str.contains('LAX|SFO|LAS|SEA|SAN|SNU|DFW|MEX|MDW|MSY|CMW|MEM|ORD|TUL|MSP|MCI|STL|MID|IAH|VRA|PNS|GDL|MTY|KSAT|BHM|SCU|HOG|TLC|HSV')]
        east=tX[tX.origin.str.contains('NAS|PHI|Toron|Bahama|DCA|HAV|ORF|TPA|LGA|JAX|SAV|SDF|PIE|GGT|PLS|CVG|PIT|CHS|CLE|JFK|CAP|IND|DTW|KEY|CMH|BUF|RDU|SFB|MYEH|MYAM|CYUL|GSP|PBI|RIC|GSO|FMY|BDL|BWI|KTEB|ZSA|KMLB|KAPF|SGJ')]

        #length de flights 
        wc=west_cent['flight_bins'].value_counts() 
        wc=pd.DataFrame(wc)
        wc.columns=['flight_time']
        wc.reset_index(level=0,inplace=True)
        wc=wc.sort_values(by="index")
        wc=wc.set_index('index')

        ea=east['flight_bins'].value_counts() 
        ea=pd.DataFrame(ea)
        ea.columns=['flight_time']
        ea.reset_index(level=0,inplace=True)
        ea=ea.sort_values(by="index")
        ea=ea.set_index('index')

        factors=[("0-60"),("60-120"),("120-180"), ("180-240"),("240-300"),("300-360"),("360-420"),("420-480"),("480-540"),("540-600"),("600-660")]
        regions=['east_time_zone','other_time_zone']
        east_data=ea.flight_time.tolist()
        west_data=wc.flight_time.tolist()

        source=ColumnDataSource(data=dict(x=factors,east_time_zone=east_data,other_time_zone=west_data,))

        p = figure(x_range=FactorRange(*factors), plot_height=250,toolbar_location=None, tools="")
        p.vbar_stack(regions, x='x', width=0.9, alpha=0.5, color=["orange", "purple"], source=source,legend=[value(x) for x in regions]) 

        p.y_range.start = 0
        p.y_range.end = 120
        p.x_range.range_padding = 0.1
        p.xaxis.major_label_orientation = 1
        p.xgrid.grid_line_color = None
        p.xaxis.axis_label='Flight Time (Minutes)'
        p.yaxis.axis_label='Frequency'
        p.legend.location = "top_right"
        p.legend.orientation = "horizontal"
        output_file("mia1.html")
        #show(p) 

        #VIZ II (time between departures)
        source1=ColumnDataSource(take1)
        airports=source1.data['origin'].tolist()
        p1=figure(x_range=airports)
        p1.vbar_stack(stackers=['diff_dep'],x='origin',source=source1,width=0.5)
        p1.title.text='Time Between Flight Departures'
        p1.title.align="center" 
        p1.title.text_color="orange"
        p1.xaxis.major_label_orientation = math.pi/4.25 
        p1.xaxis.axis_label=''
        p1.yaxis.axis_label='Minutes'
        hover=HoverTool()
        hover.tooltips=[("Time Between Flights","@diff_dep minutes")]
        hover.mode='vline'
        p1.add_tools(hover)
        output_file("mia2.html")
        #show(p1)

        #VIZ III (what time of the day do flights arrive?)
        time_arr=['Midnight to 7 AM','7 AM to 1 PM','1 PM to 7 PM','7 PM to Midnight']
        counts=[mid_sixP,seven_twelveP1,one_sixP,seven_twelveP1] 
        palette=['lavender','plum','darkviolet','indigo']

        source = ColumnDataSource(data=dict(time_arr=time_arr, counts=counts))

        p = figure(x_range=time_arr, plot_height=250, toolbar_location=None, title="When Do Flights to X Arrive?")
        p.vbar(x='time_arr', top='counts', width=0.5, source=source, color="teal",
        line_color='white')

        p.xgrid.grid_line_color = None
        p.y_range.start = 0.0
        p.y_range.end = 0.6
        p.xaxis.axis_label=""
        p.yaxis.major_label_overrides = {0:'0',0.1:'10%',0.2:'20%',0.3:'30%',0.4:'40%',0.5:'50%'}
        p.yaxis.axis_label="Total Flights"
        p.legend.orientation = "horizontal"
        p.legend.location = "top_center"
        p.title.align="center"
        output_file("mia3.html")
        #show(p)

        #VIZ IV (outlier flight time plot)
        top_diez=tX['origin'].value_counts()
        top_diez=pd.DataFrame(top_diez)
        top_diez.reset_index(level=0,inplace=True)
        air_names=top_diez.iloc[0:10]["index"]
        an=air_names
        an0=an.iloc[0]
        an1=an.iloc[1]
        an2=an.iloc[2]
        an3=an.iloc[3]
        an4=an.iloc[4]
        an5=an.iloc[5]
        an6=an.iloc[6]
        an7=an.iloc[7]
        an8=an.iloc[8]
        an9=an.iloc[9]

        sub_air=tX[(tX.origin==an0) | (tX.origin==an1) | (tX.origin==an2) | (tX.origin==an3) | (tX.origin==an4) | (tX.origin==an5) | (tX.origin==an6) | (tX.origin==an7) | (tX.origin==an8) | (tX.origin==an9)]
        df=pd.DataFrame(dict(flight_time=sub_air['flight_time'],group=sub_air['origin']))
        originS=df['group'].unique().tolist()
        groups=df.groupby('group')
        q1=groups.quantile(q=0.25)
        q2=groups.quantile(q=0.50)
        q3=groups.quantile(q=0.75)
        iqr=q3-q1 
        upper=q3+1.5*iqr
        lower=q1-1.5*iqr 

        #find outliers in each group
        def outliers(group):
            originS=group.name
            return group[(group.flight_time > upper.loc[originS]['flight_time']) | (group.flight_time < lower.loc[originS]['flight_time'])]['flight_time']
        out=groups.apply(outliers).dropna()

        #prepare outlier data for plotting? 
        if not out.empty:
            outx=[]
            outy=[]
            for keys in out.index:
                outx.append(keys[0])
                outy.append(out.loc[keys[0]].loc[keys[1]])

        p = figure(tools="", background_fill_color="#efefef", x_range=originS, toolbar_location=None)

        #if no outliers, shrink lengths of stems to be no longer than the minimums or maximums
        qmin=groups.quantile(q=0.00)
        qmax=groups.quantile(q=1.00)
        upper.score=[min([x,y]) for (x,y) in zip(list(qmax.loc[:,'flight_time']),upper.flight_time)]
        lower.score = [max([x,y]) for (x,y) in zip(list(qmin.loc[:,'flight_time']),lower.flight_time)]

        # stems
        p.segment(originS, upper.flight_time, originS, q3.flight_time, line_color="black")
        p.segment(originS, lower.flight_time, originS, q1.flight_time, line_color="black")

        # boxes
        p.vbar(originS, 0.7, q2.flight_time, q3.flight_time, fill_color="aqua", line_color="black")
        p.vbar(originS, 0.7, q1.flight_time, q2.flight_time, fill_color="maroon", line_color="black")

        # whiskers (almost-0 height rects simpler than segments)
        p.rect(originS, lower.flight_time, 0.2, 0.01, line_color="black")
        p.rect(originS,upper.flight_time, 0.2, 0.01, line_color="black")

        # outliers
        if not out.empty:
            p.circle(outx, outy, size=6, color="#F38630", fill_alpha=0.6)

        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = "white"
        p.grid.grid_line_width = 2
        p.xaxis.major_label_text_font_size="12pt"
        p.xaxis.major_label_orientation = 3.5/2
        p.xaxis.axis_label = ''
        p.yaxis.axis_label = 'Flight Time (minutes)'
        p.title.text='Flights That Are Shorter or Longer Than Average'
        p.title.align="center"
        output_file('mia4x.html')
        #show(p)

        #VIZ V
        dep=tX['diff_dep'].tolist()
        time=tX['flight_time'].tolist() 
        airports=tX['origin'].tolist() 

        source=ColumnDataSource(data=dict(dep=dep,time=time,airports=airports)) 
        p=figure(title="Flight Time Vs. Time Between Departures",x_range=Range1d(0,1000))
        p.scatter(x="dep",y="time",size=4,source=source)
        p.xaxis[0].axis_label="Time Between Flights (Minutes)"
        p.yaxis[0].axis_label="Flight Time (Minutes)"

        labels = LabelSet(x='dep', y='time', text='airports', level='glyph',x_offset=5, y_offset=5, source=source, render_mode='canvas')
        
        p.add_layout(labels)
        show(p)

if __name__=='__main__':
    flights=Flight_Arrivals()
    flights.flights()








