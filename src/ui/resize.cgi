#!/bin/bash
################################################################################################
# OpenSpeedTest Resize CGI - returns NAS hostname + client IP, resizes downloading file
################################################################################################

PKG_NAME="OpenSpeedTest"
PKG_ROOT="/var/packages/${PKG_NAME}"
TARGET_DIR="${PKG_ROOT}/target"
UI_DIR="${TARGET_DIR}/ui"
DOWNLOAD_FILE="${UI_DIR}/downloading"
LOG_DIR="${PKG_ROOT}/var"
LOG_FILE="${LOG_DIR}/resize.log"

mkdir -p "${LOG_DIR}"
touch "${LOG_FILE}"
chmod 644 "${LOG_FILE}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "${LOG_FILE}"
}

# HTTP headers
echo "Content-Type: application/json; charset=utf-8"
echo "Access-Control-Allow-Origin: *"
echo "Access-Control-Allow-Methods: GET, POST"
echo "Access-Control-Allow-Headers: Content-Type"
echo ""

# Read exactly CONTENT_LENGTH bytes instead of waiting for EOF
read -r -n "${CONTENT_LENGTH:-0}" POST_DATA

get_param() {
    echo "$POST_DATA" | tr '&' '\n' | grep "^${1}=" | head -1 | sed "s/^${1}=//" | sed 's/+/ /g' | sed 's/%\([0-9A-Fa-f][0-9A-Fa-f]\)/\\x\1/g' | xargs -0 printf '%b'
}

ACTION=$(get_param "action")
NAS_HOSTNAME=$(hostname 2>/dev/null || echo "NAS")
CLIENT_IP="${REMOTE_ADDR:-unknown}"

case "$ACTION" in
    info)
        CURRENT_SIZE_MB=$(( $(stat -c%s "$DOWNLOAD_FILE" 2>/dev/null || echo 0) / 1048576 ))
        echo "{\"success\":true, \"nas_hostname\":\"${NAS_HOSTNAME}\", \"client_ip\":\"${CLIENT_IP}\", \"current_size_mb\":${CURRENT_SIZE_MB}}"
        ;;

    resize)
        SIZE_MB=$(get_param "size_mb")

        # Validate size_mb is a positive integer and within allowed presets
        case "$SIZE_MB" in
            500|1000|1500|2000|3000|4000) ;;
            *)
                echo "{\"success\":false, \"message\":\"Invalid size. Allowed: 500, 1024, 1536, 2048, 3072, 4096\"}"
                exit 0
                ;;
        esac

        log "Resizing downloading file to ${SIZE_MB}MB (requested by ${CLIENT_IP})"

        if dd if=/dev/zero of="${DOWNLOAD_FILE}" bs=1M count="${SIZE_MB}" 2>/dev/null; then
            log "Successfully resized downloading file to ${SIZE_MB}MB"
            echo "{\"success\":true, \"message\":\"Download test file resized to ${SIZE_MB}MB\", \"size_mb\":${SIZE_MB}}"
        else
            log "Failed to resize downloading file to ${SIZE_MB}MB"
            echo "{\"success\":false, \"message\":\"Failed to resize download test file\"}"
        fi
        ;;

    *)
        echo "{\"success\":false, \"message\":\"Unknown action\"}"
        ;;
esac
