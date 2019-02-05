import argparse
import pdb

class Cmd:
  def run(self):
    parser = self.parser()
    return vars(parser.parse_args())

  def parser(self):
    r = argparse.ArgumentParser(description='similar - find similar images')
    sp = r.add_subparsers(help='sub-command to run', title="sub commands")

    p = sp.add_parser('index', help='index a given set of directories')
    p.set_defaults(command='index')
    p.add_argument('dir',
      type=str,
      nargs='+',
      help='directory to index'
    )
    p.add_argument('outfile',
      type=str,
      help='the output file to write to (json for index, html for compare)'
    )
    p.add_argument('--hash',
      type=str,
      choices=['dhash', 'phash'],
      default='dhash',
      nargs='?',
      help='the hashing algorithm to use'
    )
    
    p = sp.add_parser('compare', help='compare two previously indexed directories')
    p.set_defaults(command='compare')
    p.add_argument('a',
      type=str,
      help='the base json file'
    )
    p.add_argument('b',
      type=str,
      help='the second json file'
    )
    p.add_argument('outfile',
      type=str,
      help='the output (html) file to write to'
    )
    p.add_argument('--sample', '-s',
      type=int,
      default=0,
      help='only run the comparison until this many matches have been found'
    )
    p.add_argument('--distance',
      type=int,
      default=15,
      help='the max distance to consider a match'
    )

    p = sp.add_parser('show', help='show hashes for a set of files')
    p.set_defaults(command='show')
    p.add_argument('files',
      type=str,
      nargs='+',
      help='the base json file'
    )

    return r
