ARG ROS_DISTRO=humble
FROM ros:${ROS_DISTRO}-ros-base

ENV ROS_DISTRO=${ROS_DISTRO}
ENV DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-vcstool \
    python3-rosdep \
    git \
    sshpass \
    libboost-all-dev \
    libeigen3-dev \
    python2.7 \
    python2-dev \
    libpython2-dev \
    ros-humble-rosbridge-server \
    ros-humble-rosapi \
    ros-humble-cv-bridge \
    ros-humble-image-transport \
    ros-humble-diagnostic-updater \
    ros-humble-robot-state-publisher \
    ros-humble-tf2-ros \
    ros-humble-naoqi-libqi \
    ros-humble-naoqi-libqicore \
    ros-humble-naoqi-bridge-msgs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws

COPY src/ ./src/

RUN bash -c "\
    source /opt/ros/${ROS_DISTRO}/setup.bash && \
    colcon build --symlink-install \
        --packages-select naoqi_driver naoqi_bridge_msgs \
        --cmake-args -DCMAKE_BUILD_TYPE=Release \
    "

RUN echo "source /ws/install/setup.bash" >> /root/.bashrc

CMD ["bash"]
