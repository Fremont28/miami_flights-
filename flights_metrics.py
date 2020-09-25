#import libraries 
import pandas as pd 
import numpy as np 
import math

class Flight_Metrics():
    def _init__(self):
        pass
    
    def flights_met(self,file):
        avion=pd.read_csv(file,encoding="latin-1") #read-in csv file        
        a=avion 
        a['est_arr_time'] = a['est_arr_time'].str.replace('?', '')
        a['est_arr_time']=a['est_arr_time'].str.replace(r"\(.*\)","")
        a=a[a.est_arr_time.str.contains('0')]
        
        #datetime sring manipulation 
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

        ok2['flight_time']=ok2['est_arr_time']-ok2['dep_time'] #arrival time minus departure time 
        ok2['flight_time']=ok2['flight_time'].dt.total_seconds() #to seconds 
        ok2['flight_time']=ok2['flight_time']/60 #to minutes

        #min and max flight time by group 
        minF=ok2.groupby('origin')['flight_time'].max()
        minF=pd.DataFrame(minF)
        minF.reset_index(level=0,inplace=True)
        maxF=ok2.groupby('origin')['flight_time'].min()
        maxF=pd.DataFrame(maxF)
        maxF.reset_index(level=0,inplace=True)
        maxx=pd.merge(minF,maxF,on="origin") 
        maxx['diff_mm']=maxx.flight_time_x-maxx.flight_time_y
        maxx.sort_values(by="diff_mm")[['origin','diff_mm']]

        #1. central europe time zone (convert to standard time) 
        cest=ok2[ok2.origin.str.contains('MAD|ZRH|BRU|MXP|CDG|DUS|FCO|VIE|FRA|Pisa|BCN|ZAZ|WAW|ORY|AMS')]
        cest['flight_time']=cest['flight_time']+360 
        cest['flight_time'] = cest['flight_time'].apply(lambda x: 561 if x < 400 else x)

        #2.south america time zone (convert to standard time) 
        sa=ok2[ok2.origin.str.contains("GIG|FOR|COR|EZE|Dois de|BSB|GRU|REC|MVD|BEL|SNU")]
        sa['flight_time']=sa['flight_time']+60
        sa['flight_time']=sa['flight_time'].apply(lambda x: 451.5 if x<350 else x)
        otro=ok2[~ok2.origin.str.contains('MAD|ZRH|BRU|MXP|CDG|DUS|FCO|VIE|FRA|Pisa|BCN|ZAZ|WAW|ORY|AMS|GIG|FOR|COR|EZE|Dois de|BSB|GRU|REC|MVD|BEL|SNU')]
        todos=pd.concat([cest,sa,otro],axis=0)

        #flight time interval (seconds) 
        bins=[0,60,120,180,240,300,360,420,480,540,600,660]
        todos['flight_bins']=pd.cut(todos['flight_time'], bins)  
        pct_time=todos['flight_bins'].value_counts()
        pct_time=pd.DataFrame(pct_time)
        pct_time.reset_index(level=0,inplace=True)
        pct_time['pct']=pct_time['flight_bins']/todos.shape[0]

        #flight arrivals by time of the day 
        tiempo=todos[["origin","est_arr_time"]] 
        t=tiempo 
        t['hours']=t['est_arr_time'].dt.hour
        t['minutes']=t['est_arr_time'].dt.minute 
        mid_six=t[(t.hours>=0) & (t.hours<=6)]
        seven_twelve=t[(t.hours>=7) & (t.hours<=12)]
        one_six=t[(t.hours>=13) & (t.hours<=18)]
        seven_twelve1=t[(t.hours>=19) & (t.hours<=23)]

        #percent of flight arrivals by time of the day
        mid_sixP=mid_six.shape[0]/t.shape[0]
        print(mid_sixP)
        seven_twelveP=seven_twelve.shape[0]/t.shape[0]
        print(seven_twelveP) 
        one_sixP=one_six.shape[0]/t.shape[0]
        print(one_sixP) 
        seven_twelveP1=seven_twelve1.shape[0]/t.shape[0]
        print(seven_twelveP1) 

        #flight departure counts  
        ori=t['origin'].value_counts()
        ori=pd.DataFrame(ori)
        ori.reset_index(level=0,inplace=True)
        ori.columns=['origin','total']
        print(ori)

        #percent flight departure arrivals 
        arr1=mid_six['origin'].value_counts()
        arr1=pd.DataFrame(arr1)
        arr1.reset_index(level=0,inplace=True)
        arr1.columns=['origin','arr1']
        arr1=pd.merge(arr1,ori,on="origin")
        arr1['pct']=arr1.arr1/arr1.total

        arr2=seven_twelve['origin'].value_counts()
        arr2=pd.DataFrame(arr2)
        arr2.reset_index(level=0,inplace=True)
        arr2.columns=['origin','arr2']
        arr2=pd.merge(arr2,ori,on="origin")
        arr2['pct']=arr2.arr2/arr2.total

        arr3=one_six['origin'].value_counts()
        arr3=pd.DataFrame(arr3)
        arr3.reset_index(level=0,inplace=True)
        arr3.columns=['origin','arr3']
        arr3=pd.merge(arr3,ori,on="origin")
        arr3['pct']=arr3.arr3/arr3.total

        arr4=seven_twelve1['origin'].value_counts()
        arr4=pd.DataFrame(arr4)
        arr4.reset_index(level=0,inplace=True)
        arr4.columns=['origin','arr4']
        arr4=pd.merge(arr4,ori,on="origin")
        arr4['pct']=arr4.arr4/arr4.total
        arr4.sort_values(by="pct")

        #arrival percents (time of the day)
        arr1P=arr1.arr1.sum()/t.shape[0]
        arr2P=arr2.arr2.sum()/t.shape[0]
        arr3P=arr3.arr3.sum()/t.shape[0]
        arr4P=arr4.arr4.sum()/t.shape[0]

        #time between flights 
        tX=todos
        tX.sort_values(['origin','dep_time'],inplace=True)
        tX['diff_dep']=tX['dep_time'].diff()
        mask=tX.origin !=tX.origin.shift(1)
        tX['diff_dep'][mask]=np.nan
        tX['diff_dep']=tX['diff_dep'].dt.total_seconds() 
        tX['diff_dep']=tX['diff_dep']/60 #to minutes  
        tX=tX[~(tX.diff_dep==0)]

        #outliers
        def get_num_outliers (column):
            q1 = np.percentile(column, 25)
            q3 = np.percentile(column, 75)
            return sum((column<q1) | (column>q3))

        best=tX[["origin","flight_time"]]
        best.groupby('origin').agg([get_num_outliers])

        #iqr by departure airport 
        def get_iqr (column):
            q1 = np.percentile(column, 25)
            q3 = np.percentile(column, 75)
            return q3-q1
        iqr_range=best.groupby('origin').agg([get_iqr])
        iqr_range.columns=['iqr']
        iqr_range.sort_values(by="iqr") 
        iqr=iqr_range
        iqr=iqr[iqr['iqr']>0]
        iqr.reset_index(level=0,inplace=True)

        #difference in time between departures 
        takeoffs=tX.groupby('origin')['diff_dep'].median() 
        takeoffs=pd.DataFrame(takeoffs)
        takeoffs.reset_index(level=0,inplace=True)
        fast_dep=takeoffs.sort_values(by="diff_dep")
        print(fast_dep) 

        iqr1=pd.merge(takeoffs,iqr,on="origin")
        iqr1.sort_values(by="iqr") 
        iqr1['diff_dep'].corr(iqr1['iqr'])

if __name__=='__main__':
    metrics=Flight_Metrics()
    metrics.flights_met("fly_mia.csv")
