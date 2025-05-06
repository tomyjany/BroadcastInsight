import argparse

from sceneDetector.agents.interface import get_scene_detector


def main():
    parser = argparse.ArgumentParser(description="Select agent and file")
    parser.add_argument(
        "agent_name", type=str, help="Name of the agent used to mine data"
    )
    parser.add_argument("input_file", type=str, help="The input file path")
    parser.add_argument("output_file", type=str, help="The output file path")

    args = parser.parse_args()
    AGENT_NAME = args.agent_name
    INPUT_FILE = args.input_file
    OUTPUT_FILE = args.output_file

    sceneDetector = get_scene_detector(AGENT_NAME)
    # sceneDetector.detect_shot_with_timestamps(INPUT_FILE)# saves only cuts
    # sceneDetector.save_cuts_to_file(OUTPUT_FILE)

    sceneDetector.detect_shot_with_bondaries(INPUT_FILE)
    sceneDetector.save_boundary_cuts_to_file(OUTPUT_FILE)  # saves also boundaries
    # sceneDetector.detect_shot(INPUT_FILE)
    # sceneDetector.save_cuts_to_file(OUTPUT_FILE)


if __name__ == "__main__":
    # test()
    main()
