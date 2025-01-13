import time
from utils.rosbag_read_helper import RosbagReadHelper
from rosidl_runtime_py.utilities import get_message


def main():
    # path to the bagfile
    bag_file = "/home/seoyc/Downloads/rosbag/rosbag_0.db3"

    # topic name
    topic_name = "/camera/color/image_raw"

    rosbag_reader = RosbagReadHelper(bag_file)

    t, msgs = rosbag_reader.get_all_messages_in_topic(
        topic_name=topic_name,
        print_out=True,
    )

    msg_type = get_message(rosbag_reader.get_message_type(topic_name))

    rosbag_reader.logger.info(f"Message type: {msg_type}")

    start_time = time.time()

    for timestamp, message in zip(t, msgs):
        rosbag_reader.logger.info(f"Timestamp: {timestamp}")

        rosbag_reader.__save_iamge_from_msg(
            topic_name=topic_name,
            timestamp=timestamp,
            msg=message,
        )

    end_time = time.time()
    rosbag_reader.logger.info(f"Time taken: {end_time - start_time}")

    rosbag_reader.__close()


if __name__ == "__main__":
    main()
