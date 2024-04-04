# Address Book
Address Book application that allows the users to list, create, edit, and delete an address. Users can also search for all addresses given a coordinates and a distance.

## Local Development with Docker
### Set-up
The Docker version used for this is `version 24.0.6, build tag v24.0.6`
You only need to do this once unless you have changes in the `Dockerfile`.

1. Build the Docker image.
```
docker build . -t address-book-img
```

2. Create a Docker container using the built image. Any changes saved to the code will reload this container.
```
docker create --name address-book -p 8080:8080 --mount type=bind,source=$(pwd),target=/code address-book-img
```

### Running the application
0. Make sure you have finished creating the Docker image and container before doing the next steps.
1. Start the created Docker container to run the app.
```
docker container start address-book
```

2. Visit the docs at http://localhost:8080/docs

#### Other useful commands
- You can also run the tests via `pytest`
```
docker exec -it address-book pytest
```

- To check the logs:
```
docker logs -f address-book
```

- You can stop the container by using the following command
```
docker stop address-book
```

## Local Development without Docker
### Set-up
The app uses python `3.12.0`; there might be errors if you are using an older version.

1. Once you are in the root directory of the repository, create a virtualenv.
```
python -m venv .venv
```

2. Activate the virtualenv to isolate this repository. There should be an indicator in your terminal that you have activated the virtualenv.
```
source .venv/bin/activate
```

### Running the application
0. For the succeeding steps, make sure you have activated the virtualenv.
1. Install the dependencies.
```
pip install -r requirements.txt
```

2. Run the web app. Hotloading is also enabled for this set-up.
```
uvicorn app.main:app --reload --port 8080
```

#### Other useful commands
- You can also run tests via pytest
```
pytest
```

- To get out of the virtualenv, use the following command. The indicator should be removed after this.
```
deactivate
```
