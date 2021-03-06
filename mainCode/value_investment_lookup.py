import sys
sys.path.append('../Functions and Libs/')
sys.path.append('../../Py2GoogleDrive/mainCode')

from stock import stock, getNASDAQTickerList, getSP500TickerList, getOtherTickerList
from decimal import *
from email_msg import emailMessage, email_information
from google_sheet_class import Gsheet


def defensive_investor_portafolio(ticker, highprice=10000, 
	max_current_ratio=2, 
	min_price_earnings=26.5,#22.5 
	max_price_book_value=1, 
	min_total_revenue = 500000, 
	min_earnings_stability=0,
	years_earnings_stability = 10,
	min_earnings_growth=26,
	dividends_on = True ):

	
	try:
		TMK = stock(ticker)
	except:
		print("Error with ticker")
		return False

	
	####################### Price #####################################
	if (highprice < TMK.trade_history["Close"][-1]):
		print ("\t[Fail] Price")
		return False
	else:
		print ("\t[ Ok ] Price")

	####################### Liabilities vs assets #################
	'''
	Current Liabilities or the ratio between assets over liabilities be greater than 2
	'''
	try:
		#TMK.currentRatio('quarterly')
		TMK.ratios('quarterly')
	except Exception as insta:
		print("\t[Erro] Current Ratio")
		return False

	if TMK.company_ratio[0]["liquidityMeasurementRatios"]["currentRatio"] and TMK.company_ratio[0]["liquidityMeasurementRatios"]["currentRatio"] > max_current_ratio:
		print("\t[ Ok ] Current ratio")
	else:
		print("\t[Fail] Current ratio: ", TMK.company_ratio[0]["liquidityMeasurementRatios"]["currentRatio"])
		return False

	
	########################### Price to earning ratio ############################
	'''
	Price to Earnings is su
	'''
	
	try:
		if not TMK.trailingPE():
			print("\t[Error] Missing EPS")
			return False
	except Exception as insta:
		print("\t[Error] Trailing PE")
		return False
		
	if TMK.trading[0]["PE-TTM"] < min_price_earnings:
		print("\t[ Ok ] Price earnings")
	else:
		print("\t[Fail] Price earnings: ", TMK.trading[0]["PE-TTM"])
		return False

	########################## Price to assets ########################
	try:
		TMK.pricePerBookValue()
	except Exception as insta:
		return False
	
	if TMK.trading[0]["Price-Book value"] < max_price_book_value and TMK.trading[0]["Price-Book value"] >= 0:
		print("\t[ Ok ] Price book value")
	else:
		print("\t[Fail] Price book value: ", TMK.trading[0]["Price-Book value"])
		return False

	

	####################### Enterprise Size ######################
	'''
	Maker sure the enterprise has more than certain amount of sales a year
	'''
	try:
		TMK.income()
	except Exception as insta:
		return False

	if TMK.income_stmts[0]["Revenue"] > min_total_revenue:
		print("\t[ Ok ] Sales/Enterprise Size")
	else:
		print("\t[Fail] Sales/Enterprise Size: ", TMK.income_stmts[0]["Revenue"])
		return False

	

	########################## Earnings stability over 10 years ##################
	'''
	10 Years of Profits will make sure the enterprise is a sound enterprise
	'''
	
	try:
		TMK.income()
	except Exception as insta:
		return False

	if len(TMK.income_stmts) < years_earnings_stability:
		years_earnings_stability = len(TMK.income_stmts)

	for i in range(0,years_earnings_stability):
		if TMK.income_stmts[i]["EPS"] and TMK.income_stmts[i]["EPS"] < min_earnings_stability:
			print("\t[Fail] Earnings per share Stability")
			return False

	print("\t[ Ok ] Earnings per share Stability")
	
	

	####################### Earnings growth and profitablity ######################
	'''
	Make sure the enterprise growth with at least inflation 3% - uses (1 + 0.03)^Years

	idealy get the 3 year average at the beginning and the end to prevent dips for a 10 year

	This case will be 2 year average of 4 years

	Curretly uses 12 for 

	'''

	try:
		#print(TMK.income_stmts[0]["EPS"],TMK.income_stmts[1]["EPS"],TMK.income_stmts[2]["EPS"])	
		eps_avg_beginning = (TMK.income_stmts[0]["EPS"] + TMK.income_stmts[1]["EPS"] + TMK.income_stmts[2]["EPS"])
		
		if len(TMK.income_stmts) <= 10:
			eps_avg_end = 0
			for i in range(1,4):
				if not TMK.income_stmts[-i]["EPS"]:
					return False
				eps_avg_end += TMK.income_stmts[-i]["EPS"]
			
		else:
			eps_avg_end = (TMK.income_stmts[8]["EPS"] + TMK.income_stmts[9]["EPS"] + TMK.income_stmts[10]["EPS"])
	except TypeError:
		return False

	except IndexError:
		return False


	#for eps in TMK.income_stmts:
	#	print(eps["EPS"])

	eps_growth = 100*((eps_avg_end - eps_avg_beginning)/eps_avg_beginning)
	if eps_growth > min_earnings_growth:
		print("\t[ Ok ] Earnings per share Growth")
	else:
		print("\t[Fail] Earnings per share Growth: ", eps_growth)
		return False


	###################### Dividends more than 20 years ###########################
	'''
	Pay dividends
	'''

	if dividends_on:
		if TMK.dividendHist(20):
			print("\t[ Ok ] Dividends")
		else:
			print("\t[Fail] Dividends")
			return False

	############################# End ####################################
	return True

def valueStocks(ticker, sheetClass, cellnumber):
	'''
	Check When to buy when to sell. 
		Find the risk-rewards
		Check how managment is doing
	'''
	TMK = stock(ticker)	


	###################### Current price to book ratio #################
	TMK.bookValuePerShare()
	TMK.pricePerBookValue()


	print ("Current Price: ", TMK.trade_history["Close"][-1])
	print ("Book value: %0.2f" %(TMK.trading["book value per share"][0]))
	
	print ("Price - book value: %0.2f " %(TMK.trading["price-book value"][0]))
	#print ("Sell at: %0.2f" % (TMK.trading["book value per share"][0]*2))

	print ("Percent return: %0.2f%%" %(100*(TMK.trading["book value per share"][0]-TMK.trade_history["Close"][-1])/TMK.trade_history["Close"][-1]) )


	msg = "%s: \nCurrent Price:\t\t%0.2f\nBook value:\t\t%0.2f\nPercentage to BV:\t%0.2f\n\n"%(ticker, TMK.trade_history["Close"][-1], TMK.trading["book value per share"][0], float(TMK.trading["book value per share"][0]-TMK.trade_history["Close"][-1])/TMK.trade_history["Close"][-1])

	sheetClass.append(range_name="Example!A" + str(cellnumber), item=str(ticker))
	sheetClass.append(range_name="Example!C" + str(cellnumber), item="%0.2f" %TMK.trading["book value per share"][0])
	sheetClass.append(range_name="Example!H" + str(cellnumber), item="%0.2f" %TMK.trade_history["Close"][-1])

	return msg

def main():
	to_email, from_email, pwd_email, title, sheet_link = email_information('../../email_passwd.init')
	
	watchlist = Gsheet(sheet_link)

	tickerSwitcher = "Full"
	#tickerSwitcher = "Other"
	#tickerSwitcher = "NASDAQ"
	tickerSwitcher = "ticker list"
	#tickerSwitcher = "S&P500"

	if tickerSwitcher is "ticker list":
		print ("Specific Ticker")
		ticker_list = ["AAPL","TSLA"]

		passTestStock = []
		for ticker in ticker_list:
			print(ticker)	
			worthy = defensive_investor_portafolio(ticker,dividends_on=True)
			
			print(ticker,": ", worthy,"\n")
			if worthy:
				passTestStock.append(ticker)

	elif tickerSwitcher is "S&P500":
		print("S&P 500 list")
		SP500_ticker = getSP500TickerList()
		passTestStock = []

		for index, ticker in SP500_ticker.iterrows():
			print(ticker["Symbol"])
			try:
				worthy = defensive_investor_portafolio(ticker["Symbol"],dividends_on=False)
				print(ticker["Symbol"],": ", worthy)
				if worthy:
					passTestStock.append(ticker["Symbol"])

			except KeyError:
				pass

		print("Stock to look into: ", passTestStock)

	elif tickerSwitcher is "NASDAQ":
		print ("NASDAQ List")
		ticker_nasdaq = getNASDAQTickerList()
		passTestStock = []
		nasdaq_length = len(ticker_nasdaq)
		print (nasdaq_length)
		for index, ticker in ticker_nasdaq.iterrows():
			if "N" in ticker["ETF"]: 
				print("%s - %0.2f%%" % (ticker["Symbol"], float(index)/float(nasdaq_length)*100))
				try:
					worthy = defensive_investor_portafolio(ticker["Symbol"],dividends_on=False)
				except KeyError:
					continue
				print(ticker["Symbol"],": ", worthy)
				print("\n")
				if worthy:
					passTestStock.append(ticker["Symbol"])

	elif tickerSwitcher is "Other":
		print ("Other List")
		passTestStock = []
		ticker_other = getOtherTickerList()
		other_length = len(ticker_other)

		for index, ticker in ticker_other.iterrows():
			if "N" in ticker["ETF"]:
				print("%s - %0.2f%%" % (ticker["NASDAQ Symbol"], float(index)/float(other_length)*100))
				try:
					worthy = defensive_investor_portafolio(ticker["NASDAQ Symbol"], dividends_on=False)
				except KeyError:
					continue
				print(ticker["NASDAQ Symbol"],": ", worthy)
				print("\n")
				if worthy:
					passTestStock.append(ticker["NASDAQ Symbol"])

	elif tickerSwitcher is "Full":
		print("Full")
		passTestStock = []
		ticker_nasdaq = getNASDAQTickerList()
		ticker_other = getOtherTickerList()
		nasdaq_length = len(ticker_nasdaq)
		other_length = len(ticker_other)
		print("total tickers", nasdaq_length+other_length)

		for index, ticker in ticker_nasdaq.iterrows():
			if "N" in ticker["ETF"]: 
				print("%s - %0.3f%%" % (ticker["Symbol"], float(index)/float(nasdaq_length+other_length)*100))
				try:
					worthy = defensive_investor_portafolio(ticker["Symbol"],dividends_on=False)
				except KeyError:
					continue
				print(ticker["Symbol"],": ", worthy)
				print("\n")
				if worthy:
					passTestStock.append(ticker["Symbol"])

		for index, ticker in ticker_other.iterrows():
			if "N" in ticker["ETF"]:
				print("%s - %0.3f%%" % (ticker["NASDAQ Symbol"], float(index+nasdaq_length)/float(nasdaq_length+other_length)*100))
				try:
					worthy = defensive_investor_portafolio(ticker["NASDAQ Symbol"], dividends_on=False)
				except KeyError:
					continue
				
				print(ticker["NASDAQ Symbol"],": ", worthy)
				print("\n")
				if worthy:
					passTestStock.append(ticker["NASDAQ Symbol"])

	print("Stock to look into: ", passTestStock)

	print("Stock that pass the test")
	email_msg = ""
	cellnumber = 2
	for ticker in passTestStock:
		print (ticker)
		email_msg = email_msg + valueStocks(ticker,watchlist, cellnumber)
		print(" ")
		cellnumber = cellnumber + 1

	print("email content: ")
	print(email_msg)

	#emailMessage(to_email, from_email, pwd_email, title, email_msg)

if __name__ == '__main__':
	main()
	#testSheet()


