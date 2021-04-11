from os import write
import numpy as np
from vmem import *

# Purpose: Simulate Virtual Memory 
# Author: Trung Nguyenvo

# 1 - request for memory is made
# 2 = PAGE and OFFSET is extracted from memory address
# 3 - reference TLB for FRAME number using PAGE number
# 4 - if TLB miss, check PAGETABLE
# 5 = if PAGE fault, load 256 byte PAGE from BACKING_STORE to available FRAME, update PAGETABLE and TLB
# 5 - Go to frame and print byte
 
output_list = []
page_fault_count = 0.0
tlb_hit_count = 0.0

PAGE_SIZE = 256
NUM_PAGES = 256
NUM_FRAMES = 128
TLB_SIZE = 16
page_table = np.full(NUM_PAGES, -1)
frame_arr = []
free_frames_list = []
la_list = [] # list of logical addresses
local_tlb = tlb(16)
lru = [] 

for n in range(NUM_FRAMES):
  free_frames_list.append(n)
  frame_arr.append(-1)

# Read logical addresses into list: la
with open('addresses.txt') as f:
  for line in f:
    la_list.append(int(line))

# f = open('addresses.txt', "r")
# la_list.append(int(f.readline()))
# f.close()

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
        free_frame_num = page_table[lru.pop(0)]

      print(f'free frame:{free_frame_num}')

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

# for line in output_list:
#   print(line)

print(f'TLB Hit rate: {tlb_hit_count/1000 * 100}% Page-Fault rate: {page_fault_count/1000 * 100}%')
f = open('output.txt', "w")
for line in output_list:
    f.write(line)
f.close()  


