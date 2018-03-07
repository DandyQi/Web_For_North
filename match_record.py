# -*- coding: utf-8 -*-
# @Author: DandyQi
# @Date:   2017-05-24 20:26:21
# @Last Modified by:   DandyQi
# @Last Modified time: 2018-01-31 17:41:20

import pandas as pd
import itertools
from itertools import combinations
import numpy as np


class MathcRecord:
    """docstring for ClassName"""

    def __init__(self, fname):
        ledger = pd.read_csv(fname)
        self.company_ledger = ledger.iloc[:, 0:4].dropna(axis=0, how='all')
        bank_ledger = ledger.iloc[:, 4:].dropna(axis=0, how='all')

        self.bank_ledger = bank_ledger.apply(self.seg, axis=1)
        del self.bank_ledger['银行借贷']
        del self.bank_ledger['银行金额']

        self.company_matched = []
        self.bank_matched = []

        self.output = open('output.txt', 'w', encoding='utf-8')

    def seg(self, x):
        if x['银行借贷'] == '借':
            x['银行借款'] = x['银行金额']
            x['银行贷款'] = 0
        else:
            x['银行借款'] = 0
            x['银行贷款'] = x['银行金额']
        return x

    def oneVone(self, comp, ban):
        comp = comp.astype(np.float64)
        ban = ban.astype(np.float64)
        for c_index, c_value in comp.iteritems():
            if c_value == 0:
                continue
            else:
                for b_index, b_value in ban.iteritems():
                    if (c_value == b_value) and (c_index not in self.company_matched) and (
                            b_index not in self.bank_matched):
                        self.company_matched.append(c_index)
                        self.bank_matched.append(b_index)
                        self.write_matched(c_index, b_index)

    def oneVone_self(self, borrow, loan, comp=True):
        borrow = borrow.astype(np.float64)
        loan = loan.astype(np.float64)
        if comp:
            for b_index, b_value in borrow.iteritems():
                if b_value == 0:
                    continue
                else:
                    for l_index, l_value in loan.iteritems():
                        if (b_value == l_value) and (b_index not in self.company_matched) and (
                                l_index not in self.company_matched):
                            self.company_matched.append(b_index)
                            self.company_matched.append(l_index)
                            self.write_matched_self(b_index, l_index, comp)
        else:
            for b_index, b_value in borrow.iteritems():
                if b_value == 0:
                    continue
                else:
                    for l_index, l_value in loan.iteritems():
                        if (b_value == l_value) and (b_index not in self.bank_matched) and (
                                l_index not in self.bank_matched):
                            self.bank_matched.append(b_index)
                            self.bank_matched.append(l_index)
                            self.write_matched_self(b_index, l_index, comp)

    def nVone(self, comp, ban):
        comp = comp.astype(np.float64)
        ban = ban.astype(np.float64)
        for c_index, c_value in comp.iteritems():
            flag = 0
            if c_value == 0:
                continue
            else:
                ban_cur = ban[ban <= c_value]
                ban_cur = ban_cur[ban_cur != 0]
                ban_cur_index = ban_cur.index
                for i in range(1, 5):
                    for j in combinations(ban_cur_index, i):
                        test = [item for item in j if item in self.bank_matched]
                        if ban_cur[list(j)].sum() == c_value and (c_index not in self.company_matched) and (
                                len(test) == 0):
                            self.write_matched_nVone(c_index, list(j), comp=True)
                            self.company_matched.append(c_index)
                            self.bank_matched.extend(list(j))
                            flag = 1
                            break
                    if flag:
                        break
        for b_index, b_value in ban.iteritems():
            if b_value == 0:
                continue
            else:
                comp_cur = comp[comp <= b_value]
                comp_cur = comp_cur[comp_cur != 0]
                comp_cur_index = comp_cur.index
                for i in range(1, 5):
                    for j in combinations(comp_cur_index, i):
                        test = [item for item in j if item in self.company_matched]
                        if comp_cur[list(j)].sum() == b_value and (b_index not in self.bank_matched) and (
                                len(test) == 0):
                            self.write_matched_nVone(list(j), b_index, comp=False)
                            self.company_matched.extend(list(j))
                            self.bank_matched.append(b_index)

    # def TwoVone(self, comp, ban):
    # 	comp = comp.astype(np.float64)
    # 	ban = ban.astype(np.float64)
    # 	for c_index, c_value in comp.iteritems():
    # 		if c_value == 0:
    # 			continue
    # 		else:
    # 			print(c_value)
    # 			ban_cur = ban[ban <= c_value]
    # 			ban_cur = ban_cur[ban_cur != 0]
    # 			ban_cur_index = list(ban_cur.index)

    # 			for index, value in enumerate(ban_cur):
    # 				answer = c_value - value
    # 				result = ban_cur.where(ban_cur == answer)
    # 				print(type(result))

    def write_matched(self, c_index, b_index):

        self.output.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
            self.company_ledger.loc[c_index]['企业账目'],
            self.company_ledger.loc[c_index]['企业借款'],
            self.company_ledger.loc[c_index]['企业贷款'],
            self.company_ledger.loc[c_index]['企业摘要'],
            self.bank_ledger.loc[b_index]['银行账目'],
            self.bank_ledger.loc[b_index]['银行借款'],
            self.bank_ledger.loc[b_index]['银行贷款'],
            self.bank_ledger.loc[b_index]['银行摘要']
        ))

    def write_matched_self(self, b_index, l_index, comp):
        if comp:

            self.output.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                self.company_ledger.loc[b_index]['企业账目'],
                self.company_ledger.loc[b_index]['企业借款'],
                self.company_ledger.loc[b_index]['企业贷款'],
                self.company_ledger.loc[b_index]['企业摘要'],
                self.company_ledger.loc[l_index]['企业账目'],
                self.company_ledger.loc[l_index]['企业借款'],
                self.company_ledger.loc[l_index]['企业贷款'],
                self.company_ledger.loc[l_index]['企业摘要']
            ))

        else:

            self.output.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                self.bank_ledger.loc[b_index]['银行账目'],
                self.bank_ledger.loc[b_index]['银行借款'],
                self.bank_ledger.loc[b_index]['银行贷款'],
                self.bank_ledger.loc[b_index]['银行摘要'],
                self.bank_ledger.loc[l_index]['银行账目'],
                self.bank_ledger.loc[l_index]['银行借款'],
                self.bank_ledger.loc[l_index]['银行贷款'],
                self.bank_ledger.loc[l_index]['银行摘要']
            ))

    def write_matched_nVone(self, c_indexs, b_indexs, comp):
        if comp:
            c_index = c_indexs
            for b_index in b_indexs:
                self.output.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                    self.company_ledger.loc[c_index]['企业账目'],
                    self.company_ledger.loc[c_index]['企业借款'],
                    self.company_ledger.loc[c_index]['企业贷款'],
                    self.company_ledger.loc[c_index]['企业摘要'],
                    self.bank_ledger.loc[b_index]['银行账目'],
                    self.bank_ledger.loc[b_index]['银行借款'],
                    self.bank_ledger.loc[b_index]['银行贷款'],
                    self.bank_ledger.loc[b_index]['银行摘要']
                ))
        else:
            b_index = b_indexs
            for c_index in c_indexs:
                self.output.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                    self.company_ledger.loc[c_index]['企业账目'],
                    self.company_ledger.loc[c_index]['企业借款'],
                    self.company_ledger.loc[c_index]['企业贷款'],
                    self.company_ledger.loc[c_index]['企业摘要'],
                    self.bank_ledger.loc[b_index]['银行账目'],
                    self.bank_ledger.loc[b_index]['银行借款'],
                    self.bank_ledger.loc[b_index]['银行贷款'],
                    self.bank_ledger.loc[b_index]['银行摘要']
                ))

    def write_unmatched(self):
        for item in self.company_ledger.iterrows():
            self.output.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                item[1]['企业账目'],
                item[1]['企业借款'],
                item[1]['企业贷款'],
                item[1]['企业摘要'],
                ' ',
                ' ',
                ' ',
                ' '
            ))

        for item in self.bank_ledger.iterrows():
            self.output.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' % (
                ' ',
                ' ',
                ' ',
                ' ',
                item[1]['银行账目'],
                item[1]['银行借款'],
                item[1]['银行贷款'],
                item[1]['银行摘要']
            ))

    def main(self):
        self.output.write('一对一匹配结果：\n')
        self.output.write('企业账目\t企业借款\t企业贷款\t企业摘要\t银行账目\t银行借款\t银行贷款\t银行摘要\n')
        self.oneVone(self.company_ledger['企业借款'], self.bank_ledger['银行贷款'])
        print('完成企业借款到银行贷款一对一匹配')
        self.oneVone(self.company_ledger['企业贷款'], self.bank_ledger['银行借款'])
        print('完成企业贷款到银行借款一对一匹配')
        self.company_ledger = self.company_ledger.drop(self.company_matched)
        self.bank_ledger = self.bank_ledger.drop(self.bank_matched)
        self.company_matched = []
        self.bank_matched = []

        self.output.write('自己与自己一对一匹配结果：\n')
        self.output.write('企业账目\t企业借款\t企业贷款\t企业摘要\t企业账目\t企业借款\t企业贷款\t企业摘要\n')
        self.oneVone_self(self.company_ledger['企业借款'], self.company_ledger['企业贷款'], comp=True)
        self.company_ledger = self.company_ledger.drop(self.company_matched)
        self.company_matched = []

        print('完成企业借款到企业贷款一对一匹配')

        self.output.write('银行账目\t银行借款\t银行贷款\t银行摘要\t银行账目\t银行借款\t银行贷款\t银行摘要\n')
        self.oneVone_self(self.bank_ledger['银行借款'], self.bank_ledger['银行贷款'], comp=False)
        self.bank_ledger = self.bank_ledger.drop(self.bank_matched)
        self.bank_matched = []

        print('完成银行借款到银行贷款一对一匹配')

        self.output.write('多对一匹配结果：\n')
        self.output.write('企业账目\t企业借款\t企业贷款\t企业摘要\t银行账目\t银行借款\t银行贷款\t银行摘要\n')

        self.nVone(self.company_ledger['企业借款'], self.bank_ledger['银行贷款'])
        print('完成企业借款到银行贷款多对一、一对多匹配')
        self.nVone(self.company_ledger['企业贷款'], self.bank_ledger['银行借款'])
        print('完成企业贷款到银行借款多对一、一对多匹配')
        self.company_ledger = self.company_ledger.drop(self.company_matched)
        self.bank_ledger = self.bank_ledger.drop(self.bank_matched)
        self.company_matched = []
        self.bank_matched = []

        self.output.write('未匹配结果：\n')
        self.output.write('企业账目\t企业借款\t企业贷款\t企业摘要\t银行账目\t银行借款\t银行贷款\t银行摘要\n')
        self.write_unmatched()


if __name__ == '__main__':
    MR = MathcRecord("input0131.csv")
    MR.main()
