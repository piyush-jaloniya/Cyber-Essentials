"""Secure token storage using OS-native credential stores"""
import os
import sys
import platform
import logging

logger = logging.getLogger(__name__)

# Token storage configuration
TOKEN_STORE_NAME = "ce-agent-token"
TOKEN_STORE_USERNAME = "ce-agent"


def store_token(token: str):
    """Store agent token securely using OS-native credential store"""
    system = platform.system()
    
    try:
        if system == "Windows":
            # Use Windows DPAPI via keyring
            import keyring
            keyring.set_password(TOKEN_STORE_NAME, TOKEN_STORE_USERNAME, token)
            logger.info("Token stored securely using Windows Credential Manager")
        
        elif system == "Darwin":  # macOS
            # Use macOS Keychain via keyring
            import keyring
            keyring.set_password(TOKEN_STORE_NAME, TOKEN_STORE_USERNAME, token)
            logger.info("Token stored securely using macOS Keychain")
        
        else:  # Linux
            try:
                # Try using keyring (supports multiple backends)
                import keyring
                keyring.set_password(TOKEN_STORE_NAME, TOKEN_STORE_USERNAME, token)
                logger.info("Token stored securely using system keyring")
            except Exception as e:
                # Fallback to file with restricted permissions
                logger.warning(f"Keyring not available ({e}), using file storage")
                store_token_file(token)
    
    except Exception as e:
        logger.error(f"Failed to store token: {e}")
        raise


def get_token() -> str:
    """Retrieve agent token from secure storage"""
    system = platform.system()
    
    try:
        if system in ["Windows", "Darwin"]:
            import keyring
            token = keyring.get_password(TOKEN_STORE_NAME, TOKEN_STORE_USERNAME)
            return token
        
        else:  # Linux
            try:
                import keyring
                token = keyring.get_password(TOKEN_STORE_NAME, TOKEN_STORE_USERNAME)
                return token
            except Exception:
                # Fallback to file storage
                return get_token_file()
    
    except Exception as e:
        logger.error(f"Failed to retrieve token: {e}")
        return None


def clear_token():
    """Clear stored token"""
    system = platform.system()
    
    try:
        if system in ["Windows", "Darwin"]:
            import keyring
            keyring.delete_password(TOKEN_STORE_NAME, TOKEN_STORE_USERNAME)
            logger.info("Token cleared from secure storage")
        
        else:  # Linux
            try:
                import keyring
                keyring.delete_password(TOKEN_STORE_NAME, TOKEN_STORE_USERNAME)
                logger.info("Token cleared from secure storage")
            except Exception:
                # Fallback to file storage
                clear_token_file()
    
    except Exception as e:
        logger.warning(f"Failed to clear token: {e}")


# Fallback file-based storage for Linux
def get_token_file_path() -> str:
    """Get path to token file"""
    if os.name == 'nt':
        base_dir = os.path.join(os.environ['APPDATA'], 'CyberEssentials')
    else:
        base_dir = os.path.expanduser('~/.config/cyber-essentials')
    
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, '.agent_token')


def store_token_file(token: str):
    """Store token in file with restricted permissions"""
    token_file = get_token_file_path()
    
    # Write token to file
    with open(token_file, 'w') as f:
        f.write(token)
    
    # Set restrictive permissions (owner read/write only)
    if os.name != 'nt':
        os.chmod(token_file, 0o600)
    
    logger.info(f"Token stored in file: {token_file}")


def get_token_file() -> str:
    """Retrieve token from file"""
    token_file = get_token_file_path()
    
    if not os.path.exists(token_file):
        return None
    
    with open(token_file, 'r') as f:
        return f.read().strip()


def clear_token_file():
    """Clear token file"""
    token_file = get_token_file_path()
    
    if os.path.exists(token_file):
        os.remove(token_file)
        logger.info(f"Token file removed: {token_file}")
