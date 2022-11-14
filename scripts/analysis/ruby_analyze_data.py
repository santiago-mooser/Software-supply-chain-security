#!/usr/bin/python

import argparse
import json
import os
import subprocess

version="1.0.0"

def extract_source_code_repositories(packages_information):
    repositories = []
    errors = []

    for package in packages_information:

        try:
            source_code_uri = package['source_code_uri']
            homepage_uri    = package['homepage_uri']

            if source_code_uri is not None and source_code_uri != '' and ("github" in source_code_uri or "gitlab" in source_code_uri or ".git" in source_code_uri):
                # repositories.append(source_code_uri)
                repositories.append('/'.join(source_code_uri.split('/')[:5]))

            elif homepage_uri is not None and homepage_uri != '':

                if "github.com" in homepage_uri:
                    repositories.append('/'.join(homepage_uri.split('/')[:5]))

                elif "gitlab.com" in homepage_uri:
                    repositories.append('/'.join(homepage_uri.split('/')[:5]))

                else:
                    errors.append(package)

            else:
                errors.append(package)
        except KeyError:
            errors.append(package)
    return repositories, errors



# Basically, check whether an outputfile was given.
def parse_commandline():

    description = "This processes the data retreived from the ruby API"
    usage='''
    python process_data_ruby.py -o /path/to/file
    \t-v --version\t\t\tPrint version
    '''

    parser = argparse.ArgumentParser(description=description, usage=usage)

    parser.add_argument('-v', '--version',  action='version', version='%(prog)s '+version)
    parser.add_argument('-d', '--data-file', help='output file (default is raw JSON output)', type=str, default='./data/package_repo_data/ruby_stats.json')
    # Folder where to clone git repos
    parser.add_argument('-o', '--output-folder', help='output folder (default is ./ruby_repos)', type=str, default='./analysis/ruby_repos')

    args = parser.parse_args()
    outputfile = args.data_file

    if outputfile[-1] == "/":
        outputfile = outputfile+"stats_ruby.json"
    return outputfile

def clone_git_repo(repository):
    print("Cloning: " + repository)

    # Close repos
    os.system("git clone " + repository)

    # see: https://stackoverflow.com/questions/17371955/verifying-signed-git-commits
    signed_commits = subprocess.check_output("git log --show-signature | grep 'gpg: Good signature' -B3 | grep 'commit' | awk '{print $2}'")
    total_commits = subprocess.check_output("git log --oneline | awk '{print $1}'")

    # Scan dependencies for with dependabot
    subprocess.check_output("dependabot-core/bin/dependabot-core dependency-files --directory /home/dependabot/dependabot-core --package-manager bundler --name " + repository + " --version 1.0.0 --source git " + repository)
    # subprocess.check_output("snyk test ./ruby_repos/" + repository.split('/')[-1] + " --json > ./data/ruby" + repository.split('/')[-1] + ".json")

def process_data(datafile):

    # Read json from datafile
    try:
        with open(datafile, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("File not found: " + datafile)
        exit(1)
    # Extract source code repositories
    repositories, errors = extract_source_code_repositories(data)

    with open("log.json", 'w') as f:
        log_data = {"errors": errors}
        # write to json file
        json.dump(log_data, f, indent=4)

    for repo in repositories:
        clone_git_repo(repo)
    #  Print the results to screen
    # print(repositories)



if __name__ == '__main__':

    datafile = parse_commandline()
    process_data(datafile)
