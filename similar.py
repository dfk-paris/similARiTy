import glob
import json
import re
from wand.image import Image

import lib

import pdb

class App:
  def run(self, config):
    print(config)

    if config['command'] == 'index':
      self.index(
        dirs=config['dir'],
        outfile=config['outfile'],
        algorithm=config['hash']
      )
    
    if config['command'] == 'compare':
      self.compare(
        a=config['a'],
        b=config['b'],
        outfile=config['outfile'],
        sample=config['sample'],
        distance=config['distance']
      )

    if config['command'] == 'show':
      self.show(config['files'])

  def index(self, dirs, outfile, algorithm):
    is_pic = re.compile('^.*\\.(png|gif|jpg|jpeg|tif|tiff|bmp)$', re.I)

    store = lib.PHashMetaStore()
    for d in dirs:
      for f in glob.iglob(d + '/**/*.*', recursive=True):
        if is_pic.match(f):
          print(f)
          image = Image(filename=f)
          h = store.phash_for(image, algorithm=algorithm)
          store.add(h, f)

    with open(outfile, 'w') as io:
      io.write(store.dump())

  def compare(self, a, b, outfile, sample, distance):
    store = lib.PHashMetaStore()
    with open(a) as io:
      store.load(io)

    results = []
    with open(b) as io:
      items = json.load(io)
      print('json files loaded')

      for i, phash in enumerate(items):
        files = items[phash]

        print('%d/%d (%d matches found)' % (i, len(items), len(results)))

        if sample != 0 and len(results) >= sample:
          break
        
        phash = int(phash)
        matches = store.find(phash, distance=distance)

        # filter duplicates
        matches = [m for m in matches if len(set(m['files']).intersection(files)) == 0]

        if len(matches) > 0:
          results.append({
            'paths': files,
            'candidates': matches
          })

      html = ""
      with open('tpl/index.phtml') as tpl:
        from bottle import template
        html = template(tpl.read(), results=results)

      with open(outfile, 'w') as out:
        print(html, file=out)

  def show(self, files):
    engine = lib.PHashStore()

    first_dhash = None;
    first_phash = None;

    for i in files:
      image = Image(filename=i)
      dhash = engine.phash_for(image, algorithm='dhash')
      image = Image(filename=i)
      phash = engine.phash_for(image, algorithm='phash')

      print(i)
      print('  dhash: %s' % dhash)
      print('  phash: %s' % phash)

      if first_dhash == None:
        first_dhash = dhash
        first_phash = phash
      else:
        print('  distance dhash (binary): %d' % engine.hamming2(
          format(first_dhash, '0129b'),
          format(dhash, '0129b'))
        )
        print('  distance phash (binary): %d' % engine.hamming2(
          format(first_phash, '065b'),
          format(phash, '065b'))
        )
