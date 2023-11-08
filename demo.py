#!/usr/bin/env python3
import awpy
import json
import os.path
import sys

match os.path.splitext(sys.argv[1])[1]:
	case '.dem':
		demo = awpy.DemoParser(demofile=sys.argv[1], parse_chat=True).parse()
	case '.json':
		demo = json.load(open(sys.argv[1], encoding='utf-8'))
	case _:
		return 'usage: demo.py demofile.dem|demofile.json'

for c in demo['chatMessages']:
	if c['params']:
		print('[tick '+str(c['tick'])+'] '+c['params'][0]+': '+c['text'])
print()

me = 'ultraviewer'
wep = {}
h2h = {}
for r in demo['gameRounds']:
	if not r['isWarmup']:
		for k in r['kills']:
			if k['victimName'] == me:
				if k['attackerName'] not in h2h:
					h2h.update({str(k['attackerName']): [0,0]})
				h2h[str(k['attackerName'])][1] += 1
			if k['attackerName'] == me:
				if k['victimName'] not in h2h:
					h2h.update({k['victimName']: [0,0]})
				h2h[k['victimName']][0] += 1
				#
				if k['weapon'] not in wep:
					wep.update({k['weapon']: [0,0]})
				wep[k['weapon']][0] += 1
				if k['isHeadshot']:
					wep[k['weapon']][1] += 1
for w in wep:
	print(w + ':' + ' '*(18-len(w)-len(str(wep[w][0]))) + str(wep[w][0]), end='')
	print(' (' + str(wep[w][1]) + ', ' + str(round(wep[w][1]/wep[w][0]*100))+'%)')
print()
for h in h2h:
	print(h + ':' + ' '*(18-len(h)-len(str(h2h[h][0]))) + str(h2h[h][0]), end='')
	print('-' + str(h2h[h][1]) + ' (' + str(round(h2h[h][0]/(h2h[h][1]+h2h[h][0])*100)) + '%)')
print()

from awpy.analytics.stats import player_stats
s = player_stats(demo['gameRounds'], return_type='df')
s.insert(0, '+/-', s['kills']-s['deaths'])
s.insert(0, 'bt', round(s['blindTime'], 1))
s.insert(0, 'hsp', round(100*s['hs']/s['kills'], 1))
s.insert(0, 'kpr', round(s['kills']/s['totalRounds'], 2))
s.insert(0, '+2k', s['kills2']+s['kills3']+s['kills4']+s['kills5'])
s.insert(0, 'ud', round(s['utilityDamage'], 1))
filters = ['playerName', 'kills', 'deaths', '+/-', 'kdr', 'kpr']
filters += ['rating', 'adr', 'kast', '+2k', 'hsp', 'ud', 'bt']
print(s[filters].loc[s['isBot'] == False])
print()

for n, r in enumerate(demo['gameRounds']):
	if n == 15 or (n >= 30 and n%6 == 0):
		print('- ', end='')
	if not r['isWarmup']:
		kills = 0
		died = False
		for k in r['kills']:
			if k['attackerName'] == me:
				kills += 1
			if k['victimName'] == me:
				died = True
		print(str(kills), end='')
		if died:
			print('#', end='')
		print(' ', end='')
print()
