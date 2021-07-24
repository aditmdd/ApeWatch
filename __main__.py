import os
import time
from termcolor import colored
from web3 import Web3, HTTPProvider


w3 = Web3(HTTPProvider('https://bsc-dataseed1.binance.org/'))
pairCreated_topic = '0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9'
wbnb_topic = '0x000000000000000000000000bb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'
pancake_factory_address = '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73'
pancake_routerv2_address = '0x10ED43C718714eb63d5aA57B78B54704E256024E'
wbnb = '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'
pancake_LP_ABI = open('ApeWatch/pancake-LP-abi', 'r').read()
pancake_routerv2_ABI = open('ApeWatch/pancake-routerv2-abi', 'r').read()
pancake_factory_ABI = open('ApeWatch/pancake-factory-abi', 'r').read()
token_info_ABI = open('ApeWatch/token-info-abi', 'r').read()
pancakeRouterv2 = w3.eth.contract(address=pancake_routerv2_address, abi=pancake_routerv2_ABI)
pancake_link = 'https://exchange.pancakeswap.finance/#/swap?outputCurrency={}'


def banner():
    print(colored('''
       d8888                   888       888          888            888      
      d88888                   888   o   888          888            888      
     d88P888                   888  d8b  888          888            888      
    d88P 888 88888b.   .d88b.  888 d888b 888  8888b.  888888 .d8888b 88888b.  
   d88P  888 888 "88b d8P  Y8b 888d88888b888     "88b 888   d88P"    888 "88b 
  d88P   888 888  888 88888888 88888P Y88888 .d888888 888   888      888  888 
 d8888888888 888 d88P Y8b.     8888P   Y8888 888  888 Y88b. Y88b.    888  888 
d88P     888 88888P"   "Y8888  888P     Y888 "Y888888  "Y888 "Y8888P 888  888 
             888                                                              
             888                                                              
             888                                                              ''', 'white', 'on_yellow'))

# Return: Dict(token0: reserve, token1: reserve)
def getReserve(lp):
    contract = w3.eth.contract(address=w3.toChecksumAddress(lp), abi=pancake_LP_ABI)
    r0, r1, timestamp = contract.functions.getReserves().call()
    token0 = contract.functions.token0().call()
    if token0.lower() == wbnb:
        token0 = 'BNB'
    token1 = contract.functions.token1().call()
    if token1.lower() == wbnb:
        token1 = 'BNB'
    reserve = {token0: r0, token1: r1}
    return reserve


def getReserveTokens(lp):
    contract = w3.eth.contract(address=w3.toChecksumAddress(lp), abi=pancake_LP_ABI)
    token0 = contract.functions.token0().call()
    if token0.lower() == wbnb:
        token0name = 'BNB'
        token1name = 'Token'
    token1 = contract.functions.token1().call()
    if token1.lower() == wbnb:
        token0name = 'Token'
        token1name = 'BNB'
    reserveTokens = {token0name: token0.lower(), token1name: token1.lower()}
    return reserveTokens

# Return Dict(name, symbol, contract address, lp address, reserve)
def gatherTokenInfo(lp):
    lp_contract = w3.eth.contract(address=w3.toChecksumAddress(lp), abi=pancake_LP_ABI)
    reserveTokens = getReserveTokens(lp)
    token = w3.toChecksumAddress(reserveTokens['Token'])
    bnb = w3.toChecksumAddress(wbnb)
    token_contract = w3.eth.contract(address=token, abi=token_info_ABI)
    name = token_contract.functions.name().call()
    symbol = token_contract.functions.symbol().call()
    reserve = getReserve(lp)
    tokenData = {'name': name,
                 'symbol': symbol,
                 'contract': reserveTokens['Token'],
                 'LP': lp,
                 'reserve': '{:.4f}'.format(w3.fromWei(reserve['BNB'], 'ether'))}
    return tokenData

def ape():
    prevBlock = w3.eth.block_number
    while True:
        time.sleep(0.2)
        currentBlock = w3.eth.block_number
        if currentBlock != prevBlock:
            prevBlock = currentBlock
            logs = w3.eth.get_logs({'address': '0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73', 'fromBlock': currentBlock})
            if len(logs) > 0:
                for event in logs:
                    if event['topics'][0].hex() == pairCreated_topic:
                        if event['topics'][1].hex() == wbnb_topic or event['topics'][2].hex() == wbnb_topic:
                            lp = '0x' + event['data'][26:66]
                            tokenData = gatherTokenInfo(lp)
                            print(f'block:{currentBlock}|name:{tokenData["name"]}|symbol:{tokenData["symbol"]}\n|'
                                  f'initial BNB pool:{tokenData["reserve"]}\n|ApeIn Link: {pancake_link.format(tokenData["contract"])}')
                    else:
                        print(f'block:{currentBlock}|No new pairs', end='\r')
        elif currentBlock == prevBlock:
            print(f'block:{currentBlock}|No new pairs', end='\r')






def main():
    os.system('clear')
    banner()
    input(colored('\nPress enter to start!', 'white'))
    ape()



if __name__ == '__main__':
    main()