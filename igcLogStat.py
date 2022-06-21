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


if __name__ == '__main__':
    points = []
    alt_data = []
    climb_rate = []

    with open('files/file1.igc') as f:
        for line in f:
            parse_igc_line(line, points, alt_data, climb_rate)

    base_map = folium.Map(points[0], zoom_start=14)

    max_climb = climb_rate[0]
    min_sink = climb_rate[0]
    for rate in climb_rate:
        if rate > max_climb:
            max_climb = rate
        if rate < min_sink:
            min_sink = rate

    print(max_climb, min_sink)

    cm = ['b', 'c', 'y', 'r', 'r']
    steps = int(max_climb-min_sink)

    folium.ColorLine(
        points, climb_rate, colormap=cm, nb_steps=steps,
        weight=5
    ).add_to(base_map)

    c_map = LinearColormap(cm, vmin=min_sink, vmax=max_climb).to_step(steps)
    c_map.caption = "Sink/Climb Rates [m/s]"
    c_map.add_to(base_map)

    base_map.save('test.html')
