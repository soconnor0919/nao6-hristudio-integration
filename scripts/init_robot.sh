#!/bin/bash
# NAO6 Robot Initialization Script
# Disables autonomous life and wakes up the robot via SSH
set -e

ROBOT_IP="${NAO_IP:-10.0.0.42}"
ROBOT_USER="${NAO_USERNAME:-nao}"
ROBOT_PASS="${NAO_PASSWORD:-nao}"

echo "Initializing NAO6 robot at ${ROBOT_IP}..."

# Disable autonomous life via SSH
echo "Disabling autonomous life..."
sshpass -p "${ROBOT_PASS}" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "${ROBOT_USER}@${ROBOT_IP}" \
    "qicli call ALAutonomousLife.setState disabled" 2>/dev/null || \
    echo "Warning: Could not disable autonomous life (may already be disabled)"

sleep 1

# Wake up the robot
echo "Waking up robot..."
sshpass -p "${ROBOT_PASS}" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "${ROBOT_USER}@${ROBOT_IP}" \
    "qicli call ALMotion.wakeUp" 2>/dev/null || \
    echo "Warning: Could not wake up robot (may already be awake)"

sleep 1

# Go to neutral standing posture
echo "Setting neutral posture..."
sshpass -p "${ROBOT_PASS}" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    "${ROBOT_USER}@${ROBOT_IP}" \
    "qicli call ALRobotPosture.goToPosture Stand 0.5" 2>/dev/null || \
    echo "Warning: Could not set posture"

echo "✓ Robot initialization complete!"
echo "  - Autonomous life: disabled"
echo "  - Robot state: awake/standing"
echo "  - Ready for HRIStudio control"
