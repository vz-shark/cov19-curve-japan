import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta

#thread
import threading
import concurrent.futures

import plotly.graph_objects as go
#import plotly.offline as offline

sys.path.append('../utils/')
from curvefit import CurveF 
import covdata



class CovPlot_Curve(object):
    def __init__(self, data_x, data_y, title=''):
        self.data_x = data_x
        self.data_y = data_y
        self.title = title
        
        self.day_start = None
        self.day_size = None
        self.day_num = None
        self.datafits = []
        self.fig = None


    def make_data(self, day_start=15):
        self.day_start  = day_start
        self.day_size = len(self.data_y)
        self.day_num = self.day_size - self.day_start + 1

        obsY =   self.data_y
        obsInc = np.diff(np.insert(obsY, 0, 0))


        # データセットを時系列に整理
        for offset in range(self.day_num):
            at = self.day_start + offset
            at_obsY = obsY[0:at]
            atdic = {}
            atdic['today']=self.data_x[at-1]
            atdic['at'] = at
            atdic['day_offset'] = offset
            atdic['data_X'] = self.data_x[0:at]
            atdic['data_Y'] = at_obsY
            atdic['data_Inc'] = obsInc[0:at]
            self.datafits.append(atdic)


    def make_fit(self, thread_max=10):
        # 近似曲線オブジェクト生成
        for one in self.datafits:
            one['curve'] = CurveF( np.arange(len(one['data_Y'])), y=one['data_Y'])

        # マルチスレッドでフィット
        if( thread_max == 0):
            for i, one in enumerate(self.datafits):
                one['curve'].fit(verbose=0,idstr=f'{i:03d}')
        else:
            print(f"thread pool start !!  -  num={thread_max}")
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=thread_max)
            count = 0
            for i, one in enumerate(self.datafits):
                executor.submit(one['curve'].fit, verbose=0, idstr=f'{i:03d}')
                count += 1
            print(f"thread pool {count} submmit")
            executor.shutdown()
            print("main thread finish!!")

    def make_fig(self):

        # make data_series and layout_series  (time sequential)
        data_series = []
        layout_series = []
        for one in self.datafits:
            at = one['at']
            at14 = at + 14
            date14_range = [ self.data_x[0] + timedelta(i) for i in range(at14)] 
            calcd = {}
            for kind in one['curve'].get_fitkind():
                calcd[kind] = one['curve'].calc(kind, np.arange(at14))
            
            
            #### make data_series list of fig.data 
            a_data = []
            # observed 
            a_data += [dict( x=one['data_X'],  y=one['data_Y'],    type="scatter",  name="Total",  mode="markers" )]
            a_data += [dict( x=one['data_X'],  y=one['data_Inc'],  type="bar",      name="Increase")]
            #a_data += [dict( x=np.arange(at),  y=one['data_Inc'],  type="bar",      name="Increase")]
            # fitted curve
            for kind in one['curve'].get_fitkind():
                if( len(calcd[kind]) != 0):
                    a_data += [dict( x=date14_range, y=calcd[kind], type="scatter", name=kind, mode="lines", line={"dash": "dot"} )]
            
            data_series.append(a_data)

            #### make layout_series list of fig.layout.annotations 
            annls = []
            # observed
            annls += [dict( x=one['data_X'][-1], y=one['data_Y'][-1]
                        , text=f"Observation<br>As of {one['today'].strftime('%m/%d')}<br>{one['data_Y'][at-1]:.0f} cases"
                        , showarrow=True, arrowhead=7, ax=-20, ay=-40 )]
            # fitted curve
            for kind in one['curve'].get_fitkind():
                if( len(calcd[kind]) != 0):
                    annls += [dict( x=date14_range[-1], y=calcd[kind][-1]
                            , text=f"Estimate<br>2 weeks later<br>{calcd[kind][-1]:.0f} cases"
                            , showarrow=True, arrowhead=7, ax=-20, ay=-40 )]
            
            layout_series.append({"annotations": annls})
            
            

        # make figure
        fig_dict = {
            "data": [],
            "layout": {},
            "frames": []
        }

        fig_dict["layout"]['annotations']= layout_series[-1]["annotations"]
        fig_dict["layout"]['hovermode']='x'
        fig_dict["layout"]["updatemenus"] = [
            {
                "buttons": [
                    {
                        "args": [None, {"frame": {"duration": 200, "redraw": False},
                                        "fromcurrent": True, "transition": {"duration": 100,
                                        "easing": "quadratic-in-out"}}],
                        "label": "Play",
                        "method": "animate"
                    },
                    {
                        "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                        "mode": "immediate",
                                        "transition": {"duration": 0}}],
                        "label": "Pause",
                        "method": "animate"
                    }
                ],
                "direction": "left",
                "pad": {"r": 10, "t": 87},
                "showactive": False,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0,
                "yanchor": "top"
            }
        ]

        sliders_dict = {
            "active": 0,
            "yanchor": "top",
            "xanchor": "left",
            "currentvalue": {
                "font": {"size": 20},
                #"prefix": "Date: ",
                "visible": True,
                "xanchor": "right"
            },
            "transition": {"duration": 100, "easing": "cubic-in-out"},
            "pad": {"b": 10, "t": 50},
            "len": 0.9,
            "x": 0.1,
            "y": 0,
            "steps": []
        }

        # make plotly data
        fig_dict["data"] = data_series[-1]

        # make plotly frames
        for offset in range(self.day_num):
            atday = offset + self.day_start
            frame = {"data": [], "name": str(self.data_x[atday-1]), "layout": layout_series[offset]}
            frame["data"] = data_series[offset]
            fig_dict["frames"].append(frame)

            slider_step = {
                "args": [
                    [self.data_x[atday-1]]
                    ,
                    {
                        "frame": {"duration": 200, "redraw": False},
                        "mode": "immediate",
                        "transition": {"duration": 100}
                    }
                ],
                "label": str(self.data_x[atday-1]),
                "method": "animate"
            }
            sliders_dict["steps"].append(slider_step)


        fig_dict["layout"]["sliders"] = [sliders_dict]
        fig = go.Figure(fig_dict)
        fig.update_layout(hovermode='x unified')
        fig.update_layout(width=950, height=700, autosize=False)
        fig.update_layout(title=self.title, xaxis_title='Date', yaxis_title='Cases')
        #fig.update_layout(autosize=False)
        #fig.update_yaxes(autorange=[0,100])
        #fig.update_yaxes(range=[0,100])

        #できた
        self.fig = fig

    def show(self):   
        self.fig.show()




# for debug
if __name__ == "__main__":
    print("#### CovData ####")
    jpdata = covdata.CovDataJP()
    jpdata.read()
    jpdata.make_JHU()
    df = jpdata.df_jhu["Comfirmed"]
    
    regionstr = "日本全体"
    #regionstr = "東京"
    obs_df = df[ df['Country/Region'] == f'{regionstr}']
    data_y = obs_df.iloc[0,4:].values
    data_x = [ datetime.strptime(i, '%m/%d/%y').date()  for i in obs_df.columns[4:].values ]

    print("#### CovPlot ####")
    print("create")
    plot = CovPlot_Curve( data_x, data_y, title=f'Trends of Comfirmed Cases In {regionstr}')
    print("make_data")
    plot.make_data()
    print("make_fit")
    plot.make_fit()
    print("make_fig")
    plot.make_fig()

    print("save html")
    plot.fig.write_html(f"{regionstr}.html")

    print("show")
    plot.show()