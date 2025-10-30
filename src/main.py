import pathlib
import time
import os
import json
import sys
import logging

# Import configuration
from config import (
    setup_logger,
    LOG_FORMAT,
    REQUIRED_ENV_VARS,
    OPTIONAL_ENV_VARS,
    TELEGRAM_CHAT_ID,
    TELEGRAM_TOKEN,
    SYNOLOGY_URL,
    SYNOLOGY_LOGIN,
    SYNOLOGY_PASSWORD,
    SYNOLOGY_OTP,
    CONFIG_FILE,
    VIDEO_FILE,
    VIDEO_SEGMENT_DURATION,
    WEBHOOK_TIMEOUT,
    API_TIMEOUT,
    DEPENDENCIES,
)

# Import utilities
from utils import ensure_module_installed

# Setup logger
log = setup_logger(__name__)

# Auto-install required modules
telebot = ensure_module_installed("telebot", DEPENDENCIES["telebot"])
flask_module = ensure_module_installed("flask", DEPENDENCIES["flask"])
requests = ensure_module_installed("requests", DEPENDENCIES["requests"])

# Import Flask components
Flask = flask_module.Flask
request = flask_module.request
abort = flask_module.abort

# ============================================================================
# VALIDATION AND INITIALIZATION
# ============================================================================


def validate_required_env():
    """Validate that all required environment variables are set"""
    missing = []
    for var_name in REQUIRED_ENV_VARS:
        if var_name not in os.environ:
            missing.append(var_name)

    if missing:
        for var in missing:
            log.error(f"{var} does not exist. Please configure environment")
        sys.exit(1)

    log.info(f"All required environment variables are set")


# Validate environment
validate_required_env()

# Initialize Telegram bot
chat_id = TELEGRAM_CHAT_ID
token = TELEGRAM_TOKEN
tg_bot = telebot.TeleBot(token)
log.info(f"Telegram bot initialized for chat {chat_id}")

# Initialize Synology configuration
syno_url = SYNOLOGY_URL
syno_login = SYNOLOGY_LOGIN
syno_pass = SYNOLOGY_PASSWORD
syno_otp = SYNOLOGY_OTP
config_file = CONFIG_FILE

# Camera movement tracking (video offset tracking per camera)
arr_cam_move = {}
cam_load = {}
syno_sid = None


# Send Telegram message
def send_cammessage(message):
    """Send a text message to the configured Telegram chat

    Args:
        message (str): Message text to send

    Returns:
        None
    """
    try:
        tg_bot.send_message(chat_id, message)
        log.debug(f"Message sent to Telegram: {message[:50]}...")
    except Exception as e:
        log.error(f"Failed to send message to Telegram: {e}")


def send_camvideo(videofile, cam_id):
    """Send video to Telegram chat with camera name as caption

    Args:
        videofile (str): Path to the video file to send
        cam_id (str): Camera ID for looking up camera name

    Returns:
        None

    Raises:
        KeyError: If camera_id not found in cam_load
    """
    try:
        mycaption = f"Camera: {cam_load[cam_id]['SynoName']}"
        with open(videofile, "rb") as video:
            tg_bot.send_video(chat_id, video, None, None, None, None, mycaption)
        log.info(f"Video sent to Telegram for camera {cam_id}")
    except FileNotFoundError:
        log.error(f"Video file not found: {videofile}")
    except KeyError:
        log.error(f"Camera {cam_id} not found in configuration")
    except Exception as e:
        log.error(f"Failed to send video to Telegram: {e}")


def firstStart():
    """Initialize first start - authenticate with Synology and fetch camera configuration

    This function:
    1. Authenticates with Synology using provided credentials
    2. Fetches all camera configurations from Surveillance Station
    3. Saves the configuration to a JSON file
    4. Sends the configuration details to Telegram for verification

    Returns:
        None

    Raises:
        SystemExit: If authentication or configuration fetch fails
    """
    global syno_sid, cam_load

    try:
        log.info("Starting Synology authentication...")

        # Authenticate with Synology
        auth_params = {
            "api": "SYNO.API.Auth",
            "version": "7",
            "method": "login",
            "account": syno_login,
            "passwd": syno_pass,
            "session": "SurveillanceStation",
            "format": "cookie12",
        }

        if syno_otp:
            auth_params["otp_code"] = syno_otp
            log.info("Using two-factor authentication (OTP)")

        response = requests.get(syno_url, params=auth_params, timeout=API_TIMEOUT)
        response.raise_for_status()
        auth_data = response.json()

        if not auth_data.get("success"):
            log.error(
                f'Authentication failed: {auth_data.get("error", "Unknown error")}'
            )
            sys.exit(1)

        sid = auth_data["data"]["sid"]
        syno_sid = sid
        log.info(f"Successfully authenticated with Synology (SID: {sid[:20]}...)")

        # Fetch cameras configuration
        camera_params = {
            "api": "SYNO.SurveillanceStation.Camera",
            "_sid": sid,
            "version": "9",
            "method": "List",
        }

        response = requests.get(syno_url, params=camera_params, timeout=API_TIMEOUT)
        response.raise_for_status()
        cameras_data = response.json()

        if not cameras_data.get("success"):
            log.error(
                f'Failed to get cameras: {cameras_data.get("error", "Unknown error")}'
            )
            sys.exit(1)

        cameras = cameras_data.get("data", {}).get("cameras", [])
        log.info(f"Found {len(cameras)} camera(s)")

        # Build config from camera list
        data = {}
        cam_conf_text = ""

        for camera in cameras:
            cam_id = camera["id"]
            data[cam_id] = {
                "CamId": cam_id,
                "IP": camera.get("ip", "N/A"),
                "SynoName": camera.get("newName", "Unknown"),
                "Model": camera.get("model", "N/A"),
                "Vendor": camera.get("vendor", "N/A"),
            }
            cam_conf_text += (
                f"CamId: {cam_id} "
                f"IP: {camera.get('ip', 'N/A')} "
                f"SynoName: {camera.get('newName', 'Unknown')} "
                f"Model: {camera.get('model', 'N/A')} "
                f"Vendor: {camera.get('vendor', 'N/A')}\n"
            )

        data["SynologyAuthSid"] = sid
        cam_load = data

        # Save config to file
        with open(config_file, "w") as f:
            json.dump(data, f, indent=2)
        log.info(f"Configuration saved to {config_file}")

        # Send confirmation to Telegram
        mycaption = f"✅ Cameras config loaded:\n{cam_conf_text}"
        send_cammessage(mycaption)

    except requests.exceptions.Timeout:
        log.error(f"Request timeout to Synology ({API_TIMEOUT}s)")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        log.error(f"Failed to communicate with Synology: {e}")
        sys.exit(1)
    except (KeyError, json.JSONDecodeError) as e:
        log.error(f"Failed to parse Synology response: {e}")
        sys.exit(1)
    except IOError as e:
        log.error(f"Failed to write configuration file: {e}")
        sys.exit(1)


if not pathlib.Path(config_file).is_file():
    log.info("Not Found Syno config, need create")
    firstStart()

if pathlib.Path(config_file).stat().st_size == 0:
    log.info("Syno config is empty.")
    firstStart()

if pathlib.Path(config_file).stat().st_size == 0:
    log.info("Syno config always is empty. Exit.")
    sys.exit()

with open(config_file) as f:
    cam_load = json.load(f)
syno_sid = cam_load["SynologyAuthSid"]

for i in cam_load:
    arr_cam_move[i] = {"old_last_video_id": "0", "video_offset": "0"}
del arr_cam_move["SynologyAuthSid"]


def get_last_id_video(cam_id):
    """Get the last (most recent) video ID for a camera from Synology

    Args:
        cam_id (str): Camera ID from configuration

    Returns:
        str: Video ID if successful, None if failed

    Raises:
        None (returns None on error and logs the error)
    """
    try:
        response = requests.get(
            syno_url,
            params={
                "version": "6",
                "cameraIds": cam_id,
                "api": "SYNO.SurveillanceStation.Recording",
                "toTime": "0",
                "offset": "0",
                "limit": "1",
                "fromTime": "0",
                "method": "List",
                "_sid": syno_sid,
            },
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        take_video_id = response.json()["data"]["recordings"][0]["id"]
        log.debug(f"Got video ID for camera {cam_id}: {take_video_id}")
        return take_video_id
    except requests.exceptions.RequestException as e:
        log.error(f"Failed to get video ID for camera {cam_id}: {e}")
        return None
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        log.error(f"Failed to parse video response for camera {cam_id}: {e}")
        return None


def get_last_video(video_id, offset):
    """Download a video segment from Synology and save to temporary file

    Args:
        video_id (str): Video ID from Synology
        offset (str): Offset in milliseconds for segmented playback

    Returns:
        bool: True if successful, False if failed
    """
    try:
        response = requests.get(
            syno_url + "/temp.mp4",
            params={
                "id": video_id,
                "version": "6",
                "mountId": "0",
                "api": "SYNO.SurveillanceStation.Recording",
                "method": "Download",
                "offsetTimeMs": offset,
                "playTimeMs": VIDEO_SEGMENT_DURATION,
                "_sid": syno_sid,
            },
            allow_redirects=True,
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()

        with open(VIDEO_FILE, "wb") as f:
            f.write(response.content)

        log.debug(f"Video downloaded to {VIDEO_FILE} (offset: {offset}ms)")
        return True
    except requests.exceptions.RequestException as e:
        log.error(f"Failed to download video: {e}")
        return False
    except IOError as e:
        log.error(f"Failed to write video file: {e}")
        return False


def get_alarm_camera_state(cam_id):
    """Get current alarm/motion detection state for a camera

    Args:
        cam_id (str): Camera ID from configuration

    Returns:
        int: 1 if alarm is active, 0 otherwise
    """
    try:
        response = requests.get(
            syno_url,
            params={
                "version": "1",
                "id_list": cam_id,
                "api": "SYNO.SurveillanceStation.Camera.Status",
                "method": "OneTime",
                "_sid": syno_sid,
            },
            timeout=API_TIMEOUT,
        )
        response.raise_for_status()
        take_alarm = response.json()["data"]["CamStatus"]
        alarm_state = take_alarm.replace("[", "").replace("]", "").split()[7]
        return 1 if alarm_state == "1" else 0
    except requests.exceptions.RequestException as e:
        log.error(f"Failed to get camera state for {cam_id}: {e}")
        return 0
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        log.error(f"Failed to parse camera state for {cam_id}: {e}")
        return 0


app = Flask(__name__)


@app.route("/webhookcam", methods=["POST"])
def webhookcam():
    """Handle webhook from Synology Surveillance Station motion detection

    Expected JSON payload:
    {
        "idcam": "1"
    }

    Returns:
        tuple: ('success', 200) on success, or appropriate error code
    """
    global arr_cam_move
    if request.method == "POST":
        try:
            # Validate input
            if not request.json or "idcam" not in request.json:
                log.error("Invalid webhook: missing idcam")
                abort(400)

            cam_id = request.json["idcam"]

            # Validate camera ID exists in config
            if cam_id not in cam_load:
                log.error(f"Received webhook for unknown camera: {cam_id}")
                abort(400)

            # Validate camera ID is tracked
            if cam_id not in arr_cam_move:
                log.error(f"Camera {cam_id} not in tracking list")
                abort(400)

            log.info(
                f"Received motion detection from camera {cam_id} at {time.strftime('%d.%m.%Y %H:%M:%S', time.localtime())}"
            )
            time.sleep(WEBHOOK_TIMEOUT)  # Wait before fetching video

            # Get the latest video
            last_video_id = get_last_id_video(cam_id)
            if last_video_id is None:
                log.error(f"Failed to get video for camera {cam_id}")
                abort(500)

            # Check if this is a new motion event
            if last_video_id != arr_cam_move[cam_id]["old_last_video_id"]:
                # New motion - start from beginning with pre-recording
                get_last_video(last_video_id, "0")
                mycaption = f"🔴 Motion detected: {cam_load[cam_id]['SynoName']}"
                send_cammessage(mycaption)
                arr_cam_move[cam_id]["old_last_video_id"] = last_video_id
                arr_cam_move[cam_id]["video_offset"] = 0
            else:
                # Continuous motion - get next segment
                arr_cam_move[cam_id]["video_offset"] += VIDEO_SEGMENT_DURATION
                get_last_video(last_video_id, str(arr_cam_move[cam_id]["video_offset"]))

            # Send video to Telegram
            send_camvideo(VIDEO_FILE, cam_id)

            log.debug(f"Webhook processed successfully for camera {cam_id}")
            return "success", 200
        except Exception as e:
            log.error(f"Webhook error: {e}")
            abort(500)
    else:
        abort(400)


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint

    Returns:
        dict: Status information
    """
    return {
        "status": "healthy",
        "timestamp": time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()),
        "cameras": len(cam_load) - 1,  # -1 to exclude SynologyAuthSid key
    }, 200


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == "__main__":
    log.info("=" * 70)
    log.info("Starting Synology Surveillance Station to Telegram Bridge")
    log.info("=" * 70)

    # Initialize configuration
    if not pathlib.Path(config_file).is_file():
        log.info(f"Configuration file not found, initializing...")
        firstStart()
    elif pathlib.Path(config_file).stat().st_size == 0:
        log.info(f"Configuration file is empty, initializing...")
        firstStart()
    else:
        log.info(f"Loading configuration from {config_file}")
        try:
            with open(config_file) as f:
                cam_load = json.load(f)
            syno_sid = cam_load.get("SynologyAuthSid")
            if not syno_sid:
                log.warning("SynologyAuthSid not found in config, reinitializing...")
                firstStart()
            else:
                log.info(f"Loaded configuration with {len(cam_load) - 1} camera(s)")
        except (IOError, json.JSONDecodeError) as e:
            log.error(f"Failed to load configuration: {e}")
            firstStart()

    # Initialize camera tracking
    for cam_id in cam_load:
        if cam_id != "SynologyAuthSid":
            arr_cam_move[cam_id] = {"old_last_video_id": "0", "video_offset": "0"}

    log.info(f"Tracking {len(arr_cam_move)} camera(s)")
    log.info(f"Webhook URL: http://<your-host>:7878/webhookcam")
    log.info(f"Health check: http://<your-host>:7878/health")
    log.info("=" * 70)

    # Start Flask app
    app.run(host="0.0.0.0", port=7878, debug=False)
