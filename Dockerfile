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
    && rm -rf /var/lib/apt/lists/*

WORKDIR /ws

# Clone submodules if src/ is empty (happens when submodules aren't initialized on host)
RUN if [ ! -f "src/naoqi_libqi/CMakeLists.txt" ]; then \
        echo "Initializing git submodules..." && \
        git clone --depth 1 https://github.com/ros-naoqi/libqi.git src/naoqi_libqi && \
        cd src/naoqi_libqi && git submodule update --init --recursive && cd ../.. && \
        git clone --depth 1 https://github.com/ros-naoqi/libqicore.git src/naoqi_libqicore && \
        cd src/naoqi_libqicore && git submodule update --init --recursive && cd ../.. && \
        git clone --depth 1 https://github.com/ros-naoqi/naoqi_bridge_msgs2.git src/naoqi_bridge_msgs && \
        git clone --depth 1 https://github.com/ros-naoqi/naoqi_driver2.git src/naoqi_driver2 && \
        git clone --depth 1 https://github.com/soconnor0919/nao_launch.git src/nao_launch; \
    fi

COPY src/ ./src/

RUN bash -c "\
    source /opt/ros/${ROS_DISTRO}/setup.bash && \
    colcon build --symlink-install \
        --packages-select naoqi_libqi naoqi_libqicore naoqi_bridge_msgs naoqi_driver \
        --cmake-args -DCMAKE_BUILD_TYPE=Release \
    "

RUN echo "source /ws/install/setup.bash" >> /root/.bashrc

CMD ["bash"]
