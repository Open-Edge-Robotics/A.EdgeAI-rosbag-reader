import os
import fire
from utils.rosbag_read_data_helper import RosbagReadDataHelper

# def main():
    
#     os.chdir('/media/swstation/second/workspace-rosbag/rosbag-data')
#     os.getcwd()
    
#     bag_file = '/media/swstation/second/workspace-rosbag/rosbag-data/navibag/ros2bag_2024-04-25.14_47_52/ros2bag_2024-04-25.14_47_52_0.db3'
#     csv_file_path = '/media/swstation/second/workspace-rosbag/rosbag-data/csvfile/'

#     rosbag_read_data = RosbagReadDataHelper(bag_file, csv_file_path)
#     rosbag_read_data.rosbag2dataframe()
#     rosbag_read_data.close()
    
    
 

def main():
    fire.Fire(
        component=RosbagReadDataHelper,
        name="rosbag_read_data",
    )



# ======================
if __name__ == "__main__":
    main()    


# howto use it
# export bag_file='/media/swstation/second/workspace-rosbag/rosbag-data/navibag/ros2bag_2024-04-25.14_47_52/ros2bag_2024-04-25.14_47_52_0.db3'
# export csv_file_path='/media/swstation/second/workspace-rosbag/rosbag-data/csvfile/'
# python3 rosbag_read_data.py --bag_file=$bag_file --csv_file_path=$csv_file_path rosbag2dataframe



# added in 20240923


# navi_msgs_copy2ros.txt 
# ```
# sudo cp -r include/navi_msgs /opt/ros/humble/include/
# sudo cp -r local/lib/python3.10/dist-packages/navi_msgs /opt/ros/humble/local/lib/python3.10/dist-packages/
# sudo cp -r share/ament_index/resource_index/parent_prefix_path/navi_msgs /opt/ros/humble/share/ament_index/resource_index/parent_prefix_path/
# sudo cp -r share/ament_index/resource_index/packages/navi_msgs /opt/ros/humble/share/ament_index/resource_index/packages/
# sudo cp -r share/ament_index/resource_index/package_run_dependencies/navi_msgs /opt/ros/humble/share/ament_index/resource_index/package_run_dependencies/ 
# sudo cp -r share/ament_index/resource_index/rosidl_interfaces/navi_msgs /opt/ros/humble/share/ament_index/resource_index/rosidl_interfaces/
# ```

# sudo apt install ros-humbe-nav2-msgs
# git clone https://github.com/lge-ros2/lge-interfaces
# colcon build
# source navi_msgs_copy2ros.txt
# . /opt/ros/humble/setup.bash
# export bag_file='../rosbag-data/navibag/ros2bag_2024-04-25.14_47_52/ros2bag_2024-04-25.14_47_52_0.db3'
# export csv_file_path='../rosbag-data/csvfile/'
# python3 rosbag_read_data.py --bag_file=$bag_file --csv_file_path=$csv_file_path rosbag2dataframe
