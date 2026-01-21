#!/usr/bin/env python3
"""
Webhook server for Marxnager Bot auto-deployment
Receives GitHub webhooks and triggers Portainer stack updates
"""

from flask import Flask, request, jsonify
import subprocess
import hmac
import hashlib
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration - UPDATE THESE OR USE ENV VARIABLES
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', b'your-github-webhook-secret')
UPDATE_SCRIPT = os.environ.get('UPDATE_SCRIPT', '/usr/local/bin/update-marxnager.sh')
LOG_FILE = os.environ.get('LOG_FILE', '/var/log/webhook-server.log')

# Validate update script exists
if not os.path.exists(UPDATE_SCRIPT):
    logger.warning(f"Update script not found: {UPDATE_SCRIPT}")
    logger.warning("Webhooks will be received but deployment will fail")


def verify_signature(payload, signature):
    """Verify GitHub webhook signature"""
    if not signature:
        logger.warning("No signature provided")
        return False

    try:
        sha_name, signature = signature.split('=')
        if sha_name != 'sha256':
            logger.error(f"Unsupported hash type: {sha_name}")
            return False

        mac = hmac.new(WEBHOOK_SECRET.encode() if isinstance(WEBHOOK_SECRET, str) else WEBHOOK_SECRET,
                      payload, hashlib.sha256)

        return hmac.compare_digest(mac.hexdigest(), signature)
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False


def trigger_deployment():
    """Execute the deployment script"""
    try:
        logger.info(f"Executing deployment script: {UPDATE_SCRIPT}")
        result = subprocess.run(
            [UPDATE_SCRIPT],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0:
            logger.info("Deployment script executed successfully")
            logger.info(f"stdout: {result.stdout}")
            return True, result.stdout
        else:
            logger.error(f"Deployment script failed with code {result.returncode}")
            logger.error(f"stderr: {result.stderr}")
            return False, result.stderr

    except subprocess.TimeoutExpired:
        error_msg = "Deployment script timed out after 60 seconds"
        logger.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Failed to execute deployment script: {e}"
        logger.error(error_msg)
        return False, error_msg


@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook POST requests"""
    # Verify webhook signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, signature):
        logger.warning("Invalid webhook signature - rejecting request")
        return '', 403

    # Parse webhook event
    event_type = request.headers.get('X-GitHub-Event')
    logger.info(f"Received webhook event: {event_type}")

    # Handle push events
    if event_type == 'push':
        try:
            payload = request.json
            ref = payload.get('ref', 'unknown')
            repository = payload.get('repository', {}).get('name', 'unknown')
            pusher = payload.get('pusher', {}).get('name', 'unknown')

            logger.info(f"Push to {repository}:{ref} by {pusher}")

            # Only deploy pushes to main branch
            if 'refs/heads/main' in ref:
                logger.info("Push to main branch - triggering deployment")
                success, message = trigger_deployment()

                if success:
                    return jsonify({
                        'status': 'success',
                        'message': 'Deployment triggered',
                        'details': message
                    }), 200
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'Deployment failed',
                        'details': message
                    }), 500
            else:
                logger.info(f"Not a main branch push ({ref}), skipping deployment")
                return jsonify({'status': 'ignored', 'reason': 'Not main branch'}), 200

        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

    elif event_type == 'ping':
        logger.info("Received ping event from GitHub")
        return jsonify({'status': 'pong'}), 200

    else:
        logger.info(f"Ignoring event type: {event_type}")
        return jsonify({'status': 'ignored', 'event': event_type}), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'update_script': UPDATE_SCRIPT,
        'script_exists': os.path.exists(UPDATE_SCRIPT)
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Root endpoint with usage info"""
    return jsonify({
        'service': 'Marxnager Bot Webhook Server',
        'version': '1.0.0',
        'endpoints': {
            '/webhook': 'POST - GitHub webhook endpoint',
            '/health': 'GET - Health check'
        }
    }), 200


if __name__ == '__main__':
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting webhook server on port {port}")
    logger.info(f"Update script: {UPDATE_SCRIPT}")
    app.run(host='0.0.0.0', port=port)
