 
# PVOutput Tariff
This project is a Python-based utility that helps to determine the current tariff for a given configuration and send the price to PVOutput.

## Docker Instructions

This project can also be run using Docker. The Docker image is hosted at `ghcr.io/adampetrovic/pvoutput-tariff` using the `latest` tag.

To pull the Docker image, use the following command:

```bash
docker pull ghcr.io/adampetrovic/pvoutput-tariff:latest
```

To run the Docker image, use the following command:

```bash
docker run -it --rm -v /path/to/your/config.yaml:/config/config.yaml -e PVOUTPUT_API_KEY=your_api_key -e PVOUTPUT_SYSTEM_ID=your_system_id -e TZ=your_timezone ghcr.io/adampetrovic/pvoutput-tariff:latest
```

Replace `/path/to/your/config.yaml` with the path to your `config.yaml` file, and `your_api_key`, `your_system_id`, and `your_timezone` with your actual PVOutput API key, system ID, and timezone respectively.

An [example config.yaml](test/config.yaml) example config.yaml can be found here.

The `-v /path/to/your/config.yaml:/config/config.yaml` part of the command mounts your local `config.yaml` file to the `/config/config.yaml` path in the Docker container. This allows the application running in the Docker container to access your configuration file.
