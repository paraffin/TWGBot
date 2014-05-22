#!/usr/bin/python2

from bs4 import BeautifulSoup as bs
import numpy as np
import matplotlib.pyplot as plt
import re


class bot:
    def __init__(self):
        self.player_list = []
        self.games = []

    def readposts(self,filename):
        gamefile = open(filename, 'r')
        all_lines = gamefile.readlines()
        thisgame = { 'name': filename }
        self.games.append(thisgame)

        postheadertag = '<dt class="postheader">'

        for i in range(len(all_lines)):
            line = all_lines[i]
            if postheadertag in line:
                posterline = all_lines[i+2]
                regex = re.search('<strong>(.*)</strong> on',posterline)
                name = regex.groups()[0]
                post = all_lines[i+5]
                in_list = False
                for player in self.player_list:
                    if player['name'] == name:
                        in_list = True
                        player['posts'].append(post)
                        break
                if not in_list:
                    self.player_list.append({'name': name, 'posts': [post] })
    

    def countwords(self):
        for player in self.player_list:
            if 'wcts' not in player:
                player['wcts'] = []
            for post in player['posts']:
                soup = bs(post)
                bot.stripquotes(soup)
                numwords = len(soup.text.split())
                player['wcts'].append(numwords)

    @staticmethod
    def stripquotes(soup):
        for str in soup.findAll('blockquote'):
            str.replaceWith('')
        for str in soup.findAll('div'):
            str.replaceWith('')

    @staticmethod
    def plot_wcts(player):
        logcts = np.log10(player['wcts'])
        logcts = logcts[np.isfinite(logcts)]
        plt.cla()
        plt.hist(logcts)
        plt.title(player['name'])
        plt.draw()
        plt.show()

    def make_plots(self):
        for player in self.player_list:
            bot.plot_wcts(player)

class game:
    def __init__(self,players=[],winningteam=''):
        self.players = players
        self.winningteam = winningteam
