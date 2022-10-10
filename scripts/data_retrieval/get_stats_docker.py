#!/bin/python
import requests
import json
import argparse

version="1.0.0"

# Query docker hub API to get most downloaded images
def query_dockerhub_api():
    url = "https://hub.docker.com/v2/search/repositories/?query=*&page_size=100"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error querying docker hub API")
    else:
        return response.json()


# Basically, check whether an outputfile was given.
def parse_commandline():

    description = "This script queries the docker hub API to get metadata about the most downloaded images"
    usage='''
    python get_stats_docker.py -o /path/to/file
    \t-v --version\t\t\tPrint version
    '''

    parser = argparse.ArgumentParser(description=description, usage=usage)

    parser.add_argument('-v', '--version',  action='version', version='%(prog)s '+version)
    parser.add_argument('-o', '--out', help='output file (default is raw JSON output)', type=str, default='./stats_docker_.json')

    args = parser.parse_args()
    outputfile = args.out

    if outputfile[-1] == "/":
        outputfile = outputfile+"stats_docker.json"
    return outputfile



def main ():

    outfile = parse_commandline()

    # Query docker hub API
    packages_information = query_dockerhub_api()

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
