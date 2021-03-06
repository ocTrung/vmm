from os import write
import numpy as np
from vmem import *
 
output_list = []
page_fault_count = 0.0
tlb_hit_count = 0.0

PAGE_SIZE = 256
NUM_PAGES = 256
NUM_FRAMES = 128
TLB_SIZE = 16
page_table = np.full(NUM_PAGES, -1)
la_list = [] # list of logical addresses
frame_arr = [] # physical memory 
free_frames_list = [] 
local_tlb = tlb(TLB_SIZE)
lru = [] # LRU for page replacement

for n in range(NUM_FRAMES):
  free_frames_list.append(n)
  frame_arr.append(-1)

# Read logical addresses into list: la
with open('addresses.txt') as f:
  for line in f:
    la_list.append(int(line))

for la_int in la_list: 
  
  # Variables to store physical address
  frame_number = -1
  offset = -1
  state = 'tlb-hit'

  # (2) Get page and offset from logical address
  la = intTola(la_int)
  page_num = la["page"]
  offset = la["offset"]

  # update LRU
  if page_num in lru: 
    lru.remove(page_num)
  lru.append(page_num)

  # Find frame number
  try:
    frame_number = local_tlb.findFrame(page_num)
    tlb_hit_count += 1
  except KeyError:
    state = 'tlb-miss'

  # Check page table for frame number
  if (state == 'tlb-miss'):
    frame_number = page_table[page_num]
    
    # if page-fault
    if (frame_number == -1):
      page_fault_count += 1 
      # Find a free frame
      try:
        free_frame_num = free_frames_list.pop(0)
      except IndexError:
        # get least recently used page
        target = lru.pop(0)
        free_frame_num = page_table[target]
        page_table[target] = -1 # replace the old entry in Page Table 

      # Read in page from BACKING_STORE into free frame
      page_data = demandPage(page_num)
      frame_arr[free_frame_num] = page_data
      # Update TLB and Page Table
      page_table[page_num] = free_frame_num
      frame_number = free_frame_num
      local_tlb.update(page_num, frame_number)

  # read data at physical address then print it
  data = frame_arr[frame_number]
  val = getVal(data, offset)
  
  # calculate Physical Address as an integer 
  pa_int = paToInt(frame_number, offset)
  
  output_list.append(f'Virtual address: {la_int} Physical address: {pa_int} Value: {val}\n')

# Print Statistics
tlb_hr = tlb_hit_count/1000 * 100
tlb_hr = "{:.2f}".format(tlb_hr)
print(f'TLB Hit rate: {tlb_hr}%\nPage-Fault rate: {page_fault_count/1000 * 100}%')

# Output to file
f = open('output.txt', "w")
for line in output_list:
    f.write(line)
f.close()  


