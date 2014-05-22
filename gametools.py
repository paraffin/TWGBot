#!/usr/bin/python2

from bs4 import BeautifulSoup as bs
import re
import os

class Game:
    """Game object. Reads game file, creates players and posts"""
    def __init__(self,filename):
        self.file = open(filename, 'r')
        self.name = filename.replace('.html','').replace('./games/','')
        self.savefile = './savegames/%s-playerinfo.txt' % (self.name)
        self.players = []
        self.info_set = False
        self.readposts()
    
    def setinfo(self):
        if os.path.isfile(self.savefile):
            self.readplayerinfo()
            self.info_set = True
        else:
            self.setplayerinfo()
            self.info_set = True
            self.writeplayerinfo()

    def readposts(self):
        all_lines = self.file.readlines()
        postheadertag = '<dt class="postheader">'
        for i in range(len(all_lines)):
            line = all_lines[i]
            if postheadertag in line:
                posterline = all_lines[i+2]
                regex = re.search('<strong>(.*)</strong> on',posterline)
                name = regex.groups()[0]
                text = all_lines[i+5]
                in_list = False
                for player in self.players:
                    if player.name == name:
                        in_list = True
                        player.posts.append(Post(text))
                        break
                if not in_list:
                    p = Post(text)
                    newp = Player(name,[p])
                    newp.gamename = self.name
                    self.players.append(newp)

    def setplayerinfo(self):
        print('Set info for game %s' % (self.name))
        plnames = self.getplayernames()
        for player in self.players:
            a = raw_input('Alignment of %s?\n>>> ' % (player.name))
            player.alignment = a
            a = raw_input('Role of %s?\n>>> ' % (player.name))
            player.role = a
            done = False
            for i in range(len(plnames)):
                print('%d: %s' % (i+1, plnames[i]))
            while not done:
                print('Enter number of teammate of %s, Enter when done' % (player.name))
                a = raw_input('>>> ')
                if a.isdigit():
                    if int(a) > 0 and int(a) < len(plnames):
                        player.teammates.append(plnames[int(a)-1])
                elif a == '':
                    done = True

    def writeplayerinfo(self):
        of = open(self.savefile,'w')
        for player in self.players:
            of.write(player.name + ',' + player.alignment + ',' + player.role)
            for mate in player.teammates:
                of.write(',' + mate)
            if not player == self.players[len(self.players)-1]:
                of.write('\n')
        of.close()

    def readplayerinfo(self):
        file = open(self.savefile,'r')
        for line in file:
            a = line.split(',')
            pname = a[0]
            found_player = False
            for player in self.players:
                if player.name == pname:
                    found_player = True
                    player.alignment = a[1]
                    player.role = a[2]
                    for mate in a[3:]:
                        player.teammates.append(mate)
            if not found_player:
                print('failed to find %s in game' % (pname))
        file.close()

    def getplayernames(self):
        rv = []
        for player in self.players:
            rv.append(player.name)
        return rv

    def getalignments(self):
        rv = []
        for player in self.players:
            al = self.alignment
            if al != '':
                in_list = False
                for str in rv:
                    if al == str:
                        in_list = True
                if not in_list:
                    rv.append(al)
        return rv

class Player:
    """Player object for a single game. Stores name, posts, alignment, etc"""
    def __init__(self,name='',posts=[],alignment='',role='',teammates=[],gamename=''):
        self.name = name
        self.posts = posts
        self.alignment = alignment
        self.role = role
        self.teammates = []
        self.gamename = gamename

    def countwords(self):
        """Return array of word counts"""
        rv = []
        for post in self.posts:
            post.resetsoup()
            post.stripquotes()
            rv.append(post.countwords())
            post.resetsoup()
        return rv


class Post:
    """Post object. Provides methods for reading posts. Stores text as single-line string"""
    def __init__(self,text=''):
        self.text = text
        self.soup = bs(text)

    def stripquotes(self):
        """strip quotes and tags from soup"""
        for str in self.soup.findAll('blockquote'):
            str.replaceWith('')
        for str in self.soup.findAll('div'):
            str.replaceWith('')

    def countwords(self):
        """return number of words in soup"""
        numwords = len(self.soup.text.split())
        return numwords

    def resetsoup(self):
        self.soup = bs(self.text)
