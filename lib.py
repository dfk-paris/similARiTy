import json
import numpy as np
import pybktree
import scipy.fftpack as fft

class PHashStore:
  tree = pybktree.BKTree(pybktree.hamming_distance, [])

  def add(self, phash):
    if not self.exists(phash):
      self.tree.add(phash)

  def find(self, phash, distance=15):
    return self.tree.find(phash, distance)

  def exists(self, phash):
    return len(self.find(phash, 0)) > 0

  def load(self, io):
    data = json.load(io)
    for r in data:
      self.add(r)

  def dump(self):
    return json.dumps(sorted(self.tree))

  def phash_for(self, image, algorithm='dhash'):
    if algorithm == 'phash':
      return self.phash(image)
    else:
      return self.dhash(image)

  def phash(self, image):
    r = self.__ndarray_for(image, size="32x32!").astype(np.float64)
    h = fft.dctn(r, norm="ortho")[0:8,0:8]
    avg = np.average(h.reshape(64,)[1:])
    mask = (h <= avg)
    h = mask.reshape(64,).dot(2**np.arange(mask.size)[::-1])
    return int(h)

  def dhash(self, image):
    r = self.__ndarray_for(image)

    h = 0
    try:
      for i in range(1, 9):
        for j in range(1, 9):
          h = h << 1 | (1 if r[i][j] >= r[i][j - 1] else 0)
      for i in range(1, 9):
        for j in range(1, 9):
          h = h << 1 | (1 if r[j][i] >= r[j - 1][i] else 0)
      return h
    except IndexError as e:
      pdb.set_trace()
      return -1
    except ValueError as e:
      pdb.set_trace()
      return -2


  def __ndarray_for(self, image, size="9x9!"):
    image.alpha_channel = False
    image.format = 'gray'
    image.type = 'grayscale'
    image.depth = 8
    image.transform(resize=size)
    result = np.asarray(bytearray(image.make_blob()), dtype=np.uint8).reshape(image.size)
    image.close()
    return result

  def hamming2(self, s1, s2):
    assert len(s1) == len(s2)
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


class PHashMetaStore(PHashStore):
  files = {}

  def add(self, phash, meta):
    if not self.exists(phash):
      self.files[phash] = []
      super().add(phash)
    self.files[phash].append(meta)

  def find(self, phash, distance=15):
    results = self.tree.find(phash, distance)
    return [self.__to_result(x) for x in results]

  def load(self, io):
    data = json.load(io)
    for phash, files in data.items():
      phash = int(phash)
      if not self.exists(phash):
        super().add(phash)
        self.files[phash] = []
      for f in files:
        if not f in self.files[phash]:
          self.files[phash].append(f)

  def dump(self):
    return json.dumps(self.files)

  def __to_result(self, x):
    return {
      'distance': x[0],
      'phash': x[1],
      'files': self.files[x[1]]
    }

class PHashServer:
  def __init__(self, host='localhost', port=8001):
    self.host = host
    self.port = port

  def start(self):
    from bottle import get, post, request, route, run
    self.store = PHashStore()

    @post('/load')
    def load():
      # pdb.set_trace()
      io = request.body
      self.store.load(io)
      return self.__render_json({'message': 'ok'})

    @get('/dump')
    def dump():
      # pdb.set_trace()
      return self.__render_json(self.store.dump())

    @post('/index')
    def index():
      image = Image(file=request.files.file.file)
      h = self.store.phash_for(image)
      self.store.add(h)
      return self.__render_json({'phash': h})

    @get('/search/<phash>')
    def search(phash):
      data = []
      for r in self.store.find(int(phash)):
        data.append({'distance': r[0], 'phash': r[1]})
      return self.__render_json(data)

    run(host=self.host, port=self.port)

  def __render_json(self, data):
    from bottle import response

    response.content_type = 'application/json'
    if type(data) == 'str':
      return data
    else:
      return json.dumps(data)
