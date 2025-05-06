import json

# older version for cuts that contain only one information
# class CutManager:
#     def __init__(self):
#         self.cuts = []  # List of dictionaries to store frame and timestamp

#     def add_cut(self, frame_num, timestamp_ms):
#         if not self.is_cut(frame_num):
#             self.cuts.append({"frame": frame_num, "timestamp": timestamp_ms})

#     def remove_cut(self, frame_num):
#         self.cuts = [cut for cut in self.cuts if cut["frame"] != frame_num]

#     def is_cut(self, frame_num):
#         return any(cut["frame"] == frame_num for cut in self.cuts)

#     def save_cuts_to_file(self, file_name):
#         cuts_data = {"cuts": self.cuts}
#         with open(file_name, "w") as f:
#             json.dump(cuts_data, f, indent=4)

#     def load_cuts_from_file(self, file_name):
#         if file_name:
#             with open(file_name, "r") as f:
#                 cuts_data = json.load(f)
#                 self.cuts = cuts_data["cuts"]  # Load the cuts into the cut manager


class CutManager:
    def __init__(self):
        self.cuts = []  # List of dictionaries to store frame and timestamp

    def add_cut(self, frame_num, timestamp_ms, adr):
        # if self.is_cut(frame_num) != "start" or self.is_cut(frame_num) != "end":
        #     #self.cuts.append({"{0}": frame_num, "time_{1}".format(adr): timestamp_ms})
        #     self.cuts.append({adr: frame_num, "time_"+adr: timestamp_ms})
        color = self.is_cut(frame_num)
        if color == "start":
            self.cuts.append({adr: frame_num, "time_" + adr: timestamp_ms})

    def add_cut(self, start, end, start_time, end_time):
        self.cuts.append(
            {"start": start, "time_start": start_time, "end": end, "time_end": end_time}
        )

    def remove_cut(self, frame_num):
        print("MAZU ho")
        print("before", self.cuts)
        self.cuts = [
            cut
            for cut in self.cuts
            if cut["start"] != frame_num and cut["end"] != frame_num
        ]
        print("after", self.cuts)

    def is_cut(self, frame_num):
        green, red = False, False
        # print("START IN KEYS ", ("start" in self.cuts.keys()))
        green = any(cut["start"] == frame_num for cut in self.cuts)
        red = any(cut["end"] == frame_num for cut in self.cuts)
        if green:
            return "start"
        elif red:
            return "end"
        return "nope"

    def save_cuts_to_file(self, file_name):
        cuts_data = {"cuts": self.cuts}
        with open(file_name, "w") as f:
            json.dump(cuts_data, f, indent=4)

    def load_cuts_from_file(self, file_name):
        if file_name:
            with open(file_name, "r") as f:
                cuts_data = json.load(f)
                self.cuts = cuts_data["cuts"]  # Load the cuts into the cut manager
