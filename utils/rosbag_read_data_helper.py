# ref: https://medium.com/@mashruf.zaman/reading-ros2-db3-rosbag-file-in-python-76566521ce3d


import sqlite3
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message
import csv
# from std_msgs.msg import String
# from geometry_msgs.msg import PoseWithCovarianceStamped
# from geometry_msgs.msg import PoseWithCovariance
# from geometry_msgs.msg import Pose, Point, Quaternion
# from builtin_interfaces.msg import Time
# from geometry_msgs.msg import Twist
# from sensor_msgs.msg import LaserScan
# from nav_msgs.msg import Path
# from nav_msgs.msg import Odometry
# from navi_msgs.msg import Trajs
# from tf2_msgs.msg import TFMessage

import pandas as pd
import numpy as np
import seaborn as sns
import os
import datetime
from typing import Tuple, List, Any
import logging
from utils.logger import Logger


class RosbagReadDataHelper:

    def __init__(
        self,
        bag_file: str = "rosbag.db3",
        csv_file_path: str = '/media/swstation/second/workspace-rosbag/rosbag-data/csvfile/',
        loglevel: int = logging.ERROR
    ):
        self.logger = Logger(name="RosbagReader", level=loglevel)
        self.logger = self.logger.get_logger()

        self._conn = sqlite3.connect(bag_file)
        self._cursor = self._conn.cursor()

        self.logger.info(f"Connected to {bag_file}")
        
        self.bag_file = bag_file
        self.csv_file_path = csv_file_path
        
    # def connect(sqlite_file):
    #     conn = sqlite3.connect(sqlite_file)
    #     c = conn.cursor()
    #     return conn, c

    def close(self):
        """Close the connection to the database."""
        self.logger.info("Closing connection")
        self._conn.close()


    def getAllElements(self, table_name, print_out=False):
        """ Returns a dictionary with all elements of the table database.
        """
        # Get elements from table "table_name"
        self._cursor.execute('SELECT * from({})'.format(table_name))
        records = self._cursor.fetchall()
        if print_out:
            print("\nAll elements:")
            for row in records:
                print(row)
        return records

    def isTopic(self, topic_name, print_out=False):
        """ Returns topic_name header if it exists. If it doesn't, returns empty.
            It returns the last topic found with this name.
        """
        boolIsTopic = False
        topicFound = []

        # Get all records for 'topics'
        records = self.getAllElements('topics', print_out=False)

        # Look for specific 'topic_name' in 'records'
        for row in records:
            if(row[1] == topic_name): # 1 is 'name' TODO
                boolIsTopic = True
                topicFound = row
        if print_out:
            if boolIsTopic:
                # 1 is 'name', 0 is 'id' TODO
                print('\nTopic named', topicFound[1], ' exists at id ', topicFound[0] ,'\n')
            else:
                print('\nTopic', topic_name ,'could not be found. \n')

        return topicFound

    def getAllMessagesInTopic(self, topic_name, print_out=False):
        """ Returns all timestamps and messages at that topic.
        There is no deserialization for the BLOB data.
        """
        count = 0
        timestamps = []
        messages = []

        # Find if topic exists and its id
        topicFound = self.isTopic(topic_name, print_out=False)

        # If not find return empty
        if not topicFound:
            print('Topic', topic_name ,'could not be found. \n')
        else:
            records = self.getAllElements('messages', print_out=False)

            # Look for message with the same id from the topic
            for row in records:
                if row[1] == topicFound[0]:     # 1 and 0 is 'topic_id' TODO
                    count = count + 1           # count messages for this topic
                    timestamps.append(row[2])   # 2 is for timestamp TODO
                    messages.append(row[3])     # 3 is for all messages

            # Print
            if print_out:
                print('\nThere are ', count, 'messages in ', topicFound[1])

        return timestamps, messages

    def getAllTopicsNames(self, print_out=False):
        """ Returns all topics names.
        """
        topicNames = []
        # Get all records for 'topics'
        records = self.getAllElements('topics', print_out=False)

        # Save all topics names
        for row in records:
            topicNames.append(row[1])  # 1 is for topic name TODO
        if print_out:
            print('\nTopics names are:')
            print(topicNames)

        return topicNames

    def getAllMsgsTypes(self, print_out=False):
        """ Returns all messages types.
        """
        msgsTypes = []
        # Get all records for 'topics'
        records = self.getAllElements('topics', print_out=False)

        # Save all message types
        for row in records:
            msgsTypes.append(row[2])  # 2 is for message type TODO
        if print_out:
            print('\nMessages types are:')
            print(msgsTypes)

        return msgsTypes

    def getMsgType(self, topic_name, print_out=False):
        """ Returns the message type of that specific topic.
        """
        msg_type = []
        # Get all topics names and all message types
        topic_names = self.getAllTopicsNames(print_out=False)
        msgs_types = self.getAllMsgsTypes(print_out=False)

        # look for topic at the topic_names list, and find its index
        for index, element in enumerate(topic_names):
            if element == topic_name:
                msg_type = msgs_types[index]
        if print_out:
            print('\nMessage type in', topic_name, 'is', msg_type)

        return msg_type







    #####################################
    #  ROS2 Messge Analysis Functions   #
    #####################################

    # ======================
    # {'/tf_static': 'tf2_msgs/msg/TFMessage',
        #  '/tf': 'tf2_msgs/msg/TFMessage',
        #  '/navi_local_path': 'nav_msgs/msg/Path',
        #  '/navi_motion_traj': 'navi_msgs/msg/Trajs',
        #  '/odom': 'nav_msgs/msg/Odometry',
        #  '/received_global_plan': 'nav_msgs/msg/Path',
        #  '/scan': 'sensor_msgs/msg/LaserScan',
        #  '/cmd_vel': 'geometry_msgs/msg/Twist'}
        

    # {'/tf_static': 'tf2_msgs/msg/TFMessage',
    #  '/tf': 'tf2_msgs/msg/TFMessage',
    def get_tf2_msgs(self, timestamps, msgs, msg_type):

        # type_map = {topic_names[i]:topic_types[i] for i in range(len(topic_types))}
        # msg_type = get_message(type_map[topic_name])  # Assuming type_map is a dictionary mapping topic names to message types
        columns = {'Timestamp': 'int64', 'msg_timestamp': 'string', 'msg_sec': 'int64', 'msg_nanosec': 'int64', 'frame_id': 'string', 'child_frame_id': 'string', \
                'TX': 'float64', 'TY': 'float64', 'TZ': 'float64', 'RX': 'float64', 'RY': 'float64', 'RZ': 'float64', 'RW': 'float64'}
        schema = columns
        df = pd.DataFrame(columns=schema.keys()).astype(schema) 
        
        for timestamp, message in zip(timestamps, msgs):
            deserialized_msg = deserialize_message(message, msg_type)
            
            # print( type(deserialized_msg), deserialized_msg.get_fields_and_field_types() )
            
            sec = deserialized_msg.transforms[0].header.stamp.sec
            nanosec = deserialized_msg.transforms[0].header.stamp.nanosec
            frame_id = deserialized_msg.transforms[0].header.frame_id
            child_frame_id = deserialized_msg.transforms[0].child_frame_id

            tx = deserialized_msg.transforms[0].transform.translation.x 
            ty = deserialized_msg.transforms[0].transform.translation.y
            tz = deserialized_msg.transforms[0].transform.translation.z

            rx = deserialized_msg.transforms[0].transform.rotation.x 
            ry = deserialized_msg.transforms[0].transform.rotation.y
            rz = deserialized_msg.transforms[0].transform.rotation.z
            rw = deserialized_msg.transforms[0].transform.rotation.w
            
            # dt = pd.to_datetime(timestamp)
            # date_time = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            str_nanosec = str(nanosec)
            fill_zero = ''
            if len(str_nanosec) < 9:
                    for i in range(9 - len(str_nanosec)): 
                            fill_zero += '0'
                                                                    
            date_time = str(sec) + fill_zero + str(nanosec)
                            
            add_df = pd.DataFrame([{'Timestamp': timestamp, 'msg_timestamp': date_time, 'msg_sec': sec, 'msg_nanosec': nanosec, \
                                    'frame_id': frame_id, 'child_frame_id': child_frame_id, \
                                    'TX': tx, 'TY': ty, 'TZ':tz, 'RX': rx, 'RY': ry, 'RZ':rz, 'RW': rw}])
            df = pd.concat([df, add_df], axis=0)

            
        df['Timestamp'] =  df['Timestamp'].astype('int64')
        df['msg_timestamp'] = df['msg_timestamp'].astype('int64')
        df['delta_ns'] = df['Timestamp'] - df['msg_timestamp']
        df['delta_sec'] = df['delta_ns'] / 1e9        
        
        
        return df
                

    #  '/navi_local_path': 'nav_msgs/msg/Path',
    #  '/received_global_plan': 'nav_msgs/msg/Path',
    def get_nav_msgs(self, timestamps, msgs, msg_type):

        columns = {'Timestamp': 'int64', 'msg_timestamp': 'string', 'msg_sec': 'int64', 'msg_nanosec': 'int64', 'frame_id': 'string', \
                        'pose_index': 'int64'}
        schema = columns
        df = pd.DataFrame(columns=schema.keys()).astype(schema)
        
        columns = {'global_index': 'int64', 'local_index': 'int64', 'Timestamp': 'int64', 'msg_timestamp': 'string', 'msg_sec': 'int64', 'msg_nanosec': 'int64', 'frame_id': 'string', \
                    'PX': 'float64', 'PY': 'float64', 'PZ': 'float64', 'OX': 'float64', 'OY': 'float64', \
                    'OZ': 'float64', 'OW': 'float64'}
        schema = columns
        df_pose = pd.DataFrame(columns=schema.keys()).astype(schema)

        global_index = 0
        pose_index = 0
        
        for timestamp, message in zip(timestamps, msgs):
            deserialized_msg = deserialize_message(message, msg_type)
            
            # print( type(deserialized_msg), deserialized_msg.get_fields_and_field_types() )
            
            sec = deserialized_msg.header.stamp.sec
            nanosec = deserialized_msg.header.stamp.nanosec
            frame_id = deserialized_msg.header.frame_id

            # dt = pd.to_datetime(timestamp)
            # date_time = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            str_nanosec = str(nanosec)
            fill_zero = ''
            if len(str_nanosec) < 9:
                    for i in range(9 - len(str_nanosec)): 
                            fill_zero += '0'
                                                                    
            date_time = str(sec) + fill_zero + str(nanosec)
                            
            add_df = pd.DataFrame([{'Timestamp': timestamp, 'msg_timestamp': date_time, 'msg_sec': sec, 'msg_nanosec': nanosec, \
                                    'frame_id': frame_id, 'pose_index': pose_index}])
            df = pd.concat([df, add_df], axis=0)
                    
            ## =============================
            # local_index = 0
            pose_num = len(deserialized_msg.poses)
            
            for pose, local_index in zip(deserialized_msg.poses, range(pose_num)):
                sec = pose.header.stamp.sec
                nanosec = pose.header.stamp.nanosec
                frame_id = pose.header.frame_id
                
                px = pose.pose.position.x
                py = pose.pose.position.y
                pz = pose.pose.position.z
                                                
                ox = pose.pose.orientation.x
                oy = pose.pose.orientation.y
                oz = pose.pose.orientation.z
                ow = pose.pose.orientation.w
                    
                str_nanosec = str(nanosec)
                fill_zero = ''
                if len(str_nanosec) < 9:
                        for i in range(9 - len(str_nanosec)): 
                                fill_zero += '0'
                                                                        
                date_time = str(sec) + fill_zero + str(nanosec)
                                
                add_df_pose = pd.DataFrame([{'global_index': global_index, 'local_index': local_index, 'Timestamp': timestamp, 'msg_timestamp': date_time, 'msg_sec': sec, 'msg_nanosec': nanosec, \
                                        'frame_id': frame_id, 'PX': px, 'PY': py, 'PZ':pz, 'OX': ox, 'OY': oy, 'OZ':oz, 'OW': ow}])
                df_pose = pd.concat([df_pose, add_df_pose], axis=0)
                
            #     local_index += 1
            
            ## =============================

            pose_index += 1 
            global_index += 1
                
        return df, df_pose    

    #  '/navi_motion_traj': 'navi_msgs/msg/Trajs'
    def get_nav_msgs_trajs(self, timestamps, msgs, msg_type):
        columns = {'Timestamp': 'string', 'linear_x': 'float64', 'linear_y': 'float64', 'linear_z': 'float64', \
                        'angular_x': 'float64', 'angular_y': 'float64', 'angular_z': 'float64'}
        schema = columns
        df = pd.DataFrame(columns=schema.keys()).astype(schema) 
        pass

        return df

    #  '/odom': 'nav_msgs/msg/Odometry',
    def get_nav_msgs_odometry(self, timestamps, msgs, msg_type):
        
        columns = {'Timestamp': 'int64', 'msg_timestamp': 'string', 'msg_sec': 'int64', 'msg_nanosec': 'int64', 'frame_id': 'string', \
                'child_frame_id': 'string', 'PX': 'float64', 'PY': 'float64', 'PZ': 'float64', 'OX': 'float64', 'OY': 'float64', \
                'OZ': 'float64', 'OW': 'float64'}
        schema = columns
        df = pd.DataFrame(columns=schema.keys()).astype(schema)        
        
        for timestamp, message in zip(timestamps, msgs):
            deserialized_msg = deserialize_message(message, msg_type)
            
            # print( type(deserialized_msg), deserialized_msg.get_fields_and_field_types() )
            
            sec = deserialized_msg.header.stamp.sec
            nanosec = deserialized_msg.header.stamp.nanosec
            frame_id = deserialized_msg.header.frame_id

            child_frame_id = deserialized_msg.child_frame_id
            px = deserialized_msg.pose.pose.position.x
            py = deserialized_msg.pose.pose.position.y
            pz = deserialized_msg.pose.pose.position.z


            ox = deserialized_msg.pose.pose.orientation.x
            oy = deserialized_msg.pose.pose.orientation.y
            oz = deserialized_msg.pose.pose.orientation.z
            ow = deserialized_msg.pose.pose.orientation.w
            
            # dt = pd.to_datetime(timestamp)
            # date_time = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            str_nanosec = str(nanosec)
            fill_zero = ''
            if len(str_nanosec) < 9:
                    for i in range(9 - len(str_nanosec)): 
                            fill_zero += '0'
                                                                    
            date_time = str(sec) + fill_zero + str(nanosec)
                            
            add_df = pd.DataFrame([{'Timestamp': timestamp, 'msg_timestamp': date_time, 'msg_sec': sec, 'msg_nanosec': nanosec, \
                                    'frame_id': frame_id, 'child_frame_id': child_frame_id, \
                                    'PX': px, 'PY': py, 'PZ':pz, 'OX': ox, 'OY': oy, 'OZ':oz, 'OW': ow}])
            df = pd.concat([df, add_df], axis=0)

                    
        df['Timestamp'] =  df['Timestamp'].astype('int64')
        df['msg_timestamp'] = df['msg_timestamp'].astype('int64')
        df['delta_ns'] = df['Timestamp'] - df['msg_timestamp']
        df['delta_sec'] = df['delta_ns'] / 1e9   
        
        return df

    #  '/scan': 'sensor_msgs/msg/LaserScan'
    def get_sensor_msgs_laserscan(self, timestamps, msgs, msg_type):
        
        # columns = {'Timestamp': 'string', 'msg_timestamp': 'string', 'msg_sec': 'int64', 'msg_nanosec': 'int64', 'frame_id': 'string', \
        #     'angle_min': 'float64', 'angle_max': 'float64', 'angle_increment': 'float64', 'time_increment': 'float64', 'scan_time': 'float64', \
        #     'range_min': 'float64', 'range_max': 'float64'}
        # schema = columns
        # df = pd.DataFrame(columns=schema.keys()).astype(schema)       
        
        columns = {'Timestamp': 'string', 'msg_timestamp': 'string', 'msg_sec': 'int64', 'msg_nanosec': 'int64', 'frame_id': 'string', \
        'angle_min': 'float64', 'angle_max': 'float64', 'angle_increment': 'float64', 'time_increment': 'float64', 'scan_time': 'float64', \
        'range_min': 'float64', 'range_max': 'float64'}
        range_keys = ['range_'+str(x) for x in range(811)]
        range_values_format = ['float64']*811
        range_dict = {range_keys[i]: range_values_format[i] for i in range(len(range_keys))}

        schema = {}
        schema = columns.copy()
        schema.update(range_dict)   # 823
        df = pd.DataFrame(columns=schema.keys()).astype(schema)
        
        for timestamp, message in zip(timestamps, msgs):
            deserialized_msg = deserialize_message(message, msg_type)
            
            # print( type(deserialized_msg), deserialized_msg.get_fields_and_field_types() )
            
            sec = deserialized_msg.header.stamp.sec
            nanosec = deserialized_msg.header.stamp.nanosec
            frame_id = deserialized_msg.header.frame_id

            # dt = pd.to_datetime(timestamp)
            # date_time = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            str_nanosec = str(nanosec)
            fill_zero = ''
            if len(str_nanosec) < 9:
                    for i in range(9 - len(str_nanosec)): 
                            fill_zero += '0'
                                                                    
            date_time = str(sec) + fill_zero + str(nanosec)

            sec = deserialized_msg.header.stamp.sec
            nanosec = deserialized_msg.header.stamp.nanosec
            frame_id = deserialized_msg.header.frame_id
            angle_min = deserialized_msg.angle_min
            angle_max = deserialized_msg.angle_max
            angle_increment = deserialized_msg.angle_increment
            time_increment = deserialized_msg.time_increment
            scan_time = deserialized_msg.scan_time
            range_min = deserialized_msg.range_min
            range_max = deserialized_msg.range_max
            intensities = deserialized_msg.intensities
            range_values = deserialized_msg.ranges
            df_range_values = pd.DataFrame([range_values])
            df_range_values.columns = range_keys
                            
            add_df = pd.DataFrame([{'Timestamp': timestamp, 'msg_timestamp': date_time, 'msg_sec': sec, 'msg_nanosec': nanosec, 'frame_id': frame_id, \
                                'angle_min': angle_min, 'angle_max': angle_max, 'angle_increment': angle_increment, 'time_increment': time_increment, \
                                'scan_time': scan_time, 'range_min': range_min, 'range_max': range_max} ])
            df = pd.concat([df, add_df], axis=0)
            df = pd.concat([df, df_range_values], axis=0)

        
        # df['Timestamp'] =  df['Timestamp'].astype('int64')   #  ValueError: cannot convert float NaN to integer
        # df['msg_timestamp'] = df['msg_timestamp'].astype('int64')
        # df['delta_ns'] = df['Timestamp'] - df['msg_timestamp']
        # df['delta_sec'] = df['delta_ns'] / 1e9
        
        return df

    #  '/cmd_vel': 'geometry_msgs/msg/Twist'
    def get_geometry_msgs_twist(self, timestamps, msgs, msg_type):
        
        columns = {'Timestamp': 'string', 'linear_x': 'float64', 'linear_y': 'float64', 'linear_z': 'float64', \
                'angular_x': 'float64', 'angular_y': 'float64', 'angular_z': 'float64'}
        schema = columns
        df = pd.DataFrame(columns=schema.keys()).astype(schema)     
            
        for timestamp, message in zip(timestamps, msgs):
            deserialized_msg = deserialize_message(message, msg_type)
            
            # print( type(deserialized_msg), deserialized_msg.get_fields_and_field_types() )
            
            lx = deserialized_msg.linear.x
            ly = deserialized_msg.linear.y
            lz = deserialized_msg.linear.z
            ax = deserialized_msg.angular.x
            ay = deserialized_msg.angular.y
            az = deserialized_msg.angular.z
            
                            
            add_df = pd.DataFrame([ {'Timestamp': timestamp, 'linear_x': lx, 'linear_y': ly, 'linear_z': lz, \
                'angular_x': ax, 'angular_y': ay, 'angular_z': az} ])
            df = pd.concat([df, add_df], axis=0)


        # df = df.reset_index(drop=True)
        # df['Timestamp'] =  df['Timestamp'].astype('int64')
        # df['msg_timestamp'] = df['msg_timestamp'].astype('int64')
        # df['delta_ns'] = df['Timestamp'] - df['msg_timestamp']
        # df['delta_sec'] = df['delta_ns'] / 1e9   
        
        return df


    # '/amcl_pose' : 'geometry_msgs/msg/PoseWithCovarianceStamped'
    def get_geometry_msgs_posewithcovariancestamped(self, timestamps, msgs, msg_type):
        
        columns = {'Timestamp': 'string', 'msg_timestamp': 'string', 'msg_sec': 'int64', 'msg_nanosec': 'int64', 'PX': 'float64', 'PY': 'float64', 'PZ': 'float64', 'OX': 'float64', 'OY': 'float64', 'OZ': 'float64', 'OW': 'float64'}
        schema = columns
        df = pd.DataFrame(columns=schema.keys()).astype(schema)
        
        for timestamp, message in zip(timestamps, msgs):
            deserialized_msg = deserialize_message(message, msg_type)
            
            sec = deserialized_msg.header.stamp.sec
            nanosec = deserialized_msg.header.stamp.nanosec
            
            
            # dt = pd.to_datetime(timestamp)
            # date_time = dt.strftime("%Y-%m-%d %H:%M:%S.%f")
            str_nanosec = str(nanosec)
            fill_zero = ''
            if len(str_nanosec) < 9:
                    for i in range(9 - len(str_nanosec)): 
                            fill_zero += '0'
                                                                    
            
            date_time = str(sec) + fill_zero + str(nanosec)
                                    
                                    
            x = deserialized_msg.pose._pose.position.x
            y = deserialized_msg.pose._pose.position.y
            z = deserialized_msg.pose._pose.position.z
            
            ox = deserialized_msg.pose._pose.orientation.x
            oy = deserialized_msg.pose._pose.orientation.y
            oz = deserialized_msg.pose._pose.orientation.z
            ow = deserialized_msg.pose._pose.orientation.w
                            
            add_df = pd.DataFrame([{'Timestamp': timestamp, 'msg_timestamp': date_time, 'msg_sec': sec, 'msg_nanosec': nanosec, 'PX': x, 'PY': y, 'PZ':z, 'OX': ox, 'OY': oy, 'OZ':oz, 'OW': ow}])
            df = pd.concat([df, add_df], axis=0)
                    

        df = df.reset_index(drop=True)
        df['Timestamp'] =  df['Timestamp'].astype('int64')
        df['msg_timestamp'] = df['msg_timestamp'].astype('int64')
        df['delta_ns'] = df['Timestamp'] - df['msg_timestamp']
        df['delta_sec'] = df['delta_ns'] / 1e9    

        return df    


    ########################################
    #  ROS2 BAG file to Pandas Dataframe   #
    ########################################


    def rosbag2dataframe(self):
        
        topic_names = self.getAllTopicsNames(print_out=True)
        topic_types = self.getAllMsgsTypes(print_out=True)

        # topic_names = ['/tf_static', '/tf', '/navi_local_path', '/navi_motion_traj', '/odom', 'received_global_plan', '/scan', '/cmd_vel']

        type_map = {topic_names[i]:topic_types[i] for i in range(len(topic_types))}
        # type_map
        # {'/tf_static': 'tf2_msgs/msg/TFMessage',
        #  '/tf': 'tf2_msgs/msg/TFMessage',
        #  '/navi_local_path': 'nav_msgs/msg/Path',
        #  '/navi_motion_traj': 'navi_msgs/msg/Trajs',
        #  '/odom': 'nav_msgs/msg/Odometry',
        #  '/received_global_plan': 'nav_msgs/msg/Path',
        #  '/scan': 'sensor_msgs/msg/LaserScan',
        #  '/cmd_vel': 'geometry_msgs/msg/Twist'}

        # loop
        ### get all timestamps and all messages

        csv_file_path = self.csv_file_path

        csv_file_pathname = '' 
        csv_file_pathname2 = ''
        # for topic_name in topic_names:
        for topic_name, topic_type in zip(topic_names, topic_types):
            

            timestamps, msgs = self.getAllMessagesInTopic(topic_name, print_out=True)
            # Deserialize the message
            msg_type = get_message(type_map[topic_name])  # Assuming type_map is a dictionary mapping topic names to message types

            df = pd.DataFrame()
            df_pose = pd.DataFrame()
            if topic_type == 'tf2_msgs/msg/TFMessage':    # '/tf'   '/tf_static'

                df = self.get_tf2_msgs(timestamps, msgs, msg_type)
                csv_file_pathname = csv_file_path + topic_name + '.csv'       
                
            elif topic_type == 'navi_msgs/msg/Trajs':     # '/navi_motion_traj'
                csv_file_pathname = csv_file_path + topic_name + '.csv'
                print(' ===> (topic_name : topic_type) : ', topic_name,' : ', topic_type)
                pass
                
            elif topic_type == 'nav_msgs/msg/Odometry':       # 'nav_msgs/msg/Odometry'
            
                df = self.get_nav_msgs_odometry(timestamps, msgs, msg_type)
                csv_file_pathname = csv_file_path + topic_name + '.csv'            
                
            elif topic_type == 'nav_msgs/msg/Path':           # '/received_global_plan'    '/navi_local_path'
                df, df_pose = self.get_nav_msgs(timestamps, msgs, msg_type)
                csv_file_pathname = csv_file_path + topic_name + '.csv'
                csv_file_pathname2 = csv_file_path + topic_name + '2.csv'

                
            elif topic_type == 'sensor_msgs/msg/LaserScan':   # '/scan'
                df = self.get_sensor_msgs_laserscan(timestamps, msgs, msg_type)
                csv_file_pathname = csv_file_path + topic_name + '.csv'            

                
            elif topic_type == 'geometry_msgs/msg/Twist':     # '/cmd_vel'
                df = self.get_geometry_msgs_twist(timestamps, msgs, msg_type)
                csv_file_pathname = csv_file_path + topic_name + '.csv'            

            elif topic_type == 'geometry_msgs/msg/PoseWithCovarianceStamped':   #   '/amcl_pose' 
                df = self.get_geometry_msgs_posewithcovariancestamped(timestamps, msgs, msg_type)
                csv_file_pathname = csv_file_path + topic_name + '.csv'            

            else:
                csv_file_pathname = csv_file_path + topic_name + '.csv'   
                print('We have not seen format to input, therfore you need to register first your msg type through developer') 
                exit()
                
                
            print(' ===> (topic_name : topic_type) : ', topic_name,' : ', topic_type)
            print(df)         
            if topic_type == 'nav_msgs/msg/Path': 
                print(df_pose)                

            
            file = open(csv_file_pathname, 'w', newline='')
            df.to_csv(csv_file_pathname)
            file.close()        
            if topic_type == 'nav_msgs/msg/Path': 
                file = open(csv_file_pathname2, 'w', newline='')
                df_pose.to_csv(csv_file_pathname2)
                file.close()                 
        
        
        return df, df_pose      
      
          

