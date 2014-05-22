#!/usr/bin/python2

import numpy as np
import os
import hashlib
import gametools as gt

class Member:
    """
    A Mysticboards member. Has a main name, list of gt.Player objs for each game played
    """
    def __init__(self,name='',players=[]):
        self.name = name
        self.players = players

    def countwords(self,alignment='any',role='any'):
        rv = []
        for player in self.players:
            if alignment == 'any' and role == 'any':
                counts = player.countwords()
                rv = np.concatenate([rv,counts])
            elif alignment == player.alignment:
                if role == 'any':
                    counts = player.countwords()
                    rv = np.concatenate([rv,counts])
                elif role == player.role:
                    counts = player.countwords()
                    rv = np.concatenate([rv,counts])
        return rv

    def getposts(self,alignment='any'):
        rv = []
        for player in self.players:
            if alignment == 'any':
                rv.append(player.posts)
            elif alignment == player.alignment:
                rv.append(player.posts)
        return rv

class GameInfo:
    """
    Tools for reading multiple games
    """
    def __init__(self,members=[],games=[]):
        self.members = members
        self.games = games

    def initgameinfo(self,gamesdir='./games/'):
        self.readgames(gamesdir)
        self.setmembers()
        self.setgamesinfo()

    def readgames(self,dir='./games/'):
        for gamefile in os.listdir(dir):
            newgame = gt.Game(dir+gamefile)
            in_list = False
            for game in self.games:
                if newgame.name == game.name:
                    in_list = True
                    print('Game %s already in GameInfo.games' % (game.name))
            if not in_list:
                self.games.append(newgame)

    def setgamesinfo(self):
        for game in self.games:
            if not game.info_set:
                game.setinfo()

    def setmembers(self):
        for game in self.games:
            for player in game.players:
                phash = hashlib.md5(player.name).hexdigest()
                in_list = False
                for member in self.members:
                    if phash == member.name:
                        in_list = True
                        game_in_list = False
                        for pl in member.players:
                            if pl.gamename == game.name:
                                game_in_list = True
                        if not game_in_list:
                            member.players.append(player)
                if not in_list:
                    self.members.append(Member(phash,[player]))
