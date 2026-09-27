#!/usr/bin/env python3
"""Glass Meridian: original composition and explicitly composed two-voice solo.
One unit in the source is an eighth note. All source pitches are sounding.
Uses only the Python standard library to create MusicXML and iReal source.
"""
from pathlib import Path
from fractions import Fraction
import xml.etree.ElementTree as ET
import json, re, html
from urllib.parse import quote
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'
TITLE='Glass Meridian'
TEMPO=164
# Two symbols in one bar divide the measure at beat 3. No concealed repeats.
CHANGES=[
 ['Fmaj9#11'], ['Fmaj9#11'], ['Em7b5','A7alt'], ['Dm9'],
 ['Dbmaj9#11'], ['Cm9','F13'], ['Bbmaj9#11'], ['Gm9','C7alt'],
 ['Fmaj9#11'], ['Ebmaj9#11'], ['Dm9','G13#11'], ['Cmaj9#11'],
 ['Bm7b5','E7alt'], ['Am9'], ['Abmaj9#11'], ['Gm9','C7alt'],
 ['Emaj9#11'], ['Emaj9#11'], ['Gmaj9#11'], ['F#m7b5','B7alt'],
 ['Em9'], ['A13#11'], ['Dm9','G13#11'], ['Gm9','C7alt'],
 ['Fmaj9#11'], ['Ebmaj9#11'], ['Dm9','G13#11'], ['Dbmaj9#11','C7alt'],
 ['Fmaj9#11'], ['D7alt'], ['Gm9','C7alt'], ['F6/9']
]
# Signature cell: A-C-G-B (up minor third, down fourth, up major third).
HEAD='''
r:1 A4:1 C5:2 G4:1 B4:1 D5:2
C5:3 A4:1 G4:2 r:2
G4:1 Bb4:1 D5:2 C#5:1 Bb4:1 G4:1 F4:1
E4:1 F4:1 A4:2 C5:3 r:1
F4:1 Ab4:1 Eb5:2 G5:1 F5:1 Eb5:2
D5:1 Eb5:1 G5:2 A5:1 G5:1 Eb5:1 C5:1
D5:3 E5:1 F5:2 A4:2
Bb4:1 A4:1 G4:2 Db5:1 Eb5:1 E5:1 Bb4:1
r:1 A4:1 C5:2 G4:1 B4:1 D5:2
G4:1 Bb4:1 F5:2 A5:1 G5:1 F5:2
E5:1 F5:1 A5:2 B5:1 A5:1 F5:1 E5:1
D5:3 E5:1 F#5:2 r:2
D5:1 F5:1 A5:2 G#5:1 F5:1 D5:1 C5:1
B4:1 C5:1 E5:2 G5:3 r:1
C5:1 Eb5:1 Bb4:2 D5:1 F5:1 Eb5:2
D5:1 Bb4:1 A4:2 Ab4:1 Db5:1 C5:1 Bb4:1
G#4:3 B4:3 F#4:2
A#4:3 C#5:1 D#5:2 B4:2
B4:3 D5:3 A4:2
C5:1 E5:1 F#5:2 D#5:1 C5:1 A4:1 F#4:1
G4:2 B4:1 D5:1 F#5:2 E5:2
C#5:1 E5:1 B4:2 D#5:1 F#5:1 E5:2
F5:1 E5:1 D5:2 B4:1 A4:1 F4:1 E4:1
D4:1 G4:1 Bb4:2 Db5:1 Eb5:1 E5:1 G5:1
r:1 A5:1 C6:2 G5:1 B5:1 D6:2
Bb5:1 A5:1 G5:2 F5:2 r:2
E5:1 F5:1 A5:2 B5:1 A5:1 F5:1 E5:1
Eb5:1 F5:1 G5:2 Ab5:1 Gb5:1 Eb5:1 Db5:1
C5:3 A4:1 G4:1 B4:1 D5:2
F#5:1 Eb5:1 C5:2 Ab4:1 C5:1 Eb5:2
D5:1 Bb4:1 A4:2 Ab4:1 Db5:1 C5:1 Bb4:1
G4:1 A4:1 A4:4 r:2
'''
# Chorus I: statement, replies, mobile accompaniment, and a fragmented return.
T1='''
r:1 A4:1 C5:2 G4:1 B4:1 D5:2
C5:4 r:4
r:2 G4:1 Bb4:1 C#5:1 Bb4:1 G4:1 E4:1
F4:3 A4:1 C5:2 r:2
r:8
G4:2 Bb4:1 D5:1 Eb5:2 C5:2
A4:1 C5:1 E5:2 D5:3 r:1
r:2 Bb4:1 A4:1 Ab4:1 Gb4:1 Eb4:1 Db4:1
r:8
D5:4 C5:2 Bb4:2
A4:3 C5:1 B4:1 D5:1 E5:1 F5:1
E5:2 D5:2 B4:2 r:2
r:1 D5:1 F5:1 A5:1 G#5:1 F5:1 E5:1 D5:1
C5:3 E5:1 B4:2 r:2
r:8
A4:1 Bb4:1 D5:2 Db5:1 Eb5:1 E5:2
G#4:1 B4:1 F#4:2 A#4:1 C#5:1 B4:2
r:2 C#5:1 D#5:1 F#5:2 G#5:2
F#5:2 D5:1 B4:1 A4:2 r:2
r:2 A4:1 C5:1 D#5:1 F#5:1 A5:1 C6:1
B5:2 r:2 G5:2 r:2
r:1 F#5:1 r:1 E5:1 D#5:2 C#5:2
C5:1 A4:1 F4:2 B4:1 A4:1 F4:1 E4:1
D4:2 r:2 Db5:1 Eb5:1 E5:1 Bb4:1
r:1 A4:1 C5:2 r:1 G4:1 B4:2
D5:3 F5:1 A5:2 G5:2
F5:2 E5:1 D5:1 B4:2 A4:2
Ab4:2 G4:1 F4:1 E4:2 r:2
r:8
A4:1 C5:1 Eb5:2 F#5:3 r:1
F5:1 D5:1 Bb4:2 Ab4:1 Gb4:1 Eb4:1 Db4:1
C4:1 D4:1 F4:2 G4:1 A4:1 r:2
'''
G1='''
r:4 F3:2 G3:2
r:1 A3:1 C4:2 G3:1 B3:1 D4:2
D4:2 Bb3:2 G3:1 Bb3:1 C#4:1 E4:1
D4:2 E4:1 F4:1 A4:1 C5:1 E5:2
r:1 F4:1 Ab4:2 Eb4:1 G4:1 Bb4:2
G4:1 F4:1 Eb4:2 C4:1 A3:1 G3:2
F3:2 A3:1 C4:1 E4:1 G4:1 F4:2
D4:1 E4:1 F4:1 A4:1 Bb4:2 r:2
F4:1 A4:1 C5:1 G4:1 B4:1 D5:1 C5:2
Bb4:1 G4:1 F4:2 Eb4:1 D4:1 C4:2
F3:2 A3:1 C4:1 F4:2 E4:2
r:1 E4:1 G4:2 D4:1 F#4:1 A4:2
F4:2 D4:2 B3:2 r:2
r:2 A3:1 B3:1 C4:1 E4:1 G4:1 B4:1
C5:3 Eb5:1 Bb4:1 D5:1 F5:2
D5:1 C5:1 Bb4:2 G4:1 Gb4:1 E4:1 Db4:1
E4:2 D#4:2 C#4:1 B3:1 G#3:2
E4:1 F#4:1 G#4:1 B4:1 C5:1 D5:1 A4:1 G#4:1
B3:1 D4:1 A3:2 C#4:1 E4:1 F#4:2
E4:1 C4:1 A3:2 F#3:1 A3:1 C4:1 D#4:1
r:2 F#4:2 r:2 E4:2
C#4:1 r:1 B3:1 r:1 A3:1 B3:1 C#4:1 E4:1
D4:1 E4:1 F4:2 G4:1 A4:1 B4:1 D5:1
Bb4:1 A4:1 G4:2 Ab4:2 G4:2
E4:2 D4:2 C4:1 D4:1 E4:2
Bb3:1 D4:1 F4:2 C4:1 Eb4:1 G4:2
D4:1 F4:1 A4:2 G4:1 F4:1 E4:1 D4:1
Db4:1 Eb4:1 F4:1 G4:1 Bb4:1 Ab4:1 Gb4:1 E4:1
A3:1 C4:1 G3:2 B3:1 D4:1 E4:2
F#4:2 Eb4:1 C4:1 Ab3:2 r:2
G3:2 A3:1 Bb3:1 Db4:1 Eb4:1 E4:1 G4:1
A4:2 G4:2 E4:2 r:2
'''
# Chorus II: augmentation, exchange of foreground, three-eighth cells, climax,
# then the opening motif in contrary registers. Deliberate gaps remain audible.
T2='''
A4:3 C5:3 G4:2
B4:3 D5:1 C5:2 r:2
Bb4:1 G4:1 E4:2 C#5:1 Bb4:1 G4:1 E4:1
F4:2 r:2 A4:2 C5:2
Ab4:3 F4:3 Eb4:2
G4:1 Bb4:1 D5:2 Eb5:1 G5:1 A5:2
A5:2 F5:1 E5:1 D5:2 C5:2
Bb4:1 A4:1 G4:1 F4:1 E4:1 Gb4:1 Ab4:1 Bb4:1
r:8
G4:2 Bb4:2 F4:2 A4:2
F4:2 E4:2 D4:1 E4:1 F4:2
G4:2 B4:1 D5:1 F#5:2 E5:2
r:8
r:2 E5:1 G5:1 B5:2 A5:2
G5:1 Eb5:1 C5:2 D5:3 r:1
D5:1 F5:1 A5:2 Ab5:1 Gb5:1 Eb5:1 Db5:1
B4:1 F#5:1 G#5:1 D#5:1 A#5:1 B5:1 F#5:1 G#5:1
A5:1 G5:1 D5:1 C5:1 B4:1 C#5:1 D#5:1 F#5:1
G5:3 F#5:3 D5:2
C5:1 A4:1 F#4:2 D#5:1 F#5:1 A5:1 C6:1
B5:3 G5:1 F#5:2 E5:2
C#5:1 E5:1 G5:1 B5:1 Bb5:1 G5:1 F#5:1 D#5:1
F5:1 A5:1 C6:2 B5:1 A5:1 G5:1 F5:1
D5:1 F5:1 A5:2 Ab5:1 Gb5:1 Eb5:1 Db5:1
C5:2 r:2 A4:1 C5:1 G4:2
A4:1 C5:1 F5:2 D5:3 r:1
r:2 F4:1 A4:1 B4:2 D5:2
F5:1 Eb5:1 Db5:2 E5:1 Eb5:1 Db5:1 Bb4:1
A4:3 C5:1 G4:1 B4:1 D5:2
C5:2 Ab4:1 F#4:1 Eb4:2 r:2
r:2 A4:1 Bb4:1 Ab4:1 Gb4:1 Eb4:1 Db4:1
C4:1 D4:1 F4:2 A4:3 r:1
'''
G2='''
r:1 F3:1 A3:1 C4:1 G3:1 B3:1 D4:1 E4:1
F4:1 A4:1 C5:1 G4:1 B4:1 D5:1 C5:2
G4:2 D4:1 Bb3:1 G3:1 Bb3:1 C#4:1 E4:1
D4:1 E4:1 F4:1 A4:1 C5:2 r:2
r:1 F4:1 Ab4:2 Eb4:1 G4:1 Bb4:2
Bb4:2 G4:1 Eb4:1 C4:2 A3:2
D4:1 F4:1 A4:2 G4:1 E4:1 C4:2
Bb3:2 D4:2 E4:2 r:2
r:1 A4:1 C5:2 G4:1 B4:1 D5:2
Eb5:1 D5:1 Bb4:2 A4:1 F4:1 D4:2
r:1 A4:1 C5:1 E5:1 F5:1 E5:1 D5:1 B4:1
A4:1 G4:1 E4:2 D4:1 B3:1 G3:2
D4:1 F4:1 A4:1 C5:1 B4:1 G#4:1 F4:1 D4:1
C4:2 B3:2 A3:2 r:2
r:1 C4:1 Eb4:2 Bb3:1 D4:1 F4:2
F4:2 D4:1 Bb3:1 E4:2 G4:2
G#4:3 B4:3 F#4:2
A#4:3 C#5:1 D#5:2 B4:2
D5:1 B4:1 A4:1 F#4:1 E4:1 D4:1 B3:2
A3:1 C4:1 E4:2 F#4:1 D#4:1 C4:1 A3:1
G3:1 B3:1 D4:1 F#4:1 G4:1 A4:1 B4:1 D5:1
E5:1 C#5:1 B4:1 G4:1 F#4:1 E4:1 C#4:1 B3:1
A3:1 C4:1 E4:2 F4:1 G4:1 A4:1 B4:1
Bb4:3 A4:1 G4:2 E4:2
r:1 A3:1 C4:2 G3:1 B3:1 D4:2
Eb4:3 F4:1 A4:2 G4:2
F4:1 E4:1 D4:2 B3:1 D4:1 F4:2
Ab4:2 G4:1 F4:1 E4:2 r:2
E4:2 D4:2 C4:1 D4:1 E4:2
F#4:1 Eb4:1 C4:2 Ab3:1 C4:1 Eb4:2
D4:1 Bb3:1 A3:2 Ab3:1 Db4:1 C4:1 Bb3:1
A3:1 C4:1 D4:2 F4:3 r:1
'''

def parse(text):
    bars=[]
    for line in text.strip().splitlines():
        events=[]
        for token in line.split():
            pitch,d=token.split(':'); events.append((pitch,Fraction(d)))
        assert sum(d for p,d in events)==8,(len(bars)+1,line)
        bars.append(events)
    assert len(bars)==32,len(bars)
    return bars
H,TP,GT=parse(HEAD),parse(T1)+parse(T2),parse(G1)+parse(G2)
# Lower the high reprise of the head by an octave: preserve a playable melodic
# ceiling of concert A5 while leaving the duo's single C6 peaks for drama.
for i in [10,24,25,26]:
    H[i]=[(re.sub(r'([4-6])$',lambda m:str(int(m[1])-1),p) if p!='r' else p,d) for p,d in H[i]]

# Both players withdraw at planned handovers.
for i in [2,13,18,29,39,43,51]:
    GT[i]=[('r',Fraction(8))]
GT[6]=[('r',Fraction(4)),('F4',Fraction(2)),('r',Fraction(2))]
GT[35]=[('r',Fraction(4)),('C5',Fraction(2)),('r',Fraction(2))]

NAT={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
LETTERS='CDEFGAB'
def pitchparts(p):
    m=re.fullmatch(r'([A-G])([#b]*)(\d)',p); assert m,p
    l,a,o=m.groups(); return l,a.count('#')-a.count('b'),int(o)
def midi(p):
    l,a,o=pitchparts(p); return (o+1)*12+NAT[l]+a
def transpose(p,steps=1,semitones=2):
    l,a,o=pitchparts(p); ix=LETTERS.index(l)+steps
    nl=LETTERS[ix%7]; no=o+ix//7
    alt=midi(p)+semitones-((no+1)*12+NAT[nl])
    return nl+('#'*max(0,alt))+('b'*max(0,-alt))+str(no)
def trchord(s):
    m=re.match(r'([A-G][#b]?)(.*)',s); return transpose(m[1]+'4')[:-1]+m[2]
def sub(parent,tag,content=None,**attrs):
    x=ET.SubElement(parent,tag,{k:str(v) for k,v in attrs.items()})
    if content is not None:x.text=str(content)
    return x

def harmony(m,chord,offset):
    root,qual=re.match(r'([A-G][#b]?)(.*)',chord).groups()
    h=sub(m,'harmony',**{'placement':'above'})
    r=sub(h,'root'); sub(r,'root-step',root[0]);
    if len(root)>1:sub(r,'root-alter',1 if root[1]=='#' else -1)
    kinds={'maj9#11':('major-ninth','maj9(#11)'), 'm7b5':('half-diminished','m7b5'),
      '7alt':('other','7alt'),'m9':('minor-ninth','m9'), '13':('dominant-13th','13'),
      '13#11':('dominant-13th','13(#11)'), '6/9':('major-sixth','6/9')}
    k,display=kinds[qual]; sub(h,'kind',k,text=display,**{'use-symbols':'no'})
    if qual in ['maj9#11','13#11']:
        d=sub(h,'degree');sub(d,'degree-value',11);sub(d,'degree-alter',1);sub(d,'degree-type','add')
    if qual=='6/9':
        d=sub(h,'degree');sub(d,'degree-value',9);sub(d,'degree-alter',0);sub(d,'degree-type','add')
    if offset:sub(h,'offset',int(offset*6))

# Avoid naming techniques on performance parts; short cues describe interaction.
T_CUES={0:'I - let the answer in',8:'Guitar forward',16:'Open the colour',20:'Trade the gaps',24:'Fragments of the head',32:'II - longer arcs',40:'Guitar leads',48:'Build; keep the swing',56:'Let the head return',60:'Ease back'}
G_CUES={0:'Single-note counterline; leave air',8:'Bring out the theme',16:'Light and mobile',20:'Answer the gaps',32:'Under the long line',40:'Take the foreground',48:'Head motif, broadened',56:'Echo, then release'}

def direction(m,words=None,dynamic=None,met=False,rehearsal=None):
    d=sub(m,'direction',placement='above' if not dynamic else 'below');dt=sub(d,'direction-type')
    if words:sub(dt,'words',words,**{'font-size':'9'})
    if rehearsal:sub(dt,'rehearsal',rehearsal)
    if dynamic:sub(sub(dt,'dynamics'),dynamic)
    if met:
        metronome=sub(dt,'metronome');sub(metronome,'beat-unit','quarter');sub(metronome,'per-minute',TEMPO);sub(d,'sound',tempo=TEMPO)
    return d

def build(name,title,subtitle,parts,bb=False,duo=False):
    score=ET.Element('score-partwise',version='3.1')
    w=sub(score,'work');sub(w,'work-title',title)
    sub(score,'movement-title',title)
    ident=sub(score,'identification');sub(ident,'creator','Original music - Codex / OpenAI',type='composer')
    enc=sub(ident,'encoding');sub(enc,'software','Glass Meridian source generator');sub(enc,'encoding-date','2026-09-26')
    defaults=sub(score,'defaults');sc=sub(defaults,'scaling');sub(sc,'millimeters',7);sub(sc,'tenths',40)
    pl=sub(defaults,'page-layout');sub(pl,'page-height',1697.14);sub(pl,'page-width',1200)
    pm=sub(pl,'page-margins',type='both')
    for tag,value in [('left-margin',68),('right-margin',68),('top-margin',55),('bottom-margin',55)]:sub(pm,tag,value)
    cred=sub(score,'credit',page='1');sub(cred,'credit-type','title');sub(cred,'credit-words',title,**{'default-x':'600','default-y':'1640','justify':'center','valign':'top','font-size':'20'})
    cred=sub(score,'credit',page='1');sub(cred,'credit-type','subtitle');sub(cred,'credit-words',subtitle,**{'default-x':'600','default-y':'1597','justify':'center','valign':'top','font-size':'10'})
    plist=sub(score,'part-list')
    for ix,(label,bars,program) in enumerate(parts):
        sp=sub(plist,'score-part',id=f'P{ix+1}');sub(sp,'part-name',label);sub(sp,'part-abbreviation','Tpt.' if program==57 else 'Gtr.')
        si=sub(sp,'score-instrument',id=f'I{ix+1}');sub(si,'instrument-name',label)
        mi=sub(sp,'midi-instrument',id=f'I{ix+1}');sub(mi,'midi-channel',ix+1);sub(mi,'midi-program',program)
    for ix,(label,bars,program) in enumerate(parts):
        part=sub(score,'part',id=f'P{ix+1}')
        for i,events in enumerate(bars):
            m=sub(part,'measure',number=i+1,width='260')
            newpage=i>0 and i%(16 if duo else 32)==0
            newsys=i%4==0 or (duo and i in [50,54])
            if newsys:
                pr=sub(m,'print',**({'new-page':'yes'} if newpage else {'new-system':'yes'} if i else {}))
                sl=sub(pr,'system-layout'); sm=sub(sl,'system-margins');sub(sm,'left-margin',0);sub(sm,'right-margin',0)
                sub(sl,'top-system-distance' if i==0 or newpage else 'system-distance',80 if i==0 else 75 if duo else 90)
            if i==0:
                a=sub(m,'attributes');sub(a,'divisions',12);key=sub(a,'key');sub(key,'fifths',1 if bb else -1)
                ti=sub(a,'time');sub(ti,'beats',4);sub(ti,'beat-type',4)
                cl=sub(a,'clef');sub(cl,'sign','G');sub(cl,'line',2)
                if bb:
                    tr=sub(a,'transpose');sub(tr,'diatonic',-1);sub(tr,'chromatic',-2)
                if ix==0: direction(m,words='Medium-up swing - light eighths; two chords = two beats each');direction(m,met=True)
                direction(m,dynamic='mp' if len(bars)>32 else 'mf')
            if ix==0 and i%8==0:
                sec=['A','A2','B','C'][(i%32)//8]
                if len(bars)>32:sec=f'{"I" if i<32 else "II"} / {sec}'
                direction(m,rehearsal=sec)
            if len(bars)>32:
                cues=T_CUES if program==57 else G_CUES
                if i in cues:direction(m,words=cues[i])
                if i in [32,48,56,60]:direction(m,dynamic={32:'mf',48:'f',56:'mf',60:'mp'}[i])
            if ix==0 or not duo:
                changes=CHANGES[i%32]
                for ci,c in enumerate(changes):harmony(m,trchord(c) if bb else c,4*ci if len(changes)==2 else 0)
            pos=Fraction(0)
            # Beam contiguous eighths by beat, never across a rest.
            for ni,(p,dur) in enumerate(events):
                note=sub(m,'note')
                if p=='r':
                    sub(note,'rest',**({'measure':'yes'} if dur==8 else {}))
                else:
                    pp=transpose(p) if bb else p;l,alt,octv=pitchparts(pp)
                    pitch=sub(note,'pitch');sub(pitch,'step',l)
                    if alt:sub(pitch,'alter',alt)
                    sub(pitch,'octave',octv)
                sub(note,'duration',int(dur*6))
                dtypes={Fraction(1):('eighth',0),Fraction(2):('quarter',0),Fraction(3):('quarter',1),Fraction(4):('half',0),Fraction(6):('half',1),Fraction(8):('whole',0)}
                typ,dots=dtypes[dur]
                if dur!=8 or p!='r':sub(note,'type',typ)
                if dots:sub(note,'dot')
                if p!='r':
                    sub(note,'stem','up' if midi(pp if bb else p)<71 else 'down')
                    if dur==1:
                        prev=ni>0 and events[ni-1][1]==1 and events[ni-1][0]!='r' and int((pos-1)//2)==int(pos//2)
                        nxt=ni+1<len(events) and events[ni+1][1]==1 and events[ni+1][0]!='r' and int((pos+1)//2)==int(pos//2)
                        if prev or nxt:sub(note,'beam','continue' if prev and nxt else 'end' if prev else 'begin',number='1')
                    if i in ([0,8,24] if len(bars)==32 else [0,24,32,40,48,56,60]) and ni==1 and dur<=2:
                        art=sub(sub(note,'notations'),'articulations');sub(art,'accent')
                pos+=dur
            if (i+1)%8==0:
                bl=sub(m,'barline',location='right');sub(bl,'bar-style','light-heavy' if i==len(bars)-1 else 'light-light')
    ET.indent(score,space='  ')
    path=OUT/'musicxml'/f'{name}.musicxml'
    path.write_bytes(b'<?xml version="1.0" encoding="utf-8"?>\n<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.1 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n'+ET.tostring(score,encoding='utf-8'))
    return path

specs=[
('01_head_concert','Glass Meridian','Head | concert pitch | 32 bars - A A2 B C', [('Melody',H,57)],False,False),
('02_head_trumpet_Bb','Glass Meridian','Head | trumpet in B-flat | written pitch and transposed chords', [('Trumpet in Bb',H,57)],True,False),
('03_duo_score_concert','Glass Meridian - Duo Solo','Two choruses | concert score | guitar at sounding pitch', [('Trumpet',TP,57),('Guitar',GT,27)],False,True),
('04_trumpet_concert','Glass Meridian - Trumpet','Two choruses | concert pitch | chorus I p.1 - chorus II p.2', [('Trumpet (concert)',TP,57)],False,False),
('05_trumpet_Bb','Glass Meridian - Trumpet in Bb','Two choruses | written pitch and chords | chorus I p.1 - chorus II p.2', [('Trumpet in Bb',TP,57)],True,False),
('06_guitar_concert','Glass Meridian - Guitar','Two choruses | sounding pitch (no octave transposition) | I p.1 - II p.2', [('Guitar (sounding)',GT,27)],False,False)
]
paths=[build(*s) for s in specs]
# Native style: preserve manual system/page breaks and maintain readable spacing.
(ROOT/'source'/'engraving.mss').write_text('''<?xml version="1.0" encoding="UTF-8"?>
<museScore version="3.02"><Style>
<pageWidth>8.26772</pageWidth><pageHeight>11.6929</pageHeight>
<pagePrintableWidth>7.32772</pagePrintableWidth>
<pageEvenLeftMargin>0.47</pageEvenLeftMargin><pageOddLeftMargin>0.47</pageOddLeftMargin>
<pageEvenTopMargin>0.4</pageEvenTopMargin><pageOddTopMargin>0.4</pageOddTopMargin>
<pageEvenBottomMargin>0.4</pageEvenBottomMargin><pageOddBottomMargin>0.4</pageOddBottomMargin>
<Spatium>1.65</Spatium><minSystemDistance>9</minSystemDistance><maxSystemDistance>13</maxSystemDistance>
<staffDistance>7</staffDistance><enableVerticalSpread>1</enableVerticalSpread>
<minMeasureWidth>5</minMeasureWidth><measureSpacing>1.0</measureSpacing>
<showMeasureNumber>1</showMeasureNumber><measureNumberSystem>1</measureNumberSystem>
<showPageNumber>0</showPageNumber><showHeader>0</showHeader><showFooter>0</showFooter><chordSymbolAFontSize>10</chordSymbolAFontSize>
<concertPitch>0</concertPitch><createMultiMeasureRests>0</createMultiMeasureRests>
<swingRatio>60</swingRatio><swingUnit>240</swingUnit>
</Style></museScore>''')
(ROOT/'source'/'engraving_duo.mss').write_text((ROOT/'source'/'engraving.mss').read_text().replace('<Spatium>1.65</Spatium>','<Spatium>1.48</Spatium>').replace('<measureSpacing>1.0</measureSpacing>','<measureSpacing>0.85</measureSpacing>').replace('<chordSymbolAFontSize>10</chordSymbolAFontSize>','<chordSymbolAFontSize>9.5</chordSymbolAFontSize>'))
jobs=[]
for p in paths:
    jobs.append({'in':str(p),'out':[str(OUT/'pdf'/f'{p.stem}.pdf'),str(OUT/'musescore'/f'{p.stem}.mscz'),str(OUT/'musescore'/f'{p.stem}.mscx')]})
(ROOT/'source'/'export_jobs.json').write_text(json.dumps(jobs,indent=2))

def irealch(c):return c.replace('maj9#11','^9#11').replace('m7b5','-7b5').replace('m9','-9').replace('6/9','69')
chart='T44*A['
for i,chords in enumerate(CHANGES):
    if i and i%8==0:chart+='*'+['A','A','B','C'][i//8]
    if i==8:chart+='<A2>'
    # Exactly four cells per bar; spaces occupy cells, punctuation does not.
    if len(chords)==1:chart+=irealch(chords[0])+'   '
    else:chart+=irealch(chords[0])+' '+irealch(chords[1])+' '
    chart+=('Z' if i==31 else '|')
raw=f'{TITLE}=Codex=Medium Up Swing=F=n={chart}'
uri='irealbook://'+quote(raw,safe='')
(OUT/'ireal'/'glass_meridian.irealbook').write_text(uri+'\n')
(OUT/'ireal'/'chart_source.txt').write_text(raw+'\n\n'+ '\n'.join(' | '.join(' / '.join(x) for x in CHANGES[i:i+4]) for i in range(0,32,4))+'\n')
rows=''.join('<tr>'+''.join(f'<td><small>{j+1}</small><br>{html.escape("  /  ".join(CHANGES[j]))}</td>' for j in range(i,i+4))+'</tr>' for i in range(0,32,4))
(OUT/'ireal'/'import_glass_meridian.html').write_text(f'''<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Glass Meridian - iReal Pro</title><style>body{{font:18px system-ui;max-width:900px;margin:40px auto;padding:20px;color:#172438}}a{{display:inline-block;padding:14px;background:#e4effa}}table{{border-collapse:collapse;width:100%;margin-top:24px}}td{{border:1px solid #aaa;padding:12px;width:25%}}small{{color:#666}}@media print{{a{{display:none}}}}</style><h1>Glass Meridian</h1><p>32 bars · F · swing · quarter = 164 · A A2 B C</p><a href="{uri}">Import chart into iReal Pro</a><p>Set playback to a jazz swing style, tempo 164, and two choruses for the written duo. Each two-chord bar changes on beat 3. Chart is in concert pitch.</p><table>{rows}</table><p>Head once; duo twice around the same 32 bars; head out. Last bar is F6/9 on every pass. End on that chord after the out-head; no extra bar is required.</p></html>''')
summary={'title':TITLE,'tempo':TEMPO,'form':'32 bars: A A2 B C, 8 each','head_bars':len(H),'solo_bars':len(TP),'ranges':{k:[min(midi(p) for b in a for p,d in b if p!='r'),max(midi(p) for b in a for p,d in b if p!='r')] for k,a in [('head',H),('trumpet',TP),('guitar',GT)]},'all_bars_duration_quarters':4,'changes':CHANGES}
(ROOT/'qa'/'composition_checks.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
