import collections

class HashIndex(object) :
  def __init__(self, parent, key) :
    self._index_map = {}
    # Use a weakref instead?
    self.__parent = parent
    # Function mapping values to keys
    self._key = key

  def keys(self) :
    return self._index_map.keys()

  def __getitem__(self, key) :
    return (self.__parent[id] for id in self._index_map[key])

  def _update(self, value) :
    self._index_map.setdefault(self._key(value), set([])).add(id(value))

    
  def _remove(self, value) :
    key = self._key(value)
    try :
      s = self._index_map[key]
    except KeyError :
      # We should never reach here, but if we do, we've satisfied the
      # post-condition anyway
      return
    
    try :
      s.remove(id(value))
    except KeyError :
      # Again, we should never reach here, but if we do we've
      # satisfied the post-condition
      return
    
    if not s :
      del self._index_map[key]



class MultiIndex(object) :
  def __init__(self) :
    # Dictionary from id to record, for easy lookup
    self._records = {}

    # Map from field name to associated index
    self.index = {}

  @property
  def records(self) :
    return self._records.values()

  def add(self, value) :
    self._records[id(value)] = value

    # Update indexes...
    for index in self.index.itervalues() :
      index._update(value)

  def remove(self, value) :
    # Maybe I should have this take a variable number of args, and
    # then can remove each one...  and perhaps find faster ways to
    # rebuild the indexes.
    for index in self.index.itervalues() :
      index._remove(value)
    return self._records.pop(id(row))
    
  def __len__(self) :
    return len(self._records)
  
  def create_index(self, indexname, key) :
    index = HashIndex(self, key=key)
    for record in self :
      index._update(record)
    self.index[indexname] = index
    

  def __iter__(self) :
    return self._records.itervalues()

  
  def update(self, row, **kw) :
    # This is where a mutable tuple would help, because then I could
    # change the contents and only change the appropriate indexes...
    new_row = row._replace(**kw)
    self.remove(row)
    self.add(new_row)
