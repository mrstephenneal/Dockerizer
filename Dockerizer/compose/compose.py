import os

from looptools import Timer
from RuntimeWatch import TaskTracker
from dirutility import SystemCommand

from Dockerizer.compose.commands import DockerComposeCommands


class DockerCompose(TaskTracker):
    def __init__(self, directory=os.getcwd(), services=None):
        """
        Docker compose command wrapper.

        :param services: List of services to build
        """
        self._starting_directory = os.getcwd()
        self.directory = directory
        self.cmd = DockerComposeCommands(services)

        # Change to target directory
        os.chdir(self.directory)

    def __exit__(self):
        os.chdir(self._starting_directory)

    def pull(self):
        """Pull docker-compose images from Docker Hub."""
        print('Pulling Docker images')
        sc = SystemCommand(self.cmd.pull, decode_output=False)
        self.add_command(sc.command)
        self.add_task('Pulled docker-compose service images')

    def build(self):
        """Build a docker image for distribution to DockerHub."""
        print('Building docker-compose services')
        sc = SystemCommand(self.cmd.build, decode_output=False)
        self.add_command(sc.command)
        self.add_task('Built docker-compose services')

    def up(self):
        """Run docker-compose services locally."""
        print('Running docker-compose services locally')
        sc = SystemCommand(self.cmd.up, decode_output=False)
        self.add_command(sc.command)
        if sc.success:
            self.add_task('SUCCESS: Running docker-compose services locally')
        else:
            self.add_task('ERROR: Unable to running docker-compose services')

    def down(self):
        """Push a docker image to a DockerHub repo."""
        print('Stopping docker-compose services')
        sc = SystemCommand(self.cmd.down, decode_output=False)
        self.add_command(sc.command)
        self.add_task('Stopped docker-compose services')

    @Timer.decorator
    def bootstrap(self):
        """
        Bootstrap docker-compose service development by pulling existing images then building services.

        1. Pull existing images for docker-compose services
        2. Build fresh docker images for services with build contexts
        3. Stop running containers and replace with new builds
        """
        print('Bootstrapping docker-compose services')
        for cmd in (self.cmd.pull, self.cmd.up(detached=True), self.cmd.build, self.cmd.down(volumes=True)):
            sc = SystemCommand(cmd, decode_output=True)
            self.add_command(sc.command)
            if sc.success:
                self.add_task('SUCCESS: {}'.format(sc.command))
            else:
                self.add_task('ERROR: {}'.format(sc.command))
