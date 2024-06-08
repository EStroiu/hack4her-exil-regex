import argparse 

parser = argparse.ArgumentParser (
    prog='python3 ./script.py',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='',
    epilog=''
)

parser.add_argument('start_lat')
parser.add_argument('start_lng')
parser.add_argument('end_lat')
parser.add_argument('end_lng')

args = parser.parse_args()

start = (args.start_lat, args.start_lng)
end = (args.end_lat, args.end_lng)

print(start, end)