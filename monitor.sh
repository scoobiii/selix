#!/bin/bash

set -euo pipefail

# Emergency cleanup and monitoring script for Selix-AI
# Creates monitoring infrastructure and handles immediate resource issues

# Configuration
readonly MONITOR_DIR="/root/mobile_desk_vm_server"
readonly APP_MONITOR_DIR="/root/selix/monitoring"
readonly LOG_FILE="${MONITOR_DIR}/emergency_monitor.log"
readonly ALERTS_LOG="${MONITOR_DIR}/alerts.log"
readonly PID_FILE="${MONITOR_DIR}/monitor.pid"

# Create directory structure
setup_directories() {
    echo "$(date): Setting up monitoring directories..." >> "$LOG_FILE"
    
    mkdir -p "$MONITOR_DIR" "$APP_MONITOR_DIR"
    
    # Create subdirectories for different monitoring aspects
    mkdir -p "$MONITOR_DIR"/{logs,alerts,reports,scripts}
    mkdir -p "$APP_MONITOR_DIR"/{healthchecks,self_healing,performance,debugging}
    
    # Set proper permissions
    chmod 755 "$MONITOR_DIR" "$APP_MONITOR_DIR"
    chmod 644 "$LOG_FILE" "$ALERTS_LOG" 2>/dev/null || touch "$ALERTS_LOG"
}

# Immediate cleanup functions
perform_emergency_cleanup() {
    echo "$(date): Performing emergency cleanup..." >> "$LOG_FILE"
    
    # Clean pip cache if it's taking too much space
    if [ -d "/root/.cache/pip" ]; then
        local pip_size
        pip_size=$(du -sh /root/.cache/pip 2>/dev/null | cut -f1)
        echo "$(date): Pip cache size: $pip_size" >> "$LOG_FILE"
        
        if [[ $pip_size =~ [0-9]+[GT] ]]; then
            echo "$(date): Cleaning pip cache (too large: $pip_size)" >> "$LOG_FILE"
            rm -rf /root/.cache/pip/* 2>/dev/null || true
        fi
    fi
    
    # Clean npm cache if present
    if command -v npm >/dev/null 2>&1; then
        npm cache clean --force 2>/dev/null || true
    fi
        # Clean temporary files
    find /tmp -type f -atime +1 -delete 2>/dev/null || true
    find /root/selix -name "*.tmp" -delete 2>/dev/null || true
    
    # Clean old logs if they're too large
    find "$MONITOR_DIR"/logs -name "*.log" -size +100M -exec truncate -s 0 {} \; 2>/dev/null || true
}

# Resource monitoring function
check_resources() {
    local disk_usage mem_usage swap_usage
    disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    mem_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    swap_usage=$(free -s | awk 'NR==4{if($2>0) printf "%.0f", $3*100/$2; else print "0"}')
    
    echo "$(date): Disk: ${disk_usage}%, Memory: ${mem_usage}%, Swap: ${swap_usage}%" >> "$LOG_FILE"
    
    # Return codes for alerting
    if [ "$disk_usage" -gt 90 ] || [ "$mem_usage" -gt 90 ] || [ "$swap_usage" -gt 80 ]; then
        return 1
    fi
    return 0
}

# Generate alerts
generate_alert() {
    local alert_type="$1"
    local message="$2"
    local severity="$3"
    
    local alert_msg="[$(date)] $severity - $alert_type: $message"
    echo "$alert_msg" >> "$ALERTS_LOG"
    
    # Log to main log as well
    echo "$alert_msg" >> "$LOG_FILE"
    
    # Send to app (placeholder - customize based on your app's notification system)
    send_to_app "$alert_type" "$message" "$severity"
    
    # External notification to infrastructure manager (customize endpoint)
    send_external_notification "$alert_type" "$message" "$severity"
}

send_to_app() {
    local type="$1"
    local msg="$2"
    local severity="$3"
    
    # Placeholder for app-specific alert mechanism
    # This could be writing to a specific file watched by your app,    # making an API call, etc.
    local app_alert_file="${APP_MONITOR_DIR}/app_alerts.txt"
    echo "$(date)|$type|$severity|$msg" >> "$app_alert_file"
    
    # Keep only last 100 alerts
    tail -n 100 "$app_alert_file" > "${app_alert_file}.tmp" && mv "${app_alert_file}.tmp" "$app_alert_file"
}

send_external_notification() {
    local type="$1"
    local msg="$2"
    local severity="$3"
    
    # Placeholder for external notification
    # Customize this to send to your infrastructure manager
    # Could be email, webhook, SMS, etc.
    echo "$(date) EXTERNAL_ALERT: [$severity] $type - $msg" >> "${MONITOR_DIR}/external_notifications.log"
    
    # Example: send to a webhook (uncomment and customize if needed)
    # curl -X POST -H "Content-Type: application/json" \
    #   -d "{\"type\":\"$type\",\"message\":\"$msg\",\"severity\":\"$severity\"}" \
    #   "https://your-webhook-endpoint.com/alerts" 2>/dev/null || true
}

# Self-healing functions
detect_and_fix_lag() {
    echo "$(date): Checking for performance issues..." >> "$LOG_FILE"
    
    # Check for stuck processes
    local stuck_processes
    stuck_processes=$(ps aux | awk '$8 ~ /^[DR]/ && $10 > 1000 {print $2":"$11}' 2>/dev/null || true)
    
    if [ -n "$stuck_processes" ]; then
        echo "$(date): Found stuck processes: $stuck_processes" >> "$LOG_FILE"
        generate_alert "STUCK_PROCESSES" "Found processes in D/R state: $stuck_processes" "HIGH"
        
        # Try to interrupt them gently first
        while IFS=':' read -r pid cmd; do
            if kill -0 "$pid" 2>/dev/null; then
                echo "$(date): Attempting to interrupt process $pid ($cmd)" >> "$LOG_FILE"
                kill -INT "$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null
            fi
        done <<< "$stuck_processes"
    fi
    
    # Check for high CPU usage processes
    local high_cpu_procs
    high_cpu_procs=$(ps aux --sort=-%cpu | awk 'NR<=10 && NR>1 && $3 > 50 {print $2":"$11":"$3"%"}' 2>/dev/null || true)
    
    if [ -n "$high_cpu_procs" ]; then        echo "$(date): High CPU processes detected:" >> "$LOG_FILE"
        echo "$high_cpu_procs" >> "$LOG_FILE"
        
        # Kill processes over 90% CPU if they're not critical
        while IFS=':' read -r pid cmd cpu; do
            local cpu_num=$(echo "$cpu" | cut -d'%' -f1)
            if [ "$cpu_num" -gt 90 ]; then
                if ! echo "$cmd" | grep -E "(kthreadd|migration|ksoftirqd|rcu_|kworker|kswapd|pdflush|jbd2)" >/dev/null; then
                    generate_alert "HIGH_CPU" "Killing process $pid ($cmd) with ${cpu} CPU usage" "MEDIUM"
                    kill -TERM "$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null
                fi
            fi
        done <<< "$high_cpu_procs"
    fi
    
    # Check for memory pressure and take action
    if check_resources; then
        echo "$(date): Resources look normal" >> "$LOG_FILE"
    else
        echo "$(date): Resource pressure detected, taking corrective actions" >> "$LOG_FILE"
        
        # Drop caches (safe operation)
        sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
        
        # Restart problematic services if identified
        restart_problematic_services
    fi
}

restart_problematic_services() {
    # Restart the main API if it's consuming too many resources
    local api_pid
    api_pid=$(pgrep -f "src.api.main_v4" | head -n1)
    if [ -n "$api_pid" ] && kill -0 "$api_pid" 2>/dev/null; then
        local api_rss
        api_rss=$(ps -p "$api_pid" -o rss= 2>/dev/null || echo "0")
        if [ "$api_rss" -gt 1048576 ]; then  # More than 1GB
            generate_alert "SERVICE_RESTART" "Restarting API service due to high memory usage ($((api_rss / 1024)) MB)" "MEDIUM"
            kill -TERM "$api_pid" 2>/dev/null || kill -KILL "$api_pid" 2>/dev/null
            sleep 2
            # Optionally restart the service here
            # cd /root/selix && source venv/bin/activate && python -m src.api.main_v4 &
        fi
    fi
    
    # Restart worker if needed
    local worker_pid
    worker_pid=$(pgrep -f "src.selix.worker_v4" | head -n1)
    if [ -n "$worker_pid" ] && kill -0 "$worker_pid" 2>/dev/null; then
        local worker_rss        worker_rss=$(ps -p "$worker_pid" -o rss= 2>/dev/null || echo "0")
        if [ "$worker_rss" -gt 524288 ]; then  # More than 512MB
            generate_alert "SERVICE_RESTART" "Restarting worker service due to high memory usage ($((worker_rss / 1024)) MB)" "MEDIUM"
            kill -TERM "$worker_pid" 2>/dev/null || kill -KILL "$worker_pid" 2>/dev/null
        fi
    fi
}

# Main monitoring loop
monitor_loop() {
    echo "$(date): Starting monitoring loop..." >> "$LOG_FILE"
    
    while true; do
        # Perform health checks
        if ! check_resources; then
            generate_alert "RESOURCE_EXHAUSTION" "High resource usage detected" "CRITICAL"
        fi
        
        # Detect and fix performance issues
        detect_and_fix_lag
        
        # Check disk space specifically
        local disk_percent
        disk_percent=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
        if [ "$disk_percent" -gt 95 ]; then
            generate_alert "DISK_SPACE_CRITICAL" "Disk usage at ${disk_percent}% - performing emergency cleanup" "CRITICAL"
            perform_emergency_cleanup
        elif [ "$disk_percent" -gt 90 ]; then
            generate_alert "DISK_SPACE_WARNING" "Disk usage at ${disk_percent}%" "WARNING"
            perform_emergency_cleanup
        fi
        
        # Memory check
        local mem_percent
        mem_percent=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
        if [ "$mem_percent" -gt 95 ]; then
            generate_alert "MEMORY_CRITICAL" "Memory usage at ${mem_percent}%" "CRITICAL"
            # Trigger garbage collection and cleanup
            sync && echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
        elif [ "$mem_percent" -gt 90 ]; then
            generate_alert "MEMORY_WARNING" "Memory usage at ${mem_percent}%" "WARNING"
        fi
        
        # Check if monitored services are running
        if ! pgrep -f "src.api.main_v4" >/dev/null; then
            generate_alert "SERVICE_DOWN" "API service appears to be down" "CRITICAL"
        fi
        
        if ! pgrep -f "src.selix.worker_v4" >/dev/null; then
            generate_alert "SERVICE_DOWN" "Worker service appears to be down" "CRITICAL"        fi
        
        # Sleep before next check
        sleep 30
    done
}

# Cleanup function
cleanup() {
    echo "$(date): Stopping monitor..." >> "$LOG_FILE"
    rm -f "$PID_FILE"
    exit 0
}

# Setup signal handlers
trap cleanup SIGTERM SIGINT

# Main execution
main() {
    echo "$(date): Starting emergency monitoring and cleanup..." >> "$LOG_FILE"
    
    # Create directory structure
    setup_directories
    
    # Perform immediate cleanup
    perform_emergency_cleanup
    
    # Check if already running
    if [ -f "$PID_FILE" ]; then
        if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "$(date): Monitor already running, exiting." >> "$LOG_FILE"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi
    
    # Write PID
    echo $$ > "$PID_FILE"
    
    # Run the monitoring loop
    monitor_loop
}

# Run main function
main "$@"
