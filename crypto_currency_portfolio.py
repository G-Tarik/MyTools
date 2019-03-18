#!/usr/bin/python3
import json
import requests
import sys


def print_profits(profits, coins):
    lines = [['coin', 'buy$', 'last$', 'buy', 'last', 'profitUSD', 'profit', 'AmountUSD', 'Amount']]

    for k,v in profits.items():
        lines.append([k,
                      f'{coins[k]["usdPrice"]:.4F}',
                      f'{v["usdLast"]:.4F}',
                      f'{coins[k]["price"]:.8F}',
                      f'{v["last"]:.8F}', 
                      f'{v["profitUSD"]:.2F}',
                      f'{v["profit"]:.2F}',
                      f'{v["AmountUSD"]:.2F}',
                      f'{coins[k]["amount"]:.8F}'])
        
    col_width = [max(len(w) for w in line) for line in zip(*lines)]
    print('\n')
    for line in lines:
        print(' :'.join(word.rjust(col_width[i] + 2) for i,word in enumerate(line)))


def get_rates(pair, exch):
    # pair value might looks like "XMR-BTC" or "LTC-ETH_1" 
    # if the same coin was bought at different price and different amount
    pair = pair.split('_')[0]
    exchange = {'bittrex': {'url': 'https://bittrex.com/api/v1.1/public/getticker?market=',
                            'error': 'message',
                            'result': 'result',
                            'price': 'Last'},
                'kucoin':  {'url': 'https://api.kucoin.com/v1/open/tick?symbol=',
                            'error': 'msg',
                            'result': 'data',
                            'price': 'lastDealPrice'}}

    resp = requests.get(exchange[exch]['url'] + pair).json()
    if not resp['success']:
        print(resp[exchange[exch]['error']])
        sys.exit(1)

    return resp[exchange[exch]['result']][exchange[exch]['price']]


def check_portfolio(coins):

    total_amount_USD = 0
    profits = {coinpair:{} for coinpair in coins}
    markets = {'btc': get_rates('USDT-BTC', 'bittrex'),
               'eth': get_rates('ETH-USDT', 'kucoin')}

    for k,v in coins.items():
        coinRate = get_rates(k, v['exchange'])
        profits[k]['last'] = coinRate
        profits[k]['usdLast'] = coinRate * markets[v['market']]
        profits[k]['profit'] = ( coinRate - coins[k]['price'] ) * 100 / coins[k]['price']
        profits[k]['profitUSD'] = ( coinRate * markets[v['market']] - coins[k]['usdPrice'] ) * 100 / coins[k]['usdPrice']
        profits[k]['AmountUSD'] = coins[k]['amount'] * profits[k]['usdLast']
        total_amount_USD += profits[k]['AmountUSD']

    print_profits(profits, coins)
    print('\nTotal balance USD: {:.2F}\n'.format(total_amount_USD))


def main():
    with open('portfolio.txt', 'r') as f:
        data = json.load(f)

    check_portfolio(data['coins'])


if __name__ == "__main__":
    main()
