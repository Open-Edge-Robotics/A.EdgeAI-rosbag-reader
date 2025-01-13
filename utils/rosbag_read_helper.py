import datetime
import sqlite3
import cv_bridge
import cv2
import os
import csv

from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

from typing import Tuple, List, Any
import logging
from utils.logger import Logger


class RosbagReadHelper:
    def __init__(
        self,
        path: str = "rosbag.db3",
        loglevel: int = logging.ERROR,
    ):
        self.logger = Logger(name="RosbagReader", level=loglevel)
        self.logger = self.logger.get_logger()

        self._conn = sqlite3.connect(path)
        self._cursor = self._conn.cursor()

        self.logger.info(f"Connected to {path}")

    def __close(self):
        """Close the connection to the database."""
        self.logger.info("Closing connection")
        self._conn.close()

    def __get_all_elements(
        self,
        table_name: str,
        print_out: bool = True,
    ) -> List[Any]:
        """Returns a dictionary with all elements of the table database."""
        # Get elements from table "table_name"
        try:
            self._cursor.execute(f"SELECT * from({table_name})")
            records = self._cursor.fetchall()
        except sqlite3.OperationalError:
            self.logger.warning(f"Table {table_name} does not exist.")
            return []

        if print_out:
            for row in records:
                print(row)

        return records

    def is_topic(self, topic_name: str, print_out: bool = True) -> List[Any]:
        """Returns topic_name header if it exists. If it doesn't,
        returns empty. It returns the last topic found with this name.

        params
        ------
        topic_name : str
            Name of the topic to look for.

        print_out : bool
            If True, it prints the topic found.

        returns
        -------
        topicFound : List[Any]
            List of the topic found.
        """

        boolIsTopic = False
        topicFound = []

        # Get all records for 'topics'
        records = self.__get_all_elements(
            table_name="topics",
            print_out=False,
        )

        # Look for specific 'topic_name' in 'records'
        for row in records:
            if row[1] == topic_name:  # 1 is 'name' TODO
                boolIsTopic = True
                topicFound = row

        if print_out:
            if boolIsTopic:
                # 1 is 'name', 0 is 'id' TODO
                print(
                    f"Topic named {topicFound[1]} exists at id {topicFound[0]}"
                )  # noqa
            else:
                print(f"Topic {topic_name} could not be found.")

        return topicFound

    def get_all_messages_in_topic(
        self,
        topic_name: str,
        print_out: bool = True,
    ) -> Tuple[List[float], List[bytes]]:
        """Returns all timestamps and messages at that topic.
        There is no deserialization for the BLOB data.

        prams
        -----
        topic_name : str
            Name of the topic to look for.

        print_out : bool
            If True, it prints the number of messages in the topic.

        returns
        -------
        timestamps : List[float]
            List of timestamps for each message.

        messages : List[bytes]
            List of messages in BLOB format.
        """
        count = 0
        timestamps = []
        messages = []

        # Find if topic exists and its id
        topicFound = self.is_topic(topic_name=topic_name, print_out=False)

        # If not find return empty
        if not topicFound:
            self.logger.info(f"Topic {topic_name} could not be found.")
        else:
            records = self.__get_all_elements(
                table_name="messages",
                print_out=False,
            )

            # Look for message with the same id from the topic
            for row in records:
                if row[1] == topicFound[0]:  # 1 and 0 is 'topic_id' TODO
                    count = count + 1  # count messages for this topic
                    timestamps.append(row[2])  # 2 is for timestamp TODO
                    messages.append(row[3])  # 3 is for all messages

            # Print
            if print_out:
                print(f"Topic {topic_name} has {count} messages.")

        return timestamps, messages

    def get_all_topic_names(self, print_out: bool = True) -> List[str]:
        """Returns all topics names.

        params
        ------
        print_out : bool
            If True, it prints the topics names.

        returns
        -------
        topicNames : List[str]
            List of topics names.
        """
        topicNames = []
        # Get all records for 'topics'
        records = self.__get_all_elements(table_name="topics", print_out=False)

        # Save all topics names
        for row in records:
            topicNames.append(row[1])  # 1 is for topic name TODO

        if print_out:
            print(f"Topics names are: {topicNames}")

        return topicNames

    def get_all_message_types(self, print_out: bool = False) -> List[str]:
        """Returns all messages types.

        params
        ------
        print_out : bool
            If True, it prints the messages types.

        returns
        -------
        msgsTypes : List[str]
            List of messages types.
        """
        msgsTypes = []
        # Get all records for 'topics'
        records = self.__get_all_elements(table_name="topics", print_out=False)

        # Save all message types
        for row in records:
            msgsTypes.append(row[2])  # 2 is for message type TODO

        if print_out:
            print(f"Messages types are: {msgsTypes}")

        return msgsTypes

    def get_message_type(self, topic_name: str, print_out=False) -> str:
        """Returns the message type of that specific topic.

        params
        ------
        topic_name : str
            Name of the topic to look for.

        print_out : bool
            If True, it prints the message type.

        returns
        -------
        msg_type : str
            Message type of the topic.
        """
        # Get all topics names and all message types
        topic_names = self.get_all_topic_names(print_out=False)
        msgs_types = self.get_all_message_types(print_out=False)

        # look for topic at the topic_names list, and find its index
        for index, element in enumerate(topic_names):
            if element == topic_name:
                msg_type = msgs_types[index]

        if print_out:
            print(f"Message type in {topic_name} is {msg_type}")

        return msg_type

    def __get_next_gap_timestamp(
        self,
        timestamp: float,
        time_gap: float,
    ) -> float:
        """Returns the next timestamp with the time gap."""
        timestamp = timestamp / 1e9
        datetime_obj = datetime.datetime.fromtimestamp(timestamp)
        next_datetime_obj = datetime_obj + datetime.timedelta(seconds=time_gap)

        self.logger.info(f"Next datetime: {next_datetime_obj}")

        return next_datetime_obj.timestamp() * 1e9

    def __save_iamge_from_msg(
        self,
        topic_name: str,
        timestamp: float,
        msg: bytes,
        output_folder: str = "output",
    ) -> bool:
        """Saves image from message."""
        # Deserialize the message
        msg_type = get_message(self.get_message_type(topic_name))
        deserialized_msg = deserialize_message(msg, msg_type)

        # Print or process the deserialized message
        self.logger.info(f"Save image from message at {timestamp}")

        bridge = cv_bridge.CvBridge()

        try:
            cv_image = bridge.imgmsg_to_cv2(
                deserialized_msg,
                desired_encoding="bgr8",
            )
            cv2.imwrite(f"{output_folder}/image-{timestamp}.png", cv_image)
        except cv_bridge.CvBridgeError as e:
            self.logger.error(e.args[0])
            return False

        return True

    def __save_all_images_from_topic(
        self,
        topic_name: str,
        output_folder: str = "output",
        time_gap: float = 1.0,
    ):
        """Saves all images from a specific topic.

        params
        ------
        topic_name : str
            Name of the topic to look for.

        returns
        ------
        None

        outputs
        -------
        Saves images in the output folder. (default: output/)
        """
        t, msgs = self.get_all_messages_in_topic(
            topic_name=topic_name,
            print_out=False,
        )

        msg_type = get_message(self.get_message_type(topic_name))

        self.logger.info(f"Message type: {msg_type}")

        next_timestamp = t[1]

        for timestamp, message in zip(t, msgs):
            if timestamp < next_timestamp:
                continue

            result = self.__save_iamge_from_msg(
                topic_name=topic_name,
                timestamp=timestamp,
                msg=message,
                output_folder=output_folder,
            )

            next_timestamp = self.__get_next_gap_timestamp(
                timestamp=timestamp,
                time_gap=time_gap,
            )

            if not result:
                self.logger.error("Could not save image.")
                break

        print("Images saved.")

        self.__close()

    def __save_csv_from_msg(
        self,
        topic_name: str,
        output_folder: str = "output",
        time_gap: float = 1.0,
    ):
        """Saves csv from message."""
        # Deserialize the message
        t, msgs = self.get_all_messages_in_topic(
            topic_name=topic_name,
            print_out=False,
        )

        msg_type = get_message(self.get_message_type(topic_name))

        next_timestamp = t[1]

        # Save the message in a csv file
        with open(f"{output_folder}/data.csv", "w") as f:
            csv_writer = csv.writer(f)

            for timestamp, message in zip(t, msgs):
                if timestamp < next_timestamp:
                    continue

                self.logger.info(
                    f"Save message from topic {topic_name} at {timestamp}"
                )  # noqa
                try:
                    deserialized_msg = deserialize_message(message, msg_type)
                    csv_writer.writerow([timestamp, deserialized_msg])
                except Exception as e:
                    self.logger.error(e.args[0])
                    print("Could not save csv.")
                    break

                next_timestamp = self.__get_next_gap_timestamp(
                    timestamp=timestamp,
                    time_gap=time_gap,
                )

        print("CSV saved.")

        self.__close()

    def save_img(
        self,
        topic_name: str = "/camera/color/image_raw",
        output_folder: str = "output",
        gap: float = 1.0,
    ):
        """Saves all images from a specific topic."""
        # check if the output folder exists and create it if it doesn't
        if not os.path.exists(output_folder):
            print("Creating output folder")
            os.makedirs(output_folder)

        print("Saving images...")

        self.__save_all_images_from_topic(
            topic_name=topic_name,
            output_folder=output_folder,
            time_gap=gap,
        )

    def save_csv(
        self,
        topic_name: str = "/camera/color/image_raw",
        output_folder: str = "output",
        gap: float = 1.0,
    ):
        """Saves all images from a specific topic."""
        # check if the output folder exists and create it if it doesn't
        if not os.path.exists(output_folder):
            print("Creating output folder")
            os.makedirs(output_folder)

        print("Saving csv...")

        self.__save_csv_from_msg(
            topic_name=topic_name,
            output_folder=output_folder,
            time_gap=gap,
        )
