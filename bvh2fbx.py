import fbx
#need to figure out how to import fbx
import sys
import os

class BVHNode:
    def __init__(self, name):
        self.name = name
        self.offset = []
        self.channels = []
        self.children = []
        self.parent = None
        self.channel_order = []

def parse_bvh(filepath):
    with open(filepath, 'r') as file:
        lines = [line.strip() for line in file]

    nodes = []
    stack = []
    current_node = None
    motion_data = []
    frame_time = 0.0

    i = 0
    while i < len(lines):
        line = lines[i]
        tokens = line.split()

        if len(tokens) == 0:
            i += 1
            continue

        if tokens[0] in ("ROOT", "JOINT", "End"):
            name = tokens[1] if tokens[0] != "End" else "End_Site"
            node = BVHNode(name)
            if current_node:
                node.parent = current_node
                current_node.children.append(node)
            else:
                root_node = node
            current_node = node
            stack.append(node)
            i += 1
        elif tokens[0] == "{":
            i += 1
        elif tokens[0] == "OFFSET":
            current_node.offset = list(map(float, tokens[1:]))
            i += 1
        elif tokens[0] == "CHANNELS":
            num_channels = int(tokens[1])
            current_node.channels = tokens[2:]
            current_node.channel_order = []
            for channel in tokens[2:]:
                if 'position' in channel.lower():
                    current_node.channel_order.append(('T', channel[0].upper()))
                elif 'rotation' in channel.lower():
                    current_node.channel_order.append(('R', channel[0].upper()))
            i += 1
        elif tokens[0] == "}":
            stack.pop()
            if stack:
                current_node = stack[-1]
            i += 1
        elif tokens[0] == "MOTION":
            i += 1
            break
        else:
            i += 1

    # Read motion data
    if i < len(lines) and lines[i].startswith("Frames:"):
        num_frames = int(lines[i].split()[1])
        i += 1
    if i < len(lines) and lines[i].startswith("Frame Time:"):
        frame_time = float(lines[i].split()[2])
        i += 1

    for _ in range(num_frames):
        frame_line = lines[i]
        while len(frame_line.strip().split()) < 1:
            i += 1
            frame_line = lines[i]
        frame_values = list(map(float, frame_line.strip().split()))
        motion_data.append(frame_values)
        i += 1

    return root_node, motion_data, frame_time

