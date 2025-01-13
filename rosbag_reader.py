import fire

from utils.rosbag_read_helper import RosbagReadHelper


def main():
    fire.Fire(
        component=RosbagReadHelper,
        name="rosbag_reader",
    )


if __name__ == "__main__":
    main()
