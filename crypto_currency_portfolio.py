#!/usr/bin/python3
import requests, json, sys


def printProfits( profits, coins ):
    lines = [ [ 'coin', 'buy$', 'last$', 'buy', 'last', 'profitUSD', 'profit', 'AmountUSD' ] ]

    for k,v in profits.items():
        lines.append( [ k, f'{coins[k]["usdPrice"]:.4F}', f'{v["usdLast"]:.4F}', f'{coins[k]["price"]:.8F}', f'{v["last"]:.8F}', 
                           f'{v["profitUSD"]:.2F}', f'{v["profit"]:.2F}', f'{v["AmountUSD"]:.2F}' ] )
        
    col_width = max( len(w) for l in lines for w in l ) + 2
    for line in lines:
        print( ' :'.join( word.rjust(col_width) for word in line) )
    

def getRates(pair, exch):
    # pair value might looks like "XMR-BTC" or "LTC-ETH_1" if the same coin was bought at different price and different amount
    pair = pair.split('_')[0]
    exchange = {
                'bittrex': {'url': 'https://bittrex.com/api/v1.1/public/getticker?market=',
                            'error': 'message',
                            'result': 'result',
                            'price': 'Last'},
                'kucoin':  {'url': 'https://api.kucoin.com/v1/open/tick?symbol=',
                            'error': 'msg',
                            'result': 'data',
                            'price': 'lastDealPrice'}
                }

    resp = requests.get( exchange[exch]['url'] + pair ).json()
    if not resp['success']:
        print( resp[exchange[exch]['error']] )
        sys.exit(0)
        
    return resp[exchange[exch]['result']][exchange[exch]['price']]


def checkPortfolio(coins):

    totalAmountUSD = 0
    profits = { coinpair:{} for coinpair in coins }
    markets = { 'btc': getRates( 'USDT-BTC', 'bittrex' ),
                'eth': getRates( 'ETH-USDT', 'kucoin' ) }

    for k,v in coins.items():
        coinRate = getRates( k, v['exchange'] )
        profits[k]['last'] = coinRate
        profits[k]['usdLast'] = coinRate * markets[v['market']]
        profits[k]['profit'] = ( coinRate - coins[k]['price'] ) * 100 / coins[k]['price']
        profits[k]['profitUSD'] = ( coinRate * markets[v['market']] - coins[k]['usdPrice'] ) * 100 / coins[k]['usdPrice']
        profits[k]['AmountUSD'] = coins[k]['amount'] * profits[k]['usdLast']
        totalAmountUSD += profits[k]['AmountUSD']

    printProfits( profits, coins )
    print( '\nTotal balance USD: {:.2F}\n'.format(totalAmountUSD) )


def main():
    with open( 'portfolio.txt', 'r' ) as f:
        data = json.load(f)

    checkPortfolio( data['coins'] )


if __name__ == "__main__":
    main()


