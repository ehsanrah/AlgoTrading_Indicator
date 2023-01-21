# -*- coding: utf-8 -*-
"""
Created on Sat Jan 21 14:56:07 2023

@author: ehsan
"""

from collections import deque

# region imports
from AlgorithmImports import *
# endregion

class UglyYellowGreenWhale(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2020, 1, 1)  # Set Start Date
        self.SetEndDate(2021,1,1)
        self.SetCash(100000)  # Set Strategy Cash
        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol

        #self.sma = self.SMA(self.spy, 30, Resolution.Daily) # resolution cant be less than what is in addEquity
        #closing_prices = self.History(self.spy, 30, Resolution.Daily)["close"]
        #for time, price in closing_prices.loc[self.spy].items():
        #    self.sma.Update(time,price)

        self.sma = CustomSimpleMovingeAverage("CustomSMA", 30)
        self.RegisterIndicator(self.spy, self.sma, Resolution.Daily)
    def OnData(self, data: Slice):
        if not self.sma.IsReady:
            return

        hist = self.History(self.spy, timedelta(365), Resolution.Daily)
        low = min(hist["low"])
        high = max(hist["high"])

        price = self.Securities[self.spy].Price

        if price * 1.05 >= high and self.sma.Current.Value < price:
            if not self.Portfolio[self.spy].IsLong:
                self.SetHoldings(self.spy, 1)
            
        elif price * 0.95 <= low and self.sma.Current.Value > price:
            if not self.Portfolio[self.spy].IsShort:
                self.SetHoldings(self.spy,-1)
        else:
            self.Liquidate()

        self.Plot("Benchmark", "52w-high",high)
        self.Plot("Benchmark", "52w-low",low)
        self.Plot("Benchmark", "SMA",self.sma.Current.Value)

class CustomSimpleMovingeAverage(PythonIndicator):
    def __init__(self, name, period):
        self.Name = name
        self.Time = datetime.min
        self.Value = 0
        self.queue = deque(maxlen=period)

    def Update(self, input):
        self.queue.appendleft(input.Close)
        self.Time = input.EndTime
        count = len(self.queue)
        self.Value = sum(self.queue) / count
        return(count == self.queue.maxlen)