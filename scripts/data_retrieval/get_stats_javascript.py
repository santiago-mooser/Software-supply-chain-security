#!/bin/python
import requests
import json
import argparse

version="1.0.0"

# Get data for most downloaded javascript packages:
def get_most_downloaded_packages():

    # sort by popularity and return the top 250 packages
    url="https://api.npms.io/v2/search?q=not:unstable+popularity-weight:99.0&size=250"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error getting file")
    else:
        return response.json()

# Basically, check whether an outputfile was given.
def parse_commandline():

    description = "This script downloads the stats for the most downloaded javascript packages"
    usage=f'''
    python get_stats_javascript.py -o /path/to/file
    \t-v --version\t\t\tPrint version
    '''

    parser = argparse.ArgumentParser(description=description, usage=usage)

    parser.add_argument('-v', '--version',  action='version', version='%(prog)s '+version)
    parser.add_argument('-o', '--out', help='output file (default is raw JSON output)', type=str, default='./stats_javascript.json')

    args = parser.parse_args()
    outputfile = args.out

    if outputfile[-1] == "/":
        outputfile = outputfile+"stats_javascript.json"
    return outputfile




def main ():

    # Parse commandline
    outfile = parse_commandline()

    # Update the data
    packages_information = get_most_downloaded_packages()

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
