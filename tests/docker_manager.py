import docker
import docker.errors
import docker.models.containers
from typing import Optional, List


class DockerContainerManager:
    def __init__(self):
        self.client = docker.from_env()

    def run_container(
        self,
        image: str,
        detach,
        name: Optional[str] = None,
        network: Optional[str] = None,
        hostname: Optional[str] = None,
    ):
        try:
            container = self.client.containers.run(
                image,
                entrypoint="sleep infinity",
                detach=detach,
                name=name,
                network=network,
                hostname=hostname,
            )

            print(f"start: {container.name}")
            return container
        except docker.errors.ImageNotFound:
            print(f"image {image} is not found, pulling...")
            self.client.images.pull(image)
            return self.run_container(image, name, network, hostname, detach)
        except Exception as e:
            print(f"error when starting container: {str(e)}")
            raise

    def list_containers(
        self, all_c: bool = False
    ) -> List[docker.models.containers.Container]:
        return self.client.containers.list(all=all_c)

    def stop_container(self, container_id: str) -> None:
        try:
            container = self.client.containers.get(container_id)
            container.stop()
            print(f"container{container_id} is stopped")
        except Exception as e:
            print(f"error when stopping container: {str(e)}")
            raise

    def remove_container(self, container_id: str, force: bool = False) -> None:
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=force)
            print(f"container {container_id} is removed")
        except Exception as e:
            print(f"error when removing container: {str(e)}")
            raise
