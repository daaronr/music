#!/usr/bin/env python3
"""Validate the score data, add print footers, and build the delivery packet."""
from pathlib import Path
import xml.etree.ElementTree as ET
from fractions import Fraction
from io import BytesIO
import json, logging, re, zipfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from pypdf import PdfReader, PdfWriter
logging.getLogger('pypdf').setLevel(logging.ERROR)
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output';PDF=OUT/'pdf'
meta=json.loads((ROOT/'qa'/'composition_checks.json').read_text());changes=meta['changes']
# Compare actual imported MuseScore notes to XML, with sounding pitch corrected.
nat={'C':0,'D':2,'E':4,'F':5,'G':7,'A':9,'B':11}
checks=[]
for p in sorted((OUT/'musicxml').glob('*.musicxml')):
    tree=ET.parse(p);native=ET.parse(OUT/'musescore'/(p.stem+'.mscx'))
    parts=tree.findall('part'); staff=native.findall('./Score/Staff')
    assert len(parts)==len(staff)
    for part,msstaff in zip(parts,staff):
        trans=int(part.findtext('.//transpose/chromatic','0'));expected=[]
        for measure in part.findall('measure'):
            notes=measure.findall('note');assert sum(int(n.findtext('duration')) for n in notes)==48,(p,measure.attrib)
            for n in notes:
                pitch=n.find('pitch')
                if pitch is not None:expected.append(12*(int(pitch.findtext('octave'))+1)+nat[pitch.findtext('step')]+int(pitch.findtext('alter','0'))+trans)
            hs=measure.findall('harmony');index=(int(measure.attrib['number'])-1)%32
            if hs:
                assert len(hs)==len(changes[index])
                assert [int(h.findtext('offset','0')) for h in hs]==([0,24] if len(hs)==2 else [0])
        actual=[int(n.text) for n in msstaff.findall('.//Note/pitch')]
        assert expected==actual,(p.name,len(expected),len(actual))
    checks.append({'file':p.name,'parts':len(parts),'bars_per_part':len(parts[0].findall('measure')),'native_sounding_pitches_match':True,'durations_and_chord_offsets_valid':True})
for con,bb in [('01_head_concert','02_head_trumpet_Bb'),('04_trumpet_concert','05_trumpet_Bb')]:
    a=ET.parse(OUT/'musicxml'/(con+'.musicxml'));b=ET.parse(OUT/'musicxml'/(bb+'.musicxml'))
    def pitches(t):return [12*(int(x.findtext('octave'))+1)+nat[x.findtext('step')]+int(x.findtext('alter','0')) for x in t.findall('.//note/pitch')]
    assert all(y-x==2 for x,y in zip(pitches(a),pitches(b)))
# Quantify the actual counterpoint texture in eighth-note cells.
scores=ET.parse(OUT/'musicxml'/'03_duo_score_concert.musicxml').findall('part')
occupied=[]
for part in scores:
    cells=[]
    for m in part.findall('measure'):
        for n in m.findall('note'):cells.extend([n.find('pitch') is not None]*(int(n.findtext('duration'))//6))
    occupied.append(cells)
texture={name:sum(f(a,b) for a,b in zip(*occupied)) for name,f in [('both',lambda a,b:a and b),('trumpet_only',lambda a,b:a and not b),('guitar_only',lambda a,b:b and not a),('silence',lambda a,b:not a and not b)]}
# iReal cell/quality validation against its published custom URL specification.
raw=(OUT/'ireal'/'chart_source.txt').read_text().splitlines()[0]
body=raw.split('=',5)[5];body=re.sub(r'T44|\*[A-Z]|<[^>]*>','',body).strip('[')
ibars=body[:-1].split('|');assert len(ibars)==32
for i,b in enumerate(ibars):
    toks=re.findall(r'[A-G][#b]?(?:\^9#11|-7b5|-9|7alt|13#11|13|69)| ',b)
    assert len(toks)==4,(i,toks,b)
    assert len([x for x in toks if x!=' '])==len(changes[i])

labels={
'01_head_concert':'Head - concert pitch', '02_head_trumpet_Bb':'Head - trumpet in Bb',
'03_duo_score_concert':'Duo solo - concert score', '04_trumpet_concert':'Trumpet - concert pitch',
'05_trumpet_Bb':'Trumpet in Bb - written pitch','06_guitar_concert':'Guitar - sounding pitch'}
pagecounts={}
for stem,label in labels.items():
    p=PDF/(stem+'.pdf');reader=PdfReader(p);writer=PdfWriter();pagecounts[stem]=len(reader.pages)
    assert len(reader.pages)==(4 if stem.startswith('03') else 1 if stem.startswith(('01','02')) else 2)
    for i,page in enumerate(reader.pages):
        w=float(page.mediabox.width);h=float(page.mediabox.height);buf=BytesIO();c=canvas.Canvas(buf,pagesize=(w,h));c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#444444'))
        if stem.startswith('03'):suffix=f'Chorus {"I" if i<2 else "II"} - bars {16*i+1}-{16*(i+1)}'
        elif len(reader.pages)==2:suffix=f'Chorus {"I" if i==0 else "II"} - bars {32*i+1}-{32*(i+1)}'
        else:suffix='32 bars - swing - quarter = 164'
        c.drawString(28,16,f'Glass Meridian | {label} | {suffix}');c.drawRightString(w-28,16,f'{i+1} / {len(reader.pages)}');c.save();page.merge_page(PdfReader(buf).pages[0]);writer.add_page(page)
    writer.add_metadata({'/Title':f'Glass Meridian - {label}','/Author':'Codex / OpenAI','/Subject':'Original composition and composed counterpoint solo'});writer.write(p)

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Lead',fontName='Helvetica',fontSize=11,leading=16,spaceAfter=12))
styles.add(ParagraphStyle(name='SmallBody',fontName='Helvetica',fontSize=9.4,leading=13.6,spaceAfter=8))
styles['Title'].fontName='Helvetica-Bold';styles['Title'].fontSize=25
styles['Heading2'].fontName='Helvetica-Bold';styles['Heading2'].fontSize=12
story=[Paragraph('Glass Meridian',styles['Title']),Paragraph('Original post-bop tune and composed trumpet/guitar duo solo',styles['Lead'])]
def para(t):story.append(Paragraph(t,styles['SmallBody']))
def section(t):story.append(Paragraph(t,styles['Heading2']))
para('<b>F major centre | 4/4 | medium-up swing, quarter = 164 | 32 bars: A A2 B C.</b> Head once, duo for two choruses, then head out. End on the written F6/9 in bar 32. No extra turnaround or hidden repeat is needed.')
section('How to play it')
para('Keep the quarter-note pulse grounded and the eighths light. A modest swing ratio suits the quicker passages. Two chord symbols divide a bar at beat 3. The guitar solo is a single-note contrapuntal voice: do not add continuous comping beneath it. With bass and drums, let them hold the form; piano or extra chordal comping should be sparse. As a bare trumpet/guitar duo, the changes remain the harmonic reference but the texture will be more open.')
para('Take rests literally: they create handovers and breaths. Bring the indicated foreground voice forward without forcing the other into the background. The last four bars relax dynamically; keep time through the release. There are no quoted compositions or transcribed solos; the brief bebop gestures are generic vocabulary.')
section('The recurring idea')
para('The core cell is concert <b>A-C-G-B</b>: up a minor third, down a fourth, then up a major third. In the head it enters on the and of 1 and opens into D. It returns over different roots, in wider note values, and in broken exchanges. F and G major triads supply the bright F-Lydian colour; major-9/sharp-11 harmony and the E-major bridge broaden the tonal field without losing the swing form.')
section('What changes across the solo')
para('<b>Chorus I, bars 1-8:</b> trumpet quotes the cell; guitar answers a bar later and then takes over while trumpet rests. Bars 6-7 combine a rising trumpet with a descending guitar and a guitar withdrawal. <b>9-16:</b> guitar takes the F/G triad-pair run and later gives the motif a new home over C and A-flat; trumpet uses held tones and short replies. <b>17-24:</b> the E-major area opens up, the guitar briefly shifts a pentatonic fragment, and bars 21-22 divide the line into gaps and replies. <b>25-32:</b> the opening cell breaks apart and an altered-dominant descent resolves onto C over the final F chord.')
para('<b>Chorus II, bars 33-40:</b> the trumpet stretches the cell into 3+3+2 eighth-note spans while guitar runs F/G triad shapes underneath. <b>41-48:</b> guitar restates the head while trumpet rests or answers in slower values. <b>49-56:</b> a wider-register climax: trumpet pairs F-major-pentatonic and B-major-pentatonic fragments in bar 50 while guitar recalls the bridge melody. <b>57-64:</b> the guitar answers below the returning head; both lines settle to F/A and release together.')
section('Parts, pitch and range')
para('Each individual solo part has chorus I on page 1 and chorus II on page 2; their bar numbers continue 1-64. The combined concert score uses two pages per chorus. Trumpet PDFs and MusicXML are supplied both at concert pitch and transposed for B-flat, including the chord symbols. The guitar is deliberately shown at <b>sounding pitch</b>, with no conventional guitar octave displacement.')
para('<b>Concert ranges:</b> head D4-A5; trumpet solo C4-C6; guitar F3-F5 (middle C = C4). The trumpet has three brief concert-C6 peaks, written D6 in the B-flat part, at solo bars 20, 52 and 55. For a lower-register reading, take complete phrases 20-21 and 52-55 down an octave; the files retain the original line.')
section('Files and import')
para('The folder contains engraved PDFs, MusicXML, and native MuseScore .mscz files. Open the .mscz files for the checked layout; MusicXML is the portable editing copy. Open <b>output/ireal/import_glass_meridian.html</b> and use its import link, or use File &gt; Open in iReal Pro. Set iReal playback to jazz swing, tempo 164 and two choruses. The import preview was checked in iReal Pro; the tune was not added to the library.')
para('Checks: every measure totals four beats; both solo choruses use the same 32 changes; imported MuseScore sounding pitches match the source; B-flat notes are exactly a major second above concert notation; every iReal bar occupies four cells. Original music generated by Codex / OpenAI, 26 September 2026.')
SimpleDocTemplate(str(PDF/'07_performance_notes.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=34,bottomMargin=28).build(story)

# A clean rhythm-section chord chart, taken from the same harmonic source.
story=[Paragraph('Glass Meridian',styles['Title']),Paragraph('Concert chord chart | swing | quarter = 164 | 32 bars',styles['Lead'])]
for start,sectionname in [(0,'A'),(8,'A2'),(16,'B'),(24,'C')]:
    story.append(Paragraph(sectionname,styles['Heading2']))
    cells=[]
    for rowstart in range(start,start+8,4):
        cells.append([Paragraph(f'<font size="8" color="#666666">{i+1}</font><br/><b>'+(' &nbsp; / &nbsp; '.join(changes[i]).replace('maj9#11','maj9(#11)').replace('13#11','13(#11)'))+'</b>',styles['SmallBody']) for i in range(rowstart,rowstart+4)])
    t=Table(cells,colWidths=[127.5]*4,rowHeights=[61,61]);t.setStyle(TableStyle([('BOX',(0,0),(-1,-1),0.7,colors.black),('INNERGRID',(0,0),(-1,-1),0.5,colors.HexColor('#777777')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8)]));story.append(t);story.append(Spacer(1,6))
story.append(Spacer(1,10));story.append(Paragraph('A slash between two full chord symbols divides the bar at beat 3. Head in; two duo choruses; head out. F6/9 closes every pass. End on that chord after the out-head.',styles['SmallBody']))
SimpleDocTemplate(str(PDF/'08_chord_chart.pdf'),pagesize=A4,rightMargin=42,leftMargin=42,topMargin=34,bottomMargin=28).build(story)

packet=PdfWriter()
order=['07_performance_notes','01_head_concert','02_head_trumpet_Bb','03_duo_score_concert','04_trumpet_concert','05_trumpet_Bb','06_guitar_concert','08_chord_chart']
for stem in order:packet.append(str(PDF/(stem+'.pdf')),outline_item=stem[3:].replace('_',' '))
packet.add_metadata({'/Title':'Glass Meridian - Complete Performance Packet','/Author':'Codex / OpenAI'});packet.write(PDF/'00_complete_packet.pdf')
report={'score_checks':checks,'pdf_pages':pagecounts,'texture_eighth_note_cells':texture,'bb_transposition_verified':True,'ireal_32_bars_four_cells_each':True,'ireal_app_preview':'Verified all 32 bars in eight systems; import not committed to library','packet_pages':len(PdfReader(PDF/'00_complete_packet.pdf').pages)}
(ROOT/'qa'/'validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
