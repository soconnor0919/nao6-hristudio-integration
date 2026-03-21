#!/bin/bash
#
# NAO6 HRIStudio Integration Startup Script
#
# This script provides a comprehensive startup sequence for integrating NAO6 robots
# with the HRIStudio platform. It handles environment setup, connectivity checks,
# robot wake-up, ROS2 launch, and monitoring.
#
# Usage:
#   ./start_nao6_hristudio.sh [OPTIONS]
#
# Options:
#   --nao-ip IP        NAO robot IP address (default: nao.local)
#   --password PASS    NAO robot password (default: robolab)
#   --bridge-port PORT WebSocket bridge port (default: 9090)
#   --production       Use production launch configuration
#   --enhanced         Use enhanced launch configuration with monitoring
#   --no-wake          Skip automatic robot wake-up
#   --check-only       Only perform connectivity checks
#   --help             Show this help message
#

set -e  # Exit on any error

# =================================================================
# CONFIGURATION AND DEFAULTS
# =================================================================

# Default configuration
NAO_IP="${NAO_IP:-nao.local}"
NAO_PASSWORD="${NAO_PASSWORD:-robolab}"
NAO_USERNAME="${NAO_USERNAME:-nao}"
BRIDGE_PORT="${BRIDGE_PORT:-9090}"
ROS_WS="${HOME}/naoqi_ros2_ws"
HRISTUDIO_DIR="${HOME}/Documents/Projects/hristudio"

# Runtime options
LAUNCH_CONFIG="production"  # production, enhanced, or basic
AUTO_WAKE_UP=true
CHECK_ONLY=false
VERBOSE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =================================================================
# UTILITY FUNCTIONS
# =================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}[DEBUG]${NC} $1"
    fi
}

show_header() {
    echo -e "${CYAN}"
    echo "================================================================="
    echo "         NAO6 HRIStudio Integration Startup Script"
    echo "================================================================="
    echo -e "${NC}"
    echo "Robot IP:     $NAO_IP"
    echo "Bridge Port:  $BRIDGE_PORT"
    echo "Launch Mode:  $LAUNCH_CONFIG"
    echo "Auto Wake-up: $AUTO_WAKE_UP"
    echo "ROS Workspace: $ROS_WS"
    echo ""
}

show_help() {
    echo "NAO6 HRIStudio Integration Startup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --nao-ip IP        NAO robot IP address (default: $NAO_IP)"
    echo "  --password PASS    NAO robot password (default: $NAO_PASSWORD)"
    echo "  --username USER    NAO robot username (default: $NAO_USERNAME)"
    echo "  --bridge-port PORT WebSocket bridge port (default: $BRIDGE_PORT)"
    echo "  --production       Use production launch configuration (default)"
    echo "  --enhanced         Use enhanced launch with full monitoring"
    echo "  --basic            Use basic launch configuration"
    echo "  --no-wake          Skip automatic robot wake-up"
    echo "  --check-only       Only perform connectivity checks"
    echo "  --verbose          Enable verbose logging"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Start with defaults"
    echo "  $0 --nao-ip 192.168.1.100            # Custom robot IP"
    echo "  $0 --enhanced --verbose               # Enhanced mode with debug"
    echo "  $0 --check-only                      # Just check connectivity"
    echo ""
}

# =================================================================
# ARGUMENT PARSING
# =================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --nao-ip)
            NAO_IP="$2"
            shift 2
            ;;
        --password)
            NAO_PASSWORD="$2"
            shift 2
            ;;
        --username)
            NAO_USERNAME="$2"
            shift 2
            ;;
        --bridge-port)
            BRIDGE_PORT="$2"
            shift 2
            ;;
        --production)
            LAUNCH_CONFIG="production"
            shift
            ;;
        --enhanced)
            LAUNCH_CONFIG="enhanced"
            shift
            ;;
        --basic)
            LAUNCH_CONFIG="basic"
            shift
            ;;
        --no-wake)
            AUTO_WAKE_UP=false
            shift
            ;;
        --check-only)
            CHECK_ONLY=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# =================================================================
# MAIN FUNCTIONS
# =================================================================

check_prerequisites() {
    log_step "Checking prerequisites..."

    # Check if ROS2 workspace exists
    if [ ! -d "$ROS_WS" ]; then
        log_error "ROS2 workspace not found at $ROS_WS"
        log_info "Please ensure the NAOqi ROS2 workspace is set up"
        return 1
    fi

    # Check if launch files exist
    if [ ! -f "$ROS_WS/src/nao_launch/launch/nao6_production.launch.py" ]; then
        log_warning "Production launch file not found - using basic configuration"
        LAUNCH_CONFIG="basic"
    fi

    # Check if HRIStudio directory exists
    if [ ! -d "$HRISTUDIO_DIR" ]; then
        log_warning "HRIStudio directory not found at $HRISTUDIO_DIR"
    fi

    # Check for required tools
    local missing_tools=()

    if ! command -v ping >/dev/null 2>&1; then
        missing_tools+=("ping")
    fi

    if ! command -v sshpass >/dev/null 2>&1; then
        missing_tools+=("sshpass")
    fi

    if ! command -v ros2 >/dev/null 2>&1; then
        missing_tools+=("ros2")
    fi

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install with: sudo apt install ${missing_tools[*]}"
        return 1
    fi

    log_success "Prerequisites check passed"
    return 0
}

test_robot_connectivity() {
    log_step "Testing robot connectivity..."

    # Test basic network connectivity
    log_verbose "Testing ping to $NAO_IP..."
    if ! ping -c 3 -W 5 "$NAO_IP" >/dev/null 2>&1; then
        log_error "Cannot ping robot at $NAO_IP"
        log_info "Check network connection and robot IP address"
        return 1
    fi

    # Test NAOqi service port
    log_verbose "Testing NAOqi service on port 9559..."
    if ! timeout 5 bash -c "echo >/dev/tcp/$NAO_IP/9559" 2>/dev/null; then
        log_error "Cannot connect to NAOqi service on $NAO_IP:9559"
        log_info "Check if robot is powered on and NAOqi is running"
        return 1
    fi

    # Test SSH connectivity
    log_verbose "Testing SSH connectivity..."
    if ! timeout 10 sshpass -p "$NAO_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=5 "$NAO_USERNAME@$NAO_IP" "echo 'SSH test successful'" >/dev/null 2>&1; then
        log_warning "SSH connectivity test failed - wake-up may not work"
        log_info "Check username/password: $NAO_USERNAME / [password hidden]"
    fi

    log_success "Robot connectivity OK"
    return 0
}

wake_up_robot() {
    if [ "$AUTO_WAKE_UP" != true ]; then
        log_info "Skipping robot wake-up (--no-wake specified)"
        return 0
    fi

    log_step "Waking up NAO robot..."

    local wake_command="python2 -c \"
import sys
sys.path.append('/opt/aldebaran/lib/python2.7/site-packages')
try:
    import naoqi
    motion = naoqi.ALProxy('ALMotion', '127.0.0.1', 9559)
    motion.wakeUp()
    print('Robot awakened successfully')
except Exception as e:
    print('Wake-up failed: ' + str(e))
    exit(1)
\""

    if sshpass -p "$NAO_PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$NAO_USERNAME@$NAO_IP" "$wake_command" 2>/dev/null; then
        log_success "Robot awakened successfully"
        sleep 2  # Give robot time to fully wake up
        return 0
    else
        log_warning "Automatic wake-up failed"
        log_info "You may need to press the chest button for 3 seconds"
        log_info "Or manually wake up the robot and continue"
        return 1
    fi
}

check_port_availability() {
    log_step "Checking port availability..."

    # Check if bridge port is already in use
    if ss -an | grep -q ":$BRIDGE_PORT.*LISTEN"; then
        log_error "Port $BRIDGE_PORT is already in use"
        log_info "Kill existing processes or use a different port"
        log_info "To kill: sudo fuser -k $BRIDGE_PORT/tcp"
        return 1
    fi

    log_success "Port $BRIDGE_PORT is available"
    return 0
}

setup_ros_environment() {
    log_step "Setting up ROS2 environment..."

    # Source ROS2
    if [ -f "/opt/ros/humble/setup.bash" ]; then
        source /opt/ros/humble/setup.bash
        log_verbose "Sourced ROS2 Humble"
    else
        log_error "ROS2 Humble not found"
        return 1
    fi

    # Source workspace
    if [ -f "$ROS_WS/install/setup.bash" ]; then
        source "$ROS_WS/install/setup.bash"
        log_verbose "Sourced NAOqi ROS2 workspace"
    else
        log_error "NAOqi ROS2 workspace not built"
        log_info "Run: cd $ROS_WS && colcon build"
        return 1
    fi

    log_success "ROS2 environment ready"
    return 0
}

launch_ros_integration() {
    log_step "Launching ROS2 NAO integration..."

    # Determine launch file
    local launch_file
    case $LAUNCH_CONFIG in
        production)
            launch_file="nao6_production.launch.py"
            ;;
        enhanced)
            launch_file="nao6_hristudio_enhanced.launch.py"
            ;;
        basic)
            launch_file="nao6_hristudio.launch.py"
            ;;
        *)
            log_error "Unknown launch configuration: $LAUNCH_CONFIG"
            return 1
            ;;
    esac

    local full_launch_path="$ROS_WS/install/nao_launch/share/nao_launch/launch/$launch_file"

    if [ ! -f "$full_launch_path" ]; then
        log_warning "Launch file not found: $launch_file"
        log_info "Falling back to basic launch configuration"
        launch_file="nao6_hristudio.launch.py"
        full_launch_path="$ROS_WS/install/nao_launch/share/nao_launch/launch/$launch_file"
    fi

    # Build launch command
    local launch_cmd="ros2 launch nao_launch $launch_file"
    launch_cmd="$launch_cmd nao_ip:=$NAO_IP"
    launch_cmd="$launch_cmd password:=$NAO_PASSWORD"
    launch_cmd="$launch_cmd username:=$NAO_USERNAME"
    launch_cmd="$launch_cmd bridge_port:=$BRIDGE_PORT"

    if [ "$AUTO_WAKE_UP" = true ]; then
        launch_cmd="$launch_cmd auto_wake_up:=true"
    else
        launch_cmd="$launch_cmd auto_wake_up:=false"
    fi

    log_info "Launch command: $launch_cmd"
    log_info "Press Ctrl+C to stop the integration"
    echo ""

    # Execute launch
    cd "$ROS_WS"
    exec $launch_cmd
}

show_status_summary() {
    echo ""
    log_success "NAO6 HRIStudio Integration Status:"
    echo "  🤖 Robot IP:       $NAO_IP"
    echo "  🌐 WebSocket:      ws://localhost:$BRIDGE_PORT"
    echo "  📦 Launch Config:  $LAUNCH_CONFIG"
    echo "  🔧 Workspace:      $ROS_WS"
    echo ""
    echo "Next steps:"
    echo "  1. Start HRIStudio: cd $HRISTUDIO_DIR && bun dev"
    echo "  2. Open test page:  http://localhost:3000/nao-test"
    echo "  3. Click 'Connect' to establish WebSocket connection"
    echo "  4. Try robot commands and create experiments!"
    echo ""
}

cleanup_on_exit() {
    log_info "Cleaning up..."
    # Kill any background processes if needed
    exit 0
}

# =================================================================
# MAIN EXECUTION
# =================================================================

main() {
    # Set up signal handlers
    trap cleanup_on_exit EXIT INT TERM

    # Show header
    show_header

    # Run prerequisite checks
    if ! check_prerequisites; then
        exit 1
    fi

    # Test robot connectivity
    if ! test_robot_connectivity; then
        log_error "Robot connectivity test failed"
        exit 1
    fi

    # If only checking connectivity, exit here
    if [ "$CHECK_ONLY" = true ]; then
        log_success "All connectivity checks passed!"
        show_status_summary
        exit 0
    fi

    # Wake up robot
    if ! wake_up_robot; then
        log_warning "Robot wake-up failed, but continuing..."
        log_info "Please ensure robot is awake before sending movement commands"
    fi

    # Check port availability
    if ! check_port_availability; then
        exit 1
    fi

    # Setup ROS environment
    if ! setup_ros_environment; then
        exit 1
    fi

    # Show final status
    show_status_summary

    # Launch ROS integration
    log_info "Starting ROS2 launch - this will run until interrupted..."
    sleep 2
    launch_ros_integration
}

# Run main function
main "$@"
