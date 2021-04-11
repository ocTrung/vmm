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
NUM_FRAMES = 256
TLB_SIZE = 16
page_table = np.full(NUM_PAGES, -1)
frame_arr = []
free_frames_list = []
la_list = [] # list of logical addresses
local_tlb = tlb(16)

for n in range(256):
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

  # (3) Find frame number
  try:
    frame_number = local_tlb.findFrame(page_num)
    tlb_hit_count += 1

    print(f'TLB hit: Page-{page_num} Frame-{frame_number}')
  except KeyError:
    # print(f'TLB miss: Page-{page_num} not found!')
    state = 'tlb-miss'

  if (state == 'tlb-miss'):
    # Reference page table for frame number
    frame_number = page_table[page_num]

    # handle page-fault
    if (frame_number == -1):
      page_fault_count += 1 
      # Find a free frame
      free_frame_num = free_frames_list.pop(0)
      # Read in page from BACKING_STORE into free frame
      page_data = demandPage(page_num)
      frame_arr[free_frame_num] = page_data
      # Update TLB and Page Table
      page_table[page_num] = free_frame_num
      frame_number = free_frame_num
      # tlb[page_num] = frame_number
      # print(f'tlb {tlb}')
      local_tlb.update(page_num, frame_number)

  # read data at physical address then print it
  data = frame_arr[frame_number]
  val = getVal(data, offset)

  # calculate Physical Address as an integer 
  pa_int = paToInt(frame_number, offset)
  
  print(f'Virtual address: {la_int} Physical address: {pa_int} Value: {val}')
  output_list.append(f'Virtual address: {la_int} Physical address: {pa_int} Value: {val}\n')

# for line in output_list:
#   print(line)

print(f'TLB Hit rate: {tlb_hit_count/1000 * 100}% Page-Fault rate: {page_fault_count/1000 * 100}%')
f = open('output.txt', "w")
for line in output_list:
    f.write(line)
f.close()  


