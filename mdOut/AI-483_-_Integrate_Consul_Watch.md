---
title: "AI-483 - Integrate Consul Watch"
source_file: "AI-483_-_Integrate_Consul_Watch.doc"
converted_date: "2025-09-17T11:24:59.017051"
format: "markdown"
---

# AI-483 - Integrate Consul Watch

# Consul Watch Sidecar Integration Guide

This page outlines the technical implementation for integrating a Consul= Watch sidecar into our Docker containers for configuration management. The= integration will provide real-time configuration updates while maintaining= backward compatibility with polling-based approaches for development envir=onments.

# # Implementation= Details

## # Environmen=t Detection Logic

We need to implement a reliable mechanism to detect whether our applicat=ion is running inside a Docker container with the sidecar available. This d=etection will determine which configuration update strategy to use.

The detection logic will look for specific environment markers and can b=e overridden with explicit configuration:

import =osimport socketdef is_docker(): """Check if running inside Docker.""" # Check for .dockerenv file docker_env = os.path.exists('/.dockerenv') # Check cgroup try: with open('/proc/self/cgroup', 'r') as f: return docker_env or 'docker' in f.read() except: return docker_envdef is_consul_watch_sidecar_available(): """Check if Consul Watch sidecar is available.""" # Check for environment variable override env_override = os.getenv("USE_CONSUL_WATCH_SIDECAR") if env_override is not None: return env_override.lower() in ("true", "yes", "1") # Check if sidecar service is available on expected port sidecar_host = os.getenv("CONSUL_WATCH_SIDECAR_HOST", "localhost") sidecar_port = int(os.getenv("CONSUL_WATCH_SIDECAR_PORT", "8501")) try: s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) s.settimeout(0.5) s.connect((sidecar_host, sidecar_port)) s.close() return True except: return False

This detection should be added to the environment module and used during= application initialization.

## # BaseConf=ig Class Enhancements

The BaseConfig class needs to be updated to use our detection logic. We'=ll modify the `__init__` method to intelligently choose between =watch-based and polling-based approaches:

# Updat=e in baseConfig.pyfrom aiplus.core.env import is_consul_watch_sidecar_availabledef __init__( self, service_name: str, write_defaults: bool = True, auto_refresh: bool = False, refresh_interval: int = DEFAULT_REFRESH_INTERVAL): # Existing initialization code... # Determine configuration update strategy use_consul_watch = os.getenv("USE_CONSUL_WATCH", "false").lower() in =("true", "yes", "1") # Use environment detection if not explicitly configured if not use_consul_watch: use_consul_watch = is_consul_watch_sidecar_available() # Set up appropriate refresh mechanism if use_consul_watch: self._setup_consul_watch() logger.info( "Using Consul Watch for configuration updates", CoreEventAttributes.SERVICE_NAME, self.service_name ) elif auto_refresh: self._setup_polling_refresh() logger.info( "Using polling for configuration updates", CoreEventAttributes.SERVICE_NAME, self.service_name, "RefreshInterval", self._refresh_interval )

## # Consul= Watch Sidecar Development

The sidecar container will be responsible for watching Consul and forwar=ding updates to our application. We'll create a lightweight HTTP server tha=t our application can register with:

# consu=l_watch_sidecar.pyimport osimport jsonimport asyncioimport loggingfrom aiohttp import webimport consul.aio# Configure logginglogging.basicConfig(level=logging.INFO)logger = logging.getLogger("consul-watch-sidecar")# Environment configurationCONSUL_HOST = os.getenv("CONSUL_HOST", "localhost")CONSUL_PORT = int(os.getenv("CONSUL_PORT", "8500"))CONSUL_SCHEME = os.getenv("CONSUL_SCHEME", "http")CONSUL_TOKEN = os.getenv("CONSUL_TOKEN", None)SIDECAR_PORT = int(os.getenv("CONSUL_WATCH_SIDECAR_PORT", "8501"))# In-memory storage of registered services and callbacksregistered_watches = {}async def watch_key_prefix(prefix, callback_urls): """Watch a Consul key prefix and notify registered callbacks.""" client = consul.aio.Consul( host=CONSUL_HOST, port=CONSUL_PORT, scheme=CONSUL_SCHEME, token=CONSUL_TOKEN ) index = None while True: try: index, data = await client.kv.get( prefix, recurse=True, index=index ) if data: logger.info(f"Configuration change detected for prefix {pre=fix}") # Notify all registered callbacks for url in callback_urls: try: async with aiohttp.ClientSession() as session: async with session.post(url, json=data) as re=sponse: if response.status != 200: logger.error(f"Error notifying {url}: {=response.status}") except Exception as e: logger.error(f"Failed to notify {url}: {str(e)}") except Exception as e: logger.error(f"Error watching {prefix}: {str(e)}") await asyncio.sleep(5) # Backoff on error# API Routesasync def register_watch(request): """Register a new watch callback.""" data = await request.json() prefix = data.get('prefix') callback_url = data.get('callback_url') if not prefix or not callback_url: return web.json_response( {"error": "Both prefix and callback_url are required"}, status=400 ) if prefix not in registered_watches: registered_watches[prefix] = set() # Start watching this prefix asyncio.create_task(watch_key_prefix(prefix, registered_watches[pre=fix])) registered_watches[prefix].add(callback_url) logger.info(f"Registered watch for {prefix} with callback {callback_url=}") return web.json_response({"status": "registered"})async def deregister_watch(request): """Deregister a watch callback.""" data = await request.json() prefix = data.get('prefix') callback_url = data.get('callback_url') if not prefix or not callback_url: return web.json_response( {"error": "Both prefix and callback_url are required"}, status=400 ) if prefix in registered_watches and callback_url in registered_watches[=prefix]: registered_watches[prefix].remove(callback_url) logger.info(f"Deregistered watch for {prefix} with callback {callba=ck_url}") return web.json_response({"status": "deregistered"})async def health_check(request): """Simple health check endpoint.""" return web.json_response({ "status": "healthy", "watches_count": sum(len(callbacks) for callbacks in registered_wat=ches.values()) })# App initializationapp = web.Application()app.add_routes([ web.post('/register', register_watch), web.post('/deregister', deregister_watch), web.get('/health', health_check)])if __name__ == '__main__': web.run_app(app, port=SIDECAR_PORT)

## # WatchMana=ger Implementation

We need to update the watch manager to support communicating with the si�car:python

# watch=Manager.pyimport osimport aiohttpimport asyncioimport threadingfrom typing import Callable, Dict, Set, Anyfrom aiplus.core.log.logger import get_loggerfrom aiplus.core.log.eventAttributes import CoreEventAttributeslogger = get_logger(__name__)class WatchManager: """ Manages Consul watch registrations and callbacks. Supports both direct Consul watches and sidecar-based watches. """ def __init__(self): self._callbacks = {} self._lock = threading.RLock() self._sidecar_host = os.getenv("CONSUL_WATCH_SIDECAR_HOST", "loca=lhost") self._sidecar_port = int(os.getenv("CONSUL_WATCH_SIDECAR_PORT", "�01")) self._use_sidecar = os.getenv("USE_CONSUL_WATCH", "false").lower(=) in ("true", "yes", "1") # Get service information for callback URL self._service_host = os.getenv("HOST", "localhost") self._service_port = int(os.getenv("PORT", "8000")) # Sidecar registration state self._registered_with_sidecar = set() def register_callback(self, prefix: str, callback: Callable[[Any], None=]) -> bool: """ Register a callback for a Consul key prefix. Args: prefix: Consul key prefix to watch callback: Callback function to invoke on changes Returns: True if registration was successful, False otherwise """ with self._lock: if prefix not in self._callbacks: self._callbacks[prefix] = set() self._callbacks[prefix].add(callback) # If using sidecar, register with it if self._use_sidecar: success = self._register_with_sidecar(prefix) if success: self._registered_with_sidecar.add(prefix) return success return True def _register_with_sidecar(self, prefix: str) -> bool: """ Register a watch with the sidecar. Args: prefix: Consul key prefix to watch Returns: True if registration was successful, False otherwise """ try: # Construct callback URL the sidecar will use to notify us callback_url = f"http://{self._service_host}:{self._service_p=ort}/api/config/watch-update" # Register with sidecar response = requests.post( f"http://{self._sidecar_host}:{self._sidecar_port}/register=", json={"prefix": prefix, "callback_url": callback_url}, timeout=5 ) if response.status_code == 200: logger.info( "Registered with Consul Watch sidecar", "Prefix", prefix, "CallbackURL", callback_url ) return True else: logger.error( "Failed to register with Consul Watch sidecar", "Prefix", prefix, "StatusCode", response.status_code, "Response", response.text ) return False except Exception as e: logger.error( "Error registering with Consul Watch sidecar", "Prefix", prefix, CoreEventAttributes.ERROR_MESSAGE, str(e) ) return False def handle_watch_update(self, prefix: str, data: Any) -> None: """ Handle a watch update from Consul or the sidecar. Args: prefix: Consul key prefix that was updated data: Updated data """ with self._lock: if prefix in self._callbacks: for callback in self._callbacks[prefix]: try: callback(data) except Exception as e: logger.error( "Error in watch callback", "Prefix", prefix, CoreEventAttributes.ERROR_MESSAGE, str(e) )# Singleton instancewatch_manager = WatchManager()

## # Docker Co=mpose Configuration

Here's a sample Docker Compose configuration that includes the sidecar:y=aml

version=: '3.8'services: app: image: aiplus/myservice:latest environment: - CONSUL_HOST=consul - CONSUL_PORT=8500 - USE_CONSUL_WATCH=true - CONSUL_WATCH_SIDECAR_HOST=consul-watch-sidecar - CONSUL_WATCH_SIDECAR_PORT=8501 depends_on: consul-watch-sidecar: condition: service_healthy networks: - aiplus-network consul-watch-sidecar: image: aiplus/consul-watch-sidecar:latest environment: - CONSUL_HOST=consul - CONSUL_PORT=8500 - CONSUL_TOKEN=${CONSUL_TOKEN} depends_on: consul: condition: service_healthy healthcheck: test: ["CMD", "curl", "-f", "http://localhost:8501/health"] interval: 10s timeout: 5s retries: 3 networks: - aiplus-network consul: image: consul:latest ports: - "8500:8500" volumes: - consul-data:/consul/data networks: - aiplus-network healthcheck: test: ["CMD", "consul", "members"] interval: 10s timeout: 5s retries: 3networks: aiplus-network:volumes: consul-data:

## # Kub=ernetes Implementation \(Future\)

For Kubernetes, we'll use a sidecar container pattern:

apiVers=ion: apps/v1kind: Deploymentmetadata: name: aiplus-servicespec: replicas: 3 selector: matchLabels: app: aiplus-service template: metadata: labels: app: aiplus-service spec: containers: - name: aiplus-service image: aiplus/myservice:latest env: - name: CONSUL_HOST value: "consul.service.consul" - name: CONSUL_PORT value: "8500" - name: USE_CONSUL_WATCH value: "true" - name: CONSUL_WATCH_SIDECAR_HOST value: "localhost" - name: CONSUL_WATCH_SIDECAR_PORT value: "8501" ports: - containerPort: 8000 readinessProbe: httpGet: path: /health port: 8000 initialDelaySeconds: 5 periodSeconds: 10 - name: consul-watch-sidecar image: aiplus/consul-watch-sidecar:latest env: - name: CONSUL_HOST value: "consul.service.consul" - name: CONSUL_PORT value: "8500" - name: CONSUL_TOKEN valueFrom: secretKeyRef: name: consul-secrets key: token ports: - containerPort: 8501 livenessProbe: httpGet: path: /health port: 8501 initialDelaySeconds: 5 periodSeconds: 10

## # Testing Implem=entation

Here's a sample test script to verify the integration:

import =unittestimport osimport timefrom unittest.mock import patch, MagicMockfrom aiplus.core.config.baseConfig import BaseConfigfrom aiplus.core.env import is_consul_watch_sidecar_availableclass TestConsulWatchIntegration(unittest.TestCase): def setUp(self): # Set up environment for tests os.environ["CONSUL_HOST"] = "localhost" os.environ["CONSUL_PORT"] = "8500" # Clear any previous settings if "USE_CONSUL_WATCH" in os.environ: del os.environ["USE_CONSUL_WATCH"] if "USE_CONSUL_WATCH_SIDECAR" in os.environ: del os.environ["USE_CONSUL_WATCH_SIDECAR"] def test_environment_detection(self): # Test Docker environment detection with patch('os.path.exists', return_value=True): self.assertTrue(is_docker()) # Test sidecar availability detection with patch('socket.socket') as mock_socket: mock_socket.return_value.connect.return_value = None self.assertTrue(is_consul_watch_sidecar_available()) with patch('socket.socket') as mock_socket: mock_socket.return_value.connect.side_effect = ConnectionRefu=sedError self.assertFalse(is_consul_watch_sidecar_available()) @patch('aiplus.core.config.baseConfig.BaseConfig._setup_consul_watch') @patch('aiplus.core.config.baseConfig.BaseConfig._setup_polling_refresh=') @patch('aiplus.core.env.is_consul_watch_sidecar_available') def test_config_initialization_with_sidecar(self, mock_sidecar_availabl=e, mock_setup_polling, mock_setu=p_watch): # Test that watch is used when sidecar is available mock_sidecar_available.return_value = True config = BaseConfig("test-service", auto_refresh=True) mock_setup_watch.assert_called_once() mock_setup_polling.assert_not_called() @patch('aiplus.core.config.baseConfig.BaseConfig._setup_consul_watch') @patch('aiplus.core.config.baseConfig.BaseConfig._setup_polling_refresh=') @patch('aiplus.core.env.is_consul_watch_sidecar_available') def test_config_initialization_without_sidecar(self, mock_sidecar_avail�le, mock_setup_polling, mock_s=etup_watch): # Test that polling is used when sidecar is not available mock_sidecar_available.return_value = False config = BaseConfig("test-service", auto_refresh=True) mock_setup_watch.assert_not_called() mock_setup_polling.assert_called_once() @patch('aiplus.core.config.baseConfig.BaseConfig._setup_consul_watch') @patch('aiplus.core.config.baseConfig.BaseConfig._setup_polling_refresh=') def test_environment_override(self, mock_setup_polling, mock_setup_watc=h): # Test that environment variable overrides detection os.environ["USE_CONSUL_WATCH"] = "true" config = BaseConfig("test-service", auto_refresh=True) mock_setup_watch.assert_called_once() mock_setup_polling.assert_not_called()if __name__ == '__main__': unittest.main()

# # Development Plan

To ensure a smooth transition, we'll follow this migration plan:

1. Deploy the Consul Watch sidecar alongside existing services without enab=ling it \(USE\_CONSUL\_WATCH=false\)

2. Update the AI+ Common library with the new detection logic and enhanceme=nts

3. Enable the sidecar for a small subset of non-critical services in develo=pment and staging

4. Monitor performance and resource usage metrics to ensure the approach is= working correctly

5. Gradually roll out to all services in production

6. Update documentation and developer guides to reflect the new approach