#!/usr/bin/env python

import os
import sys
import pickle
import numpy as np
import pandas as pd
import base64
import argparse
from datetime import datetime, date, timedelta

import dash
import dash_core_components as dcc
import dash_html_components as html

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


def cli():
    parser = argparse.ArgumentParser(description='app')
    parser.add_argument('--host', type=str, default="127.0.0.1",  help='Specifiy web server bind address')
    parser.add_argument('--port', type=int, default=8050,         help='Specifiy web server bind port')
    parser.add_argument('--topnum', type=int, default=10,         help='Specifiy number of region')
    parser.add_argument('--cache_dir', type=str, default="../cache/",  help='Specifiy cache directory')
    parser.add_argument('--forced',  action='store_true',  help='forced not using cache.')
    parser.add_argument('--only_update_cache', action='store_true', default=False, help='Only update cache.')
    # for debug
    parser.add_argument('--debug', action='store_true', default=False, help='Enable Dash debug mode ')
    parser.add_argument('--dont_show_fig', action='store_true', help='Disable fig show ')
    args = parser.parse_args()

    plots = {}
    if( not args.dont_show_fig ):
        print("######### make fig #############")
        figpkl = os.path.join(args.cache_dir, "cache_fig.pkl" )
        if( os.path.exists(figpkl) and args.forced is False):
            print(f"using cache.....{figpkl}")
            with open(figpkl, "rb") as fd:
                plots = pickle.load(fd)
        else:
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
            regions = sorted_region[0:args.topnum]
            # for one in ["茨城"]:
            #     if( not one in regions):
            #         regions.append(one)
            print(f"regions: {regions}")

            for one in regions:
                plots[one] = makefig(jpdf, one)
            print(f"saving cache....{figpkl}")
            with open(figpkl, "wb") as fd:
                pickle.dump(plots, fd)
    
    if(args.only_update_cache):
        print("Finish !. only update cache.")
        

    # htmlコンポーネットを用意
    print("######## make html components ########")
    with open('./contents/description_approximation.md', 'r') as fd:
        markdown_section_approximation =  fd.read()

    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

    with open("./contents/shark.png", "rb") as fd:
        b64img = base64.b64encode(fd.read()).decode(encoding='utf-8')

    header = html.Header(children=[
                html.Center( children=[
                    html.Img( src=f"data:image/png;base64,{b64img}", width="4%", height="4%"),
                    html.P("NCS (neko covid system)"),
                    html.Hr()
                ])
            ])

    print(header)

    partsls = []
    partsls += [header]
    partsls += [html.H1("Trends of COVID-19 Epidemic in Japan") ]
    partsls += [html.Br() for _ in range(2)]
    partsls += [dcc.Markdown( markdown_section_approximation)]
    for key, val in plots.items():
        partsls += [html.Br()]
        partsls += [dcc.Graph(id=f'id-curve-{key}', figure=val.fig)] 
    partsls += [ html.Br() for _ in range(2)]

    app.layout = html.Div(children=partsls)

    # run server
    app.run_server(debug=args.debug, host=args.host, port=args.port )


def debug_args_set():
    sys.argv += ['--topnum', '1']
    sys.argv += ['--forced']
    #sys.argv += ['--only_update_cache']
    #sys.argv += ['--dont_show_fig']

if __name__ == '__main__':
    #debug_args_set()
    cli()
