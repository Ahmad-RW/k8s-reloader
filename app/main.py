from kubernetes import client, config
import time, atexit, datetime, pytz
from enum import Enum
import this

# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
RELOADER_ANNOT = "reloader.sh/reload-on-change"
INTERVAL = 3
DEBUG_MODE = True
class LogLevel(Enum):
    info = "INFO"
    debug = "DEBUG"
    error = "ERROR"

resource_tracker = {}

coreV1 = client.CoreV1Api()
appV1 = client.AppsV1Api()

def log(text, level = LogLevel.info.value):
    if level == LogLevel.debug.value and not DEBUG_MODE:
        return
    
    print(f"\n [{level}] {text}")

def exit_handler():
    log("exiting, wiping out resource tracker dict. Will populate again on start up. Bye now")
    log(resource_tracker, LogLevel.debug.value)

def restart_deployment(namespace_name, deployment_name):
    try:
        deployment = appV1.read_namespaced_deployment(deployment_name, namespace_name)
        log(deployment, LogLevel.debug.value)

        deployment.spec.template.metadata.annotations = {
            "kubectl.kubernetes.io/restartedAt": datetime.datetime.utcnow()
            .replace(tzinfo=pytz.UTC)
            .isoformat()
        }

        # patch the deployment
        resp = appV1.patch_namespaced_deployment(
            name=deployment_name, namespace=namespace_name, body=deployment
        )
        log(resp, LogLevel.debug.value)
        log("deployment {deployment_name} restarted.\n")
    except Exception as error:
        log(f"Faced Error when attempting to restart deployment {deployment_name} error : {error}", LogLevel.error.value)

atexit.register(exit_handler)


while(True):
    log(resource_tracker, LogLevel.debug.value)
    time.sleep(INTERVAL)
    result = coreV1.list_config_map_for_all_namespaces()
    for item in result.items:
        if not item.metadata.annotations:
            continue

        reloader_annot_exists = item.metadata.annotations.get(RELOADER_ANNOT, "None") != "None"
        if(reloader_annot_exists):

            if(resource_tracker.get(item.metadata.name)):
                tracked = resource_tracker.get(item.metadata.name)
                log(f"already tracking this configmap. Checking with change since last run time")
                log(f"stored resource version: {tracked.get('version')}. incoming version {item.metadata.resource_version}")
                
                if(tracked.get('version') == item.metadata.resource_version):
                    log("no change. no restart required")
                    continue
                log("new version detected. Updating necessary deployments")
                # update deployment here 
                tracked_annot_values = tracked['annot_values']
                deployments = tracked_annot_values.split(',')

                for deployment in deployments:
                    [namespace_name, deployment_name] = deployment.split('/')
                    restart_deployment(namespace_name, deployment_name)                
                # update tracker with new verson
                resource_tracker[item.metadata.name]['version'] = item.metadata.resource_version
                resource_tracker[item.metadata.name]['annot_values'] = item.metadata.annotations.get(RELOADER_ANNOT)
            
            log(f"found {item.metadata.name} confimap in {item.metadata.namespace} namespace with annotations")
            resource_tracker[item.metadata.name] = {
                "version" : item.metadata.resource_version,
                "annot_values": item.metadata.annotations.get(RELOADER_ANNOT)
            }


