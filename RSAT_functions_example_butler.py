# -*- coding: utf-8 -*-
"""
Created on Mon Sep 25 19:57:35 2023

@author: HMEUW
"""

import time
import itertools
import math
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as pltb
import numpy as np
import os
import pandas as pd
import string
import tkinter as tk

########################### FUNCTIONS ###############################
class Slugtest:

    def normalize_df(self):
        """
        Normalizes a DataFrame. Assumes DataFrame has the recovery of a rising head test.
        Head observations are relative to a recovered groundwater level, i.e.:
            last observation is close to 0
            all observations have a positive sign
        Input like table 6.2 in book Butler
        """
        # base level, used to calculate H_0, the drop during test
        self.h_base = self.df_ts.iloc[-1].obs_head
        # minimum head
        self.h_start = self.df_ts.obs_head.max()
        # H_0
        self.H0 = np.abs(self.h_base - self.h_start)

        # nomalize data
        self.df_ts['head_norm'] = self.df_ts.obs_head / self.H0
        # drop 0 rows, gives error in log
        self.df_ts.drop(
            self.df_ts.loc[self.df_ts.head_norm == 0].index,
            inplace=True)

        self.df_ts['head_norm_ln'] = self.df_ts.head_norm.map(lambda a: math.log(a))

    def linear_regression(self):
        # create dataframe with period for regression analysis
        if (self.h_norm_min is not None) & (self.h_norm_max is not None):
            # slice data
            self.df_ts_linreg = self.df_ts.loc[
                (self.df_ts.head_norm >= self.h_norm_min) &
                (self.df_ts.head_norm <= self.h_norm_max)
                ].copy()
        else:
            self.df_ts_linreg = self.df_ts.copy()

        if len(self.df_ts_linreg) == 0:
            print('no data for linear regression')
            return

        # save regression parameters
        self.t_min = self.df_ts_linreg.index[0]
        self.t_max: self.df_ts_linreg.index[-1]

        # fit on data
        self.LinRegCoef = np.polyfit(self.df_ts_linreg.index,
                                     self.df_ts_linreg.head_norm_ln,
                                     1
                                     )

        # get charateristics
        self.H01 = math.exp(self.LinRegCoef[1]) * self.H0
        self.T01 = (-1-self.LinRegCoef[1])/self.LinRegCoef[0]
        self.corr_coef = np.corrcoef(self.df_ts_linreg.index,
                                     self.df_ts_linreg.head_norm_ln)[0, 1]

        # create dataframe with fitted data
        x_fit = np.array(range(int(self.df_ts_linreg.index[0]),
                               int(self.df_ts_linreg.index[-1])+1
                               )
                         )

        self.df_fit = pd.DataFrame(
            [x_fit,
             np.exp(x_fit*self.LinRegCoef[0] + self.LinRegCoef[1]),
             ],
            index=['time_s', 'h_norm_fit']
            ).transpose().set_index('time_s')

    def KhBouwerRice_PP(self):
        """Bouwer-Rice calculations for unconfined aquifer, partially penetrating well
        The method is documented in Butler, 2019, The Design, Performance, and Analysis
        of Slug Tests. References to equations for each variable in comments below."""

        # rw_as is defined in equation 6.2
        self.rw_as = self.rw*math.sqrt(self.Aniso)

        self.coeff = math.log(
            (self.AqThick - (self.d + self.Le)) / self.rw_as
            )
        if self.coeff > 6:
            # check is described below equation 6.4a
            self.coeff = 6

        # A is defined in equation 6.5a
        self.A = 1.4720 + \
            3.537e-2 * (self.Le / self.rw_as) - \
            8.148e-5 * (self.Le / self.rw_as)**2 + \
            1.028e-7 * (self.Le / self.rw_as)**3 - \
            6.484e-11 * (self.Le / self.rw_as)**4 + \
            1.573e-14 * (self.Le / self.rw_as)**5
        # B is given as equation 6.5b
        # in Butler, 2019, The Design, Performance, and Analysis of Slug Tests
        self.B = 0.2372 + \
            5.151e-3 * (self.Le / self.rw_as) - \
            2.682e-6 * (self.Le / self.rw_as)**2 - \
            3.491e-10 * (self.Le / self.rw_as)**3 + \
            4.738e-13 * (self.Le / self.rw_as)**4

        # equation 6.4a
        self.logterm_BR_PP = (1.1 / math.log((self.d+self.Le) / self.rw_as) +
            ((self.A + (self.B * self.coeff)) / (self.Le / self.rw_as)))**(-1)

        # equation 6.3
        self.Kh_BR_PP = round((self.rc**2 * self.logterm_BR_PP) / (2*self.Le * self.T01),
                              5)  # rounding off to five decimals