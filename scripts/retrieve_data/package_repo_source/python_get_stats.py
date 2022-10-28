#!/bin/python
import requests
import json
import argparse

version="1.0.0"

# Get data for most downloaded packages:
def get_most_downloaded_packages():
    url = "https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error getting file")
    else:
        return response.json()


# Basically, check whether an outputfile was given.
def parse_commandline():

    description = "This script retrieves PyPi download stats from hugovk.github.io"
    usage=f'''
    python python_get_stats.py -o /path/to/file
    \t-v --version\t\t\tPrint version
    '''

    parser = argparse.ArgumentParser(description=description, usage=usage)

    parser.add_argument('-v', '--version',  action='version', version='%(prog)s '+version)
    parser.add_argument('-o', '--out', help='output file (default is raw JSON output)', type=str, default='./python_stats.json')
    # if the quiet argument is passed, the script will not print the results to screen
    parser.add_argument('-q', '--quiet', help='do not print results to screen', action='store_true')

    args = parser.parse_args()
    outputfile = args.out
    quiet = args.quiet

    if outputfile[-1] == "/":
        outputfile = outputfile+"python_stats.json"
    return {"outputfile": outputfile,
            "quiet": quiet}



def main ():

    # Parse commandline
    settings = parse_commandline()

    outfile = settings["outputfile"]
    quiet = settings["quiet"]

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
    if not quiet:
        print(json_object)


if __name__ == '__main__':
    main()
