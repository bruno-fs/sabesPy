
# coding: utf-8

def getData(date):
    """recebe um objeto date ou uma string com a data no 
    formato YYYY-MM-DD e retorna uma 'Série' (do pacote pandas)
    com os níveis dos reservatórios da sabesp"""
    fixPercent = lambda s: float(s.replace(",",".").replace("%",""))

    import datetime
    if type(date) == datetime.date:
        date = date.isoformat()

    ## vamos ser educados e nao fazer taaaaantas requisições de uma vez
    from time import sleep
    sleep(1)

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


def percFixer(p,volMax,volumeMorto=0):
    volAtual = volMax*(p/100) - volumeMorto
    q = 100*volAtual/volMax
    #import numpy as np
    q = round(q,1)
    return q


def fixPerc(p, data, log=True, sistema='Cantareira', fixFunc=percFixer):
    """corrige o percentual divulgado pela sabesp"""

    def str2date(data, format='%Y-%m-%d'):
        """converte uma string contendo uma data e retorna um objeto date"""
        import datetime as dt
        return dt.datetime.strptime(data,format)
    
    if log:
        def decora(f):
            def printLog(a,*args,**kwargs):
                b = f(a,*args, **kwargs)
                if 'volumeMorto' in kwargs:
                    print('%s: %5.1f ===> %5.1f  VOLUME MORTO %5.1f GL' % (data, a, b, kwargs['volumeMorto']))
                else:
                    print('%s: %5.1f ===> %5.1f' % (data, a, b))
                return b
            return printLog
        fixFunc = decora(fixFunc)
            
    if sistema == 'Cantareira':
        vm1day = str2date('16/05/2014', format='%d/%m/%Y')
        vm2day = str2date('24/10/2014', format='%d/%m/%Y')

        vm1 = 182.5
        vm2 = 105.4
        capacity = 982.07

        if str2date(data) < vm1day:
            return fixFunc(p, capacity)

        elif str2date(data) < vm2day:
            return fixFunc(p, capacity, volumeMorto=vm1)
        else:
            return fixFunc(p, capacity, volumeMorto=vm1+vm2)
    else:
        return p



reverseDate = lambda x: '.'.join(x.split('-')[::-1])
def humanReadableDates(f):
    def decorator(dataframes,*args,**kwargs):
        import pandas as pd
        copias = []
        for i, x in enumerate(dataframes):
            if type(x) == pd.core.frame.DataFrame or type(x) == pd.core.series.Series:
                copias.append(x.copy())
                copias[i].index = map(reverseDate, x.index)
        #print (copias)
        return f(copias,*args,**kwargs)
    return decorator


@humanReadableDates
def plotSideBySide(dfTupl, cm=['Spectral', 'coolwarm'], titles=[None, None]):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1,2, figsize=(17,5))

    for i, ax in enumerate(axes):
        dfTupl[i].ix[:].T.plot(
            kind='bar', ax=ax,
            rot=0, colormap=cm[i],
            title=titles[i])


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


