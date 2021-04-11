import binascii

PAGE_SIZE = 256
# converts integer to logical address
def intTola(integer): 
  # 32 bit address for testing
  binary32 = bin(int(integer)) 
  binary32 = binary32[2:] #removes 0b char that denotes binary string
  binary32 = binary32.zfill(32) #sets length to 32 bits

  #get the last 16 bits that holds page number + offset
  last16 = binary32[16:] 
  page_bin = last16[:8] 
  offset_bin = last16[-8:]

  return {
    "integer": integer,
    "page": int(page_bin,2),
    "offset": int(offset_bin,2)
  }

def paToInt(frame_number, offset):
  left = bin(frame_number)[2:]
  left = left.zfill(8)
  right = bin(offset)[2:]
  right = right.zfill(8)
  
  physical_a = left + right
  pa_int = int(physical_a,2)

  return pa_int

# get 256 byte page from BACKING_STORE 
def demandPage(page):
  f = open('BACKING_STORE.bin', 'rb')
  f.seek((page * PAGE_SIZE)) # num in bytes

  # in bytes
  # hexlify removes irrelevant characters to allow offsetting on the sequence
  page_data = binascii.hexlify(f.read(PAGE_SIZE)) # in bytes
  f.close()

  return page_data

# given the page and offset, return the byte value as an integer
def getVal(page, offset):
  o = offset * 2
  value = page[o:o+2] # value at offset
  value_hex = binascii.unhexlify(value)
  value_int = int.from_bytes(value_hex, byteorder='big', signed=True)

  return value_int

class tlb:
  table = {}
  stack = []

  def __init__(self, max_size):
    self.max_size = max_size

  def update(self, pn, fn):
  # add page_num and frame_num to TLB
    if(self.full()):
      # get least recently used page from stack
      target = self.stack.pop(0)
      # remove target page from TLB
      del self.table[target]
      # swap in new page
      self.table[pn] = fn
      # add new page to the end of stack
      self.stack.append(pn)
    else:  
      self.table[pn] = fn
      self.stack.append(pn)

  def findFrame(self, pn):
    frame = self.table[pn]

    if pn in self.stack:
      self.stack.remove(pn)
      self.stack.append(pn)

    return frame

  def full(self):
    return len(self.table) == self.max_size