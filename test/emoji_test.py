#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv


filename1 = 'D:\\Code\\qzone_analyse\\example\\emotion\\emotion.csv'
filename2 = 'D:\\Code\\qzone_analyse\\example\\emotion\\emotion-sort.csv'
with open(filename1, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    a = list(reader)
    b = []
    for i in a:
        c = (i['code'], i['symbol'])
        b.append(c)
    d = sorted(b, key=lambda t: t[0])
with open(filename2, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['code', 'symbol'])
    for row in d:
        writer.writerow(row)

'''


strs = ['[em]e401181[/em]', '[em]e401203[/em]', '[em]e401210[/em]', '[em]e401287[/em]', '[em]e401298[/em]', '[em]e401329[/em]', '[em]e401328[/em]', '[em]e401398[/em]', '[em]e401385[/em]', '[em]e401691[/em]']

emojis = ['☺', '☝', '✌', '♨', '✈', '☁', '☀', '☎', '♣', '〽']


print(len(strs), len(emojis))

for i in range(len(strs)):
    print('%s,%s' % (strs[i], emojis[i]))
'''
'''
for i in emojis:
    print(i)
print(12121)
'''
