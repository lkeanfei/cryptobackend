
import itertools
import json

f = open("test.json" , "r")
json_data = json.load(f)
d_list = json_data["results"]

# d_list.append( { "id" : 1 , "model_type" : "a" , "count" :2})
# d_list.append( { "id" : 2 , "model_type" : "a" , "count" :3})
# d_list.append( { "id" : 3 , "model_type" : "b" , "count" :12})
# d_list.append( { "id" : 4 , "model_type" : "b" , "count" :22})
# d_list.append( { "id" : 1 , "model_type" : "b" , "count" :222})
# d_list.append( { "id" : 2 , "model_type" : "b" , "count" :24})
# d_list.append( { "id" : 4 , "model_type" : "c" , "count" :52})

for k,v in itertools.groupby(d_list , key = lambda x:x["model_type"]):
    print("********")
    print(k)

    for obj in v:
        print(obj)


import re

str1 = 'Ethereum is a <a href="https://www.coingecko.com/en?category_id=29&view=market">smart contract platform</a> that enables developers to build tokens and decentralized applications (dapps). ETH is the native currency for the Ethereum platform and also works as the transaction fees to miners on the Ethereum network. Ethereum is the pioneer for blockchain based smart contracts. Smart contract is essentially a computer code that runs exactly as programmed without any possibility of downtime, censorship, fraud or third-party interference. It can facilitate the exchange of money, content, property, shares, or anything of value. When running on the blockchain a smart contract becomes like a self-operating computer program that automatically executes when specific conditions are met. Ethereum allows programmers to run complete-turing smart contracts that is capable of any customizations. Rather than giving a set of limited operations, Ethereum allows developers to have complete control over customization of their smart contract, giving developers the power to build unique and innovative applications. Ethereum being the first blockchain based smart contract platform, they have gained much popularity, resulting in new competitors fighting for market share. The competitors includes: <a href="https://www.coingecko.com/en/coins/ethereum_classic">Ethereum Classic</a> which is the oldchain of Ethereum, <a href="https://www.coingecko.com/en/coins/qtum">Qtum</a>, <a href="https://www.coingecko.com/en/coins/eos">EOS</a>, <a href="https://www.coingecko.com/en/coins/neo">Neo</a>, <a href="https://www.coingecko.com/en/coins/icon">Icon</a>, <a href="https://www.coingecko.com/en/coins/tron">Tron</a> and <a href="https://www.coingecko.com/en/coins/cardano">Cardano</a>. Ethereum wallets are fairly simple to set up with multiple popular choices such as myetherwallet, <a href="https://www.coingecko.com/buzz/complete-beginners-guide-to-metamask?locale=en">metamask</a>, and <a href="https://www.coingecko.com/buzz/trezor-model-t-wallet-review">Trezor</a>. Read here for more guide on using ethereum wallet: <a href="https://www.coingecko.com/buzz/how-to-use-an-ethereum-wallet">How to Use an Ethereum Wallet</a>'

ret = str1.replace("</a>" , "")

l1 = [m.start() for m in re.finditer( '<a', ret)]
l2 = [m.start() for m in re.finditer( '>', ret)]


finalStr = str1[:l1[0]]

cnt = 0
for cnt in range(0 , len(l1)-1):
    finalStr = finalStr + ret[l2[cnt]+1 :l1[cnt+1]]


print(finalStr)

print(l1)
print(l2)

print(finalStr)



 