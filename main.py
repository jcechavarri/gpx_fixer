from dateutil import parser
from datetime import timedelta

fp = "20221208Mountain hike.gpx"

d, m, y = fp[6:8], fp[4:6], fp[0:4]
sport = fp[8:].replace(" ", "")
out_path = f"{d}-{m}-{y}_{sport}"

with open(fp, "r") as file:
    lines = file.readlines()

prev_position_data = None
prev_time_data = None

index: int = None  # type: ignore
for i, line in enumerate(lines):
    pos_data = line[8:58]  # This is the pos data
    time_data = line[75:112]  # This is the time data
    if pos_data == prev_position_data and prev_time_data != time_data:
        index = i + 1  # Start index of wrong position data
        break
    prev_position_data = pos_data
    prev_time_data = time_data

print("index", index)

# Get start and end times
start_time_li = lines[index].find("<time>") + 6
start_time_ri = lines[index].find("</time>")

start_time_str = lines[index][start_time_li:start_time_ri]
start_time = parser.parse(start_time_str)

end_time_li = lines[-2].find("<time>") + 6
end_time_ri = lines[-2].find("</time>")

end_time_str = lines[-2][end_time_li:end_time_ri]
end_time = parser.parse(end_time_str)

total_time = end_time - start_time

ms = total_time.seconds
n_lines = index - 6

print(ms)
print(n_lines)
if (gap := ms / n_lines - 1) > 0.01:
    raise ValueError(f"Gap too big: {gap}")

lines = lines[:index] + [lines[-1]]


def d2s(date):
    return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def get_indexes(line: str, tag: str):
    s = line.find(tag) + len(tag)
    end_tag = tag[0] + "/" + tag[1:]
    e = line.find(end_tag)
    return s, e


count = 0
with open(out_path, "w") as file:
    for i in range(len(lines)):
        if "<metadata>" in lines[i]:
            # meta_time_s = lines[i].find("<time>") + 6
            # meta_time_f = lines[i].find("</time>")
            meta_time_s, meta_time_f = get_indexes(lines[i], "<time>")
            lines[i] = lines[i][:meta_time_s] + d2s(start_time) + lines[i][meta_time_f:]

        elif "<time>" in lines[i]:
            # time_s = lines[i].find("<time>") + 6
            # time_f = lines[i].find("</time>")
            time_s, time_f = get_indexes(lines[i], "<time>")
            new_time = start_time + timedelta(seconds=count)
            lines[i] = lines[i][:time_s] + d2s(new_time) + lines[i][time_f:]
            count += 1

        if "<ele>" in lines[i]:
            s, f = get_indexes(lines[i], "<ele>")
            lines[i] = lines[i][: s - 5] + lines[i][f + 6 :]
        file.write(lines[i])
