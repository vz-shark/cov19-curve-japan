import pandas as pd
import numpy as np
from abc import ABCMeta, abstractmethod




class CovDataBase(metaclass=ABCMeta):
    def __init__(self, urls = {}, verbose=0):
        self.urls = urls
        self.verbose = verbose
        self.raw_data = {}
        self.df = None

    def read(self):
        for key,val in self.urls.items():
            ext = val.split('.')[-1]
            tmp = None
            if(ext == 'csv'):
                tmp = pd.read_csv(val)
            assert tmp is not None, f'read error!! ext={ext} ( {key}: {val} )' 
            self.raw_data[key] = tmp
        return(True)        

    def disp(self):
        pass

    @abstractmethod 
    def make_df(self):
        pass

class CovDataJP(CovDataBase):
    def __init__(self
                 ,urls = {'byDate': 'https://raw.githubusercontent.com/swsoyee/2019-ncov-japan/master/Data/byDate.csv'}
                 ,verbose=0
                  ):
        
        super().__init__(urls=urls, verbose=verbose)    

    def make_df(self):
        pass

    def make_JHU(self):
        df_raw = self.raw_data['byDate']
        # 全部 Nanの行は削除
        if( df_raw.iloc[-1:,1:].isnull().all(axis=1).values[0] == True ):
            df_raw = df_raw.drop(df_raw.index.values[-1])
            if(self.verbose >=  1): 
                print('drop [.isnull().all()] record')
        # 日付に変換
        df_raw['date'] = pd.to_datetime(df_raw['date'], format='%Y%m%d')
        days = df_raw['date'].dt.strftime('%m/%d/%y').values.tolist()
        # 欠損値を0にする
        df_raw = df_raw.fillna(0)
        # 増加数と日本全体(クルーズ船とチャーター便を除く)
        inc = df_raw
        inc['日本全体'] = inc.drop(columns=['クルーズ船','チャーター便']).iloc[:,1:].sum(axis=1)
        # 累積数を出す
        tot = pd.concat( [inc.iloc[:,0:1], inc.iloc[:,1:].cumsum()], axis=1)

        # 流用元(global版)と同じ構成になるよう
        tmp = tot.set_index('date').T.reset_index()
        tmp.columns.name = None
        tmp = tmp.rename(columns={'index':'Country/Region'})
        tmp['Province/State'] = np.nan
        tmp['Lat'] = np.nan
        tmp['Long'] = np.nan
        tmp = pd.concat([tmp[['Province/State', 'Country/Region', 'Lat', 'Long']], tmp.iloc[:, 1:-3]], axis=1)
        tmp.columns = tmp.columns[0:4].values.tolist() + days

        #出来た。
        self.df_jhu = {}
        self.df_jhu['Comfirmed'] = tmp






# for debug
if __name__ == "__main__":
    jp = CovDataJP()
    jp.read()
    jp.make_JHU()
    print( jp.df_jhu['Comfirmed'].head())