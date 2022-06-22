import argparse
import folium
from branca.colormap import LinearColormap


def convert(str_coord):
    degrees = str_coord[0:2]
    ll = len(str_coord)
    three_last = str_coord[ll - 3:ll]
    minutes = str_coord[2:ll - 3]

    res = int(degrees) + int(minutes)/60 + int(three_last)/60/1000
    return res


def ts_to_sec(ts):
    hours = ts[0:2]
    minutes = ts[2:4]
    seconds = ts[4:6]

    return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


def parse_igc_line(file_item, pts, alts, rates):
    if file_item.startswith('B'):
        time_stamp = file_item[1:7]
        seconds = ts_to_sec(time_stamp)
        lat = file_item[7:14]
        lon = file_item[16:23]
        alt = file_item[25:30]

        n_lat = convert(lat)
        n_lon = -convert(lon)
        n_alt = int(alt)

        if len(alts) > 0:
            aa = alts[-1]
            rates.append((n_alt - aa[1]) / (seconds - aa[0]))

        alts.append([seconds, n_alt])
        pts.append([n_lat, n_lon])


def get_min_max_rates(cl_rate):
    climb = climb_rate[0]
    sink = climb_rate[0]
    for rate in cl_rate:
        if rate > climb:
            climb = rate
        if rate < sink:
            sink = rate
    return sink, climb


def parse_file(file_name):
    pts = []
    alt_data = []
    climb_rates = []

    print('Processing {}'.format(file_name))
    with open(file_name) as f:
        for line in f:
            parse_igc_line(line, pts, alt_data, climb_rates)

    return pts, climb_rates


def draw_map(pts, climb):
    colors = ['b', 'c', 'y', 'r', 'r']
    base_map = folium.Map(pts[0], zoom_start=15)

    min_sink, max_climb = get_min_max_rates(climb)
    steps = int(max_climb - min_sink)

    folium.ColorLine(
        pts, climb, colormap=colors, nb_steps=steps, weight=5
    ).add_to(base_map)

    c_map = LinearColormap(colors, vmin=min_sink, vmax=max_climb).to_step(steps)
    c_map.caption = "Sink/Climb Rate [m/s]"
    c_map.add_to(base_map)

    base_map.save('{}.html'.format(args.file))
    print('File {}.html saved'.format(args.file))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='igcLogStat')
    parser.add_argument('file', help='IGC file to analyze')
    args = parser.parse_args()

    if args.file is None:
        parser.print_help()
    else:
        points, climb_rate = parse_file(args.file)

        draw_map(points, climb_rate)
