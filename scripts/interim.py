#!/usr/bin/python


import os
from multiprocessing import Pool

import code_analysis
import git_clone
from retrieve_data import python

api_data = python.query_api(5)

parsed_data = python.parse_metadata_to_elasticseach_mapping(api_data)

# use Pool to download git repos in parallel

p = Pool(5)

results =[]

for key, value in parsed_data.items():
    path = os.path.join('/app/repos/', key)
    print(f"Cloning {key} from {value['repo_url']} into {path}")
    arguments = (value["repo_url"], path)
    results.append(p.apply_async(git_clone.clone_git_repo, args=(arguments,)))


p.close()
p.join()
print("\nCloning complete\n")

analysis_pool = Pool(5)
# list comprehension to appent "tmp" to all keys to the keys of hte parsed_data dict
paths = [f"/app/repos/{key}" for key in parsed_data.keys()]
print(f"Paths: {paths}")
results = analysis_pool.map(code_analysis.run_analysis, paths,)
analysis_pool.close()
analysis_pool.join()

print(results)
