from kubernetes import client, config, watch
import time, atexit, datetime, pytz
# Configs can be set in Configuration class directly or using helper utility
config.load_kube_config()
RELOADER_ANNOT = "reloader.sh/reload-on-change"
INTERVAL = 3
resource_tracker = {}

coreV1 = client.CoreV1Api()
appV1 = client.AppsV1Api()

def exit_handler():
    print("exiting, wiping out resource tracker dict. Will populate again on start up. Bye now")
    print(resource_tracker)

def restart_deployment(namespace_name, deployment_name):

    deployment = appV1.read_namespaced_deployment(deployment_name, namespace_name)
    print(deployment)

    deployment.spec.template.metadata.annotations = {
        "kubectl.kubernetes.io/restartedAt": datetime.datetime.utcnow()
        .replace(tzinfo=pytz.UTC)
        .isoformat()
    }

    # patch the deployment
    resp = appV1.patch_namespaced_deployment(
        name=deployment_name, namespace=namespace_name, body=deployment
    )
    print(resp)
    print("\n[INFO] deployment `deployment_name` restarted.\n")


atexit.register(exit_handler)


while(True):
    time.sleep(INTERVAL)
    result = coreV1.list_config_map_for_all_namespaces()
    for item in result.items:
        if not item.metadata.annotations:
            continue

        reloader_annot_exists = item.metadata.annotations.get(RELOADER_ANNOT, "None") != "None"
        if(reloader_annot_exists):

            if(resource_tracker.get(item.metadata.name)):
                tracked = resource_tracker.get(item.metadata.name)
                print(f"already tracking this configmap. Checking with change since last run time")
                print(f"stored resource version: {tracked.get('version')}. incoming version {item.metadata.resource_version}")
                
                if(tracked.get('version') == item.metadata.resource_version):
                    print("no change. no restart required")
                    continue
                print("new version detected. Updating necessary deployments")
                # update deployment here 
                tracked_annot_values = tracked['annot_values']
                deployments = tracked_annot_values.split(',')

                for deployment in deployments:
                    [namespace_name, deployment_name] = deployment.split('/')
                    restart_deployment(namespace_name, deployment_name)                
                # update tracker with new verson
                resource_tracker[item.metadata.name]['version'] = item.metadata.resource_version
                resource_tracker[item.metadata.name]['annot_values'] = item.metadata.annotations.get(RELOADER_ANNOT)
            
            print(f"found {item.metadata.name} confimap in {item.metadata.namespace} namespace with annotations")
            resource_tracker[item.metadata.name] = {
                "version" : item.metadata.resource_version,
                "annot_values": item.metadata.annotations.get(RELOADER_ANNOT)
            }


