#!/usr/bin/python

import argparse
import json

version="1.0.0"

def extract_source_code_repositories(packages_information):
    repositories = []
    errors = []

    for package in packages_information:

        try:
            source_code_uri = package['source_code_uri']
            homepage_uri    = package['homepage_uri']

            if source_code_uri is not None and source_code_uri != '' and ("github" in source_code_uri or "gitlab" in source_code_uri or "git" in source_code_uri):
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
    parser.add_argument('-d', '--data-file', help='output file (default is raw JSON output)', type=str, default='./stats_ruby.json')

    args = parser.parse_args()
    outputfile = args.out

    if outputfile[-1] == "/":
        outputfile = outputfile+"stats_ruby.json"
    return outputfile



def main ():

    datafile = parse_commandline()


    # REad json from datafile
    with open(datafile, 'r') as f:
        data = json.load(f)

    # Extract source code repositories
    repositories, errors = extract_source_code_repositories(data)

    #  Print the results to screen
    print(repositories)



if __name__ == '__main__':
    main()
