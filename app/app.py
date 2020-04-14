#!/usr/bin/env python

import os
import sys
import pickle
import numpy as np
import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html

from datetime import datetime, date, timedelta


sys.path.append('../utils/')
import covdata
from covplot import CovPlot_Curve

def makefig(df, regionstr, startlim = 10):
    print(f"## makefig() #{regionstr} ")
    obs_df = df[ df['Country/Region'] == f'{regionstr}']
    data_y = obs_df.iloc[0,4:].values
    data_x = [ datetime.strptime(i, '%m/%d/%y').date()  for i in obs_df.columns[4:].values ]
    data_x = np.array(data_x)

    data_bool = data_y >= startlim
    data_y = data_y[data_bool]
    data_x = data_x[data_bool]

    print("#CovPlot", end='')
    print("- create", end='')
    plot = CovPlot_Curve( data_x[0:-1], data_y[0:-1], title=f'Comfirmed Cases In {regionstr}')
    print("- make_data", end='')
    plot.make_data()
    print("- make_fit", end='')
    plot.make_fit()
    print("- make_fig", end='')
    plot.make_fig()

    return(plot)

#データセット読み込み
print(f"load dataset")
jpdata = covdata.CovDataJP()
jpdata.read()
jpdata.make_JHU()
jpdf = jpdata.df_jhu["Comfirmed"]

# 罹患者総数が多い順に並べる
cases = jpdf.iloc[:,[1,-1]].groupby('Country/Region').sum()
mostrecentdate = cases.columns[0]
print('\nTotal number of cases (in countries with at least 100 cases) as of', mostrecentdate)
cases = cases.sort_values(by = mostrecentdate, ascending = False).drop("クルーズ船")
#cases = cases[cases[mostrecentdate] >= 100]
sorted_region = cases.index.values.tolist()
regions = sorted_region[0:10]
# for one in ["茨城"]:
#     if( not one in regions):
#         regions.append(one)
print(f"regions: {regions}")

# figを作る
print("######### make fig #############")
figpkl = "./cache/cache_fig.pkl"
plots = {}
if( os.path.exists(figpkl)):
    print(f"using cache.....{figpkl}")
    with open(figpkl, "rb") as fd:
        plots = pickle.load(fd)
else:
    for one in regions:
        plots[one] = makefig(jpdf, one)
    print(f"saving cache....{figpkl}")
    with open(figpkl, "wb") as fd:
        pickle.dump(plots, fd)


# htmlコンポーネットを用意
print("######## make html components ########")
with open('./elements/description_approximation.md', 'r') as fd:
    markdown_section_approximation =  fd.read()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

partsls = []
partsls += [html.H1(children='Trends of COVID-19 Epidemic In Japan ')]
partsls += [html.Hr()]
partsls += [dcc.Markdown( markdown_section_approximation)]
for key, val in plots.items():
    partsls += [html.Br()]
    partsls += [dcc.Graph(id=f'id-curve-{key}', figure=val.fig)] 
partsls += [ html.Br() for _ in range(2)]

app.layout = html.Div(children=partsls)



if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')

