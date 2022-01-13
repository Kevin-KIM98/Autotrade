from logging import exception
import ccxt
import pprint
import time
from datetime import datetime

with open("binanceAPI.txt") as f:
    lines = f.readlines()
    api_key = lines[0].strip()
    secret = lines[1].strip()

binance = ccxt.binance(config={
    'apiKey':api_key,
    'secret':secret,
    
    'rateLimit': 3000,
    'enableRateLimit':True,
    'options':{
        'defaultType':'future'
    }
})

# 변수 설정
symbol = 'XTZUSDT'
initQty = 75
priceGap = 0.05
ptofit = 0.025
timeSleep = 3
cutCount = 10

# print('=============================================================================')
# print('* Symbol      : ',symbol)
# print('* 초기매매수량 : ',initQty)
# print('* 매매가격폭   : ',priceGap)
# print('* 수익가격폭   : ',ptofit)
# print('=============================================================================')

def initTrade(symbol):
    orderBook = binance.fetch_order_book(symbol)
    
    initLong = round(orderBook['bids'][0][0] - 0.02,3)
    initShort = round(orderBook['asks'][0][0] + 0.02,3)
    
    print('=============================================================================')
    print(datetime.now())
    print('***매수/매도 호가조회***')
    print(' ')
    print('초기 매수/롱 초기매매수량 :',initQty,' 초기 매수가격 : ', initLong)
    print('초기 매수/숏 초기매매수량 :',initQty,' 초기 매도가격 : ', initShort)

    # 매수/롱 
    order1 = binance.create_order(symbol,'limit','buy',initQty,initLong,params={'reduce_only':False})
    # 매도/숏
    order2 = binance.create_order(symbol,'limit','sell',initQty,initShort,params={'reduce_only':False})
    
    return 

def longTrade(symbol,qty,price):
    
    buyqty = qty
    buyprice = round(price - priceGap,3)

    sellqty = qty
    sellprice = round(price + ptofit,3)
    
    print(' ')
    print(datetime.now())
    print('물타기 매수/롱 매수수량 : ', buyqty, ' 매수 가격 : ', buyprice )
    print('롱 포지션 청산 매도수량 : ', sellqty,' 매도 가격 : ', sellprice )

    # 물타기 매수/롱 
    order1 = binance.create_order(symbol,'limit','buy',buyqty,buyprice,params={'reduce_only':False})
    # 롱 포지션 청산
    order2 = binance.create_order(symbol,'limit','sell',sellqty,sellprice,params={'reduce_only':True})
    return

def shortTrade(symbol,qty,price):

    sellqty = qty
    sellprice = round(price + priceGap,3)

    buyqty = qty
    buyprice = round(price - ptofit,3)
    
    print(' ')
    print(datetime.now())
    print('물타기 매수/숏 매도수량 : ', sellqty,' 매수 가격 : ', sellprice )
    print('숏 포지션 청산 매수수량 : ', buyqty, ' 매도 가격 : ', buyprice )
    
    # 물타기 매수/숏
    order1 = binance.create_order(symbol,'limit','sell',sellqty,sellprice,params={'reduce_only':False})
    # 숏 포지션 청산
    order2 = binance.create_order(symbol,'limit','buy',buyqty,buyprice,params={'reduce_only':True})
   
    return

def cancelOrder(symbol,gubun):

    orders = binance.fetch_open_orders(symbol)

    if len(orders) == 1:

        respCancel = binance.cancel_all_orders(symbol=symbol)
    
        if gubun == 'A':
            print(datetime.now())
            print('초기 매수/롱 체결완료, 초기 매도/숏 주문취소')
            print('=============================================================================')
        elif gubun == 'B':
            print(datetime.now())
            print('초기 매도/숏 체결완료, 초기 매수/롱 주문취소')
            print('=============================================================================')
        elif gubun == 'C':
            print(datetime.now())
            print('물타기 매수/롱 체결완료, 롱 포지션 청산 주문 취소')
            print('=============================================================================')
        elif gubun == 'D':
            print(datetime.now())
            print('롱 포지션 청산 체결완료, 물타기 매수/롱 주문 취소')
            print('=============================================================================')
        elif gubun == 'E':
            print(datetime.now())
            print('물타기 매도/숏 체결완료, 숏 포지션 청산 주문 취소')
            print('=============================================================================')
        elif gubun == 'F':
            print(datetime.now())
            print('숏 포지션 청산 체결완료, 물타기 매도/숏 주문 취소')  
            print('=============================================================================') 
    return 

def cancelAllOrder(symbol):

    respCancel = binance.cancel_all_orders(symbol=symbol)
    
    print(' ')
    print(datetime.now())
    print('##### 모든 주문 취소 #####')

    return

def searchOrder(symbol):

    orders = binance.fetch_open_orders(symbol)

    return len(orders)

def searchPosition(symbol):

    balance = binance.fetch_balance()
    
    symbolIndex = 0
    index = 0

    for i in balance['info']['positions']:
        if i['symbol'] == symbol:
            symbolIndex = index
        index = index + 1
    #print(symbolIndex)
    #print(balance['info']['positions'][symbolIndex])
    entryPrice =  balance['info']['positions'][symbolIndex]['entryPrice'] # 포지션 평균단가
    positionAmt = balance['info']['positions'][symbolIndex]['positionAmt'] # 포지션 사이즈

    return entryPrice, positionAmt

def quitBalance():

    balance = binance.fetch_balance()

    if balance['USDT']['total'] < 5 :
        print(' ')
        print(datetime.now())
        print('***** USDT잔고가 5달러미만으로 프로그램 종료합니다. *****')
        print(' ')

        quit()       
    return

def searchBlance():

    balance = binance.fetch_balance()

    return balance['USDT']['total'] 

print('start')

quitBalance()

while True:
    
    try:

        print('=============================================================================')
        print('* Symbol      : ',symbol)
        print('* 초기매매수량 : ',initQty)
        print('* 매매가격폭   : ',priceGap)
        print('* 수익가격폭   : ',ptofit)
        print('=============================================================================')
        
        count = 0
        
        # 초기 포지션 점검        
        entryPrice, positionAmt = searchPosition(symbol)

        entryPrice = float(entryPrice)
        positionAmt = float(positionAmt)    

        if entryPrice == 0.0 and positionAmt == 0.0:
            # 초기 주문 등록
            initTrade(symbol)

            while True:

                try: #2
                
                    orderCount = searchOrder(symbol)
                    entryPrice, positionAmt = searchPosition(symbol)
                    
                    entryPrice = float(entryPrice)
                    positionAmt = float(positionAmt)              

                    # 초기 롱 포지션 진입
                    if orderCount == 1 and entryPrice != 0.0 and positionAmt > 0.0 :
                        
                        # 초기 숏 주문 취소
                        cancelOrder(symbol,'A')                
                        
                        while True:

                            try:
                                orderCount = searchOrder(symbol)
                                entryPrice, positionAmt = searchPosition(symbol)
                                balance = searchBlance()
                            
                                entryPrice = float(entryPrice)
                                positionAmt = float(positionAmt)  

                                # 물타기 롱 주문
                                if orderCount == 0 and entryPrice != 0.0 and positionAmt !=0.0 and balance > entryPrice*positionAmt:
                                    
                                    longAMT = positionAmt
                                    
                                    longTrade(symbol,longAMT,entryPrice)

                                    count = count + 1

                                elif orderCount == 1 and entryPrice != 0.0 and positionAmt !=0.0 :

                                    # 물타기 롱 체결, 롱 포지션 정산 주문 취소
                                    cancelOrder(symbol,'C')

                                elif orderCount == 1 and entryPrice == 0.0 and positionAmt ==0.0 :
                                    
                                    # 롱 포지션 체결, 물타기 롱 주문 취소
                                    cancelOrder(symbol,'D')
                                    break
                                
                                elif orderCount == 2 and entryPrice == 0.0 and positionAmt ==0.0 :

                                    cancelAllOrder(symbol)
                                    break

                                # elif count == cutCount:

                                #     # 손절
                                #     print("*********************")
                                #     print("***** 강제 손절 *****")
                                #     print("*********************")
                                #     cancelAllOrder(symbol)
                                    
                                #     # 시장가 포지션 정리
                                #     order = binance.create_order(symbol,'market','sell',positionAmt,price=None,params={'reduce_only':True})
                                #     break
                                
                                quitBalance()

                                time.sleep(timeSleep)
                            except exception as e:
                                
                                print(e) 
                                time.sleep(timeSleep)
                                continue

                    # 초기 숏 포지션 진입
                    elif orderCount == 1 and entryPrice != 0.0 and positionAmt < 0.0 :
                        
                        # 초기 롱 주문 취소
                        cancelOrder(symbol,'B')
                        
                        while True:
                            
                            try:                        
                                orderCount = searchOrder(symbol)
                                entryPrice, positionAmt = searchPosition(symbol)
                                balance = searchBlance()
                                
                                entryPrice = float(entryPrice)
                                positionAmt = float(positionAmt)  

                                # 물타기 숏 주문
                                if orderCount == 0 and entryPrice != 0.0 and positionAmt !=0.0 and balance > entryPrice*positionAmt:
                                    
                                    longAMT = -1 * positionAmt
                                    
                                    shortTrade(symbol,longAMT,entryPrice)

                                    count = count + 1

                                elif orderCount == 1 and entryPrice != 0.0 and positionAmt !=0.0 :

                                    # 물타기 숏 체결, 숏 포지션 정산 주문 취소
                                    cancelOrder(symbol,'E')

                                elif orderCount == 1 and entryPrice == 0.0 and positionAmt == 0.0 :
                                    
                                    # 숏 포지션 정산 체결, 물타기 숏 주문 취소
                                    cancelOrder(symbol,'F')
                                    break    

                                elif orderCount == 2 and entryPrice == 0.0 and positionAmt ==0.0 :

                                    cancelAllOrder(symbol)
                                    break

                                # elif count == cutCount:

                                #     # 손절
                                #     print("*********************")
                                #     print("***** 강제 손절 *****")
                                #     print("*********************")
                                #     cancelAllOrder(symbol)

                                #     # 시장가 포지션 정리
                                #     order = binance.create_order(symbol,'market','buy',-1 * positionAmt,price=None,params={'reduce_only':True})
                                #     break  

                                quitBalance() 
                                
                                time.sleep(timeSleep) 

                            except exception as e:
                                print(e)  
                                time.sleep(timeSleep)
                                continue

                    elif orderCount == 0 and entryPrice == 0.0 and positionAmt == 0.0 :
                        break
                
                    time.sleep(timeSleep) 

                except exception as e:
                    print(e) 
                    time.sleep(timeSleep)
                    continue

        time.sleep(timeSleep)

    except exception as e:
        print(e) 
        time.sleep(timeSleep)    
        continue     
 