from Blockchain import Block
import time
do_cycles = 5
final_results = []
for i in range(do_cycles):
    block = Block(index=0, timestamp=time.time(), hardness=5)
    hashesh_per_cycle = increase_value = 500
    is_done = False
    results = []
    while not is_done:
        tic = time.time()
        block.calculate_correct_hash_multiprocess(
            hashes_per_cycle=hashesh_per_cycle)
        toc = time.time()
        if len(results) == 0 or (toc - tic) < results[-1][0]:
            results.append([toc - tic, hashesh_per_cycle])
            hashesh_per_cycle += increase_value
            print(f"Cycle #{i}: hashes increased: {hashesh_per_cycle}")
            continue
        is_done = True
    final_results.append(hashesh_per_cycle)
    print(f"Cycle #{i}: Fininshed, {hashesh_per_cycle} hashes_per_cycle")


print(sum(final_results) / len(final_results))
