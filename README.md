# A.EdgeAI-rosbag-reader
Reader function to extract the data (including images) from rosbag of ROS2

```
연구개발과제명: 일상생활 공간에서 자율행동체의 복합작업 성공률 향상을 위한 자율행동체 엣지 AI SW 기술 개발

세부 개발 카테고리
● 지속적 지능 고도화를 위한 자율적 흐름제어 학습 프레임워크 기술 분석 및 설계
- 기밀성 데이터 활용 지능 고도화를 위한 엣지와 클라우드 분산 협업 학습 프레임워크 기술
- 엣지와 클라우드 협력 학습 간 최적 자원 활용 및 지속적 지능 배포를 위한 자율적 학습흐름제어 기술

개발 내용 
- 엣지와 클라우드 분산 협업을 위한 지속적 지능 배포 프레임워크 
- 자율행동체 엣지 기반 클러스터링 솔루션 및 분산 학습 프레임워크 개발
```

---

# ROS bag reader

This project is a simple project for reading rosbag files and saving images, messages to disk.

## Overview

- [rosbag_image_save](./rosbag_image_save.py) Read rosbag file and save images to disk.
- [rosbag_reader_cli](./rosbag_reader.py) CLI application for Rosbag file reading and save images to disk.

## Installation

- ROS2 Humble version required.

```bash
pip install -r requirements.txt
```

## Usage

### rosbag_image_save.py

- Execute python script to save images from rosbag file.
- If you want to save images from a specific rosbag file path and topic, you can change the topic name in the script.

```bash
# Run rosbag_image_save.py
python rosbag_image_save.py
```

### rosbag_reader.py CLI

- Rosbag reader CLI application for reading rosbag files.
- You can use the CLI application to save images to disk.
- You can use the CLI application to save messages to CSV file to disk.

```bash
# Run rosbag_reader.py
python rosbag_reader.py --path=<rosbag_file_path> <command> <options>

# Help rosbag_reader.py
python rosbag_reader.py --help
python rosbag_reader.py --path=<rosbag_file_path> --help

# Help rosbag_reader.py command
python rosbag_reader.py --path=<rosbag_file_path> <command> --help

# Example
# Get all topic names in the rosbag file.
python rosbag_reader.py --path=/home/user/data/rosbag/rosbag.db3 get_all_topic_names
# Get all message types in the rosbag file.
python rosbag_reader.py --path=/home/user/data/rosbag/rosbag.db3 get_all_message_types
# Get all messages in the topic.
python rosbag_reader.py --path=/home/user/data/rosbag/rosbag.db3 get_all_messages_in_topic -t /topic_name
# Get message type in the topic.
python rosbag_reader.py --path=/home/user/data/rosbag/rosbag.db3 get_message_type -t /topic_name
# Check whether the topic exists in the rosbag file.
python rosbag_reader.py --path=/home/user/data/rosbag/rosbag.db3 is_topic -t /topic_name
# Save messages in the topic as a CSV file.
python rosbag_reader.py --path=/home/user/data/rosbag/rosbag.db3 save_csv -t /topic_name -o output_folder -g 1.0
# Save images in the topic as a PNG file.
python rosbag_reader.py --path=/home/user/data/rosbag/rosbag.db3 save_img -t /topic_name -o output_folder -g 1.0
```

#### Commands

|Command|Description|Options|
|---|----|----|
|`get_all_messages_in_topic`|Returns all timestamps and messages at that topic. There is no deserialization for the BLOB data.|-t topic_name|
|`get_all_message_types`|Returns all message types in the rosbag file.|-|
|`get_all_topic_names`|Returns all topic names in the rosbag file.|-|
|`get_message_type`|Returns the message type of that specific topic.|-t topic_name|
|`is_topic`|Returns whether the topic exists in the rosbag file.|-t topic_name|
|`save_csv`|Saves the messages in the topic as a CSV file.|-t topic_name -o output_folder(default: output) -g time_gap(default: 1.0sec)|
|`save_img`|Saves the images in the topic as a PNG file.|-t topic_name -o output_folder(default: output) -g time_gap(default: 1.0sec)|

#### Logging

- You can change the logging level with the `--loglevel` option.

```bash
# Set logging level to DEBUG
python rosbag_reader.py --path=/home/user/data/rosbag/rosbag.db3 --loglevel=DEBUG get_all_topic_names
```


---

## Related Project

```
https://github.com/Open-Edge-Robotics/A.EdgeAI-fl-perception
To deploy Perception engine,  which is model resulted from Federated Learning 

https://github.com/Open-Edge-Robotics/A.RobotAI-ros2-streamer
To make and send stream of ROS 2 images captured from carmera attached to Robot.

https://github.com/Open-Edge-Robotics/A.EdgeAI-rosbag-reader
Reader function to extract the data (including images) from rosbag of ROS2

https://github.com/Open-Edge-Robotics/A.CloudAI-fl-flower
Flower Framework, which is Federated Learning to be used as Distributed Collaborative Learing Framework

https://github.com/Open-Edge-Robotics/A.CloudAI-kube-multi-ctl
Customized kubectl to manage multiple k8s master node (standalone node)

https://github.com/Open-Edge-Robotics/A.RobotAI-kube-crd  (ebme-crd)
Kubernetes custom resource definition to deploy the specific robot engines and applications
```
