#!/bin/python
import requests
import json
import argparse

version="1.0.0"


def query_rubygems_api():

    # Get results from first 10 pages of ruby API:
    packages_information = []
    for page in range(1, 11):
        url = f"https://rubygems.org/api/v1/search.json?query=*&page={page}"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"Error querying rubygems API for page {page}")
        else:
            packages_information += response.json()

    return packages_information


# Basically, check whether an outputfile was given.
def parse_commandline():

    description = "This script queries the Ruby Gems API to get metadata about the most downloaded packages"
    usage='''
    python get_stats_ruby.py -o /path/to/file
    \t-v --version\t\t\tPrint version
    '''

    parser = argparse.ArgumentParser(description=description, usage=usage)

    parser.add_argument('-v', '--version',  action='version', version='%(prog)s '+version)
    parser.add_argument('-o', '--out', help='output file (default is raw JSON output)', type=str, default='./stats_ruby.json')

    args = parser.parse_args()
    outputfile = args.out

    if outputfile[-1] == "/":
        outputfile = outputfile+"stats_ruby.json"
    return outputfile



def main ():

    outfile = parse_commandline()

    # Query Ruby gems API
    packages_information = query_rubygems_api()

    # Write output to file
    json_object = json.dumps(packages_information, indent=4)
    if outfile[-4:] == "json":
        jsonfile = open(outfile, "w")
        jsonfile.write(json_object)
    else:
        jsonfile = open(f'{outfile}.json', 'w')
        jsonfile.write(json_object)

    #  Print the results to screen
    print(json_object)

if __name__ == '__main__':
    main()
