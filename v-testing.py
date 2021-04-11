from vmem import *

PAGE_SIZE = 256
page_table = []
tlb = []
frames = []

la_int = 64243 # logical address for testing
la = intTola(la_int)

page = la["page"]
offset = la["offset"] * 2 
print(f'page: {page} offset: {offset}')

page_data = demandPage(page)
val = getVal(page_data, offset)
print(val)

