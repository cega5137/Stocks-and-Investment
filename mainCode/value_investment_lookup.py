from stock import stock, getTickerList
from decimal import *

def defensive_investor_portafolio(ticker):
	TMK = stock(ticker)

	#TMK.priceBookRatio('quarterly')
	#TMK.EPS('quarterly')
	
	#TMK.grahamNumber('quarterly')
	#TMK.priceEarning('quarterly')
	#TMK.priceGraham('quarterly')
	#print(TMK.valuations[["Price-Book","price-earnings","Graham-number", "price-Graham"]])
	#print(TMK.financial[["EPS","current-ratio"]])
	#print("\n",TMK.income_stmts["Close"])
	#print(TMK.trade_history)
	#print("Close:", TMK.trade_history["Close"][-1])

	#print (TMK.financial["current-ratio"])

	try:
		TMK.currentRatio('quarterly')
	except Exception as insta:
		return False

	if TMK.financial["current-ratio"][0] > 2:
		print("\tCurrent ratio: Ok")
	else:
		print("\tCurrent ratio: Fail")
		return False

	TMK.EPS('quarterly')
	if TMK.financial["EPS"][0] > 0:
		print("\tEarnings per share: Ok")
	else:
		print("\tEarnings per share: Fail")
		return False

	TMK.priceGraham('quarterly')
	if TMK.valuations["price-Graham"][0] < 100:
		print("\tGraham percentage: Ok")
	else:
		print("\tGraham percentage: Fail")
		return False

	TMK.grahamNumber('quarterly')
	if TMK.valuations["Graham-number"][0] < TMK.trade_history["Close"][0]:
		print("\tGraham Number: Ok")
	else:
		print ("\tGraham Number: Fail")
		return False

	return True

def main():
	ticker_list = ['GPRO','SNAP','SPOT','TSLA','AAPL',"KO"]
	#sticker_list = ["AAPL"]
	ticker_nasdaq = getTickerList()
	#print (ticker_nasdaq)
	
	for index,ticker in ticker_nasdaq.iterrows():
		#print (ticker["ETF"])
		if "N" in ticker["ETF"]: 
			print(ticker["Symbol"])
			print(ticker["Symbol"],": ", defensive_investor_portafolio(ticker["Symbol"]))
			print()

if __name__ == '__main__':
	main()