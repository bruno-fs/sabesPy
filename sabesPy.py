
# coding: utf-8


def getData(date):
    """recebe um objeto date ou uma string com a data no
    formato YYYY-MM-DD e retorna uma 'Série' (do pacote pandas)
    com os níveis dos reservatórios da sabesp"""

    fixPercent = lambda s: float(s.replace(",",".").replace("%",""))

    import datetime
    if type(date) == datetime.date:
        date = date.isoformat()

    ## requisição
    import urllib.request
    req = urllib.request.urlopen("https://sabesp-api.herokuapp.com/" + date).read().decode()

    ## transforma o json em dicionario
    import json
    data = json.loads(req)

    ## serie
    dados = [ fixPercent(x['data'][0]['value']) for x in data ]
    sistemas = [ x['name'] for x in data ]

    import pandas as pd
    return pd.Series(dados, index=sistemas, name=date)


def plotSideBySide(dfTupl, cm=['Spectral', 'coolwarm']):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1,2, figsize=(17,5))

    for i, ax in enumerate(axes):
        dfTupl[i].ix[:].T.plot(
            kind='bar', ax=ax,
            rot=0, colormap=cm[i])


        for j in range(len(dfTupl[i].columns)):
            itens = dfTupl[i].ix[:,j]
            y = 0
            if itens.max() > 0:
                y = itens.max()
            ax.text(j, y +0.5,
                '$\Delta$\n{:0.1f}%'.format(itens[1] - itens[0]),
                ha='center', va='bottom',
                fontsize=14, color='k')

    plt.show()



def fixPercent(p, data, log=True, sistema='Cantareira'):
    """corrige o percentual divulgado pela sabesp"""

    def str2date(data, format='%Y-%m-%d'):
        """converte uma string contendo uma data e retorna um objeto date"""
        import datetime as dt
        return dt.datetime.strptime(data,format)


    def percReal(a,volumeMorto=0):
        volMax = 982.07
        volAtual = volMax*(a/100) -volumeMorto
        b = 100*volAtual/volMax
        import numpy as np
        b = np.round(b,1)
        if log:
            print('%s: %5.1f ===> %5.1f  VOLUME MORTO %5.1f (bi L)' % (data, a, b, volumeMorto))
        return b

    if sistema == 'Cantareira':

        vm1day = str2date('16/05/2014', format='%d/%m/%Y')
        vm2day = str2date('24/10/2014', format='%d/%m/%Y')

        vm1 = 182.5
        vm2 = 105.4

        if str2date(data) < vm1day:
            perc = percReal(p)
            return perc

        elif str2date(data) < vm2day:
            perc = percReal(p, volumeMorto=vm1)
            return perc

        else:
            perc = percReal(p, volumeMorto=vm1+vm2)
            return perc


if __name__ == '__main__':
    pass
